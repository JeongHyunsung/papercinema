"""Contact sheet of a video at N fps (default 1), timestamped tiles.
  python3 contact_sheet.py film.mp4 --fps 1 --cols 6 --w 320 --out sheet.png
Large films produce several sheets (sheet_0.png, sheet_1.png, ...)."""
import argparse, glob, os, subprocess, tempfile
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--fps", type=float, default=1)
ap.add_argument("--cols", type=int, default=6); ap.add_argument("--w", type=int, default=320)
ap.add_argument("--rows", type=int, default=6); ap.add_argument("--out", default="sheet.png")
a = ap.parse_args()
tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.video, "-vf",
                f"fps={a.fps},scale={a.w}:-2", os.path.join(tmp, "f%05d.png")], check=True)
fr = sorted(glob.glob(os.path.join(tmp, "f*.png")))
per = a.cols * a.rows
base, ext = os.path.splitext(a.out)
for s in range(0, len(fr), per):
    ims = [Image.open(f) for f in fr[s:s + per]]
    w, h = ims[0].size
    S = Image.new("RGB", (a.cols * w, ((len(ims) - 1) // a.cols + 1) * (h + 16)), "white")
    d = ImageDraw.Draw(S)
    for j, im in enumerate(ims):
        x, y = (j % a.cols) * w, (j // a.cols) * (h + 16)
        S.paste(im, (x, y + 16))
        t = (s + j) / a.fps
        d.text((x + 3, y + 2), f"{int(t // 60)}:{t % 60:05.2f}", fill="black")
    p = a.out if len(fr) <= per else f"{base}_{s // per}{ext}"
    S.save(p); print(p)
