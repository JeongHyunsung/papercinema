"""Render stills or video segments of the B-Flex film.

  python3 render.py stills  --w 960 --times 2.5 5.8 ...   -> out/stills/*.png
  python3 render.py video   --w 3840 --fps 60 --start 0 --end 62 --out seg.mkv
"""
import argparse, os, subprocess, sys, time
import numpy as np
from engine import Canvas, Post
import film


SHUTTER = 0.5 / 60          # 180-degree shutter


def render_frame(cv, post, t, fidx):
    n = film.blur_n(t)
    if n <= 1:
        film.draw(cv, t)
        return post.process(cv.surf, fidx)
    acc = None
    for j in range(n):
        film.draw(cv, t + (j / (n - 1) - .5) * SHUTTER)
        f = post.grab(cv.surf).astype(np.float32)
        acc = f if acc is None else acc + f
    rgb = np.clip(acc / n + .5, 0, 255).astype(np.uint8)
    return post.process_rgb(rgb, fidx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stills", "video"])
    ap.add_argument("--w", type=int, default=960)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=film.DURATION)
    ap.add_argument("--times", type=float, nargs="*", default=[])
    ap.add_argument("--out", default="out/seg.mkv")
    ap.add_argument("--codec", default="ffv1")
    a = ap.parse_args()
    W = a.w
    H = W * 9 // 16
    cv = Canvas(W, H)
    post = Post(W, H)
    if a.mode == "stills":
        from PIL import Image
        os.makedirs("out/stills", exist_ok=True)
        for t in a.times:
            img = render_frame(cv, post, t, int(t * 60))
            p = f"out/stills/t{t:06.2f}.png"
            Image.fromarray(img).save(p)
            print(p)
        return
    f0 = int(round(a.start * a.fps))
    f1 = int(round(a.end * a.fps))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    if a.codec == "ffv1":
        enc = ["-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv444p"]
    else:
        enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "15",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-g", "120",
               "-bf", "2", "-x264-params",
               "aq-mode=3:deblock=-1,-1:rc-lookahead=8:sync-lookahead=0",
               "-tune", "animation", "-threads", "1"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(a.fps), "-i", "-",
           *enc, a.out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        img = render_frame(cv, post, f / a.fps, f)
        pr.stdin.write(img.tobytes())
        if (f - f0) % 60 == 0:
            el = time.time() - t0
            done = f - f0 + 1
            print(f"{a.out}: frame {done}/{f1 - f0}  "
                  f"{el / done:.2f}s/f  eta {el / done * (f1 - f) / 60:.1f} min",
                  flush=True)
    pr.stdin.close()
    pr.wait()
    print("done", a.out, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
