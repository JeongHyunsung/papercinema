"""Build the PPT figure set from the film's drawing code.

  python3 make_figs.py [--k 3] [--preview]

Outputs in figs/out/: PNG (white background, 300 dpi tag), SVG and PDF per
figure. Composite figures are drawn on one cairo surface, so they stay vector
except where a panel is a numpy-composited raster (the 568M unit chart), which
is embedded as an image.
"""
import argparse, math, os, json
import numpy as np
import cairo
from PIL import Image
import figlib as FL
import design as DZ
from figlib import F
import engine
from engine import (DW, DH, PAPER, INK, GRAPHITE, DIM, TEAL, CORAL, AMBER,
                    BLUE, F_MONO, F_MONO_M)

OUT = os.path.join(FL.HERE, "out")


# ======================================================== composite canvas ===
class PanelCanvas(engine.Canvas):
    """Draws one film frame into a sub-rectangle of a shared surface."""
    def __init__(self, surf, K):
        self.surf, self.c, self.K = surf, cairo.Context(surf), K
        self.k = K
        fo = cairo.FontOptions()
        fo.set_hint_style(cairo.HINT_STYLE_NONE)
        fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
        self.c.set_font_options(fo)
        self.base = (0, 0, 1.0, (0, 0, DW, DH))

    def begin(self):
        dx, dy, s, (bx, by, bw, bh) = self.base
        c = self.c
        c.reset_clip()
        c.identity_matrix()
        c.scale(self.K, self.K)
        c.translate(dx, dy)
        c.scale(s, s)
        c.translate(-bx, -by)
        c.rectangle(bx, by, bw, bh)
        c.clip()
        c.set_source_rgb(*PAPER)
        c.paint()


def composite(name, W, H, panels, arrows=(), K=3.0, kinds=("png", "svg", "pdf")):
    """panels: list of dict(kind='draw'|'image', fn|img, box, dx, dy, s).
    Coordinates in composite design units (W×H)."""
    os.makedirs(OUT, exist_ok=True)
    for kind in kinds:
        path = os.path.join(OUT, f"{name}.{kind}")
        if kind == "png":
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(W * K), int(H * K))
            k = K
        elif kind == "svg":
            surf = cairo.SVGSurface(path, W, H); k = 1.0
        else:
            surf = cairo.PDFSurface(path, W, H); k = 1.0
        cv = PanelCanvas(surf, k)
        c = cv.c
        c.identity_matrix(); c.scale(k, k)
        c.set_source_rgb(*PAPER); c.paint()
        for p in panels:
            if p["kind"] == "draw":
                cv.base = (p["dx"], p["dy"], p["s"], p["box"])
                p["fn"](cv)
            else:
                img = p["img"]                      # RGB uint8, covers box at p['ik'] px/unit
                h, w = img.shape[:2]
                a = np.zeros((h, w, 4), np.uint8)
                a[..., 0], a[..., 1], a[..., 2], a[..., 3] = img[..., 2], img[..., 1], img[..., 0], 255
                isurf = cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_ARGB32, w, h)
                c.reset_clip(); c.identity_matrix(); c.scale(k, k)
                c.translate(p["dx"], p["dy"])
                c.scale(p["s"] / p["ik"], p["s"] / p["ik"])
                c.set_source_surface(isurf, 0, 0)
                c.get_source().set_filter(cairo.FILTER_BEST)
                c.paint()
        c.reset_clip(); c.identity_matrix(); c.scale(k, k)
        for (p0, p1) in arrows:
            cv.line(p0, p1, GRAPHITE, .9, 2.2)
            cv.arrowhead(p1, p0, GRAPHITE, .9, 15)
        if kind == "png":
            surf.flush()
            a = np.ndarray((surf.get_height(), surf.get_width(), 4), np.uint8, surf.get_data())
            Image.fromarray(np.ascontiguousarray(a[..., [2, 1, 0]])).save(path, dpi=(300, 300))
        else:
            surf.finish()
    return os.path.join(OUT, f"{name}.png")


def box_of(fn, M=300, pad=24):
    rgb = FL.raster(fn, 1.0, M)
    return FL.content_box(rgb, 1.0, pad, M=M)


def raster_panel(fn, box, ik):
    rgb = FL.raster(fn, ik, 0)
    x0, y0, w, h = box
    return rgb[int(y0 * ik):int((y0 + h) * ik), int(x0 * ik):int((x0 + w) * ik)]


def row_layout(boxes, gap, H=None, valign="center"):
    """Place boxes left→right at scale 1; returns (W, H, [(dx, dy)])."""
    Hm = H or max(b[3] for b in boxes)
    x, out = 0.0, []
    for b in boxes:
        dy = (Hm - b[3]) / 2 if valign == "center" else 0
        out.append((x, dy)); x += b[2] + gap
    return x - gap, Hm, out


# ================================================================ hooks ======
def pareto_hook(cv, t, S, oa):
    pts = sorted((so, en) for (_, _, so, en) in F.T2)
    front, best = [], 1e9
    for so, en in pts:
        if en < best:
            front.append((so, en)); best = en
    P = [S((so * F.RPX, -en * F.EY)) for so, en in front]
    # staircase boundary of the dominated region (min overhead, min energy)
    stair = [P[0]]
    for a, b in zip(P, P[1:]):
        stair += [(b[0], a[1]), b]
    c = cv.c
    for k in range(len(stair) - 1):
        cv.line(stair[k], stair[k + 1], AMBER, .85 * oa, 2.0, [7, 6])
    for p in P:
        cv.circle(p, 13, AMBER, .85 * oa, w=1.6)
    F.FIG_PARETO_FRONT = front


# ===================================================== non-convergence layer =
def nonconv_layer(t3):
    """δ(00,11) = 01 and δ(00,01) = 11: under (D,CK) = 00 the state shuttles
    11 → 01 → 11 … and never reaches a fixed point (StableSucc undefined)."""
    def fn(cv):
        cam = F.stage_cam(t3)
        H = F.H_E
        a, b = F.slot_uv(0, 3), F.slot_uv(0, 1)      # (00,11) and (00,01)
        init = F.slot_uv(*F.INIT)
        # entry edge: CK falls from the start pair
        pts = F.est_pts(F.INIT, (0, 3))
        F.draw_proj_path(cv, cam, pts, H, INK, .85, 1.8, dash=True)
        # the two-state loop, drawn as two arcs (above / below)
        def arc(p, q, bulge):
            c1 = (p[0] + (q[0] - p[0]) * .25, p[1] + bulge)
            c2 = (p[0] + (q[0] - p[0]) * .75, q[1] + bulge)
            pts = [F.bez(p, c1, c2, q, k / 50) for k in range(51)]
            return [x for x in pts if math.dist(x, p) > 30 and math.dist(x, q) > 32]
        F.draw_proj_path(cv, cam, arc(a, b, -58), H, CORAL, 1, 2.4)
        F.draw_proj_path(cv, cam, arc(b, a, 58), H, CORAL, 1, 2.4)
        # rings on the two shuttling states
        for ij in ((0, 3), (0, 1)):
            x, y, sc, _ = cam.P((*F.slot_uv(*ij), H))
            cv.circle((x, y), 25 * sc, CORAL, 1, w=F.sw(sc, 2.4))
        # chips
        F.chip(cv, cam, (*a, H), 30, -98, "δ(00,11) = 01", CORAL, 1, size=13)
        F.chip(cv, cam, (*b, H), -70, 84, "δ(00,01) = 11", CORAL, 1, size=13)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, H)
        F.bb_text(cv, cam, mid, 170, -150,
                  "11 → 01 → 11 → …  never settles: non-convergence",
                  engine.F_UI_M, 17, CORAL, 1)
        # δ panel rows written by this candidate (same card transform)
        panel_push(cv)
        x0 = F.PX
        cols = [0, 40, 98, 138, 236, 276]
        for r, v in ((3, 1), (1, 3)):
            y = F.prow_y(r)
            i, s = r >> 2, r & 3
            cv.rrect(x0 - 18, y - 18, 342, 24, 5, CORAL, 1, fill=PAPER, fa=1, lw=1.6)
            cv.rrect(x0 - 18, y - 18, 342, 24, 5, None, 1, fill=CORAL, fa=.12)
            for kk, bv in enumerate([i >> 1, i & 1, s >> 1, s & 1]):
                cv.text(x0 + cols[kk], y, str(bv), F_MONO, 15, INK, 1, anchor="c")
            for kk, bv in ((4, v >> 1), (5, v & 1)):
                cv.text(x0 + cols[kk], y, str(bv), F_MONO_M, 15, CORAL, 1, anchor="c")
        cv.c.restore()
    return fn


_STAGE_CAM = F.stage_cam
_TREE_HUD = F.scene_tree_hud
# One fixed, near-orthographic oblique camera for the 3-D stage (2c–2j):
# a very distant eye with a matching focal length removes perspective, so every
# pill, label and chip is drawn at the same size and the stage fills the area
# left of the δ table.
_D = 40000.0
STEP_CAM = F.StageCam(960, 570, 60, _D, .62, -.10, -300, 5, f=1.36 * _D)

# The δ table is the subject of every step, so on slides it is enlarged and
# placed beside the stage: the whole card (rows, highlights, conflict mark and
# the node→row tethers) is scaled by PANEL_S about its top-left corner and moved
# to PANEL_AT. The film's small search-tree inset is left out of the figures.
PANEL_S, PANEL_AT = 1.42, (1335.0, 150.0)
_PA = (F.PX - 26, F.PY + 44)                       # card corner in film coords


def panel_fwd(p):
    return (PANEL_AT[0] + (p[0] - _PA[0]) * PANEL_S,
            PANEL_AT[1] + (p[1] - _PA[1]) * PANEL_S)


def panel_inv(p):
    return (_PA[0] + (p[0] - PANEL_AT[0]) / PANEL_S,
            _PA[1] + (p[1] - PANEL_AT[1]) / PANEL_S)


def panel_push(cv):
    c = cv.c
    c.save()
    c.translate(PANEL_AT[0], PANEL_AT[1])
    c.scale(PANEL_S, PANEL_S)
    c.translate(-_PA[0], -_PA[1])


def _fig_panel(raw, cv, t, node_px):
    nodes = {k: panel_inv(p) for k, p in node_px.items()}
    panel_push(cv)
    try:
        raw(cv, t, nodes)
    finally:
        cv.c.restore()
STEP_BOOST = 1.15           # small in-scene text (< 20 units) ×1.15 for slides


def frame_plus(t3, extra=None, opts=None, hooks=None, cam=None):
    def fn(cv):
        F.FIG_OPTS.clear(); F.FIG_OPTS.update(opts or {})
        F.FIG_HOOKS.clear(); F.FIG_HOOKS.update(hooks or {})
        if cam is not None:
            F.stage_cam = lambda t: cam
            F.FIG_PANEL = _fig_panel
            F.scene_tree_hud = lambda *a, **k: None
        try:
            F.draw3(cv, t3)
            if extra:
                extra(cv)               # overlay in the same design space
        finally:
            F.stage_cam = _STAGE_CAM
            F.FIG_PANEL = lambda f, *a: f(*a)
            F.scene_tree_hud = _TREE_HUD
            F.FIG_HOOKS.clear()
    return fn


# ============================================================== figure set ===
def build(K=3.0, preview=False):
    vec = not preview
    kinds = ("png",) if preview else ("png", "svg", "pdf")
    made = []

    # ---- 1. motivation: purpose-built static figure (design.py) -----------
    FL.BOOST["k"] = 1.0
    bx = None
    for nm, box in (("1_motivation", None),
                    ("1a_wrong_output", (60, 42, 1000, 660)),
                    ("1b_search_space", (1130, 42, 745, 660))):
        made.append(FL.export(nm, DZ.motivation, OUT, k=K, box=box, pad=30,
                              vector=vec)[0])

    # ---- 2. methodology: RBG / ESTG on the 3-D stage, step by step ---------
    steps = [
        ("2a_rbg", 14.26, None),
        ("2b_rbg_failing_path", 16.98, None),
        ("2c_estg_over_rbg", 19.46, None),
        ("2d_step1_start_pair", 21.55, None),
        ("2e_step2_wrong_output", 24.55, None),
        ("2f_step3_instantiate", 28.45, None),
        ("2g_step4_repeat", 30.15, None),
        ("2h_step5_entry_conflict", 33.55, None),
        ("2i_step5_branch_pruned", 34.35, None),
        ("2j_non_convergence", 22.95, nonconv_layer(22.95)),
    ]
    # steps 2d–2j share one camera AND one crop, so they flip cleanly in PPT
    FL.BOOST["k"] = STEP_BOOST
    fns = {nm: frame_plus(t3, extra, cam=STEP_CAM if nm >= "2c" else None)
           for nm, t3, extra in steps}
    sb = [box_of(fns[nm]) for nm, _, _ in steps if nm >= "2d"]
    x0 = min(b[0] for b in sb); y0 = min(b[1] for b in sb)
    x1 = max(b[0] + b[2] for b in sb); y1 = max(b[1] + b[3] for b in sb)
    ubox = (x0, y0, x1 - x0, y1 - y0)
    for nm, _, _ in steps:
        FL.BOOST["k"] = STEP_BOOST
        bx = ubox if nm >= "2d" else None
        made.append(FL.export(nm, fns[nm], OUT, k=K, box=bx, vector=vec, M=300)[0])

    # ---- 3. key result: purpose-built static figure (design.py) -----------
    FL.BOOST["k"] = 1.0
    made.append(FL.export("3_key_result", DZ.key_result, OUT, k=K, pad=30,
                          vector=vec)[0])
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, default=3.0)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    for p in build(a.k, a.preview):
        print(p)
    print("pareto front:", getattr(F, "FIG_PARETO_FRONT", None))
