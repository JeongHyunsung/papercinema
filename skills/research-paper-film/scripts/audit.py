"""Readability audit: how long is every on-screen string readable?

Instruments Canvas.text, steps the film clock at FPS, records each string's
opacity; readable = opacity >= 0.5. Reports the longest continuous readable
window per string and lists strings under the budget.
  python3 audit.py film docs/audit_film.json [--budget 2.5]
Budgets: labels 2.5 s, headline results 3-4 s, two-line reasoning 4-7 s.
Pure numbers are excluded from the short list (live counters are expected).
"""
import argparse, collections, importlib, json, os, re, sys
sys.path.insert(0, os.getcwd())
import engine                                                  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("film", nargs="?", default="film")
ap.add_argument("out", nargs="?", default=None)
ap.add_argument("--budget", type=float, default=2.5)
ap.add_argument("--fps", type=int, default=20)
args = ap.parse_args()
mod = importlib.import_module(args.film)
seen = {}
_orig = engine.Canvas.text


def text(self, x, y, s, font=engine.F_UI, size=28, col=engine.INK, a=1.0,
         anchor="l", track=0.0, reveal=1.0):
    if s and a > 0.002:
        k = s.strip()
        seen[k] = max(seen.get(k, 0), a * (1 if reveal >= .999 else 0))
    return _orig(self, x, y, s, font, size, col, a, anchor, track, reveal)


engine.Canvas.text = text
cv = engine.Canvas(384, 216)
tracks = collections.defaultdict(list)
for f in range(int(mod.DURATION * args.fps) + 1):
    t = f / args.fps
    seen.clear()
    mod.draw(cv, t)
    for k, al in seen.items():
        tracks[k].append((t, al))
res = {}
for k, tr in tracks.items():
    best, cur, first, start, prev = 0, None, None, None, None
    for t, al in tr:
        if al >= .5:
            if cur is None or prev is None or t - prev > 1.5 / args.fps:
                cur = t
            first = t if first is None else first
            if t - cur + 1 / args.fps > best:
                best, start = t - cur + 1 / args.fps, cur
            prev = t
        else:
            cur = prev = None
    res[k] = dict(first=first, best=round(best, 2), at=start)
out = args.out or f"audit_{args.film}.json"
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
short = sorted(((v["at"] if v["at"] is not None else (v["first"] or -1)), k, v["best"])
               for k, v in res.items()
               if v["best"] < args.budget and not re.fullmatch(r"[\d,.\s×]+", k))
for t, k, b in short:
    print(f"{t:7.2f}  {b:5.2f}s  {k}")
print(len(res), "strings,", len(short), f"under {args.budget} s ->", out)
