"""Gate check for a slide-figure folder (quality bar E2-E4, E6, E8).

  python3 lint_figs.py figs/out [--width-in 12] [--min-pt 9] [--sequence 2d,2e,2f]

Per figure:
  aspect   PNG width/height (full-width slide figures: 2.0-2.6 is the target;
           halves/panels are reported, not failed)
  min pt   smallest drawn text at the given placement width (from
           _textsizes.json, written by figkit.export) - FAIL below --min-pt
  files    PNG + SVG + PDF present
Folder:
  fonts    faces embedded across PDFs (pdffonts) - WARN if more than one family
  sequence figures whose names start with the given prefixes must share one
           PNG size (identical crop -> slides overlay exactly)
"""
import argparse, glob, json, os, subprocess
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("dir"); ap.add_argument("--width-in", type=float, default=12.0)
ap.add_argument("--min-pt", type=float, default=9.0)
ap.add_argument("--sequence", default="")
a = ap.parse_args()
sizes = {}
p = os.path.join(a.dir, "_textsizes.json")
if os.path.exists(p):
    sizes = json.load(open(p))
fails = 0
print(f"{'figure':34s} {'px':>11s} {'aspect':>6s} {'min pt':>7s}  {'files':11s}  verdict")
for png in sorted(glob.glob(os.path.join(a.dir, "*.png"))):
    name = os.path.basename(png)[:-4]
    w, h = Image.open(png).size
    have = "/".join(k if os.path.exists(os.path.join(a.dir, f"{name}.{k}")) else "---"
                    for k in ("png", "svg", "pdf"))
    s = sizes.get(name)
    pt = None
    if s and s["min"]:
        pt = s["min"] * a.width_in * 72 / s["box"][2]
    bad = (pt is not None and pt < a.min_pt)
    fails += bad
    verdict = "FAIL text" if bad else ("ok" if pt is not None else "ok (no size data)")
    print(f"{name:34s} {w:5d}x{h:<5d} {w / h:6.2f} {('%.1f' % pt) if pt else '   -':>7s}  {have:11s}  {verdict}")
    if bad:
        small = [t for t in s["text"] if t[0] * a.width_in * 72 / s["box"][2] < a.min_pt][:4]
        print("      smallest:", small)
fonts = {}
for pdf in glob.glob(os.path.join(a.dir, "*.pdf")):
    out = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout.splitlines()[2:]
    for l in out:
        f = l.split()[0].split("+")[-1]
        fonts[f] = fonts.get(f, 0) + 1
fam = {f.split("-")[0] for f in fonts}
print("fonts:", fonts, "->", "ok" if len(fam) <= 1 else "WARN: more than one family")
if a.sequence:
    pre = a.sequence.split(",")
    seq = [p for p in sorted(glob.glob(os.path.join(a.dir, "*.png")))
           if os.path.basename(p).startswith(tuple(pre))]
    dims = {Image.open(p).size for p in seq}
    ok = len(dims) == 1
    fails += not ok
    print(f"sequence {pre}: {len(seq)} figures, sizes {dims} ->", "ok" if ok else "FAIL (crops differ)")
print("LINT", "PASS" if fails == 0 else f"FAIL ({fails})")
raise SystemExit(1 if fails else 0)
