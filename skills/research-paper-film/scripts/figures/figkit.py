"""Slide-figure toolkit: reuse a film's drawing code without modifying it.

    import figkit as FK
    FK.use_inter(); FK.use_contrast()                # before loading the film
    F = FK.load_patched("src/film.py", patches=[(old, new), ...],
                        nop=["act_label", "caption", "tag", "breadcrumb"])
    FK.DROP |= {"Partial transition table"}          # strings never drawn
    FK.BOOST["k"] = 1.2                              # small-text boost
    fn = lambda cv: F.draw_anim(cv, 33.55)           # any drawfn(cv)
    FK.export("2h_conflict", fn, "out", k=3, M=300)  # PNG + SVG + PDF

Design notes (see references/09-slide-figures.md):
  * patches are exact text replacements; each target must occur exactly once
  * HUD overlays become no-ops; unwanted strings are filtered by exact match
  * BigCanvas adds a margin M so content a film camera pushed off-frame is kept
  * export crops to the content box; SVG/PDF use the same box. Raster layers
    (numpy composites) cannot become vector - say so in the figure README.
  * union_box() gives one crop for a sequence (consecutive slides overlay).
"""
import os, sys, types
import numpy as np
import cairo
from PIL import Image

import engine
from engine import DW, DH, PAPER

# ------------------------------------------------------------ fonts ----------
INTER = {"F_UI": "Inter Regular", "F_MONO": "Inter Regular",
         "F_MONO_M": "Inter Medium", "F_MONO_L": "Inter Light",
         "F_TITLE": "Inter SemiBold", "F_TITLE_L": "Inter Light"}


def use_inter(mapping=INTER):
    """Rebind engine font names (call BEFORE loading the film module, so its
    `from engine import *` picks them up). 'Inter Regular' needs setup_fonts.py."""
    for k, v in mapping.items():
        setattr(engine, k, v)


# ------------------------------------------------------------ slide contrast -
# Slides are viewed small and projected, so figures default to: strokes 1.5x,
# faded strokes/text darkened (alpha**0.6 above 0.12; near-invisible layers
# untouched), secondary greys darker, text one weight heavier and 8 % larger
# (hero numbers >= 40 u stay Light). Set BOLD["stroke"] = 1 and
# BOLD["text_k"] = 1 to get the film's original weights. Call use_contrast()
# BEFORE loading a film module so its greys pick up the darker values.
BOLD = {"stroke": 1.5, "arrow": 1.3, "gamma": .6, "gamma_from": .12, "text_k": 1.08,
        "weights": {"Inter Light": "Inter Regular", "Inter Regular": "Inter Medium"},
        "keep_light_above": 40}


def use_contrast(dim="C2CBD2", graphite="4B5967"):
    engine.DIM, engine.GRAPHITE = engine.hexc(dim), engine.hexc(graphite)


def _g(a):
    return a if a < BOLD["gamma_from"] else min(1.0, a) ** BOLD["gamma"]


def _font(font, size):
    if font == "Inter Light" and size >= BOLD["keep_light_above"]:
        return font
    return BOLD["weights"].get(font, font)


# ------------------------------------------------------------ loader ---------
def load_patched(path, patches=(), nop=(), name="figfilm", attrs=None, cwd=None):
    src = open(path).read()
    for a, b in patches:
        n = src.count(a)
        assert n == 1, f"patch target found {n}x: {a[:70]!r}"
        src = src.replace(a, b)
    mod = types.ModuleType(name)
    mod.__file__ = path
    for k, v in (attrs or {}).items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    old = os.getcwd()
    os.chdir(cwd or os.path.dirname(os.path.abspath(path)))
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    try:
        exec(compile(src, path, "exec"), mod.__dict__)
    finally:
        os.chdir(old)
    for n_ in nop:
        setattr(mod, n_, lambda *a, **k: None)
    return mod


# ------------------------------------------------------------ text filter ----
DROP = set()
BOOST = {"k": 1.0, "below": 20}
_orig_text, _orig_measure = engine.Canvas.text, engine.Canvas.measure
_IN_TEXT = [False]
_REC = [None]          # export() records drawn text sizes here (for lint_figs)


def _bs(size):
    return size * BOOST["k"] if size < BOOST["below"] else size


def _text(self, x, y, s, font=None, size=28, *a, **k):
    if s in DROP:
        return 0
    alpha = a[1] if len(a) > 1 else k.get("a", 1.0)
    if _REC[0] is not None and str(s).strip() and alpha > .05:
        dx, dy = self.c.user_to_device_distance(0, _bs(size) * BOLD["text_k"])
        _REC[0].append((round((dx * dx + dy * dy) ** .5, 2), str(s)[:40]))
    _IN_TEXT[0] = True               # text() measures internally: no double boost
    sz = _bs(size) * BOLD["text_k"]
    font = _font(font or engine.F_UI, sz)
    a = list(a)
    if len(a) > 1:
        a[1] = _g(a[1])
    elif "a" in k:
        k["a"] = _g(k["a"])
    try:
        return _orig_text(self, x, y, s, font, sz, *a, **k)
    finally:
        _IN_TEXT[0] = False


def _measure(self, s, font, size, track=0.0):
    if _IN_TEXT[0]:
        return _orig_measure(self, s, font, size, track)
    sz = _bs(size) * BOLD["text_k"]
    return _orig_measure(self, s, _font(font, sz), sz, track)


engine.Canvas.text, engine.Canvas.measure = _text, _measure

_o = {n: getattr(engine.Canvas, n) for n in ("line", "poly", "circle", "rrect", "bezier", "arrowhead")}


def _keepfill(a, fa):
    na = _g(a)
    return na, (fa * a / na if na > 0 else fa)


def _line(self, p, q, col, a=1, w=2, *x, **k):
    return _o["line"](self, p, q, col, _g(a), w * BOLD["stroke"], *x, **k)


def _poly(self, pts, col, a=1, w=2, close=False, fill=None, fa=1.0, *x, **k):
    na, nfa = _keepfill(a, fa)
    return _o["poly"](self, pts, col, na, w * BOLD["stroke"], close, fill, nfa, *x, **k)


def _circle(self, p, r, col=None, a=1, fill=None, fa=1.0, w=2):
    na, nfa = _keepfill(a, fa) if col is not None else (a, fa)
    return _o["circle"](self, p, r, col, na, fill, nfa, w * BOLD["stroke"])


def _rrect(self, x, y, w, h, r, col=None, a=1, fill=None, fa=1, lw=1.5, *z, **k):
    na, nfa = _keepfill(a, fa) if col is not None else (a, fa)
    return _o["rrect"](self, x, y, w, h, r, col, na, fill, nfa, lw * BOLD["stroke"], *z, **k)


def _bez(self, p, c1, c2, q, col, a=1, w=2, *x, **k):
    return _o["bezier"](self, p, c1, c2, q, col, _g(a), w * BOLD["stroke"], *x, **k)


def _arrow(self, tip, frm, col, a=1, size=11):
    return _o["arrowhead"](self, tip, frm, col, _g(a), size * BOLD["arrow"])


(engine.Canvas.line, engine.Canvas.poly, engine.Canvas.circle, engine.Canvas.rrect,
 engine.Canvas.bezier, engine.Canvas.arrowhead) = _line, _poly, _circle, _rrect, _bez, _arrow


# ------------------------------------------------------------ canvases -------
def _fontopts(c):
    fo = cairo.FontOptions()
    fo.set_hint_style(cairo.HINT_STYLE_NONE)
    fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
    c.set_font_options(fo)


class BigCanvas(engine.Canvas):
    """Raster canvas: design area plus an M-unit margin on every side."""
    def __init__(self, k, M):
        super().__init__(int((DW + 2 * M) * k), int((DH + 2 * M) * k))
        self.k, self.M = k, M

    def begin(self):
        c = self.c
        c.identity_matrix(); c.scale(self.k, self.k); c.translate(self.M, self.M)
        c.set_source_rgb(*PAPER); c.paint()


class VecCanvas(engine.Canvas):
    """SVG/PDF surface cropped to box=(x0, y0, w, h) in design units."""
    def __init__(self, path, box, k=1.0, kind="svg"):
        x0, y0, w, h = box
        self.W, self.H, self.k, self.box = int(w * k), int(h * k), k, box
        if kind == "svg":
            self.surf = cairo.SVGSurface(path, self.W, self.H)
            self.surf.set_document_unit(cairo.SVGUnit.PX)
        else:
            self.surf = cairo.PDFSurface(path, self.W, self.H)
        self.c = cairo.Context(self.surf)
        _fontopts(self.c)

    def begin(self):
        c = self.c
        c.identity_matrix(); c.scale(self.k, self.k)
        c.translate(-self.box[0], -self.box[1])
        c.set_source_rgb(*PAPER); c.paint()


def raster(drawfn, k=3.0, M=0):
    cv = BigCanvas(k, M) if M else engine.Canvas(int(DW * k), int(DH * k))
    drawfn(cv)
    cv.surf.flush()
    a = np.ndarray((cv.H, cv.W, 4), np.uint8, cv.surf.get_data())
    return np.ascontiguousarray(a[..., [2, 1, 0]])


def content_box(rgb, k, pad=24, thr=250, M=0):
    m = (rgb < thr).any(axis=2)
    ys, xs = np.where(m)
    x0, x1 = xs.min() / k - pad - M, xs.max() / k + pad - M
    y0, y1 = ys.min() / k - pad - M, ys.max() / k + pad - M
    x0, y0 = max(-M, x0), max(-M, y0)
    x1, y1 = min(DW + M, x1), min(DH + M, y1)
    return (x0, y0, x1 - x0, y1 - y0)


def box_of(drawfn, M=300, pad=24):
    return content_box(raster(drawfn, 1.0, M), 1.0, pad, M=M)


def union_box(boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return (x0, y0, x1 - x0, y1 - y0)


def export(name, drawfn, outdir, k=3.0, box=None, pad=24, vector=True, M=0):
    """PNG (k x design scale, 300 dpi tag, cropped) + SVG + PDF of the same box."""
    os.makedirs(outdir, exist_ok=True)
    rgb = raster(drawfn, k, M)
    if box is None:
        box = content_box(rgb, k, pad, M=M)
    x0, y0, w, h = box
    X0, Y0 = int((x0 + M) * k), int((y0 + M) * k)
    png = os.path.join(outdir, name + ".png")
    Image.fromarray(rgb[Y0:Y0 + int(h * k), X0:X0 + int(w * k)]).save(png, dpi=(300, 300))
    kinds = ("svg", "pdf") if vector else ("pdf-probe",)
    for kind in kinds:
        path = os.path.join(outdir, f"{name}.{kind}") if vector else os.devnull
        vc = VecCanvas(path, box, 1.0, "svg" if kind == "svg" else "pdf")
        _REC[0] = [] if kind != "svg" else None
        try:
            drawfn(vc)
        finally:
            rec, _REC[0] = _REC[0], None
        vc.surf.finish()
        if rec is not None:                      # text sizes in design units
            _write_sizes(outdir, name, box, rec)
    return png, box


def _write_sizes(outdir, name, box, rec):
    import json
    p = os.path.join(outdir, "_textsizes.json")
    try:
        d = json.load(open(p))
    except (OSError, ValueError):
        d = {}
    d[name] = dict(box=[round(v, 2) for v in box], text=sorted(rec)[:12],
                   min=min((r[0] for r in rec), default=None), n=len(rec))
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)


def scaled_panel(cv, at, corner, s):
    """Context manager-ish helper: push a transform that maps design point
    `corner` to `at` and scales by s (enlarge a fixed panel beside a stage).
    Use panel_inv to pre-map points passed into the panel (e.g. tethers)."""
    c = cv.c
    c.save(); c.translate(*at); c.scale(s, s); c.translate(-corner[0], -corner[1])
    return lambda: c.restore()


def panel_inv(p, at, corner, s):
    return (corner[0] + (p[0] - at[0]) / s, corner[1] + (p[1] - at[1]) / s)
