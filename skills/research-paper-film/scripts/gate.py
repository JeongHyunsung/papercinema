"""Automated gates for a film checkpoint (quality bar B1, D1-D5).

  cd src && python3 ../../scripts/gate.py --audit ../out/audit.json \\
      --videos ../out/final/NAME.mp4 ../out/final/NAME_1080p.mp4 \\
      --srt-report ../out/srt_check.txt --mix-log ../out/mix_check.txt
Any argument may be omitted; its gate is then skipped. Exit code 1 on FAIL.
  B1  readability: strings under --budget (numbers excluded; --allow REGEX for
      deliberate live readouts)
  D1  EDL: no narration overlaps, clips inside the film   (needs edl.py import)
  D2  loudness of each video: -16 +- 0.5 LUFS integrated, true peak <= -1.0
  D5  durations: video and audio streams == EDL duration (+- 0.05 s)
  D4  SRT vs delivered audio word differences (WARN above 10 %: inspect them;
      ASR spelling variants are expected)
  D3  mix intelligibility (from mix_check.py output): FAIL above 1 %
  G1  motion: static seconds <= 25 % of the film           (--motion motion.json)
  G2  motion: longest static run <= 3 s outside --holds windows
  G3  camera: seconds with camera motion >= 30 % (centrepiece act >= 40 %, --centre)
  G4  motion: mean per-second change >= 2.0 %
      (calibration in references/14: case-study v4 17 % / 2 s / 55 % / 4.3 %;
       a fresh build that passed every other gate: 50 % / 7 s / 10 % / 0.8 %)
  W1-W7 peaks: copies the rows of the JSON written by wow_audit.py   (--wow wow.json)
  R1-R11 argument: copies the rows written by argument_audit.py        (--arg arg.json)
      (plan, reveal contrast, hold, signature budget <= 2, sound cue, key word,
       claim + trade-off; references/15)
"""
import argparse, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--audit"); ap.add_argument("--budget", type=float, default=2.5)
ap.add_argument("--allow", default=None)
ap.add_argument("--videos", nargs="*", default=[])
ap.add_argument("--srt-report"); ap.add_argument("--mix-log")
ap.add_argument("--no-edl", action="store_true")
ap.add_argument("--motion", help="JSON written by motion_audit.py")
ap.add_argument("--centre", default=None, help="act name of the centrepiece (stricter G3)")
ap.add_argument("--wow", help="JSON written by wow_audit.py (W1-W7)")
ap.add_argument("--arg", help="JSON written by argument_audit.py (R1-R11)")
a = ap.parse_args()
rows, fail = [], 0


def gate(code, ok, msg, warn=False):
    global fail
    st = "PASS" if ok else ("WARN" if warn else "FAIL")
    fail += (not ok and not warn)
    rows.append(f"{code:3s} {st:4s}  {msg}")


dur = None
if not a.no_edl:
    sys.path.insert(0, os.getcwd())
    try:
        import io, contextlib, edl
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = edl.check()
        dur = edl.DURATION
        gate("D1", ok, f"EDL clips: {len(edl.clips())}, duration {dur:.2f} s"
             + ("" if ok else " | " + " ".join(l for l in buf.getvalue().splitlines() if "OVERLAP" in l or "outside" in l)))
    except Exception as e:                                      # noqa: BLE001
        gate("D1", False, f"cannot import/check edl: {e}", warn=True)
if a.audit:
    res = json.load(open(a.audit))
    allow = re.compile(a.allow) if a.allow else None
    short = [(v["best"], k) for k, v in res.items()
             if v["best"] < a.budget and not re.fullmatch(r"[\d,.\s×]+", k)
             and not (allow and allow.search(k))]
    gate("B1", not short, f"{len(res)} strings, {len(short)} under {a.budget} s"
         + ("" if not short else ": " + "; ".join(f"{k!r} {b}s" for b, k in sorted(short)[:6])))
for v in a.videos:
    out = subprocess.run(["ffmpeg", "-nostats", "-i", v, "-filter_complex", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
    P = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)[-1])
    gate("D2", abs(I + 16) <= .5 and P <= -1.0, f"{os.path.basename(v)}: {I} LUFS, true peak {P} dBTP")
    if dur:
        ds = []
        for sel in ("v:0", "a:0"):
            r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", sel, "-show_entries",
                                "stream=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout.strip()
            ds.append(float(r) if r and r != "N/A" else None)
        ok = all(d is not None and abs(d - dur) <= .05 for d in ds)
        gate("D5", ok, f"{os.path.basename(v)}: video {ds[0]}, audio {ds[1]}, EDL {dur:.3f}")
if a.srt_report:
    m = re.search(r"TOTAL word differences: (\d+)/(\d+)", open(a.srt_report).read())
    e, n = int(m.group(1)), int(m.group(2))
    gate("D4", e / max(n, 1) <= .10, f"SRT vs delivered audio: {e}/{n} words differ "
         "(inspect each; ASR spelling variants are fine)", warn=True)
if a.mix_log:
    m = re.search(r"(\d+)/(\d+) words differ", open(a.mix_log).read())
    e, n = int(m.group(1)), int(m.group(2))
    gate("D3", e / max(n, 1) <= .01, f"mix intelligibility: {e}/{n} words differ")
if a.motion:
    m = json.load(open(a.motion))
    fm = m["film"]
    gate("G1", fm["static_pct"] <= 25, f"static seconds {fm['static_pct']} % (<= 25 %)")
    gate("G2", fm["longest_static_s"] <= 3, f"longest static run {fm['longest_static_s']} s (<= 3 s)")
    gate("G3", fm["camera_pct"] >= 30, f"camera-motion seconds {fm['camera_pct']} % (>= 30 %), "
         f"{fm['camera_moves']} moves")
    if a.centre and a.centre in m.get("acts", {}):
        c = m["acts"][a.centre]
        gate("G3", c["camera_pct"] >= 40, f"centrepiece act {a.centre}: camera {c['camera_pct']} % (>= 40 %)")
    gate("G4", fm["mean_change_pct"] >= 2.0, f"mean change {fm['mean_change_pct']} % (>= 2.0 %)")
for path in [p for p in (a.wow, a.arg) if p]:
    for g in json.load(open(path))["gates"]:
        gate(g["code"], g["status"] == "PASS", g["msg"], warn=g["status"] == "WARN")
print("\n".join(rows))
print("GATES", "PASS" if fail == 0 else f"FAIL ({fail})")
sys.exit(1 if fail else 0)
