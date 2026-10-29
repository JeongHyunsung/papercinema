"""Motion audit: is the film alive, second by second? (quality bar G1-G4)

Decodes the video at --fps (default 10) to 320x180 grayscale and measures,
for each pair of consecutive frames:
  change  share of all pixels that changed by > 6/255 (anything moving or appearing)
  camera  True when >= 25 % of the *content* pixels (ink on the white page)
          changed at once and > 1 % of the frame changed: the whole picture
          moved, i.e. a camera move, a zoom or a cut/crossfade
Per second it keeps the maximum change and whether a camera frame occurred.

Report (whole film, and per act with --acts):
  static %        seconds in which < 0.3 % of pixels change: nothing moves
  longest static  longest run of static seconds (excluding --holds windows)
  camera %        seconds containing camera motion
  camera moves    number of separate camera-motion runs
  mean change %   average per-second change

  python3 motion_audit.py film.mp4 --json motion.json \\
      --acts "I:0-29,II:29-53,III:53-87,IV:87-123,V:123-129" --holds 123-129

Calibration (references/14): the case-study film v4 (116 s) measured
static 17 %, longest static 2 s, camera 55 %, mean change 4.3 %; a fresh build
that passed every legibility gate measured static 50 %, longest 7 s, camera 10 %,
mean change 0.8 %. gate.py --motion applies the G thresholds to this JSON.
"""
import argparse, json, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--fps", type=int, default=10)
ap.add_argument("--json")
ap.add_argument("--acts", default="", help='e.g. "I:0-29,II:29-53"')
ap.add_argument("--holds", default="", help='intended still windows, e.g. "123-129,40-41"')
ap.add_argument("--static", type=float, default=.003)
ap.add_argument("--camera", type=float, default=.25)
a = ap.parse_args()
W, H = 320, 180
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-vf",
                      f"fps={a.fps},scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
n = len(F)
chg, cam = np.zeros(n), np.zeros(n, bool)
for k in range(1, n):
    d = np.abs(F[k] - F[k - 1]) > 6
    chg[k] = d.mean()
    content = (F[k] < 245) | (F[k - 1] < 245)
    if content.sum() > 200:
        cam[k] = d[content].mean() >= a.camera and chg[k] > .01
secs = int(np.ceil(n / a.fps))
per = np.array([chg[s * a.fps:(s + 1) * a.fps].max() for s in range(secs)])
cams = np.array([bool(cam[s * a.fps:(s + 1) * a.fps].any()) for s in range(secs)])
hold = np.zeros(secs, bool)
for w in filter(None, a.holds.split(",")):
    s0, s1 = map(float, w.split("-"))
    hold[int(s0):int(np.ceil(s1))] = True


def stats(s0, s1):
    p, c, h = per[s0:s1], cams[s0:s1], hold[s0:s1]
    st = p < a.static
    run = best = 0
    for x, y in zip(st, h):
        run = run + 1 if (x and not y) else 0
        best = max(best, run)
    moves, prev = 0, False
    for x in c:
        moves += bool(x and not prev)
        prev = bool(x)
    return dict(seconds=int(s1 - s0), static_pct=round(100 * float(st.mean()), 1),
                longest_static_s=int(best), camera_pct=round(100 * float(c.mean()), 1),
                camera_moves=int(moves), mean_change_pct=round(100 * float(p.mean()), 2))


res = dict(video=a.video, film=stats(0, secs), acts={})
for spec in filter(None, a.acts.split(",")):
    name, rng = spec.split(":")
    s0, s1 = map(float, rng.split("-"))
    res["acts"][name] = stats(int(s0), min(secs, int(np.ceil(s1))))
res["per_second"] = [round(float(x) * 100, 2) for x in per]
res["camera_seconds"] = [int(x) for x in cams]
print("film ", res["film"])
for k, v in res["acts"].items():
    print(f"act {k:4s}", v)
if a.json:
    json.dump(res, open(a.json, "w"), indent=1)
