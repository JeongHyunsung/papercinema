"""Rasterize every PDF/SVG in a folder next to its PNG, tile them, and list the
fonts actually embedded in the PDFs.
  python3 verify_vectors.py figs/out sheet.png
Look at the sheet: each figure's PNG / PDF / SVG must match."""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

d, out = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
tiles = []
for png in sorted(glob.glob(os.path.join(d, "*.png"))):
    b = png[:-4]
    row = [("png", Image.open(png).convert("RGB"))]
    if os.path.exists(b + ".pdf"):
        o = os.path.join(tmp, os.path.basename(b) + "_pdf")
        subprocess.run(["pdftoppm", "-r", "24", "-png", "-singlefile", b + ".pdf", o], check=True)
        row.append(("pdf", Image.open(o + ".png").convert("RGB")))
    if os.path.exists(b + ".svg"):
        import cairosvg
        o = os.path.join(tmp, os.path.basename(b) + "_svg.png")
        cairosvg.svg2png(url=b + ".svg", write_to=o, scale=.3)
        row.append(("svg", Image.open(o).convert("RGB")))
    tiles.append((os.path.basename(b), row))
cw = 420
rows = []
for name, row in tiles:
    ims = [(k, i.resize((cw, max(1, int(i.height * cw / i.width))))) for k, i in row]
    h = max(i.height for _, i in ims) + 18
    rows.append((name, ims, h))
S = Image.new("RGB", (3 * (cw + 8), sum(h for *_, h in rows)), "#999")
dr = ImageDraw.Draw(S)
y = 0
for name, ims, h in rows:
    for j, (k, i) in enumerate(ims):
        S.paste(i, (j * (cw + 8), y + 16)); dr.text((j * (cw + 8) + 2, y + 2), f"{name} [{k}]", fill="black")
    y += h
S.save(out)
print("sheet:", out)
fonts = {}
for p in glob.glob(os.path.join(d, "*.pdf")):
    r = subprocess.run(["pdffonts", p], capture_output=True, text=True).stdout.splitlines()[2:]
    for l in r:
        f = l.split()[0].split("+")[-1]
        fonts[f] = fonts.get(f, 0) + 1
print("embedded fonts:", fonts)
