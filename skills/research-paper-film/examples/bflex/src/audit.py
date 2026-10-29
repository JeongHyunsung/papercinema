"""Readability audit: how long every on-screen string is readable.

Instruments Canvas.text, steps the film clock at FPS, and records each string's
opacity. A string counts as readable while its opacity >= 0.5. Output: the
longest continuous readable window per string, and its first time.
  python3 audit.py film     -> v4 (narration clock)
  python3 audit.py film_v3  -> v3, for comparison
"""
import sys, json, re, importlib, collections
import engine
FPS = 20
mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "film")
seen = {}
_orig = engine.Canvas.text
def text(self, x, y, s, font=engine.F_UI, size=28, col=engine.INK, a=1.0, anchor="l", track=0.0, reveal=1.0):
    if s and a > 0.002:
        k = s.strip()
        seen[k] = max(seen.get(k, 0), a * (1 if reveal >= .999 else 0))
    return _orig(self, x, y, s, font, size, col, a, anchor, track, reveal)
engine.Canvas.text = text
cv = engine.Canvas(384, 216)
N = int(mod.DURATION * FPS)
tracks = collections.defaultdict(list)
for f in range(N + 1):
    t = f / FPS
    seen.clear()
    mod.draw(cv, t)
    for k, a in seen.items():
        tracks[k].append((t, a))
res = {}
for k, tr in tracks.items():
    best, cur, first, start = 0, None, None, None
    prev = None
    for t, a in tr:
        ok = a >= .5
        if ok and (cur is None or prev is None or t - prev > 1.5 / FPS):
            cur = t
        if ok:
            if first is None: first = t
            if t - cur + 1 / FPS > best:
                best, start = t - cur + 1 / FPS, cur
            prev = t
        else:
            cur = None; prev = None
    res[k] = dict(first=first, best=round(best, 2), at=start)
out = sys.argv[2] if len(sys.argv) > 2 else f"../docs/audit_{sys.argv[1] if len(sys.argv)>1 else 'film'}.json"
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
short = [(v["at"] if v["at"] is not None else v["first"] or -1, k, v["best"]) for k, v in res.items()
         if v["best"] < 2.5 and not re.fullmatch(r"[\d,.\s×]+|[\d]+", k)]
for t, k, b in sorted(short, key=lambda x: (x[0] is None, x[0])):
    print(f"{t if t is not None else -1:7.2f}  {b:5.2f}s  {k}")
print(len(res), "strings,", len(short), "under 2.5 s")
