"""Review pack: the reviewer's view of a film, built from the delivered files alone.

The independent reviewer (references/18, 19) never sees the generator's code, plans or
gate outputs. This script gives it everything it can learn from the video (and its
subtitle file) the way an audience gets it:

  python3 review_pack.py film.mp4 [--srt film.srt] --out review/packs/r03 [--every 3] [--cut 0.3]

Writes into --out:
  INDEX.md        duration, resolution, fps, audio, loudness (LUFS, dBTP), silences, cuts, files
  sheet*.png      1-fps contact sheets with timestamps          (contact_sheet.py)
  stills/         1080p frames every --every s and either side of each detected cut,
                  plus 2x2 sheets of them (stills/sheet_*.png)
  timeline.png    per second: picture change, camera moves, audio level, speech windows
  motion.json     G1-G4 measurements                            (motion_audit.py)
  transcript.txt  subtitle cues with times; plus ASR of the film's own audio when
                  $SHERPA_DIR points at an installed sherpa-onnx model (narration/asr.py)

Needs ffmpeg/ffprobe, numpy, Pillow. No network.
"""
import argparse, glob, json, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--srt")
ap.add_argument("--out", required=True)
ap.add_argument("--every", type=float, default=3.0, help="seconds between 1080p stills")
ap.add_argument("--cut", type=float, default=0.3, help="scene-change threshold for cut detection")
ap.add_argument("--no-asr", action="store_true")
a = ap.parse_args()
os.makedirs(os.path.join(a.out, "stills"), exist_ok=True)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ts(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


# ---- metadata ---------------------------------------------------------------------------
probe = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json",
                        a.video], check=True).stdout)
vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
aus = [s for s in probe["streams"] if s["codec_type"] == "audio"]
dur = float(probe["format"]["duration"])
num, den = map(int, vs.get("avg_frame_rate", "0/1").split("/"))
fps = num / den if den else 0.0
W, H = int(vs["width"]), int(vs["height"])

# ---- loudness and silences ----------------------------------------------------------------
lufs = tp = None
silences = []
if aus:
    err = run(["ffmpeg", "-nostats", "-i", a.video, "-map", "0:a:0", "-af", "ebur128=peak=true",
               "-f", "null", "-"]).stderr
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else err
    m = re.search(r"I:\s*(-?[\d.]+|-inf) LUFS", summ)
    lufs = m.group(1) if m else None
    m = re.search(r"True peak:\s*Peak:\s*(-?[\d.]+|-inf) dBFS", summ, re.S)
    tp = m.group(1) if m else None
    err = run(["ffmpeg", "-nostats", "-i", a.video, "-map", "0:a:0", "-af",
               "silencedetect=noise=-45dB:d=1.5", "-f", "null", "-"]).stderr
    st = None
    for line in err.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            st = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and st is not None:
            silences.append((st, float(m.group(1))))
            st = None
    if st is not None:
        silences.append((st, dur))

# ---- cuts -----------------------------------------------------------------------------------
err = run(["ffmpeg", "-nostats", "-i", a.video, "-vf",
           f"scale=480:-2,select='gt(scene,{a.cut})',showinfo", "-an", "-f", "null", "-"]).stderr
cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", err)]

# ---- contact sheets + motion audit ----------------------------------------------------------
sheets = run([sys.executable, os.path.join(HERE, "contact_sheet.py"), a.video, "--fps", "1",
              "--out", os.path.join(a.out, "sheet.png")], check=True).stdout.split()
mj = os.path.join(a.out, "motion.json")
mout = run([sys.executable, os.path.join(HERE, "motion_audit.py"), a.video, "--json", mj],
           check=True).stdout
motion = json.load(open(mj))

# ---- 1080p stills ---------------------------------------------------------------------------
times = list(np.arange(0.0, dur - 0.05, a.every))
for c in cuts:
    times += [max(0.0, c - 0.4), min(dur - 0.05, c + 0.4)]
times = sorted({round(t, 1) for t in times})
scale = "scale=-2:1080" if H > 1080 else "null"
stills = []
for t in times:
    p = os.path.join(a.out, "stills", f"t{t:07.1f}.png")
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", a.video, "-frames:v", "1",
         "-vf", scale, p])
    if os.path.exists(p):
        stills.append((t, p))
still_sheets = []
for i in range(0, len(stills), 4):
    grp = stills[i:i + 4]
    ims = [Image.open(p).convert("RGB") for _, p in grp]
    w, h = ims[0].size
    w2, h2 = w // 2, h // 2
    S = Image.new("RGB", (2 * w2, 2 * (h2 + 22)), "white")
    d = ImageDraw.Draw(S)
    for j, ((t, _), im) in enumerate(zip(grp, ims)):
        x, y = (j % 2) * w2, (j // 2) * (h2 + 22)
        S.paste(im.resize((w2, h2), Image.LANCZOS), (x, y + 22))
        d.rectangle([x, y + 22, x + w2 - 1, y + 22 + h2 - 1], outline=(170, 170, 170))  # films are white
        tag = ts(t) + ("  (cut)" if any(abs(t - c) < 0.45 for c in cuts) else "")
        d.text((x + 6, y + 5), tag, fill="black")
    p = os.path.join(a.out, "stills", f"sheet_{i // 4:03d}.png")
    S.save(p)
    still_sheets.append(p)

# ---- subtitles ------------------------------------------------------------------------------
cues = []
if a.srt and os.path.exists(a.srt):
    txt = open(a.srt, encoding="utf-8-sig").read().replace("\r", "")
    for blk in re.split(r"\n\s*\n", txt.strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", blk)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        t0 = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        t1 = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        body = " ".join(blk[m.end():].strip().splitlines())
        cues.append((t0, t1, body))

# ---- audio envelope -------------------------------------------------------------------------
env = None
SR = 16000
pcm = None
if aus:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-map", "0:a:0", "-ac", "1",
                          "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    hop = SR // 10
    n = len(pcm) // hop
    rms = np.sqrt((pcm[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    env = 20 * np.log10(rms)  # dBFS per 100 ms

# ---- ASR (optional) -------------------------------------------------------------------------
asr_lines, asr_note = [], "not run (--no-asr)" if a.no_asr else ""
if not a.no_asr and pcm is not None:
    sd = os.environ.get("SHERPA_DIR")
    if not sd or not os.path.isdir(sd):
        asr_note = "not run: $SHERPA_DIR not set to an installed sherpa-onnx model; subtitles only"
    else:
        try:
            sys.path.insert(0, os.path.join(HERE, "narration"))
            import asr  # noqa: E402
            step = 15 * SR
            for s in range(0, len(pcm), step):
                text, _, _ = asr.transcribe(pcm[s:s + step], SR)
                if text.strip():
                    asr_lines.append(f"[{ts(s / SR)}] {text.strip()}")
            asr_note = f"sherpa-onnx, 15 s windows, model {sd}"
        except Exception as e:  # missing package or model files
            asr_note = f"not run: {type(e).__name__}: {e}"

with open(os.path.join(a.out, "transcript.txt"), "w", encoding="utf-8") as f:
    f.write("# Subtitles (as delivered)\n")
    for t0, t1, b in cues:
        f.write(f"[{ts(t0)}-{ts(t1)}] {b}\n")
    if not cues:
        f.write("(no subtitle file)\n")
    f.write(f"\n# ASR of the film's own audio: {asr_note}\n")
    f.write("\n".join(asr_lines) + ("\n" if asr_lines else ""))

# ---- timeline -------------------------------------------------------------------------------
per = motion["per_second"]
cam = motion["camera_seconds"]
PX, ROW_S = 14, 60                     # px per second, seconds per row
rows = int(np.ceil(dur / ROW_S))
LH, GAP, LM = 150, 34, 70
T = Image.new("RGB", (LM + ROW_S * PX + 20, rows * (LH + GAP) + 30), "white")
d = ImageDraw.Draw(T)
d.text((LM, 6), "grey bars: picture change % per s (dashed = 0.3 % static line)  |  blue ticks: camera move  |  "
       "orange line: audio dBFS (-60..0)  |  green band: subtitle cue  |  red: cut  |  hatched: silence",
       fill="black")
for r in range(rows):
    y0 = 30 + r * (LH + GAP)
    s0 = r * ROW_S
    s1 = min(int(np.ceil(dur)), s0 + ROW_S)
    d.rectangle([LM, y0, LM + ROW_S * PX, y0 + LH], outline=(200, 200, 200))
    for s in range(s0, s1, 5):
        x = LM + (s - s0) * PX
        d.line([x, y0 + LH, x, y0 + LH + 4], fill="black")
        d.text((x - 8, y0 + LH + 6), ts(s)[:-2], fill="black")
    base = y0 + 100
    lin = lambda v: base - min(1.0, v / 20.0) * 90          # noqa: E731  change % scaled 0..20
    for s in range(s0, min(s1, len(per))):
        x = LM + (s - s0) * PX
        d.rectangle([x + 1, lin(per[s]), x + PX - 2, base], fill=(150, 150, 150))
        if cam[s]:
            d.rectangle([x + 1, y0 + 2, x + PX - 2, y0 + 8], fill=(40, 90, 200))
    d.line([LM, lin(0.3), LM + ROW_S * PX, lin(0.3)], fill=(120, 120, 120), width=1)
    for t0, t1, _ in cues:
        if t1 > s0 and t0 < s1:
            d.rectangle([LM + (max(t0, s0) - s0) * PX, y0 + 128, LM + (min(t1, s1) - s0) * PX,
                         y0 + 140], fill=(60, 170, 120))
    for t0, t1 in silences:
        if t1 > s0 and t0 < s1:
            xa, xb = LM + (max(t0, s0) - s0) * PX, LM + (min(t1, s1) - s0) * PX
            for xx in range(int(xa), int(xb), 4):
                d.line([xx, y0 + 142, xx + 3, y0 + 148], fill=(120, 120, 120))
    for c in cuts:
        if s0 <= c < s1:
            x = LM + (c - s0) * PX
            d.line([x, y0, x, y0 + LH], fill=(210, 40, 40))
    if env is not None:
        pts = []
        for k in range(int(s0 * 10), min(len(env), int(s1 * 10))):
            v = max(-60.0, min(0.0, float(env[k])))
            pts.append((LM + (k / 10 - s0) * PX, y0 + 10 + (-v / 60.0) * 110))
        if len(pts) > 1:
            d.line(pts, fill=(235, 130, 20), width=1)
T.save(os.path.join(a.out, "timeline.png"))

# ---- index ----------------------------------------------------------------------------------
f = motion["film"]
with open(os.path.join(a.out, "INDEX.md"), "w", encoding="utf-8") as o:
    o.write(f"# Review pack: {os.path.basename(a.video)}\n\n")
    o.write(f"- Duration {dur:.2f} s; video {W}x{H} @ {fps:.2f} fps ({vs.get('codec_name')})\n")
    if aus:
        s = aus[0]
        o.write(f"- Audio {s.get('codec_name')} {s.get('sample_rate')} Hz, {s.get('channels')} ch, "
                f"stream duration {float(s.get('duration', dur)):.2f} s\n")
        o.write(f"- Loudness: integrated {lufs} LUFS, true peak {tp} dBTP (target -16 +/- 0.5 LUFS, <= -1 dBTP)\n")
        o.write(f"- Silences >= 1.5 s below -45 dB: "
                + (", ".join(f"{ts(x)}-{ts(y)}" for x, y in silences) or "none") + "\n")
    else:
        o.write("- Audio: NONE\n")
    o.write(f"- Video vs container duration: {float(vs.get('duration', dur)):.2f} s vs {dur:.2f} s\n")
    o.write(f"- Cuts detected (scene > {a.cut}): {len(cuts)}: " + ", ".join(ts(c) for c in cuts) + "\n")
    o.write(f"- Motion (G1-G4): static {f['static_pct']} %, longest static run {f['longest_static_s']} s, "
            f"camera {f['camera_pct']} % ({f['camera_moves']} moves), mean change {f['mean_change_pct']} %\n")
    static_runs, run0 = [], None
    for s, v in enumerate(per + [99]):
        if v < 0.3 and run0 is None:
            run0 = s
        elif v >= 0.3 and run0 is not None:
            if s - run0 >= 3:
                static_runs.append((run0, s))
            run0 = None
    o.write("- Static runs >= 3 s: " + (", ".join(f"{ts(x)}-{ts(y)}" for x, y in static_runs) or "none")
            + "\n")
    o.write(f"- Subtitles: {len(cues)} cues" + (f" from {a.srt}" if cues else "") + "\n")
    o.write(f"- ASR: {asr_note}\n\n## Files\n")
    o.write("- contact sheets (1 fps): " + ", ".join(os.path.basename(x) for x in sheets) + "\n")
    o.write(f"- stills (1080p, every {a.every} s and +/-0.4 s at cuts): {len(stills)} frames in stills/, "
            f"{len(still_sheets)} 2x2 sheets (stills/sheet_*.png)\n")
    o.write("- timeline.png, motion.json, transcript.txt\n")
print(open(os.path.join(a.out, "INDEX.md")).read())
