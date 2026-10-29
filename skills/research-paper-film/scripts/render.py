"""Render stills or video segments of a code-generated film.

The film module must provide  draw(cv, t)  and  DURATION ; optionally
blur_n(t) -> number of motion-blur sub-frames at t (1 = none), and
post(rgb, t) -> rgb, a raster hook for budgeted signature breaks
(peak_kit.night_rgb / spotlight_rgb; references/15).

  python3 render.py stills --film film --w 1280 --times 2.5 5.8   -> out/stills/
  python3 render.py video  --film film --w 3840 --fps 60 --start 0 --end 14.4 \\
                           --codec x264 --out out/c000.0.mkv

x264 settings: CRF 15, -tune animation (flat colour, thin lines), 1 thread per
process (parallelism comes from chunking; see render_chunks.sh).
"""
import argparse, importlib, os, subprocess, sys, time
import numpy as np
from engine import Canvas, Post

SHUTTER = 0.5 / 60          # 180-degree shutter at 60 fps


def render_frame(film, cv, post, t, fidx):
    rgb = _render_frame(film, cv, post, t, fidx)
    return film.post(rgb, t) if hasattr(film, "post") else rgb


def _render_frame(film, cv, post, t, fidx):
    n = film.blur_n(t) if hasattr(film, "blur_n") else 1
    if n <= 1:
        film.draw(cv, t)
        return post.process_rgb(post.grab(cv.surf), fidx)
    acc = None
    for j in range(n):
        film.draw(cv, t + (j / (n - 1) - .5) * SHUTTER)
        f = post.grab(cv.surf).astype(np.float32)
        acc = f if acc is None else acc + f
    return np.clip(acc / n + .5, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["stills", "video"])
    ap.add_argument("--film", default=os.environ.get("FILM", "film"))
    ap.add_argument("--w", type=int, default=960)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--times", type=float, nargs="*", default=[])
    ap.add_argument("--out", default="out/seg.mkv")
    ap.add_argument("--stills-dir", default="out/stills")
    ap.add_argument("--codec", default="x264", choices=["x264", "ffv1"])
    a = ap.parse_args()
    sys.path.insert(0, os.getcwd())
    film = importlib.import_module(a.film)
    end = film.DURATION if a.end is None else a.end
    W = a.w
    H = W * 9 // 16
    cv, post = Canvas(W, H), Post(W, H)
    if a.mode == "stills":
        from PIL import Image
        os.makedirs(a.stills_dir, exist_ok=True)
        for t in a.times:
            p = os.path.join(a.stills_dir, f"t{t:06.2f}.png")
            Image.fromarray(render_frame(film, cv, post, t, int(t * 60))).save(p)
            print(p)
        return
    f0, f1 = int(round(a.start * a.fps)), int(round(end * a.fps))
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
        pr.stdin.write(render_frame(film, cv, post, f / a.fps, f).tobytes())
        if (f - f0) % 60 == 0:
            el, done = time.time() - t0, f - f0 + 1
            print(f"{a.out}: frame {done}/{f1 - f0}  {el / done:.2f}s/f  "
                  f"eta {el / done * (f1 - f) / 60:.1f} min", flush=True)
    pr.stdin.close()
    pr.wait()
    print("done", a.out, f"{time.time() - t0:.0f}s")     # render_chunks.sh looks for this


if __name__ == "__main__":
    main()
