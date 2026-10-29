"""Data-level grounding: show WHAT a buffer, cache, queue or PE holds, element by element
(references/16). A box labelled "copy" says nothing about reuse, duplication or capacity;
a grid of W[k, n] cells, identical in both branches, says it at a glance.

    from data_kit import loop_nest_tile, tile_ranges, elem_grid, tensor3d, same_link, load_meter

Compute contents (never type them)
  loop_nest_tile(index_fn, mapping, j, outer)   the set of operand coordinates a storage
        placed at loop level j (wrapping loops j..L, 1-based) holds, for the given values of
        the loops above it (outer = {loop position: iteration}); spatial loops above it are
        the branch index. index_fn: list of affine index expressions, each a tuple of dims.
  tile_ranges(cells)                            per-axis "lo–hi" ranges for labels ("K0–7")

Draw contents
  elem_grid(cv, x, y, rows, cols, cell, col, a, on=, hl=, row_lab=, col_lab=)
        a 2-D operand tile, one cell per element; on(r, c) -> 0..1 presence (ghost when 0),
        hl(r, c) -> 0..1 highlight ring; returns centre(r, c)
  tensor3d(cv, x, y, depth, rows, cols, cell, col, a, step=(14, -12), on=)
        a 3-D tensor as stacked slabs (back to front); on(d, r, c)
  same_link(cv, A, B, pairs, prog, col, a)      thin connectors between corresponding cells
        of two grids (A, B are centre functions): "these elements are the same"
  load_meter(cv, x, y, n, total, col, a, label) an exact counter bar for loads / capacity

Rules (gate R5 in argument_audit.py): every mechanism beat about storage or data movement
shows contents with elem_grid / tensor3d, computed with loop_nest_tile and asserted against
the capacity numbers on screen.
"""
import itertools, math
from engine import INK, GRAPHITE, DIM, PAPER, AMBER, clamp, mix
import engine as _engine

_MC = None


def text_w(s, font, size):
    """Exact advance width of s (same cairo metrics the renderer uses), for layout before drawing."""
    global _MC
    if _MC is None:
        _MC = _engine.Canvas(64, 36)
    return _MC.measure(s, font, size)


def eff(size):
    """Rendered size of text drawn at `size` (slide-figure exports may boost small text)."""
    return text_w("0", MONO, size) / .6


def ortho_wire(cv, pts, col, a=1.0, w=2.6, prog=1.0, head=True, taps=None, tap_len=12):
    """A data path as an axis-aligned polyline that flows one way from its source (a read-port tip)
    to its consumers. Asserts every segment is horizontal or vertical and that no segment doubles
    back (a hook reads as a wrong direction). taps: points on the last segment, each gets a short
    downward branch with an arrowhead into a consumer (a bus with one tap per destination)."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        assert abs(x0 - x1) < 1e-6 or abs(y0 - y1) < 1e-6, "wire segments must be axis-aligned"
    for (u, v_), (v2, w2) in zip(zip(pts, pts[1:]), zip(pts[1:], pts[2:])):
        d1 = (v_[0] - u[0], v_[1] - u[1]); d2 = (w2[0] - v2[0], w2[1] - v2[1])
        assert d1[0] * d2[0] + d1[1] * d2[1] >= 0, "wire doubles back"
    if a <= .002 or prog <= 0:
        return
    L = [math.dist(u, v_) for u, v_ in zip(pts, pts[1:])]
    tot, acc, drawn = sum(L), 0.0, [pts[0]]
    for (u, v_), l_ in zip(zip(pts, pts[1:]), L):
        if acc + l_ >= tot * min(prog, 1):
            r = (tot * min(prog, 1) - acc) / max(l_, 1e-6)
            drawn.append((u[0] + (v_[0] - u[0]) * r, u[1] + (v_[1] - u[1]) * r))
            break
        drawn.append(v_); acc += l_
    for u, v_ in zip(drawn, drawn[1:]):
        cv.line(u, v_, col, a, w)
    if prog >= 1:
        if head and not taps:
            cv.arrowhead(pts[-1], pts[-2], col, a, 9 + w)
        for tp in taps or []:
            q = (tp[0], tp[1] + tap_len)
            cv.line(tp, q, col, a, w)
            cv.circle(tp, w + 1.6, None, a, fill=col)
            cv.arrowhead(q, tp, col, a, 8 + w)


def row_labels(cv, x, y0, labs, cell, size, a, col=GRAPHITE):
    """Row labels right-aligned at x, centred on their rows; every k-th when rows are shorter than
    the text (cells shrunk to fit a container) -- never overlapping."""
    if not labs:
        return
    k = max(1, math.ceil((eff(size) * .8 + 2) / cell))
    for r, s_ in enumerate(labs):
        if s_ and r % k == 0:
            cv.text(x, y0 + (r + .5) * cell + eff(size) * .36, s_, MONO, size, col, a, anchor="r")


def col_labels(cv, x0, y, labs, cell, size, a, col=GRAPHITE):
    """Column labels centred on their cells; when a label is wider than its cell, only every
    k-th label is drawn (k chosen so labels never touch) -- never overlapping glyphs."""
    if not labs:
        return
    wmax = max(text_w(s_ or "", MONO, size) for s_ in labs)
    k = max(1, math.ceil((wmax + 2) / cell))
    for c, s_ in enumerate(labs):
        if s_ and c % k == 0:
            cv.text(x0 + (c + .5) * cell, y, s_, MONO, size, col, a, anchor="c")

MONO = "JetBrains Mono"


# ------------------------------------------------------------ contents -------
def _strides(mapping):
    """For each loop position, the stride of its iteration in its dimension's index
    (product of the factors of the same dimension's loops nested inside it)."""
    st = []
    for i, (d, f, _) in enumerate(mapping):
        st.append(math.prod(ff for dd, ff, _ in mapping[i + 1:] if dd == d))
    return st


def loop_nest_tile(index_fn, mapping, j, outer=None):
    """Operand coordinates held by a storage wrapping loops j..L (1-based), for fixed
    iteration values of the loops above (outer: {position(1-based): value}, default 0)."""
    outer = outer or {}
    st = _strides(mapping)
    dims = sorted({d for d, _, _ in mapping})
    base = {d: 0 for d in dims}
    for i, (d, f, _) in enumerate(mapping[:j - 1]):
        base[d] += outer.get(i + 1, 0) * st[i]
    inner = list(range(j - 1, len(mapping)))
    cells = set()
    for it in itertools.product(*[range(mapping[i][1]) for i in inner]):
        idx = dict(base)
        for i, v in zip(inner, it):
            idx[mapping[i][0]] += v * st[i]
        cells.add(tuple(sum(idx.get(d, 0) for d in expr) for expr in index_fn))
    return cells


def tile_ranges(cells):
    if not cells:
        return []
    n = len(next(iter(cells)))
    out = []
    for k in range(n):
        v = sorted({c[k] for c in cells})
        out.append(f"{v[0]}–{v[-1]}" if len(v) > 1 else f"{v[0]}")
    return out


# ------------------------------------------------------------ drawing --------
def elem_grid(cv, x, y, rows, cols, cell, col, a=1.0, on=None, hl=None, hl_col=AMBER,
              row_lab=None, col_lab=None, lab_size=13, gap=2, fill_a=.78, ghost=True):
    """One cell per element. on(r, c) -> presence 0..1 (0 = ghost outline if ghost=True)."""
    if a <= .002:
        return lambda r, c: (x + (c + .5) * cell, y + (r + .5) * cell)
    for r in range(rows):
        for c in range(cols):
            p = 1.0 if on is None else clamp(on(r, c))
            cx, cy = x + c * cell + gap / 2, y + r * cell + gap / 2
            s = cell - gap
            if p < 1 and ghost:
                cv.rrect(cx, cy, s, s, 2.5, col, a * .35 * (1 - p), lw=.9, dash=[2, 2])
            if p > 0:
                cv.rrect(cx, cy, s, s, 2.5, None, a * p, fill=col, fa=fill_a)
            if hl is not None:
                h = clamp(hl(r, c))
                if h > .01:
                    cv.rrect(cx - 1.5, cy - 1.5, s + 3, s + 3, 3.5, hl_col, a * h, lw=2.0)
    if row_lab:
        row_labels(cv, x - 6, y, row_lab, cell, lab_size, a)
    if col_lab:
        col_labels(cv, x, y - 6, col_lab, cell, lab_size, a)
    return lambda r, c: (x + (c + .5) * cell, y + (r + .5) * cell)


def tensor3d(cv, x, y, depth, rows, cols, cell, col, a=1.0, step=(14, -12), on=None, fill_a=.7):
    """A 3-D tensor drawn as `depth` stacked slabs, back slab first."""
    for d in reversed(range(depth)):
        ox, oy = x + d * step[0], y + d * step[1]
        cv.rrect(ox - 3, oy - 3, cols * cell + 6, rows * cell + 6, 4, GRAPHITE, a * .5, fill=PAPER, fa=1, lw=1)
        elem_grid(cv, ox, oy, rows, cols, cell, col, a,
                  on=(lambda r, c, d=d: on(d, r, c)) if on else None, fill_a=fill_a)


def same_link(cv, A, B, pairs, prog, col=INK, a=1.0, w=1.0):
    """Connect corresponding cells (pairs: [((r, c), (r2, c2))]) of two grids."""
    if a <= .002 or prog <= 0:
        return
    n = len(pairs)
    for k, (p, q) in enumerate(pairs):
        f = clamp(prog * n - k)
        if f <= 0:
            break
        P, Q = A(*p), B(*q)
        cv.line(P, (P[0] + (Q[0] - P[0]) * f, P[1] + (Q[1] - P[1]) * f), col, a * .5, w)


def load_meter(cv, x, y, n, total, col, a=1.0, label="", w=260, h=14, size=15):
    """Exact counter bar: n of total (e.g. elements loaded, capacity used)."""
    if a <= .002:
        return
    cv.rrect(x, y, w, h, h / 2, DIM, a, fill=PAPER, fa=1, lw=1)
    if n > 0:
        cv.rrect(x, y, max(h, w * clamp(n / max(total, 1))), h, h / 2, None, a, fill=col, fa=.85)
    cv.text(x + w + 10, y + h - 2, f"{label}{n}", MONO, size, INK, a)


# ================================================== canonical storage glyph =====
# One concept that recurs across a film (here: a storage / buffer / scratchpad) gets ONE
# detailed glyph, defined once and reused in every scene and figure (references/16 §1b).
# Anatomy (every part is data, nothing is decoration):
#   header      name · level tag · occupancy "used / capacity"
#   write port  a tab on one edge (default top) with an inbound arrow; active while data is written;
#               exact write counter ("wr 24")
#   body        one cell per element, banked into column groups; per-cell state:
#               'empty' (dashed) · 'valid' (light fill) · 'live' (solid) · 'idle' (held but not needed:
#               hatched, coral outline when called out) · 'new' (just written: amber ring)
#   read port   a tab on the opposite edge (default bottom) with an outbound arrow; exact read counter
#   occupancy   a thin vertical bar on the right edge: used / capacity
#   pruned      the whole glyph turns coral, drops and fades (a candidate removed)
STATE_FA = {"empty": 0.0, "valid": .38, "live": .85, "idle": .3, "new": .85}


class Storage:
    def __init__(self, name, rows, cols, cell, col, level=None, row_lab=None, col_lab=None,
                 bank=None, wr="top", rd="bottom", pad=14, head=50, lab_size=12, min_w=214,
                 port_lab=None, cap_hint=None, arrow=40, drop=26):
        """arrow: port arrow length; drop: how far a pruned glyph falls.
        port_lab: {"wr"|"rd": "side" | "left" | "under" | (dx, dy, anchor)} where each port's counter goes
        ("side": right of the tab, the default; "left": left of a top/bottom tab; "under": below the glyph, right-aligned to the port
        edge -- use it when the port's outbound side is crowded). cap_hint: widest expected
        "used / cap" (sizes the header so the occupancy tag never overflows)."""
        self.name, self.rows, self.cols, self.cell, self.col = name, rows, cols, cell, col
        self.cell0 = cell
        self.level, self.row_lab, self.col_lab, self.bank = level, row_lab, col_lab, bank
        self.wr, self.rd, self.pad, self.head0, self._lab = wr, rd, pad, head, lab_size
        self.min_w, self.port_lab = min_w, dict(port_lab or {})
        self.arrow, self.drop = arrow, drop                # port arrow length; pruned drop distance
        self.cap_hint = cap_hint or rows * cols
        self._tag = 12
        self._layout()

    @property
    def tag_size(self):
        return self._tag

    @tag_size.setter
    def tag_size(self, v):                             # raise for slide figures (>= 9 pt); relayouts
        self._tag = v
        self._layout()

    @property
    def lab(self):
        return self._lab

    @lab.setter
    def lab(self, v):                                  # element index label size; relayouts
        self._lab = v
        if hasattr(self, "_tag"):
            self._layout()

    def _layout(self):
        """Width/height from the grid AND the header text (exact cairo metrics), so the
        header never overflows; the level tag shares the name line when it fits, else gets a line."""
        lab_w = max([text_w(s_, MONO, self.lab) for s_ in (self.row_lab or [])] or [0])
        self.lm = max(30, lab_w + 12) if self.row_lab else 0      # room for row labels
        self.tm = eff(self.lab) + 4 if self.col_lab else 0
        occ = f"{self.cap_hint} / {self.cap_hint} elements"
        name_w = text_w(self.name, "Inter Medium", 15)
        lev_w = text_w(self.level or "", MONO, self._tag)
        self.w = max(self.min_w, self.lm + self.cols * self.cell + 2 * self.pad + 12,
                     text_w(occ, MONO, self._tag) + 22, name_w + 22)
        self.lev_inline = not self.level or (name_w + lev_w + 34 <= self.w)
        ns, ts = eff(15), eff(self._tag)
        self.y_name = 6 + .95 * ns                               # baselines inside the header
        self.y_occ = self.y_name + ts + 6
        self.y_lev = self.y_occ + ts + 5
        last = self.y_occ if self.lev_inline else self.y_lev
        self.head = max(self.head0, last + 10)
        self.gx_off = (self.w - (self.lm + self.cols * self.cell + 12)) / 2 + self.lm   # centre the grid
        self.h = self.head + self.tm + self.rows * self.cell + 2 * self.pad

    def fit(self, max_h):
        """Largest integer cell (<= the designed one) so the whole glyph, header included, fits in
        max_h -- use when a container (a branch box) bounds it and header text may grow."""
        self.cell = self.cell0
        self._layout()
        while self.h > max_h and self.cell > 8:
            self.cell -= 1
            self._layout()
        return self

    def size(self):
        return self.w, self.h

    def cell_xy(self, x, y, r, c):
        """Centre of element (r, c) when the glyph's top-left is at (x, y)."""
        return (x + self.gx_off + (c + .5) * self.cell,
                y + self.head + self.tm + self.pad + (r + .5) * self.cell)

    def port(self, x, y, which):
        side = self.wr if which == "wr" else self.rd
        return {"top": (x + self.w / 2, y - 16), "bottom": (x + self.w / 2, y + self.h + 16),
                "left": (x - 16, y + self.h / 2), "right": (x + self.w + 16, y + self.h / 2)}[side]

    def port_tip(self, x, y, which):
        """Outer end of a port's arrow: where an external wire must attach (never the tab itself)."""
        px, py = self.port(x, y, which)
        side = self.wr if which == "wr" else self.rd
        d = {"top": (0, -1), "bottom": (0, 1), "left": (-1, 0), "right": (1, 0)}[side]
        return (px + d[0] * self.arrow, py + d[1] * self.arrow)

    def draw(self, cv, x, y, a=1.0, state=None, used=None, cap=None, wr_n=None, rd_n=None,
             wr_on=0.0, rd_on=0.0, pruned=0.0, callout_idle=0.0, t=0.0, hl=None, fill=None):
        """fill(r, c) -> 0..1: partial progress of an element (e.g. k accumulated / K for a partial
        sum); drawn as a bottom-up fill inside the cell, exact per element."""
        if a <= .002:
            return
        col = mix(self.col, (0.784, 0.247, 0.271), pruned) if pruned > 0 else self.col
        dy = self.drop * pruned
        a = a * (1 - .65 * pruned)
        y = y + dy
        # ports (tabs + arrows), drawn first so the body overlaps their roots
        for which, on, n in (("wr", wr_on, wr_n), ("rd", rd_on, rd_n)):
            px, py = self.port(x, y, which)
            side = self.wr if which == "wr" else self.rd
            vert = side in ("top", "bottom")
            ls = max(12, self.tag_size - 1)
            tw, th = (max(54, 1.2 * ls + 30), ls + 6) if vert else (1.2 * ls + 10, 54)
            cv.rrect(px - tw / 2, py - th / 2, tw, th, 5, col, a, fill=mix(col, PAPER, .8 - .5 * on), fa=1, lw=1.4)
            cv.text(px, py + .36 * ls, which, MONO, ls, INK, a, anchor="c")
            inward = (which == "wr")
            d = {"top": (0, -1), "bottom": (0, 1), "left": (-1, 0), "right": (1, 0)}[side]
            p0 = (px + d[0] * 14, py + d[1] * 14)
            p1 = (px + d[0] * self.arrow, py + d[1] * self.arrow)
            src, dst = (p1, p0) if inward else (p0, p1)
            cv.line(src, dst, col, a * (.45 + .55 * on), 2.2 + 1.2 * on)
            cv.arrowhead(dst, src, col, a * (.45 + .55 * on), 9 + 3 * on)
            if on > .02:                                   # moving ticks along the port arrow
                for k in range(3):
                    f = ((t * 2.2 + k / 3) % 1)
                    q = (src[0] + (dst[0] - src[0]) * f, src[1] + (dst[1] - src[1]) * f)
                    cv.circle(q, 3.2, None, a * on, fill=col)
            if n is not None:
                ns = max(13, self.tag_size)
                mode = self.port_lab.get(which, "side")
                if isinstance(mode, tuple):
                    dx, dy, an = mode
                elif mode == "under" and not vert:     # below the glyph, ending at its edge
                    dx = -16 if side == "right" else 16
                    dy, an = self.h / 2 + 10 + ns, ("r" if side == "right" else "l")
                elif mode == "left" and vert:          # left of the tab
                    dx, dy, an = -tw / 2 - 10, .36 * eff(ns), "r"
                elif vert:
                    dx, dy, an = tw / 2 + 10, .36 * eff(ns), "l"
                else:
                    dx, dy, an = 0, -th / 2 - 10, "c"
                cv.text(px + dx, py + dy, f"{n}", MONO, ns, INK, a, anchor=an)
        # body
        cv.rrect(x, y, self.w, self.h, 10, col, a, fill=mix(col, PAPER, .95), fa=1, lw=1.7)
        cv.rrect(x, y, self.w, self.head, 10, None, a, fill=mix(col, PAPER, .82), fa=1)
        cv.text(x + 10, y + self.y_name, self.name, "Inter Medium", 15, INK, a)
        if self.level and self.lev_inline:
            cv.text(x + self.w - 10, y + self.y_name, self.level, MONO, self.tag_size, GRAPHITE, a, anchor="r")
        if used is not None and cap:
            cv.text(x + 10, y + self.y_occ, f"{used} / {cap} elements", MONO, self.tag_size, GRAPHITE, a)
        if self.level and not self.lev_inline:
            cv.text(x + 10, y + self.y_lev, self.level, MONO, self.tag_size, GRAPHITE, a)
        gx, gy = x + self.gx_off, y + self.head + self.tm + self.pad
        if self.bank:                                      # bank separators
            for b in range(self.bank, self.cols, self.bank):
                xx = gx + b * self.cell
                cv.line((xx, gy - 4), (xx, gy + self.rows * self.cell + 4), GRAPHITE, a * .5, 1, dash=[3, 3])
        for r in range(self.rows):
            for c in range(self.cols):
                st = state(r, c) if state else "live"
                cx, cy = gx + c * self.cell + 1, gy + r * self.cell + 1
                s = self.cell - 2
                fa = STATE_FA[st]
                if st == "empty":
                    cv.rrect(cx, cy, s, s, 2.5, col, a * .4, lw=.9, dash=[2, 2])
                    continue
                if fill is not None and st in ("live", "new"):
                    p_ = clamp(fill(r, c))
                    cv.rrect(cx, cy, s, s, 2.5, col, a * .5, lw=.8)
                    if p_ > 0:
                        cv.rrect(cx, cy + s * (1 - p_), s, s * p_, 2.0, None, a, fill=col, fa=fa)
                else:
                    cv.rrect(cx, cy, s, s, 2.5, None, a, fill=col if st != "idle" else GRAPHITE, fa=fa)
                if st == "idle":
                    for k in range(0, int(2 * s), 6):      # hatch: held but not needed
                        p = (cx + min(k, s), cy + max(0, k - s))
                        q = (cx + max(0, k - s), cy + min(k, s))
                        cv.line(p, q, GRAPHITE, a * .5, .8)
                    if callout_idle > .01:
                        cv.rrect(cx - 1, cy - 1, s + 2, s + 2, 3, (0.784, 0.247, 0.271), a * callout_idle, lw=1.6)
                if st == "new":
                    cv.rrect(cx - 1.5, cy - 1.5, s + 3, s + 3, 3.5, AMBER, a, lw=1.8)
                if hl is not None:
                    h = clamp(hl(r, c))
                    if h > .01:
                        cv.rrect(cx - 1.5, cy - 1.5, s + 3, s + 3, 3.5, AMBER, a * h, lw=2.0)
        if self.row_lab:
            row_labels(cv, gx - 6, gy, self.row_lab, self.cell, self.lab, a)
        if self.col_lab:
            col_labels(cv, gx, gy - 5, self.col_lab, self.cell, self.lab, a)
        if used is not None and cap:                       # occupancy bar
            bx, by, bh = x + self.w - 9, gy, self.rows * self.cell
            cv.rrect(bx, by, 5, bh, 2.5, DIM, a, fill=PAPER, fa=1, lw=.8)
            f = clamp(used / cap)
            cv.rrect(bx, by + bh * (1 - f), 5, bh * f, 2.5, None, a, fill=col, fa=.85)


def storage_icon(cv, x, y, w, h, col, a=1.0, pruned=0.0):
    """The same glyph at icon size (an option slot): header strip, two port ticks, body."""
    if a <= .002:
        return
    col = mix(col, (0.784, 0.247, 0.271), pruned) if pruned > 0 else col
    y += 14 * pruned
    a *= (1 - .55 * pruned)
    cv.line((x + w / 2, y - 7), (x + w / 2, y), col, a, 1.6)
    cv.line((x + w / 2, y + h), (x + w / 2, y + h + 7), col, a, 1.6)
    cv.rrect(x, y, w, h, 5, col, a, fill=mix(col, PAPER, .85), fa=1, lw=1.5)
    cv.rrect(x, y, w, h * .28, 5, None, a, fill=col, fa=.45)
    for r in range(2):
        for c in range(3):
            cv.rrect(x + 5 + c * (w - 10) / 3, y + h * .38 + r * (h * .26), (w - 10) / 3 - 2, h * .22, 1.5,
                     None, a, fill=col, fa=.55)
