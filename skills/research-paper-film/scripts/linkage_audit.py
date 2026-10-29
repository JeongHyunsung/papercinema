"""Linkage audit (quality bar L1): does every finding point at what it is about?

Steps the film clock at --fps, instruments Canvas.text, and classifies each
drawn string:
  finding   it states a rule outcome or a concrete value: matches --pattern
            (default: =, ≠, →, ×, δ, "pruned", "conflict", "wrong", "needs",
            "fixed", "infer", "settles", "must")
  anchored  it was drawn through motion_kit.callout_at() in the same frame
            (the leader line to its referent was drawn), or it matches --allow
            (HUD readouts, axis labels, source tags, breadcrumbs)
Reports every finding that is shown for >= --min seconds without an anchor,
with its first time. FAIL if any (exit 1).

  cd src && python3 ../scripts/linkage_audit.py film --from 29 --to 87 \\
      --allow "^(step|STEP|Fig\\.|§)"
Only films that draw annotations with callout_at can pass; a film built with
free-floating chips fails by design (that is the defect this gate catches).
"""
import argparse, collections, importlib, os, re, sys
sys.path.insert(0, os.getcwd())
import engine                                                  # noqa: E402
import motion_kit                                              # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("film", nargs="?", default="film")
ap.add_argument("--fps", type=float, default=5)
ap.add_argument("--from", dest="t0", type=float, default=0.0)
ap.add_argument("--to", dest="t1", type=float, default=None)
ap.add_argument("--min", type=float, default=0.6)
ap.add_argument("--pattern", default=r"(=|≠|→|×|δ|pruned|conflict|wrong|needs|fixed|infer|settles|must)")
ap.add_argument("--allow", default=r"^$")
a = ap.parse_args()
mod = importlib.import_module(a.film)
pat, allow = re.compile(a.pattern), re.compile(a.allow)
seen = set()
_orig = engine.Canvas.text


def text(self, x, y, s, *args, **kw):
    al = kw.get("a", args[3] if len(args) > 3 else 1.0)
    if s and al > .5:
        seen.add(s.strip())
    return _orig(self, x, y, s, *args, **kw)


engine.Canvas.text = text
cv = engine.Canvas(384, 216)
t1 = a.t1 if a.t1 is not None else mod.DURATION
loose = collections.defaultdict(list)
anch = set()
f = 0
while a.t0 + f / a.fps <= t1:
    t = a.t0 + f / a.fps
    seen.clear()
    motion_kit.ANCHORED.clear()          # in case the film does not call begin_frame()
    mod.draw(cv, t)
    anch |= motion_kit.ANCHORED
    for s in seen:
        if pat.search(s) and not allow.search(s) and s not in motion_kit.ANCHORED:
            loose[s].append(t)
    f += 1
bad = {s: ts for s, ts in loose.items() if len(ts) / a.fps >= a.min}
for s, ts in sorted(bad.items(), key=lambda kv: kv[1][0]):
    print(f"{ts[0]:7.2f}  {len(ts) / a.fps:5.1f}s  UNANCHORED  {s}")
print(f"L1 {'PASS' if not bad else 'FAIL'}: {len(bad)} unanchored findings, "
      f"{len(anch)} anchored annotation strings")
sys.exit(1 if bad else 0)
