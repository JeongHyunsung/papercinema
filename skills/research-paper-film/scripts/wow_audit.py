"""Peak ("wow") audit: does each planned peak actually land? (quality bar W1-W7)

Reads the peak plan exported by peak_kit.PeakPlan.export(), and optionally the
video, the sound-cue times, the narration placement and the claim ledger.

  python3 wow_audit.py --peaks out/peaks.json --video out/preview.mp4 \\
      --cues out/audio/cues.json --placement out/audio/placement.json \\
      --ledger docs/CLAIM_LEDGER.md --json out/wow.json
  python3 gate.py ... --wow out/wow.json          # adds the W rows to the gates

  W1  plan      3-6 peaks; >= 1 concept and >= 1 result; >= 8 s apart;
                first peak by max(20 s, 20 % of the film)               (WARN for the last)
  W2  reveal    the reveal is the biggest change of its peak: the max per-frame change
                in [reveal - 0.1, reveal + 0.6] is >= 2.5x the median change of the
                setup window and >= 4 % of the frame                    (needs --video)
  W3  hold      after the reveal, no other change as big as 0.6x the reveal spike
                before t_hold (one change at a time)                     (WARN; --video)
  W4  budget    <= 2 signature breaks, each <= 6 s; and in the video no dark-stage
                second (mean luma < 110) outside a declared night/spot window
  W5  sound     a cue within 80 ms of every reveal; hits outside peaks are listed (WARN)
  W6  word      the key word starts within 0.35 s of the reveal          (needs --placement)
  W7  fidelity  every peak names a claim id that exists in the ledger; every result
                peak shows its trade-off within 12 s of the reveal

cues.json: a list of times, or {"name": t, ...}, or [{"t": ..}, ...] (film time, s).
"""
import argparse, json, re, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--peaks", required=True)
ap.add_argument("--video")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--cues")
ap.add_argument("--placement")
ap.add_argument("--ledger")
ap.add_argument("--json")
a = ap.parse_args()

plan = json.load(open(a.peaks))
P = plan["peaks"]
dur = plan.get("duration")
rows, res = [], {"gates": []}


def gate(code, status, msg):
    rows.append(f"{code:3s} {status:4s}  {msg}")
    res["gates"].append(dict(code=code, status=status, msg=msg))


# ---- W1 plan --------------------------------------------------------------
kinds = [p["kind"] for p in P]
gaps = [b["t_reveal"] - a_["t_reveal"] for a_, b in zip(P, P[1:])]
ok = 3 <= len(P) <= 6 and "concept" in kinds and "result" in kinds and all(g >= 8 for g in gaps)
gate("W1", "PASS" if ok else "FAIL",
     f"{len(P)} peaks ({', '.join(kinds)}); min gap {min(gaps) if gaps else '-'} s")
if dur and P:
    lim = max(20.0, .2 * dur)
    gate("W1", "PASS" if P[0]["t_reveal"] <= lim else "WARN",
         f"first peak at {P[0]['t_reveal']:.1f} s (hook by {lim:.0f} s)")

# ---- video measurements ----------------------------------------------------
chg = luma = None
if a.video:
    W, H = 320, 180
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-vf",
                          f"fps={a.fps},scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    chg = np.zeros(len(F))
    chg[1:] = (np.abs(np.diff(F, axis=0)) > 6).mean((1, 2))
    luma = F.mean((1, 2))
    fr = lambda t: int(round(t * a.fps))           # noqa: E731
    res["per_peak"] = []
    for p in P:
        r0, r1 = fr(p["t_reveal"] - .1), fr(p["t_reveal"] + .6)
        spike = float(chg[r0:r1 + 1].max()) if r1 > r0 else 0.0
        s0, s1 = fr(p["t_setup"]), fr(p["t_reveal"] - .6)
        base = float(np.median(chg[s0:s1])) if s1 > s0 else 0.0
        ratio = spike / max(base, 1e-4)
        ok = spike >= .04 and ratio >= 2.5
        gate("W2", "PASS" if ok else "FAIL",
             f"'{p['name']}': reveal spike {100 * spike:.1f} % vs setup median "
             f"{100 * base:.2f} % ({ratio:.1f}x)")
        h0, h1 = fr(p["t_reveal"] + .8), fr(p["t_hold"])
        after = float(chg[h0:h1].max()) if h1 > h0 else 0.0
        gate("W3", "PASS" if after < .6 * spike or after < .02 else "WARN",
             f"'{p['name']}': largest change in hold {100 * after:.1f} % (< 60 % of reveal)")
        res["per_peak"].append(dict(name=p["name"], spike=spike, setup_median=base,
                                    ratio=ratio, hold_max=after))

# ---- W4 signature budget ---------------------------------------------------
sig = [p for p in P if p.get("signature")]
lens = [p["sig_out"] - p["sig_in"] for p in sig]
ok = len(sig) <= plan.get("max_signatures", 2) and all(L <= 6.0 for L in lens)
gate("W4", "PASS" if ok else "FAIL",
     f"{len(sig)} signature breaks ({', '.join(p['signature'] for p in sig) or 'none'}); "
     f"longest {max(lens) if lens else 0:.1f} s (<= 2, <= 6 s)")
if luma is not None:
    dark = np.where(luma < 110)[0] / a.fps
    wins = [(p["sig_in"] - .5, p["sig_out"] + .5) for p in sig if p["signature"] in ("night", "spot")]
    stray = [t for t in dark if not any(w0 <= t <= w1 for w0, w1 in wins)]
    secs = sorted({int(t) for t in stray})
    gate("W4", "PASS" if not secs else "FAIL",
         f"dark-stage seconds outside declared windows: {secs[:10] if secs else 'none'}")

# ---- W5 sound -------------------------------------------------------------
if a.cues:
    c = json.load(open(a.cues))
    if isinstance(c, dict):
        times = [float(v) for v in c.values()]
    else:
        times = [float(x["t"] if isinstance(x, dict) else x) for x in c]
    times = np.array(sorted(times))
    for p in P:
        d = float(np.min(np.abs(times - p["t_reveal"]))) if len(times) else 99
        gate("W5", "PASS" if d <= .08 else "FAIL", f"'{p['name']}': nearest cue {1000 * d:.0f} ms from reveal")
    outside = [t for t in times if not any(p["t_setup"] <= t <= p["t_hold"] for p in P)]
    res["cues_outside_peaks"] = outside
    if outside:
        gate("W5", "WARN", f"{len(outside)} cues outside peaks (keep hits for peaks; ticks/thumps are fine)")

# ---- W6 key word ----------------------------------------------------------
if a.placement:
    clips = json.load(open(a.placement))["clips"]
    words = [(re.sub(r"[^a-z0-9.%]", "", w["w"].lower()), w["t0"]) for c in clips for w in c["words"]]
    for p in P:
        kw = re.sub(r"[^a-z0-9.%]", "", p["key_word"].lower())
        cand = [t for w, t in words if w == kw or w.startswith(kw)]
        d = min((abs(t - p["t_reveal"]) for t in cand), default=99)
        gate("W6", "PASS" if d <= .35 else "FAIL",
             f"'{p['name']}': key word '{p['key_word']}' {('%.2f s' % d) if cand else 'not spoken'} from reveal")

# ---- W7 fidelity ----------------------------------------------------------
led = open(a.ledger).read() if a.ledger else None
for p in P:
    msgs, ok = [], True
    if not p.get("claim"):
        ok, msgs = False, msgs + ["no claim id"]
    elif led is not None and not re.search(rf"\b{re.escape(p['claim'])}\b", led):
        ok, msgs = False, msgs + [f"claim {p['claim']} not in ledger"]
    if p["kind"] == "result":
        tt = p.get("tradeoff_t")
        if tt is None or not 0 < tt - p["t_reveal"] <= 12:
            ok, msgs = False, msgs + ["trade-off not within 12 s"]
    gate("W7", "PASS" if ok else "FAIL", f"'{p['name']}': claim {p.get('claim')}"
         + (f" ({'; '.join(msgs)})" if msgs else ""))

print("\n".join(rows))
nf = sum(g["status"] == "FAIL" for g in res["gates"])
print("WOW", "PASS" if nf == 0 else f"FAIL ({nf})")
if a.json:
    json.dump(res, open(a.json, "w"), indent=1)
sys.exit(1 if nf else 0)
