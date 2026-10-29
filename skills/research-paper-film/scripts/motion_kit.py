"""Motion, camera and linkage components: the craft that made the case study read
as alive and precise. A film that passes every legibility gate without them
can still be a slide show (see references/14-motion-camera-linkage.md).

    from engine import *
    from scene_kit import *
    from motion_kit import *

Camera direction
  beat_keys(wide, beats)        keyframes that push in to each mechanism beat and
                                pull back to the wide framing between beats
  lagged(fn, t)                 deterministic smooth follow of a moving target
  stage_cam(t, keys)            StageCam from keyframes (distance log-interpolated)
  View2                         2-D pan/zoom camera for flat scenes (waveforms, charts)

Focus and motion primitives
  focus(t, windows, key)        dim everything that is not part of the current finding
  path_point(pts, f)            point at fraction f along a polyline
  tracer(cv, pts, f, col, a)    a dot that travels along a path, with a short trail
  proposal(cv, pts, prog, ...)  a dashed arc drawn from source to candidate
  pulse(cv, p, r, col, t, t0)   one expanding ring when something is written / decided

Linkage (every finding points at what it is about)
  callout_at(cv, anchor, offset, text, col, a)   annotation with a leader line to its referent
  tether(cv, p, q, col, a)                       curve that joins a node to a table cell
  AddressTable                                    fixed-address state table: one row per
                                                  key, cells written in place, row_anchor()
                                                  gives the tether end point
  pill(cv, cam, ...) / slot_node / stable_loop    the full state space above a reference
                                                  node: ghost (dashed) / live / pruned slots
  breadcrumb(cv, step, text, a)                   "STEP 3 · destination discovery" HUD

Registry for linkage_audit.py
  ANCHORED     strings drawn by callout_at in the current frame
  begin_frame()  call at the start of draw(): clears OVERLAY and ANCHORED
"""
import math
from engine import (seg, smooth, io3, ocub, clamp, lerp, lerp2, mix, bez, DW, DH, INK,
                    GRAPHITE, DIM, TEAL, CORAL, AMBER, BLUE, PAPER, window)
from scene_kit import OVERLAY, overlay, kfv, StageCam, sw

MONO_M = "JetBrains Mono Medium"
MONO = "JetBrains Mono"
MED = "Inter Medium"
ANCHORED = set()


def begin_frame():
    OVERLAY.clear()
    ANCHORED.clear()


# ===================================================== camera direction =====
def lagged(fn, t, tau=.25, n=9):
    """Deterministic smooth follow: exponentially weighted past samples of fn(t)
    (a list of numbers). Use for a camera that trails a moving target."""
    acc, ws = None, 0.0
    for j in range(n):
        q = t - tau * 2.2 * j / (n - 1)
        w = math.exp(-3.5 * j / (n - 1))
        v = fn(q)
        acc = [x * w for x in v] if acc is None else [p + x * w for p, x in zip(acc, v)]
        ws += w
    return [p / ws for p in acc]


def beat_keys(t0, wide, beats, push=.6, pull=.6, ease_in="io", ease_out="io", drift=.04):
    """Camera keyframes for a mechanism-heavy scene.

    wide   : the context framing (tuple of camera values)
    beats  : [(t_in, t_out, close)] - a beat's camera is pushed in to `close`
             by t_in, holds (with a slow drift toward it) until t_out, then
             pulls back to `wide` over `pull` seconds.
    drift  : fraction of the close->wide difference crept during the hold, so
             a held shot is never perfectly static (a living camera).
    Returns keys for kfv(t, keys, logi=(index_of_distance,)).
    """
    keys = [(t0, list(wide), "l")]
    for t_in, t_out, close in beats:
        start = max(keys[-1][0] + .05, t_in - push)
        keys.append((start, list(keys[-1][1]), "l"))
        keys.append((t_in, list(close), ease_in))
        held = [c + (w - c) * drift for c, w in zip(close, wide)]
        keys.append((t_out, held, "s"))
        keys.append((t_out + pull, list(wide), ease_out))
    return keys


def stage_cam(t, keys, logi=(3,), f=1400.0):
    """StageCam from keys whose values are (tx, ty, th, D, tau, psi, ox, oy)."""
    v = kfv(t, keys, logi=logi)
    return StageCam(*v[:8], f=f)


class View2:
    """2-D camera: pan/zoom a flat scene. push(cv) ... pop(cv); S(p) maps a point."""

    def __init__(self, cx, cy, z, ax=DW / 2, ay=DH / 2):
        self.cx, self.cy, self.z, self.ax, self.ay = cx, cy, z, ax, ay

    def push(self, cv):
        c = cv.c
        c.save()
        c.translate(self.ax, self.ay)
        c.scale(self.z, self.z)
        c.translate(-self.cx, -self.cy)

    def pop(self, cv):
        cv.c.restore()

    def S(self, p):
        return (self.ax + (p[0] - self.cx) * self.z, self.ay + (p[1] - self.cy) * self.z)


# ===================================================== focus and motion =====
def focus(t, windows, key, floor=.3, fin=.35, fout=.4):
    """Alpha multiplier: inside a window, keys not in its keep-set fade to floor.
    windows: [((t0, t1), keep_set)]."""
    f = 1.0
    for (a, b), keep in windows:
        if key not in keep:
            f = min(f, 1 - (1 - floor) * window(t, a, b, fin, fout))
    return f


def path_point(pts, f):
    if not pts:
        return None
    if len(pts) == 1:
        return pts[0]
    L = [0.0]
    for p, q in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(p, q))
    s = clamp(f) * L[-1]
    for k in range(len(pts) - 1):
        if L[k + 1] >= s:
            u = (s - L[k]) / max(L[k + 1] - L[k], 1e-9)
            return lerp2(pts[k], pts[k + 1], u)
    return pts[-1]


def tracer(cv, pts, f, col, a=1.0, r=7.0, trail=.18, n=8):
    """A token travelling along a screen-space path (e.g. a settling path, a
    request, a tile). f in [0, 1]. Draws a fading trail behind the dot."""
    if a <= .002 or f <= 0 or not pts:
        return None
    for j in range(n, 0, -1):
        g = f - trail * j / n
        if g <= 0:
            continue
        p = path_point(pts, g)
        cv.circle(p, r * (.45 + .4 * (1 - j / n)), None, a * .35 * (1 - j / n), fill=col)
    p = path_point(pts, f)
    cv.circle(p, r + 3, None, a, fill=PAPER)
    cv.circle(p, r, None, a, fill=col)
    return p


def proposal(cv, p, q, prog, col, a=1.0, w=2.2, bend=.28, dash=(7, 6), head=True):
    """A candidate transition: dashed arc drawn from p toward q (prog 0..1)."""
    if a <= .002 or prog <= 0:
        return None
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    c = (mx - dy * bend, my + dx * bend)
    pts = [((1 - u) ** 2 * p[0] + 2 * (1 - u) * u * c[0] + u * u * q[0],
            (1 - u) ** 2 * p[1] + 2 * (1 - u) * u * c[1] + u * u * q[1])
           for u in [k / 40 * clamp(prog) for k in range(41)]]
    ctx = cv.c
    ctx.new_path()
    ctx.move_to(*pts[0])
    for pt in pts[1:]:
        ctx.line_to(*pt)
    cv.rgba(col, a)
    ctx.set_line_width(w)
    ctx.set_dash(list(dash) if dash else [])
    ctx.stroke()
    ctx.set_dash([])
    if head and prog > .97:
        cv.arrowhead(pts[-1], pts[-3], col, a, 12)
    return pts


def pulse(cv, p, r, col, t, t0, dur=.7, a=1.0):
    """One expanding ring at t0: marks the instant something is written/decided."""
    u = seg(t, t0, t0 + dur)
    if u <= 0 or u >= 1 or a <= .002:
        return
    cv.circle(p, r * (1 + .9 * ocub(u)), col, a * (1 - u), w=2.4)


# ============================================================ linkage =======
def callout_at(cv, anchor, offset, s, col=INK, a=1.0, size=20, font=MED, fill=PAPER,
               leader=True, dot=True, anchor_r=0.0, align="c"):
    """Annotation pinned to its referent: chip at anchor+offset, leader line to
    the anchor (stopping anchor_r short of it), small dot at the anchor.
    s may hold "\n" for a 2-3 line chip (narrow gaps). align="l": offset gives the chip's
    left edge (so a chip can sit beside its anchor whatever its measured width).
    Registers the text (and each line) in ANCHORED (linkage_audit.py checks findings use this)."""
    if a <= .002:
        return None
    ANCHORED.add(s.strip())
    lines = s.split("\n")
    for ln in lines:
        ANCHORED.add(ln.strip())
    lh = size * 1.28
    w = max(cv.measure(ln, font, size) for ln in lines) + 24
    h = size + 16 + lh * (len(lines) - 1)
    cx, cy = anchor[0] + offset[0], anchor[1] + offset[1]
    if align == "l":
        cx += w / 2
    x0 = cx - w / 2
    if leader:
        # leader from the chip edge nearest the anchor
        ex = min(max(anchor[0], x0), x0 + w)
        if x0 <= anchor[0] <= x0 + w or abs(anchor[1] - cy) > h / 2:
            ey = cy + (h / 2 if anchor[1] > cy else -h / 2)
        else:                                      # anchor beside the chip: leave from its side
            ey = cy
        d = math.dist((ex, ey), anchor)
        if d > anchor_r + 6:
            k = (d - anchor_r) / d
            tip = (ex + (anchor[0] - ex) * k, ey + (anchor[1] - ey) * k)
            cv.line((ex, ey), tip, col, a * .85, 1.6)
            if dot:
                cv.circle(tip, 3.4, None, a, fill=col)
    cv.rrect(x0, cy - h / 2, w, h, 8, col, a, fill=fill, fa=.96, lw=1.5)
    for i, ln in enumerate(lines):
        cv.text(x0 + 12, cy - h / 2 + 8 + size * .86 + i * lh, ln, font, size, col, a)
    return (x0, cy - h / 2, w, h)


def tether(cv, p, q, col, a=1.0, bend=.25, w=1.7, prog=1.0, dash=None, dots=True, via=None):
    """Curve from a scene element (p) to a panel address (q), e.g. node -> table row.
    via: screen-space waypoints routed through first (straight runs along gaps, so the tether
    never crosses content); the last leg to q is the usual curve."""
    if a <= .002 or prog <= 0:
        return None
    path = [p] + list(via or [])
    s0 = path[-1]
    c1 = (s0[0] + (q[0] - s0[0]) * .45, s0[1] - (0 if via else abs(q[0] - s0[0]) * bend))
    c2 = (s0[0] + (q[0] - s0[0]) * .75, q[1])
    full = []
    for u, v_ in zip(path, path[1:]):
        full += [lerp2(u, v_, k / 12) for k in range(12)]
    full += [bez(s0, c1, c2, q, k / 48) for k in range(49)]
    seglen = [math.dist(u, v_) for u, v_ in zip(full, full[1:])]
    tot, acc, pts = sum(seglen), 0.0, [full[0]]
    for u, v_, L in zip(full, full[1:], seglen):
        if acc + L >= tot * clamp(prog):
            r = (tot * clamp(prog) - acc) / max(L, 1e-6)
            pts.append(lerp2(u, v_, r))
            break
        pts.append(v_)
        acc += L
    ctx = cv.c
    ctx.new_path()
    ctx.move_to(*pts[0])
    for pt in pts[1:]:
        ctx.line_to(*pt)
    cv.rgba(col, a)
    ctx.set_line_width(w)
    ctx.set_dash(list(dash) if dash else [])
    ctx.stroke()
    ctx.set_dash([])
    if dots:
        cv.circle(p, 3.6, None, a, fill=col)
        if prog > .98:
            cv.circle(q, 3.6, None, a, fill=col)
    return pts


class AddressTable:
    """Fixed-address state table (e.g. every (input, state) of a transition table).

    Every key has its own row from the start, so a write, an inference or a
    conflict always happens at the same place on screen and can be tethered:
    unknown cells show '·'; written cells fade in with a tint; a conflicting
    cell gets a coral frame and a strike; a 'prune' cell (an outcome that removes
    something) gets a coral frame and coral text, no strike, so it stays readable;
    row_anchor(key) is the tether target.

        T = AddressTable(keys, x=1330, y=150, w=540, cols=[...])
        T.draw(cv, t, cells, a)     cells: {key: dict(v=(...), t=t_write,
                                             style='write'|'infer'|'conflict'|'prune',
                                             need=(...), note='infer')}
    """

    def __init__(self, keys, x, y, w, head, key_fmt, val_fmt, col_x, val_x, row_h=29,
                 title=None, size=19):
        self.keys, self.x, self.y, self.w = list(keys), x, y, w
        self.head, self.key_fmt, self.val_fmt = head, key_fmt, val_fmt
        self.col_x, self.val_x, self.rh, self.title, self.size = col_x, val_x, row_h, title, size
        self.top = y + (66 if title else 40)

    def row_y(self, key):
        return self.top + self.rh * (self.keys.index(key) + 1)

    def row_anchor(self, key):
        """Left edge, vertical centre of the key's row (for tether())."""
        return (self.x + 10, self.row_y(key) - self.size * .36)

    def height(self):
        return self.top - self.y + self.rh * (len(self.keys) + 1)

    def draw(self, cv, t, cells, a=1.0, highlight=None):
        if a <= .002:
            return
        x, y, w = self.x, self.y, self.w
        h = self.height()
        # everything in a fixed-address panel sits at its own address: register
        # it as anchored for linkage_audit.py (tether() links rows to the scene)
        ANCHORED.update(s.strip() for s in self.head)
        if self.title:
            ANCHORED.add(self.title.strip())
        ANCHORED.update(str(c.get("note", "")).strip() for c in cells.values() if c)
        cv.shadow(x, y, w, h, 12, a)
        cv.rrect(x, y, w, h, 12, DIM, a, fill=PAPER, fa=1, lw=1.2)
        if self.title:
            cv.text(x + 20, y + 36, self.title, MED, 18, GRAPHITE, a)
        hy = self.top - 6
        for cx, s in zip(self.col_x, self.head):
            cv.text(x + cx, hy, s, MED, 17, GRAPHITE, a, anchor="c")
        cv.line((x + 14, hy + 9), (x + w - 14, hy + 9), DIM, a, 1.1)
        for key in self.keys:
            yy = self.row_y(key)
            c = cells.get(key)
            on = c is not None and t >= c["t"]
            if highlight and key in highlight:
                cv.rrect(x + 12, yy - self.rh + 8, w - 24, self.rh - 2, 5, None, a,
                         fill=mix(highlight[key], PAPER, .85), fa=1)
            if on:
                style = c.get("style", "write")
                tint = {"write": TEAL, "infer": AMBER, "conflict": CORAL, "prune": CORAL}[style]
                ta = 1.0 if style in ("conflict", "prune") else 1 - .6 * smooth(seg(t, c["t"] + 1.0, c["t"] + 2.2))
                cv.rrect(x + 12, yy - self.rh + 8, w - 24, self.rh - 2, 5,
                         CORAL if style in ("conflict", "prune") else None, a,
                         fill=mix(tint, PAPER, .84), fa=ta, lw=1.6)
            for cx, s in zip(self.col_x, self.key_fmt(key)):
                cv.text(x + cx, yy, s, MONO, self.size, INK if on else GRAPHITE, a, anchor="c")
            if on:
                ra = a * smooth(seg(t, c["t"], c["t"] + .3))
                col = {"write": TEAL, "infer": AMBER, "conflict": INK, "prune": CORAL}[c.get("style", "write")]
                for cx, s in zip(self.val_x, self.val_fmt(c["v"])):
                    cv.text(x + cx, yy, s, MONO_M, self.size, col, ra, anchor="c")
                if c.get("style") == "conflict":
                    sx0 = x + self.val_x[0] - 20
                    sx1 = x + self.val_x[-1] + 20
                    cv.line((sx0, yy + 4), (sx1, yy - self.size - 2), CORAL, ra, 2.4)
                    cv.line((sx0, yy - self.size - 2), (sx1, yy + 4), CORAL, ra, 2.4)
                if c.get("note"):
                    cv.text(x + w - 16, yy, c["note"], MED, 16,
                            CORAL if c.get("style") in ("conflict", "prune") else AMBER, ra, anchor="r")
            else:
                for cx in self.val_x:
                    cv.text(x + cx, yy, "·", MONO, self.size, GRAPHITE, a * .7, anchor="c")


def pill(cv, cam, cu, cv_, h, w, hgt, a, col=GRAPHITE, lw=2.0, fill=PAPER, fa=.92, n=8):
    """A rounded container in the plane z = h around world centre (cu, cv_):
    the slot group of one reference node (all candidate states it may hold)."""
    if a <= .002:
        return None
    r = hgt / 2
    pts = []
    for (cx, cy, a0) in [(cu + w / 2 - r, cv_, -90), (cu - w / 2 + r, cv_, 90)]:
        for j in range(n * 2 + 1):
            ang = math.radians(a0 + 180 * j / (n * 2))
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    P = [cam.P((u, v, h)) for u, v in pts]
    sc = sum(p[2] for p in P) / len(P)
    cv.poly([(p[0], p[1]) for p in P], col, a, sw(sc, lw), close=True, fill=fill, fa=fa)
    return sc


def slot_node(cv, p, r, label, state, a=1.0, font=MONO_M, size=24):
    """state: 'ghost' (possible, not reached: dashed), 'live' (instantiated),
    'proposed' (a candidate being considered), 'pruned' (rejected), 'start'."""
    if a <= .002:
        return
    col = {"ghost": GRAPHITE, "live": TEAL, "proposed": AMBER, "pruned": CORAL,
           "start": TEAL}[state]
    ctx = cv.c
    ctx.new_path()
    ctx.arc(p[0], p[1], r, 0, 2 * math.pi)
    cv.rgba(PAPER, a)
    ctx.fill_preserve()
    cv.rgba(col, a * (.75 if state == "ghost" else 1))
    ctx.set_line_width(2.6 if state != "ghost" else 1.6)
    ctx.set_dash([4, 4] if state == "ghost" else [])
    ctx.stroke()
    ctx.set_dash([])
    cv.text(p[0], p[1] + size * .36, label, font, size, INK if state != "ghost" else GRAPHITE,
            a * (1 if state != "ghost" else .8), anchor="c")


def stable_loop(cv, p, r, col, a=1.0):
    """Small self-loop above a node: delta(i, s) = s (the pair is stable)."""
    if a <= .002:
        return
    rr = r * .32
    cx, cy = p[0], p[1] - r - rr * .55
    ctx = cv.c
    ctx.new_path()
    ctx.arc(cx, cy, rr, math.radians(130), math.radians(410))
    cv.rgba(col, a)
    ctx.set_line_width(1.8)
    ctx.stroke()
    ex = cx + rr * math.cos(math.radians(410))
    ey = cy + rr * math.sin(math.radians(410))
    cv.arrowhead((ex, ey), (ex - 3, ey - 3), col, a, 7)


@overlay
def breadcrumb(cv, step, text, a, x=64, y=104):
    """'STEP 3  destination discovery · wrong output' under the act label."""
    if a <= .002:
        return
    w = cv.text(x, y, step.upper(), MED, 16, AMBER, a, track=.12)
    cv.text(x + w + 14, y, text, MONO, 17, INK, a)
