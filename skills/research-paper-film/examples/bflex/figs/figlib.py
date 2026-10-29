"""Static PPT figures from the B-Flex film, without touching the film pipeline.

The film's own drawing code (src/film.py) is loaded into a separate module
namespace with a few figure-only patches applied to the *source text in
memory*; nothing under src/ is modified. Frames are drawn on the v3 animation
clock (film.draw3), so every structure is the same object as in the film.

Text policy (agreed with the author): titles, subtitles, legends, captions,
source tags, act labels, step markers and breadcrumbs are removed (they will be
typed in PowerPoint); in-scene annotation chips, node labels, numbers and axis
ticks are kept.
"""
import os, sys, math, types
import numpy as np
import cairo
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src")
sys.path.insert(0, SRC)
import engine                                    # noqa: E402
from engine import DW, DH, PAPER                 # noqa: E402

# ------------------------------------------------------------ patched film ----
PATCHES = [
    # 2-bit search-space count (hidden in the film since V4; wanted in the figure)
    ("(0.0 * window(t, T_SQ0, T_CB0 - .2, .4, .35), \"2-bit state\"",
     "(window(t, T_SQ0, T_CB0 - .2, .4, .35), \"2-bit state\""),
    # step-3 X1/X2 tags (removed from the film for exposure time; fine in a still)
    ("    aa = 0.0   # v4: X1/X2 tags removed (too brief); the step marker carries it\n",
     "    aa = a * window(t, T_X1 + .45, T_FOLLOW + .3, .2, .3)\n"),
    ("xa = 0.0 * window(t, T_X1 + .3, T_S4 + .3, .2, .3)",
     "xa = ia * window(t, T_X1 + .3, T_S4 + .3, .2, .3)"),
    ("xa2 = 0.0 * window(t, T_X2 + .45, T_S4 + .3, .2, .3)",
     "xa2 = ia * window(t, T_X2 + .45, T_S4 + .3, .2, .3)"),
    ("ka = 0.0   # v4: carried by the step marker (readable for the whole step)",
     "ka = ia * window(t, T_KEEP, T_S4 + .3, .2, .3)"),
    # white knockout behind the (removed) stage headers would cut the arc edges
    ("cv.rrect(100, 120, 1120, 146, 10, fill=PAPER, fa=.88 * max(a, a2k))",
     "pass"),
    # step-2 label sits under the δ panel in the fixed step camera: shift left
    ("    bb_text(cv, cam, (*RN[(0, 1)], H_E), -10, 92,\n",
     "    bb_text(cv, cam, (*RN[(0, 1)], H_E), -150, 92,\n"),
    # slide legibility (text is boosted): pill labels clear of the node rings,
    # the conflict hint as a chip so it reads over the faded pills, and room
    # under the last δ row for its label
    ("            bb_text(cv, cam, (u - w / 2 + 12, v - hh / 2 - 12, h), 0, 0,\n",
     "            bb_text(cv, cam, (u - w / 2 + 12, v - hh / 2 - 20, h), 0, 0,\n"),
    ("    bb_text(cv, cam, (fp[0] + 20, fp[1], 0), 0, 0,\n"
     "            \"CK rises with D = 1 → Q must become 1\", F_UI_M, 13, AMBER, aa4,\n"
     "            anchor=\"l\")\n",
     "    chip(cv, cam, (fp[0] + 20, fp[1], 0), -140, 80,\n"
     "         \"CK rises with D = 1 → Q must become 1\", AMBER, aa4, size=13)\n"),
    # δ panel hook: figures may re-place/scale the whole card (with tethers)
    ("@overlay\ndef draw_panel(cv, t, node_px):\n",
     "@overlay\ndef draw_panel(cv, t, node_px):\n"
     "    return FIG_PANEL(_draw_panel_raw, cv, t, node_px)\n\n\n"
     "def _draw_panel_raw(cv, t, node_px):\n"),
    # scatter: optional Pareto front + optional legend
    # δ panel: drop the (removed) title band so the card hugs the table
    ("    cv.shadow(x0 - 26, y0 - 18, 392, 96 + 16 * PROW + 12, 14, a)\n"
     "    cv.rrect(x0 - 26, y0 - 18, 392, 96 + 16 * PROW + 12, 14, DIM,",
     "    cv.shadow(x0 - 26, y0 + 44, 392, 34 + 16 * PROW + 30, 14, a)\n"
     "    cv.rrect(x0 - 26, y0 + 44, 392, 34 + 16 * PROW + 30, 14, DIM,"),
    ("        lx, ly = 1250, 300\n",
     "        FIG_HOOKS.get('scatter', lambda *a: None)(cv, t, S, oa)\n"
     "        lx, ly = (1250, 300) if FIG_OPTS.get('legend') else (-9e4, -9e4)\n"),
]


# ------------------------------------------------------------ fonts ----------
# Figures use Inter throughout (the film uses JetBrains Mono for data labels and
# Inter Display for big numerals). Rebinding the engine names before the film
# source is exec'd makes every `from engine import *` name resolve to Inter.
# "Inter Regular" is a renamed copy of Inter-Regular.otf (setup_fonts.py): the
# plain family name "Inter" resolves to the Medium face under fontconfig here.
INTER = {"F_UI": "Inter Regular", "F_MONO": "Inter Regular",
         "F_MONO_M": "Inter Medium", "F_MONO_L": "Inter Light",
         "F_TITLE": "Inter SemiBold", "F_TITLE_L": "Inter Light"}
for _k, _v in INTER.items():
    setattr(engine, _k, _v)


# ------------------------------------------------------------ slide contrast -
# Slides are viewed small and projected: strokes thicker, faded elements and
# secondary greys darker, text one weight heavier. Set before the film loads so
# its `from engine import *` picks up the darker greys.
BOLD = {"stroke": 1.5, "arrow": 1.3, "gamma": .6, "gamma_from": .12,
        "text_k": 1.08,
        "weights": {"Inter Light": "Inter Regular", "Inter Regular": "Inter Medium"},
        "keep_light_above": 40}           # hero numbers (>= 40 u) stay Light
engine.DIM = engine.hexc("C2CBD2")
engine.GRAPHITE = engine.hexc("4B5967")
engine.BG_IN = engine.PAPER


def load_film():
    path = os.path.join(SRC, "film.py")
    src = open(path).read()
    for a, b in PATCHES:
        assert src.count(a) == 1, ("patch target not found", a[:60])
        src = src.replace(a, b)
    mod = types.ModuleType("figfilm")
    mod.__file__ = path
    mod.FIG_HOOKS, mod.FIG_OPTS = {}, {}
    mod.FIG_PANEL = lambda f, *a: f(*a)
    cwd = os.getcwd()
    os.chdir(SRC)
    try:
        exec(compile(src, path, "exec"), mod.__dict__)
    finally:
        os.chdir(cwd)
    # HUD-only overlays: removed entirely
    nop = lambda *a, **k: None                   # noqa: E731
    for name in ("act_label", "tag", "caption", "breadcrumb", "stage_hud",
                 "hud_race", "hud_ff1"):
        setattr(mod, name, nop)
    return mod


F = load_film()

# ------------------------------------------------------------ text filter -----
DROP = {
    "Prior automated FF search stops at 2-bit states.",
    "Partial transition table",
    "δ(i, s) → s'   ·   · = not yet assigned",
    "SEARCH TREE",
    "valid 3-bit-state FF FSMs",
    "exhaustive search · 787 s · 16 threads (Table 1)",
    "average of 5 runs · cell order is arbitrary",
    "§4.1 search space: Q = ¬s2 · initial state 011 · ≤ 1 bit flip per transition",
    "valid FSMs with C_FF ≤ 20",
    "1 cell = 1 FSM",
    "1 cell = 1 valid FSM",
    "circled: the step-5 conflict",
}
EXTRA_DROP = set()
_orig_text = engine.Canvas.text
_orig_measure = engine.Canvas.measure
# small-text boost for film frames on slides: sizes below BOOST["below"] are
# multiplied by BOOST["k"] (text and measure alike, so chips resize with text)
BOOST = {"k": 1.0, "below": 20}


def _bs(size):
    return size * BOOST["k"] if size < BOOST["below"] else size


_IN_TEXT = [False]


def _text(self, x, y, s, font=engine.F_UI, size=28, *a, **k):
    if s in DROP or s in EXTRA_DROP:
        return 0
    _IN_TEXT[0] = True                 # text() measures with the boosted size
    sz = _bs(size) * BOLD["text_k"]
    font = _font(font, sz)
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


engine.Canvas.text = _text
engine.Canvas.measure = _measure


def _g(a):
    """Darken faded strokes/text, keeping their order; leave near-invisible
    layers (e.g. alpha .05 trails) as they are."""
    return a if a < BOLD["gamma_from"] else min(1.0, a) ** BOLD["gamma"]


_o_line, _o_poly, _o_circle = engine.Canvas.line, engine.Canvas.poly, engine.Canvas.circle
_o_rrect, _o_bez, _o_arrow = engine.Canvas.rrect, engine.Canvas.bezier, engine.Canvas.arrowhead


def _line(self, p, q, col, a=1, w=2, *x, **k):
    return _o_line(self, p, q, col, _g(a), w * BOLD["stroke"], *x, **k)


def _keepfill(a, fa):
    na = _g(a)
    return na, (fa * a / na if na > 0 else fa)


def _poly(self, pts, col, a=1, w=2, close=False, fill=None, fa=1.0, *x, **k):
    na, nfa = _keepfill(a, fa)
    return _o_poly(self, pts, col, na, w * BOLD["stroke"], close, fill, nfa, *x, **k)


def _circle(self, p, r, col=None, a=1, fill=None, fa=1.0, w=2):
    na, nfa = _keepfill(a, fa) if col is not None else (a, fa)
    return _o_circle(self, p, r, col, na, fill, nfa, w * BOLD["stroke"])


def _rrect(self, x, y, w, h, r, col=None, a=1, fill=None, fa=1, lw=1.5, *z, **k):
    na, nfa = _keepfill(a, fa) if col is not None else (a, fa)
    return _o_rrect(self, x, y, w, h, r, col, na, fill, nfa, lw * BOLD["stroke"], *z, **k)


def _bez(self, p, c1, c2, q, col, a=1, w=2, *x, **k):
    return _o_bez(self, p, c1, c2, q, col, _g(a), w * BOLD["stroke"], *x, **k)


def _arrow(self, tip, frm, col, a=1, size=11):
    return _o_arrow(self, tip, frm, col, _g(a), size * BOLD["arrow"])


engine.Canvas.line, engine.Canvas.poly, engine.Canvas.circle = _line, _poly, _circle
engine.Canvas.rrect, engine.Canvas.bezier, engine.Canvas.arrowhead = _rrect, _bez, _arrow


def _font(font, size):
    if font == "Inter Light" and size >= BOLD["keep_light_above"]:
        return font
    return BOLD["weights"].get(font, font)


# ------------------------------------------------------------ canvases --------
class VecCanvas(engine.Canvas):
    """Same drawing API on an SVG/PDF surface, cropped to (x0, y0, w, h) in
    design units."""
    def __init__(self, path, box, k=1.0, kind="svg"):
        x0, y0, w, h = box
        self.W, self.H, self.k, self.box = int(w * k), int(h * k), k, box
        if kind == "svg":
            self.surf = cairo.SVGSurface(path, self.W, self.H)
            self.surf.set_document_unit(cairo.SVGUnit.PX)
        else:
            self.surf = cairo.PDFSurface(path, self.W, self.H)
        self.c = cairo.Context(self.surf)
        fo = cairo.FontOptions()
        fo.set_hint_style(cairo.HINT_STYLE_NONE)
        fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
        self.c.set_font_options(fo)

    def begin(self):
        c = self.c
        c.identity_matrix()
        c.scale(self.k, self.k)
        c.translate(-self.box[0], -self.box[1])
        c.set_source_rgb(*PAPER)
        c.paint()


class BigCanvas(engine.Canvas):
    """Raster canvas with an M-unit margin around the 1920×1080 design area,
    so content the film camera pushes off-screen is still captured."""
    def __init__(self, k, M):
        super().__init__(int((DW + 2 * M) * k), int((DH + 2 * M) * k))
        self.k, self.M = k, M

    def begin(self):
        c = self.c
        c.identity_matrix()
        c.scale(self.k, self.k)
        c.translate(self.M, self.M)
        c.set_source_rgb(*PAPER)
        c.paint()


def raster(drawfn, k=3.0, M=0):
    """Render drawfn(cv) at k × design size (plus margin M); RGB array."""
    cv = BigCanvas(k, M) if M else engine.Canvas(int(DW * k), int(DH * k))
    drawfn(cv)
    cv.surf.flush()
    a = np.ndarray((cv.H, cv.W, 4), np.uint8, cv.surf.get_data())
    return np.ascontiguousarray(a[..., [2, 1, 0]])


def content_box(rgb, k, pad=24, thr=250, M=0):
    """Bounding box (design units) of non-white content, padded."""
    m = (rgb < thr).any(axis=2)
    ys, xs = np.where(m)
    x0, x1 = xs.min() / k - pad - M, xs.max() / k + pad - M
    y0, y1 = ys.min() / k - pad - M, ys.max() / k + pad - M
    x0, y0 = max(-M, x0), max(-M, y0)
    x1, y1 = min(DW + M, x1), min(DH + M, y1)
    return (x0, y0, x1 - x0, y1 - y0)


def frame(t3, extra=None):
    """A drawing function for the film frame at v3 time t3 (+ extra layer)."""
    def fn(cv):
        F.draw3(cv, t3)
        if extra:
            extra(cv)
    return fn


def export(name, drawfn, outdir, k=3.0, box=None, pad=24, vector=True, M=0):
    """PNG (cropped, white bg) + optional SVG/PDF of the same crop."""
    os.makedirs(outdir, exist_ok=True)
    rgb = raster(drawfn, k, M)
    if box is None:
        box = content_box(rgb, k, pad, M=M)
    x0, y0, w, h = box
    X0, Y0 = int((x0 + M) * k), int((y0 + M) * k)
    crop = rgb[Y0:Y0 + int(h * k), X0:X0 + int(w * k)]
    png = os.path.join(outdir, name + ".png")
    Image.fromarray(crop).save(png, dpi=(300, 300))
    if vector:
        for kind in ("svg", "pdf"):
            vc = VecCanvas(os.path.join(outdir, f"{name}.{kind}"), box, 1.0, kind)
            drawfn(vc)
            vc.surf.finish()
    return png, box
