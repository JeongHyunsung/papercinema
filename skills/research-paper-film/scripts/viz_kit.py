"""Reusable CS/EE visual components, in the house style (white identity,
semantic palette, Inter), for both films and slide figures.

All coordinates are design units (1920x1080 space). Every component draws in
its *final state* by default; pass `p` (0..1 progress) where noted to animate.

    from engine import *
    from viz_kit import *
    T = TYPE                                   # type scale (units; 1 u ~ 0.5 pt at 12 in)
    ax = Axes(cv, (1200, 250, 600, 380), (0, 80), (0, 3),
              xticks=[0, 20, 40, 60, 80], yticks=[1, 2, 3],
              xlabel="latency (ms)", ylabel="energy (mJ)")
    scatter(cv, ax, [(19.1, 2.26, "ours"), (48.2, 1.53, "base")])
    pareto(cv, ax, [(x, y) for x, y, _ in pts])

Components
  text roles   label(cv, x, y, s, role, col, anchor), sub_label (X_sub)
  annotation   chip2d, callout (leader line + text), brace, vspan
  logic        waveform (digital signals with transitions), marker_row
  graphs       graph (nodes/edges, straight or arced, highlights)
  tables       table_panel (card, header, rows, per-row highlight, strike)
  charts       Axes, bars (grouped, value labels), lines, scatter (+ markers),
               pareto (staircase + rings), unit_histogram (1 cell = 1 item)
  scale        unit_block (huge count as a block) + lens (magnified tiny set)
  hardware     block (titled box with ports), wire (bus/arrow with label),
               grid_array (PE array / matrix / heatmap), pipeline (stage x cycle)
"""
import math
import cairo
from engine import (INK, GRAPHITE, DIM, TEAL, BLUE, CORAL, AMBER, PAPER, mix,
                    lerp2, clamp)

# ----------------------------------------------------------------- type -----
REG, LIGHT, MED, SEMI = "Inter Regular", "Inter Light", "Inter Medium", "Inter SemiBold"
TYPE = {   # role: (font, size). Every size >= 19 u so text stays >= 9 pt when a
           # ~1900-u-wide figure is placed 12 in wide (lint_figs.py checks this)
    "hero": (LIGHT, 56), "approx": (LIGHT, 34), "title": (SEMI, 30),
    "axis": (MED, 21), "tick": (REG, 21), "body": (REG, 22), "value": (MED, 19),
    "node": (MED, 22), "chip": (MED, 20), "eyebrow": (MED, 19), "note": (REG, 20),
}
SEMANTIC = {"valid": TEAL, "pruned": CORAL, "reference": BLUE, "headline": AMBER,
            "neutral": INK, "muted": GRAPHITE, "inactive": DIM}


def label(cv, x, y, s, role="body", col=INK, anchor="l", a=1.0):
    f, size = TYPE[role]
    track = .14 if role == "eyebrow" else 0.0
    if role == "eyebrow":
        s = s.upper()
    return cv.text(x, y, s, f, size, col, a, anchor=anchor, track=track)


def sub_label(cv, xc, y, base, sub, role="axis", col=GRAPHITE, a=1.0):
    """Centered base with subscript, e.g. C_FF, V_DD, T_setup."""
    f, size = TYPE[role]
    ss = max(size * .7, 19)                       # subscripts stay >= 9 pt
    w1, w2 = cv.measure(base, f, size), cv.measure(sub, f, ss)
    x = xc - (w1 + w2) / 2
    cv.text(x, y, base, f, size, col, a)
    cv.text(x + w1 + 1, y + size * .22, sub, f, ss, col, a)


# ------------------------------------------------------------ annotation ----
def chip2d(cv, x, y, s, col=TEAL, a=1.0, role="chip", anchor="l"):
    """Rounded label chip; reads over busy geometry. (x, y) = left/centre-mid."""
    f, size = TYPE[role]
    w, h = cv.measure(s, f, size) + 20, size + 14
    x0 = x - w / 2 if anchor == "c" else x
    cv.rrect(x0, y - h / 2, w, h, 7, col, a, fill=PAPER, fa=.95, lw=1.4)
    cv.text(x0 + 10, y + size * .36, s, f, size, col, a)
    return w


def callout(cv, p, q, s, col=INK, role="note", a=1.0):
    """Leader line from point p to text anchored at q (left/right by side)."""
    cv.line(p, q, col, a * .8, 1.3)
    cv.circle(p, 3.5, None, a, fill=col)
    right = q[0] >= p[0]
    label(cv, q[0] + (8 if right else -8), q[1] + 7, s, role, col,
          "l" if right else "r", a)


def brace(cv, x0, x1, y, s, col=GRAPHITE, a=1.0, up=False):
    """Horizontal bracket with a centred label (e.g. a speed-up span)."""
    d = -1 if up else 1
    cv.poly([(x0, y - 8 * d), (x0, y), (x1, y), (x1, y - 8 * d)], col, a, 1.6)
    label(cv, (x0 + x1) / 2, y + (30 if not up else -14), s, "value", col, "c", a)


def vspan(cv, x, y0, y1, s, col=AMBER, a=1.0, side="r"):
    """Vertical bracket between two values at one x (e.g. a gap between two
    curves) with its label beside it."""
    d = 8 if side == "r" else -8
    cv.poly([(x - d, y0), (x, y0), (x, y1), (x - d, y1)], col, a, 1.8)
    label(cv, x + (12 if side == "r" else -12), (y0 + y1) / 2 + 7, s, "value", col,
          "l" if side == "r" else "r", a)


# ------------------------------------------------------------------ logic ---
def waveform(cv, x0, x1, y, name, start, switches, amp=32, col=INK,
             col_after=None, after_x=None, w=3.2, a=1.0):
    """Digital signal. switches = [(x, new_level), ...] in x order.
    Segments right of after_x are drawn in col_after (e.g. a wrong output)."""
    label(cv, x0 - 36, y + 11, name, "title", INK, "r", a)
    Y = lambda lv: y + (amp if lv == 0 else -amp)            # noqa: E731
    lvl, x = start, x0
    segs = []
    for xs, nl in switches:
        segs += [((x, Y(lvl)), (xs, Y(lvl))), ((xs, Y(lvl)), (xs, Y(nl)))]
        lvl, x = nl, xs
    segs.append(((x, Y(lvl)), (x1, Y(lvl))))
    for p, q in segs:
        c = col_after if (col_after and after_x is not None
                          and min(p[0], q[0]) >= after_x - .1) else col
        cv.line(p, q, c, a, w, cap=cairo.LINE_CAP_SQUARE)
    return Y


def marker_row(cv, xs, y, verdicts, a=1.0):
    """Numbered markers with pass (True) / fail (False) / None glyphs."""
    for k, (x, v) in enumerate(zip(xs, verdicts)):
        bad = v is False
        cv.circle((x, y), 18, None, a, fill=CORAL if bad else DIM, fa=1)
        cv.text(x, y + 7.5, str(k + 1), MED, 20, PAPER if bad else INK, a, anchor="c")
        if v is True:
            _check(cv, (x + 38, y + 1), 9, TEAL, a)
        elif v is False:
            _xmark(cv, (x + 38, y), 9, CORAL, a)


def _xmark(cv, p, r, col, a, w=3):
    cv.line((p[0] - r, p[1] - r), (p[0] + r, p[1] + r), col, a, w)
    cv.line((p[0] - r, p[1] + r), (p[0] + r, p[1] - r), col, a, w)


def _check(cv, p, r, col, a, w=3):
    cv.poly([(p[0] - r, p[1]), (p[0] - r * .3, p[1] + r * .7),
             (p[0] + r, p[1] - r * .8)], col, a, w)


# ----------------------------------------------------------------- graphs ---
def graph(cv, nodes, edges, r=34, a=1.0, node_col=None, edge_col=None):
    """nodes: {id: (x, y, label)}; edges: [(u, v, opts)] with opts keys:
    col, w, dash, bend (px, + = left of travel), arrow (bool), label.
    node_col: {id: colour} for highlights (ring + label)."""
    node_col = node_col or {}
    for u, v, o in edges:
        (x0, y0, _), (x1, y1, _) = nodes[u], nodes[v]
        col, w = o.get("col", edge_col or GRAPHITE), o.get("w", 2.0)
        bend = o.get("bend", 0.0)
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        c = ((x0 + x1) / 2 + nx * bend, (y0 + y1) / 2 + ny * bend)
        pts = []
        for k in range(41):
            t = k / 40
            px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * c[0] + t * t * x1
            py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * c[1] + t * t * y1
            if math.dist((px, py), (x0, y0)) > r + 2 and math.dist((px, py), (x1, y1)) > r + 4:
                pts.append((px, py))
        if len(pts) < 2:
            continue
        if o.get("dash"):
            for k in range(0, len(pts) - 1, 2):
                cv.line(pts[k], pts[k + 1], col, a, w)
        else:
            cv.poly(pts, col, a, w)
        if o.get("arrow", True):
            cv.arrowhead(pts[-1], pts[-3], col, a, 12)
        if o.get("label"):
            m = pts[len(pts) // 2]
            chip2d(cv, m[0], m[1] - 18, o["label"], col, a, anchor="c")
    for k, (x, y, s) in nodes.items():
        col = node_col.get(k, INK)
        cv.circle((x, y), r, col, a, fill=PAPER, fa=1, w=2.2 if k in node_col else 2)
        label(cv, x, y + 8, s, "node", col, "c", a)


# ----------------------------------------------------------------- tables ---
def table_panel(cv, x, y, header, rows, col_x, row_h=34, highlight=None,
                strike=None, note=None, a=1.0, width=None):
    """A floating 'document': card + header + rows.
    col_x: column centre offsets from x. highlight: {row: colour}.
    strike: {row: column} draws an x over that cell. note: (row, text, colour)
    printed under the row. Returns the y of each row baseline."""
    highlight, strike = highlight or {}, strike or {}
    W = width or (col_x[-1] + 60)
    H = 56 + row_h * len(rows) + (34 if note else 18)
    cv.shadow(x - 24, y - 20, W + 24, H, 14, a)
    cv.rrect(x - 24, y - 20, W + 24, H, 14, DIM, a, fill=PAPER, fa=.98, lw=1.2)
    for cx, h in zip(col_x, header):
        label(cv, x + cx, y + 10, h, "note", GRAPHITE, "c", a)
    cv.line((x - 10, y + 22), (x + W - 20, y + 22), DIM, a, 1)
    ys = []
    for i, row in enumerate(rows):
        yy = y + 56 + i * row_h
        ys.append(yy)
        if i in highlight:
            cv.rrect(x - 14, yy - row_h * .68, W - 8, row_h * .86, 5, None, a,
                     fill=mix(PAPER, highlight[i], .16), fa=1)
        for j, (cx, v) in enumerate(zip(col_x, row)):
            col = highlight.get(i, INK) if j >= len(row) - 2 and i in highlight else INK
            label(cv, x + cx, yy, str(v), "body", col, "c", a * (1 if i in highlight else .8))
        if i in strike:
            _xmark(cv, (x + col_x[strike[i]], yy - 7), 12, CORAL, a, 2.4)
    if note:
        r, s, c = note
        label(cv, x + W / 2 - 12, ys[r] + 30, s, "note", c, "c", a)
    return ys


# ----------------------------------------------------------------- charts ---
class Axes:
    """Plot box (x, y, w, h) with data ranges; draws axes, ticks, grid.
    Use ax.X(v), ax.Y(v), ax.P((vx, vy)). log=('x' and/or 'y')."""

    def __init__(self, cv, box, xr, yr, xticks=(), yticks=(), xlabel="", ylabel="",
                 log="", grid=True, xfmt=str, yfmt=str, a=1.0, draw=True):
        self.box, self.xr, self.yr, self.log = box, xr, yr, log
        x, y, w, h = box
        if not draw:
            return
        cv.line((x, y + h), (x + w, y + h), GRAPHITE, a, 1.4)
        cv.line((x, y + h), (x, y - 10), GRAPHITE, a, 1.4)
        for v in xticks:
            px = self.X(v)
            cv.line((px, y + h), (px, y + h + 7), GRAPHITE, a, 1.2)
            label(cv, px, y + h + 36, xfmt(v), "tick", GRAPHITE, "c", a)
        for v in yticks:
            py = self.Y(v)
            if grid:
                cv.line((x, py), (x + w, py), DIM, a, 1, [2, 6])
            label(cv, x - 14, py + 8, yfmt(v), "tick", GRAPHITE, "r", a)
        if xlabel:
            label(cv, x + w / 2, y + h + 72, xlabel, "axis", GRAPHITE, "c", a)
        if ylabel:
            label(cv, x - 14, y - 28, ylabel, "axis", GRAPHITE, "l", a)

    def _n(self, v, r, lg):
        if lg:
            return (math.log10(v) - math.log10(r[0])) / (math.log10(r[1]) - math.log10(r[0]))
        return (v - r[0]) / (r[1] - r[0])

    def X(self, v):
        return self.box[0] + self._n(v, self.xr, "x" in self.log) * self.box[2]

    def Y(self, v):
        return self.box[1] + self.box[3] - self._n(v, self.yr, "y" in self.log) * self.box[3]

    def P(self, p):
        return (self.X(p[0]), self.Y(p[1]))


def bars(cv, ax, cats, series, colors=None, value_fmt="{:g}", gap=.28, a=1.0,
         cat_role="tick", p=1.0):
    """Grouped bars. series: {name: [v per category]}; colors: {name: col}.
    p animates growth (0..1)."""
    names = list(series)
    colors = colors or {n: c for n, c in zip(names, [GRAPHITE, TEAL, AMBER, BLUE, CORAL])}
    n, x, y, w, h = len(cats), *ax.box
    slot = w / n
    bw = slot * (1 - gap) / len(names)
    base = ax.Y(ax.yr[0])
    for i, c in enumerate(cats):
        x0 = x + i * slot + slot * gap / 2
        for j, nm in enumerate(names):
            v = series[nm][i]
            top = base + (ax.Y(v) - base) * clamp(p)
            cv.rrect(x0 + j * bw, top, bw * .92, base - top, 2, None, a,
                     fill=colors[nm], fa=.95)
            if p >= 1:
                label(cv, x0 + j * bw + bw * .46, top - 10, value_fmt.format(v), "value",
                      colors[nm] if colors[nm] != GRAPHITE else INK, "c", a)
        label(cv, x + i * slot + slot / 2, base + 36, c, cat_role, GRAPHITE, "c", a)


def lines(cv, ax, series, colors=None, w=2.6, dots=True, end_labels=True, a=1.0):
    """series: {name: [(x, y), ...]}. Direct end labels instead of a legend."""
    colors = colors or {}
    pal = [TEAL, GRAPHITE, AMBER, BLUE, CORAL]
    for k, (nm, pts) in enumerate(series.items()):
        col = colors.get(nm, pal[k % len(pal)])
        P = [ax.P(q) for q in pts]
        cv.poly(P, col, a, w)
        if dots:
            for q in P:
                cv.circle(q, 4.5, None, a, fill=col)
        if end_labels:
            label(cv, P[-1][0] + 12, P[-1][1] + 7, nm, "value", col, "l", a)


MARKERS = {"ours": ("diamond", TEAL), "headline": ("diamond", AMBER),
           "baseline": ("triangle", INK), "prior": ("circle", GRAPHITE),
           "auto": ("square", GRAPHITE)}


def marker(cv, p, kind, col, size=9, a=1.0):
    x, y = p
    if kind == "diamond":
        cv.poly([(x, y - size), (x + size, y), (x, y + size), (x - size, y)], col, a, 2,
                close=True, fill=col)
    elif kind == "triangle":
        cv.poly([(x, y - size * 1.1), (x + size, y + size * .8), (x - size, y + size * .8)],
                col, a, 2, close=True, fill=col)
    elif kind == "square":
        cv.rrect(x - size * .8, y - size * .8, size * 1.6, size * 1.6, 1.5, col, a, lw=2)
    else:
        cv.circle(p, size * .85, col, a, w=2)


def scatter(cv, ax, pts, a=1.0):
    """pts: [(x, y, group[, label])]; groups from MARKERS (or (kind, col))."""
    for q in pts:
        g = MARKERS.get(q[2], q[2]) if isinstance(q[2], str) else q[2]
        kind, col = g
        sz = 12 if q[2] == "headline" else 9
        marker(cv, ax.P(q[:2]), kind, col, sz, a)
        if len(q) > 3 and q[3]:
            px, py = ax.P(q[:2])
            label(cv, px + 18, py - 8, q[3], "value", col, "l", a)


def pareto_front(pts, minimize=(True, True)):
    sx = 1 if minimize[0] else -1
    sy = 1 if minimize[1] else -1
    front, best = [], math.inf
    for x, y in sorted(pts, key=lambda q: (sx * q[0], sy * q[1])):
        if sy * y < best:
            front.append((x, y)); best = sy * y
    return front


def pareto(cv, ax, pts, minimize=(True, True), col=AMBER, a=.9, rings=True):
    """Dashed staircase of the non-dominated set + rings. Returns the front."""
    F = pareto_front(pts, minimize)
    P = [ax.P(q) for q in F]
    stair = [P[0]]
    for p, q in zip(P, P[1:]):
        stair += [(q[0], p[1]), q]
    for p, q in zip(stair, stair[1:]):
        cv.line(p, q, col, a, 2.2, [7, 6])
    if rings:
        for p in P:
            cv.circle(p, 14, col, a, w=1.6)
    return F


def unit_histogram(cv, x0, base, counts, cats, per_row=6, pitch=8.6, cell=7.0,
                   gap=10, col=TEAL, a=1.0, count_labels=True, axis_sub=None):
    """1 cell = 1 item, stacked per category. Returns cell_xy(k, j)."""
    bw = per_row * pitch

    def cell_xy(k, j):
        return (x0 + k * (bw + gap) + (j % per_row) * pitch + cell / 2,
                base - (j // per_row) * pitch - cell / 2)
    for k, n in enumerate(counts):
        for j in range(n):
            cx, cy = cell_xy(k, j)
            cv.rrect(cx - cell / 2, cy - cell / 2, cell, cell, 1.2, None, a, fill=col, fa=.85)
        xc = x0 + k * (bw + gap) + bw / 2
        label(cv, xc, base + 36, str(cats[k]), "tick", GRAPHITE, "c", a)
        if count_labels:
            label(cv, xc, base - math.ceil(n / per_row) * pitch - 10, str(n), "value", INK, "c", a)
    x1 = x0 + len(counts) * (bw + gap) - gap
    cv.line((x0 - 10, base + 6), (x1 + 10, base + 6), GRAPHITE, a, 1.4)
    if axis_sub:
        sub_label(cv, (x0 + x1) / 2, base + 72, *axis_sub)
    return cell_xy


# ------------------------------------------------------------------ scale ---
def unit_block(cv, x, y, size, c0=(0.827, 0.910, 0.918), c1=(0.663, 0.824, 0.839)):
    """A huge count as one block (light gradient; never 'to scale' by cells)."""
    g = cairo.LinearGradient(x, y, x + size, y + size)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(.75, *c0)
    g.add_color_stop_rgb(1, *c1)
    cv.c.rectangle(x, y, size, size)
    cv.c.set_source(g)
    cv.c.fill()


def lens(cv, dot, center, r, inner=None, a=1.0):
    """Magnifier: a dot at true scale, a leader, a white lens with content
    drawn by inner(cv, center, r). Draw it AFTER anything that crosses it."""
    cv.circle(dot, 4.5, INK, a, fill=INK, fa=1, w=1)
    v = (center[0] - dot[0], center[1] - dot[1])
    n = math.hypot(*v) or 1
    cv.line(dot, (center[0] - v[0] / n * r, center[1] - v[1] / n * r), INK, a * .8, 1.4)
    cv.circle(center, r, INK, a, fill=PAPER, fa=1, w=1.6)
    if inner:
        inner(cv, center, r)


def count_block(cv, x, y, n, per_row, pitch, cell, col, fa=.95):
    """n cells in rows of per_row; (x, y) = bottom-left."""
    for j in range(n):
        cx, cy = x + (j % per_row) * pitch, y - (j // per_row) * pitch
        cv.rrect(cx, cy - cell, cell, cell, 1.6, None, 1, fill=col, fa=fa)


# --------------------------------------------------------------- hardware ---
def block(cv, x, y, w, h, title, col=INK, fill=PAPER, sub=None, a=1.0, ports=()):
    """Titled box (module, PE, cache, accelerator unit). ports: [(side, frac, name)]
    side in 'lrtb'. Returns {name: (px, py)} port coordinates."""
    cv.rrect(x, y, w, h, 10, col, a, fill=fill, fa=1, lw=2)
    label(cv, x + w / 2, y + h / 2 + (0 if sub else 8), title, "node", col, "c", a)
    if sub:
        label(cv, x + w / 2, y + h / 2 + 30, sub, "note", GRAPHITE, "c", a)
    out = {}
    for side, f, nm in ports:
        p = {"l": (x, y + h * f), "r": (x + w, y + h * f),
             "t": (x + w * f, y), "b": (x + w * f, y + h)}[side]
        cv.circle(p, 4, None, a, fill=col)
        out[nm] = p
    return out


def wire(cv, pts, col=GRAPHITE, w=2.2, arrow=True, text=None, bus=False, a=1.0, p=1.0):
    """Orthogonal or free polyline connection; bus=True draws a slash mark.
    p (0..1) animates the reveal along the path."""
    L = [math.dist(u, v) for u, v in zip(pts, pts[1:])]
    tot, acc, out = sum(L) * clamp(p), 0.0, [pts[0]]
    for (u, v), l in zip(zip(pts, pts[1:]), L):
        if acc + l >= tot:
            out.append(lerp2(u, v, (tot - acc) / l if l else 1)); break
        out.append(v); acc += l
    cv.poly(out, col, a, w)
    if arrow and p >= .999:
        cv.arrowhead(out[-1], out[-2], col, a, 12)
    if bus and len(pts) > 1:
        m = lerp2(pts[0], pts[1], .5)
        cv.line((m[0] - 6, m[1] + 8), (m[0] + 6, m[1] - 8), col, a, 1.6)
    if text:
        m = lerp2(pts[0], pts[1], .5)
        label(cv, m[0], m[1] - 12, text, "note", col, "c", a)


def grid_array(cv, x, y, rows, cols, cell, value=None, col=TEAL, gap=4, a=1.0,
               text=None):
    """PE array / matrix / heatmap. value(i, j) -> 0..1 intensity (None = empty
    outline). text(i, j) -> optional cell label."""
    for i in range(rows):
        for j in range(cols):
            cx, cy = x + j * (cell + gap), y + i * (cell + gap)
            v = value(i, j) if value else 1.0
            if v is None:
                cv.rrect(cx, cy, cell, cell, 3, DIM, a, lw=1.2)
            else:
                cv.rrect(cx, cy, cell, cell, 3, None, a, fill=mix(PAPER, col, .15 + .85 * v), fa=1)
            if text:
                s = text(i, j)
                if s:
                    label(cv, cx + cell / 2, cy + cell / 2 + 7, s, "note", INK, "c", a)


def pipeline(cv, x, y, stages, schedule, cw=56, rh=40, a=1.0, colors=None):
    """Stage x cycle diagram. schedule: [(item, stage_index, cycle, kind)] with
    kind in {'busy','stall','flush'} -> teal / amber / coral."""
    colors = colors or {"busy": TEAL, "stall": AMBER, "flush": CORAL}
    ncyc = max(c for _, _, c, _ in schedule) + 1
    for s, nm in enumerate(stages):
        label(cv, x - 14, y + s * rh + rh / 2 + 7, nm, "note", GRAPHITE, "r", a)
    for c in range(ncyc):
        label(cv, x + c * cw + cw / 2, y - 12, str(c), "note", GRAPHITE, "c", a)
    for s in range(len(stages)):
        for c in range(ncyc):
            cv.rrect(x + c * cw + 2, y + s * rh + 2, cw - 4, rh - 4, 4, DIM, a, lw=1)
    for item, s, c, kind in schedule:
        cv.rrect(x + c * cw + 2, y + s * rh + 2, cw - 4, rh - 4, 4, None, a,
                 fill=mix(PAPER, colors[kind], .75), fa=1)
        label(cv, x + c * cw + cw / 2, y + s * rh + rh / 2 + 7, str(item), "note", PAPER
              if kind == "busy" else INK, "c", a)
