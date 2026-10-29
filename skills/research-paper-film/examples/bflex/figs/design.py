"""Purpose-built static figures (not film frames) for slides.

Same palette, strokes and primitives as the film (engine.Canvas + film helpers),
but laid out once, for a 16:9 slide, with every element in its final state.
Typeface: Inter only.

Design units: the drawing is made in a 1920×1080 design space; export crops to
content. Sizes are chosen for a figure placed ~12 in wide on a 13.33 in slide
(1 design unit ≈ 0.5 pt), so body labels are ≥ 22 units (≈ 11 pt).
"""
import math, random
import cairo
import figlib as FL
from figlib import F
import engine
from engine import INK, GRAPHITE, DIM, TEAL, CORAL, AMBER, BLUE, PAPER

UI, UI_L, UI_M, UI_SB = ("Inter Regular", "Inter Light", "Inter Medium",
                         "Inter SemiBold")
TEAL_L = engine.hexc("D3E8EA")          # light teal of the 568M block
TEAL_M = engine.hexc("A9D2D6")


# ============================================================ helpers ========
def placed(points, box):
    """Affine-fit a dict of projected points into box=(x0,y0,w,h), keeping
    aspect; returns (dict, scale)."""
    xs = [p[0] for p in points.values()]; ys = [p[1] for p in points.values()]
    w0, h0 = max(xs) - min(xs), max(ys) - min(ys)
    s = min(box[2] / w0, box[3] / h0)
    cx0, cy0 = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    cx1, cy1 = box[0] + box[2] / 2, box[1] + box[3] / 2
    return {k: ((p[0] - cx0) * s + cx1, (p[1] - cy0) * s + cy1)
            for k, p in points.items()}, s


def state_graph(cv, nbits, box, t_cam, r=30, label=24):
    """2-bit square / 3-bit cube, film geometry and node style."""
    cam = F.cube_cam(t_cam)
    ext = 1.0 if nbits == 3 else 0.0
    raw, scl = {}, {}
    for s in range(2 ** nbits):
        st = s if nbits == 3 else s << 1
        p, sc, _ = cam.proj(F.vpos(st, 3, ext))
        raw[s], scl[s] = p, sc
    P, _ = placed(raw, box)
    for a, b in F.cube_edges(nbits):
        z = nbits == 3 and (a ^ b) == 1
        cv.line(P[a], P[b], GRAPHITE if z else INK, .8, 2.2)
    for s in sorted(P, key=lambda k: scl[k]):          # far nodes first
        rr = r * (scl[s] / max(scl.values())) ** .5
        cv.circle(P[s], rr, INK, 1, fill=PAPER, fa=1, w=2)
        cv.text(P[s][0], P[s][1] + label * .36, F.bits(s, nbits), UI_M,
                label * rr / r, INK, 1, anchor="c")
    return P


def arrow(cv, p, q, col=GRAPHITE, a=1, w=2.2, size=15):
    cv.line(p, q, col, a, w)
    cv.arrowhead(q, p, col, a, size)


def sub_text(cv, xc, y, base, sub, font, size, col, a=1):
    """Centered 'base' with a subscript, e.g. C_FF."""
    w1 = cv.measure(base, font, size); w2 = cv.measure(sub, font, size * .66)
    x = xc - (w1 + w2) / 2
    cv.text(x, y, base, font, size, col, a)
    cv.text(x + w1 + 1, y + size * .22, sub, font, size * .66, col, a)


def count_block(cv, x, y, n, per_row, pitch, cell, col, fa=.95, r=1.6):
    for j in range(n):
        cx = x + (j % per_row) * pitch
        cy = y - (j // per_row) * pitch
        cv.rrect(cx, cy - cell, cell, cell, r, None, 1, fill=col, fa=fa)


# ============================================================ 1. motivation ==
def motivation(cv):
    cv.begin()
    # ---------------- left: one reordered transition, wrong Q ---------------
    X0, XE = 170, 1010
    xs = [X0 + (k + 1) * (XE - X0) / 7 for k in range(6)]
    WY = {"D": 250, "CK": 385, "Q": 520}
    A = 32
    for nm, y in WY.items():
        cv.text(X0 - 36, y + 11, nm, UI_M, 32, INK, 1, anchor="r")

    def sig(name, start, switches, col_of=None, end=XE):
        y0 = WY[name]
        Y = lambda lvl: y0 + (A if lvl == 0 else -A)       # noqa: E731
        lvl, x = start, X0
        segs = []
        for xsw, nl in switches:
            segs.append(((x, Y(lvl)), (xsw, Y(lvl)), xsw))
            segs.append(((xsw, Y(lvl)), (xsw, Y(nl)), xsw))
            lvl, x = nl, xsw
        segs.append(((x, Y(lvl)), (end, Y(lvl)), end))
        for p, q, xk in segs:
            c = col_of(p, q) if col_of else INK
            cv.line(p, q, c, 1, 3.2, cap=cairo.LINE_CAP_SQUARE)

    for k, x in enumerate(xs):                       # transition guides
        cv.line((x, 175), (x, 560), GRAPHITE, .5, 1.3, [2, 6])
    sig("D", 0, [(xs[2], 1), (xs[5], 0)])
    sig("CK", 1, [(xs[0], 0), (xs[1], 1), (xs[3], 0), (xs[4], 1)])
    qr, qf = xs[4] + 10, xs[5] + 10
    sig("Q", 0, [(qr, 1), (qf, 0)],
        col_of=lambda p, q: CORAL if min(p[0], q[0]) >= qf - .1 else INK)
    yq1 = WY["Q"] - A
    cv.line((qf, yq1), (XE, yq1), BLUE, .9, 2.4, [4, 8])
    cv.text(XE, yq1 - 14, "expected Q", UI_M, 22, BLUE, 1, anchor="r")
    cv.text(XE, WY["Q"] + A + 32, "SeGen-20 output", UI_M, 22, CORAL, 1,
            anchor="r")
    for k, x in enumerate(xs):                       # 1–5 pass, 6 fails
        bad = k == 5
        cv.circle((x, 140), 18, None, 1, fill=CORAL if bad else DIM, fa=1)
        cv.text(x, 140 + 7.5, str(k + 1), UI_M, 20, PAPER if bad else INK, 1,
                anchor="c")
        if bad:
            F.xmark(cv, (x + 38, 140), 9, CORAL, 1, 3)
        else:
            F.check(cv, (x + 38, 141), 9, TEAL, 1, 1.0, 3)
    cv.text(xs[5] - 26, 88, "D 1→0 replaces CK 1→0", UI_M, 21, CORAL, 1,
            anchor="c")

    # ---------------- divider -----------------------------------------------
    cv.line((1100, 110), (1100, 600), DIM, 1, 1.5)

    # ---------------- right: 2-bit square → 3-bit cube ----------------------
    sq = state_graph(cv, 2, (1190, 230, 150, 150), 8.02, r=27, label=21)
    cb = state_graph(cv, 3, (1500, 130, 290, 330), 9.65, r=31, label=21)
    arrow(cv, (1385, 305), (1462, 305))
    for x, lab, big, approx in ((1190, "2-bit state", "3^{16}", "≈ 4.3 × 10^{7}"),
                                (1500, "3-bit state", "4^{32}", "≈ 1.8 × 10^{19}")):
        cv.text(x, 510, lab.upper(), UI_M, 18, AMBER, 1, track=.14)
        cv.text(x, 580, big, UI_L, 64, INK, 1)
        cv.text(x, 628, approx, UI_L, 32, INK, 1)       # stacked: no collision
    cv.text(1500, 672, "brute force, 1 thread: ~10^{6} years", UI, 21, CORAL, 1)


# ============================================================ 3. key result ==
def key_result(cv):
    cv.begin()
    BASE = 640                                         # common baseline
    # ---------------- A: 568,832,054 vs 18 ----------------------------------
    S0, S = (80, 250), 390                             # big block
    c = cv.c
    g = cairo.LinearGradient(S0[0], S0[1], S0[0] + S, S0[1] + S)
    g.add_color_stop_rgb(0, *TEAL_L)
    g.add_color_stop_rgb(.75, *TEAL_L)
    g.add_color_stop_rgb(1, *TEAL_M)
    c.rectangle(S0[0], S0[1], S, S); c.set_source(g); c.fill()
    cv.text(S0[0], S0[1] - 74, "3-BIT STATE", UI_M, 18, AMBER, 1, track=.14)
    cv.text(S0[0], S0[1] - 20, "568,832,054", UI_L, 50, INK, 1)
    L, LR = (S0[0] + 165, S0[1] + 150), 82

    # ---------------- B: the 468 with C_FF ≤ 20, by C_FF ---------------------
    cff, cnt = F.H_CFF, F.H_CNT
    HX0, PER, P, CELL, GAP = 590, 6, 8.6, 7.0, 10
    BW = PER * P
    def cell_xy(k, j):
        return (HX0 + k * (BW + GAP) + (j % PER) * P + CELL / 2,
                BASE - (j // PER) * P - CELL / 2)
    # mapping: each of the 468 leaves the block and lands on its bar
    rng = random.Random(21)
    lens_r2 = (LR + 14) ** 2
    srcs = []
    for k, n_ in enumerate(cnt):
        for j in range(n_):
            while True:
                u = (S0[0] + 12 + rng.random() * (S - 24),
                     S0[1] + 12 + rng.random() * (S - 24))
                if (u[0] - L[0]) ** 2 + (u[1] - L[1]) ** 2 > lens_r2:
                    break
            srcs.append((u, cell_xy(k, j)))
    for u, h in srcs:
        mid = ((u[0] + h[0]) / 2, min(u[1], h[1]) - 60)
        cv.bezier(u, engine.lerp2(u, mid, .75), engine.lerp2(h, mid, .75), h,
                  TEAL, .05, 1.0)
    for u, _ in srcs:
        cv.rrect(u[0] - 2.4, u[1] - 2.4, 4.8, 4.8, 1, None, 1, fill=TEAL, fa=.7)
    for k, n_ in enumerate(cnt):
        for j in range(n_):
            x, y = cell_xy(k, j)
            cv.rrect(x - CELL / 2, y - CELL / 2, CELL, CELL, 1.2, None, 1,
                     fill=TEAL, fa=.85)
    # 18 at true scale is ~0.07 units: a corner dot, magnified in a lens
    dot = (S0[0] + 3, S0[1] + 3)
    cv.circle(dot, 4.5, INK, 1, fill=INK, fa=1, w=1)
    v = (L[0] - dot[0], L[1] - dot[1]); n = math.hypot(*v)
    cv.line(dot, (L[0] - v[0] / n * LR, L[1] - v[1] / n * LR), INK, .8, 1.4)
    cv.circle(L, LR, INK, 1, fill=PAPER, fa=1, w=1.6)
    count_block(cv, L[0] - 3 * 13 + 2.5, L[1] + 13 - 4, 18, 6, 13, 10.5,
                INK, fa=.9)
    cv.text(L[0], L[1] - 30, "2-BIT STATE", UI_M, 14, AMBER, 1,
            anchor="c", track=.14)
    cv.text(L[0], L[1] + 56, "18", UI_L, 34, INK, 1, anchor="c")

    x1 = HX0 + 9 * (BW + GAP) - GAP
    cv.line((HX0 - 10, BASE + 6), (x1 + 10, BASE + 6), GRAPHITE, 1, 1.4)
    for k in range(9):
        xc = HX0 + k * (BW + GAP) + BW / 2
        cv.text(xc, BASE + 36, str(cff[k]), UI, 21, GRAPHITE, 1, anchor="c")
        top = BASE - math.ceil(cnt[k] / PER) * P
        cv.text(xc, top - 10, str(cnt[k]), UI_M, 19, INK, 1, anchor="c")
    sub_text(cv, (HX0 + x1) / 2, BASE + 72, "C", "FF", UI_M, 21, GRAPHITE)
    cv.text(HX0, S0[1] - 20, "468", UI_L, 50, TEAL, 1)

    # ---------------- 20 sampled → circuits -----------------------------------
    BX, BY = x1 + 62, BASE - 150                     # 4 × 5 amber block
    count_block(cv, BX, BY, 20, 4, 14, 11, AMBER, fa=.95)
    cv.text(BX + 25, BY - 5 * 14 - 14, "20", UI_L, 38, AMBER, 1, anchor="c")
    arrow(cv, (x1 + 14, BY - 32), (BX - 14, BY - 32))

    # ---------------- C: energy vs. sequencing overhead + Pareto front -------
    CX0, CX1, CY1 = 1350, 1850, 250                  # plot box (BASE = y0)
    XM, YM = 80.0, 3.0
    X = lambda ps: CX0 + ps / XM * (CX1 - CX0)        # noqa: E731
    Y = lambda fj: BASE - fj / YM * (BASE - CY1)      # noqa: E731
    arrow(cv, (BX + 4 * 14 + 14, BY - 32), (CX0 - 26, BY - 32))
    cv.line((CX0, BASE), (CX1, BASE), GRAPHITE, 1, 1.4)
    cv.line((CX0, BASE), (CX0, CY1 - 10), GRAPHITE, 1, 1.4)
    for v in range(0, 81, 20):
        cv.line((X(v), BASE), (X(v), BASE + 7), GRAPHITE, 1, 1.2)
        cv.text(X(v), BASE + 36, str(v), UI, 21, GRAPHITE, 1, anchor="c")
    for v in (1, 2, 3):
        cv.line((CX0, Y(v)), (CX1, Y(v)), DIM, 1, 1, [2, 6])
        cv.text(CX0 - 14, Y(v) + 8, str(v), UI, 21, GRAPHITE, 1, anchor="r")
    cv.text((CX0 + CX1) / 2, BASE + 72, "sequencing overhead (ps)", UI_M, 21,
            GRAPHITE, 1, anchor="c")
    cv.text(CX0 - 14, CY1 - 26, "energy (fJ)", UI_M, 21, GRAPHITE, 1)
    pts = sorted((so, en) for (_, _, so, en) in F.T2)
    front, best = [], 1e9
    for so, en in pts:
        if en < best:
            front.append((so, en)); best = en
    Pf = [(X(a), Y(b)) for a, b in front]
    stair = [Pf[0]]
    for a, b in zip(Pf, Pf[1:]):
        stair += [(b[0], a[1]), b]
    for p, q in zip(stair, stair[1:]):
        cv.line(p, q, AMBER, .9, 2.2, [7, 6])
    for p in Pf:
        cv.circle(p, 14, AMBER, .9, w=1.6)
    # samples → their circuits (the five B-Flex points reported in Table 2)
    for nm, grp, so, en in F.T2:
        if grp != "bflex":
            continue
    for nm, grp, so, en in F.T2:
        p = (X(so), Y(en))
        if nm == "FF1":
            continue
        if grp == "prior":
            cv.circle(p, 7.5, GRAPHITE, 1, w=2)
        elif grp == "auto":
            cv.rrect(p[0] - 7, p[1] - 7, 14, 14, 1.5, GRAPHITE, 1, lw=2)
        elif grp == "tgff":
            cv.poly([(p[0], p[1] - 10), (p[0] + 9, p[1] + 7), (p[0] - 9, p[1] + 7)],
                    INK, 1, 2, close=True, fill=INK)
            cv.text(p[0] + 18, p[1] - 6, "TGFF", UI_M, 21, INK, 1)
        else:
            cv.poly([(p[0], p[1] - 9), (p[0] + 9, p[1]), (p[0], p[1] + 9),
                     (p[0] - 9, p[1])], TEAL, 1, 2, close=True, fill=TEAL)
    p = (X(19.1), Y(2.26))
    cv.poly([(p[0], p[1] - 12), (p[0] + 12, p[1]), (p[0], p[1] + 12),
             (p[0] - 12, p[1])], AMBER, 1, 2, close=True, fill=AMBER)
    cv.text(p[0], p[1] + 44, "FF1", UI_SB, 22, AMBER, 1, anchor="c")
    F.FIG_PARETO_FRONT = front


FIGS = {"1_motivation": motivation, "3_key_result": key_result}
