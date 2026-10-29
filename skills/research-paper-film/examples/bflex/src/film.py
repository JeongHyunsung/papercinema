"""B-Flex research film — v3, the comprehension cut.

Every structure is data-driven (data/scene_data.json, produced by the
re-implementation in bflex_model.py) or typed from the paper's tables; see
docs/VERIFICATION.md.

Editing rules for this cut
  * fast   = repetition and scale (fast-forwarded links, tree growth, 568M fill)
  * medium = camera moves and changes of representation
  * slow   = mechanisms: anticipation -> action -> consequence -> hold
  * never change camera, highlight and caption text in the same instant
"""
import json, math, os, random
import numpy as np
import cairo
from engine import *

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = json.load(open(os.path.join(ROOT, "data", "scene_data.json")))

# ===================================================== THE TIMING SHEET =====
# Act I — the challenge
T_HEAD0, T_HEAD1 = 1.3, 3.6          # test vector applied (tracking)
T_REW0, T_REW1 = 4.0, 4.5            # anticipation: rewind to transition 6
T_MOD0, T_MOD1 = 4.5, 5.2            # action: D falls instead of CK
T_PB0, T_PB1 = 6.05, 6.5             # (consequence hold 5.2-6.05) pull back
T_ST0 = 6.5                          # SeGen-20 internal states appear
T_FLY0 = 6.9                         # states fly into the 2-bit square
T_SQ0 = 7.5                          # 2-bit count
T_EXT0, T_EXT1 = 8.25, 8.85          # extrude to 3 bits
T_CB0 = 8.85                         # 3-bit count + "prior search stops"
T_COL0 = 10.05                       # collapse ...
T_TTL = 10.67                        # ... into the wordmark
# Act II — the idea
T_STAGE = 11.9
T_NODE0, T_EDGE0 = 12.0, 12.45       # reference graph builds
T_TOK0, T_TOKD = 14.3, .35           # Act I's vector replayed on the graph
T_TOK1 = T_TOK0 + 6 * T_TOKD         # 16.4; consequence hold to 17.15
T_TILT = 17.15
T_LIFT0, T_LIFT1 = 17.75, 18.65      # nodes lift and split into states
T_SLOT = 18.55
T_CALL = 19.0                        # callout + hold
T_PANEL = 19.5                       # δ panel arrives
# Act III — inside the algorithm
T_S1 = 19.95                         # step 1 camera move
T_INIT, T_ROW7 = 20.5, 20.8
T_S2 = 21.85                         # step 2 camera move
T_ANT2 = 22.4                        # anticipation: CK falls -> Q holds
T_CAND = [23.05 + .2 * k for k in range(4)]
T_REJ = 23.95                        # consequence: wrong output
T_RETRACT = 24.75                    # decision: branches cut
T_S3 = 26.05                         # (hold 25.25-26.05) step 3 camera move
T_X1, T_X2 = 26.6, 27.3
T_KEEP = 28.0
T_FOLLOW = 28.6
T_S4 = 28.9                          # fast-forward (repetition)
LINK_T = [29.2, 29.52, 29.84]
T_S4B = 30.2                         # conflict camera push
T_ANT4 = 30.85                       # anticipation: CK rises with D = 1
T_CPATH = 31.45                      # action
T_CONF = 33.05                       # consequence: entry conflict
T_CUT = 33.65                        # decision: branch pruned
T_PIP = 34.7                         # (hold 34.05-34.7) PiP -> full tree
T_GROW0, T_GROW1 = 35.3, 36.7
# Act IV — impact
T_CELLS0 = 37.95
T_FILL0, T_FILL1 = 39.15, 42.55      # climax 1 (scale), hold to 44.55
T_HIST0 = 44.55
T_BLK0 = 46.65
T_AMB0 = 47.1
T_DIVE0, T_DIVE1 = 47.8, 48.45
T_FF = [49.15, 49.5, 49.85, 50.2, 50.6]
D_FF = [.28, .28, .28, .28, .75]
T_RACE_IN = 51.6
T_R0 = 52.4                          # climax 2 (significance)
V_PS = 20.0                          # ps per second of film time
T_FF1_STOP = T_R0 + 19.1 / V_PS
T_TG_STOP = T_R0 + 48.2 / V_PS
T_BRK = T_TG_STOP + .1
T_SLAM = T_TG_STOP + .55             # controlled reveal of 2.53x
T_SCAT = 56.8
# Act V
T_FINAL = 59.0
DURATION = DUR3 = 62.2

# =============================================================== HUD ========
OVERLAY = []


def overlay(fn):
    """Defer HUD drawing until after all camera-space content."""
    def wrap(*a, **k):
        OVERLAY.append(lambda: fn(*a, **k))
    return wrap


@overlay
def act_label(cv, t, a, b, num, name):
    al = window(t, a, b, .6, .6) * .9
    cv.text(120, 92, num, F_MONO_M, 15, AMBER, al, track=.12)
    cv.text(158, 92, name, F_MONO, 15, GRAPHITE, al, track=.22)


STEP_TITLES = {
    "STEP 1": "start from a stable input–state pair",
    "STEP 2": "destination discovery · wrong output",
    "STEPS 3–4": "infer δ entries · no contradiction → both branches kept "
                 "· the check repeats",
    "STEP 5": "entry conflict",
}


@overlay
def caption(cv, t, a, b, l1, l2=None, step=None, y=930):
    """v4: the narration (and the SRT) carries the sentences. The caption band
    is gone; only the step marker remains, under the act label."""
    if not step:
        return
    al = window(t, a, b, .35, .35)
    if al <= 0:
        return
    w = cv.text(120, 126, step, F_MONO_M, 15, AMBER, al, track=.16)
    cv.text(120 + w + 18, 126, STEP_TITLES[step], F_MONO, 15, INK, al,
            track=.04)


@overlay
def tag(cv, t, a, b, s):
    cv.text(1800, 92, s, F_MONO, 14, GRAPHITE, window(t, a, b, .5, .5) * .8,
            anchor="r", track=.06)


def xmark(cv, p, r, col, a, w=3):
    cv.line((p[0] - r, p[1] - r), (p[0] + r, p[1] + r), col, a, w)
    cv.line((p[0] - r, p[1] + r), (p[0] + r, p[1] - r), col, a, w)


def check(cv, p, r, col, a, prog=1.0, w=3):
    pts = [(p[0] - r, p[1]), (p[0] - r * .3, p[1] + r * .7),
           (p[0] + r, p[1] - r * .8)]
    if prog < .5:
        cv.poly([pts[0], lerp2(pts[0], pts[1], prog * 2)], col, a, w)
    else:
        cv.poly([pts[0], pts[1], lerp2(pts[1], pts[2], (prog - .5) * 2)], col,
                a, w)


def marker(cv, p, n, a, col=DIM, txt=INK, r=15, size=16):
    """Numbered transition marker — the same identity in Act I and Act II."""
    if a <= 0.002:
        return
    cv.circle(p, r, None, a, fill=col, fa=1)
    cv.text(p[0], p[1] + size * .37, str(n), F_MONO_M, size, txt, a,
            anchor="c")


def bits(v, n):
    return format(v, f"0{n}b")


# ============================================================ cameras =======
EASE = {"io": io3, "o": oexpo, "oc": ocub, "s": smooth, "l": clamp,
        "i": lambda x: clamp(x) ** 3}


def kfv(t, keys, logi=()):
    """Keyframes [(t, values, ease)] -> interpolated list (log for logi)."""
    if t <= keys[0][0]:
        return list(keys[0][1])
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = EASE[b[2]](seg(t, a[0], b[0]))
            out = []
            for k, (x, y) in enumerate(zip(a[1], b[1])):
                if k in logi:
                    out.append(math.exp(lerp(math.log(x), math.log(y), u)))
                else:
                    out.append(lerp(x, y, u))
            return out
    return list(keys[-1][1])


def lagged(fn, t, tau=.25, n=9):
    """Deterministic smooth follow: exponentially weighted past samples."""
    acc, ws = None, 0.0
    for j in range(n):
        q = t - tau * 2.2 * j / (n - 1)
        w = math.exp(-3.5 * j / (n - 1))
        v = fn(q)
        acc = [x * w for x in v] if acc is None else \
            [p + x * w for p, x in zip(acc, v)]
        ws += w
    return [p / ws for p in acc]


class View2:
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
        return (self.ax + (p[0] - self.cx) * self.z,
                self.ay + (p[1] - self.cy) * self.z)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


class StageCam:
    """Look-at camera. World: x right, y 'down the layout', z up (height).
    tau = tilt from straight-down, psi = azimuth, D = distance."""

    def __init__(self, tx, ty, th, D, tau, psi, ox=0.0, oy=0.0, f=1400.0):
        st, ct, sp, cp = math.sin(tau), math.cos(tau), math.sin(psi), \
            math.cos(psi)
        self.eye = (tx + D * sp * st, ty + D * cp * st, th + D * ct)
        self.fwd = (-sp * st, -cp * st, -ct)
        self.up = (-sp * ct, -cp * ct, st)
        self.right = _cross(self.up, self.fwd)
        self.f, self.ox, self.oy, self.D = f, ox, oy, D

    def P(self, p):
        d = (p[0] - self.eye[0], p[1] - self.eye[1], p[2] - self.eye[2])
        xc = d[0] * self.right[0] + d[1] * self.right[1] + d[2] * self.right[2]
        yc = d[0] * self.up[0] + d[1] * self.up[1] + d[2] * self.up[2]
        zc = max(d[0] * self.fwd[0] + d[1] * self.fwd[1] + d[2] * self.fwd[2],
                 1.0)
        s = self.f / zc
        return (DW / 2 + self.ox + xc * s, DH / 2 + self.oy - yc * s, s, zc)


def sw(sc, w):
    """Projected stroke width: grows with proximity, but sub-linearly."""
    return w * max(sc, .25) ** .8 * .85


# ======================================================= ACT I: waveform ====
WX0, WXE = 400, 1500
WXS = [560, 720, 880, 1040, 1200, 1360]
WY = {"D": 410, "CK": 520, "Q": 630}
WA = 25


def wave_head(t):
    if t < T_REW0:
        return WX0 + (WXE - WX0) * io3(seg(t, T_HEAD0, T_HEAD1)), False
    if t < T_MOD0:
        return lerp(WXE, WXS[5] - 30, io3(seg(t, T_REW0, T_REW1))), False
    return lerp(WXS[5] - 30, WXE, io3(seg(t, T_MOD0, T_MOD1))), True


def _first_cross(fn, x, a, b):
    for q in np.linspace(a, b, 4001):
        if fn(q) >= x:
            return float(q)
    return b


T_TRANS = [_first_cross(lambda q: wave_head(q)[0], x, T_HEAD0, T_HEAD1)
           for x in WXS]
T_CAP = T_TRANS[4]
T_MOD6 = _first_cross(lambda q: wave_head(q)[0], WXS[5], T_MOD0, T_MOD1)


def sig_segments(start, switches, x_end):
    out, lvl, col = [], start, "n"
    pts = [(WX0, lvl)]
    for (xs, nl, ck) in switches:
        if xs >= x_end:
            break
        pts.append((xs, lvl))
        if ck != col:
            out.append((col, pts))
            pts = [(xs, lvl)]
            col = ck
        pts.append((xs, nl))
        lvl = nl
    pts.append((x_end, lvl))
    out.append((col, pts))
    return out


def draw_signal(cv, name, start, switches, x_end, a, colmap):
    y0 = WY[name]
    for ck, pts in sig_segments(start, switches, x_end):
        P = [(x, y0 + (WA if l == 0 else -WA)) for x, l in pts]
        cv.poly(P, colmap[ck], a, 3)


CUBE_L = 250


def vpos(state, nbits, ext=1.0, L=CUBE_L):
    b = [(state >> (nbits - 1 - k)) & 1 for k in range(nbits)]
    x = (b[0] - .5) * L
    y = (.5 - b[1]) * L
    z = ((b[2] - .5) * L * ext) if nbits == 3 else 0.0
    return (x, y, z)


def cube_edges(n):
    E = []
    for a in range(2 ** n):
        for k in range(n):
            b = a ^ (1 << k)
            if a < b:
                E.append((a, b))
    return E


def cube_col(t):
    return smooth(seg(t, T_COL0, T_COL0 + .65))


def cube_cam(t):
    col = cube_col(t)
    return Cam3(yaw=-.35 + .55 * io3(seg(t, T_FLY0 - .3, T_COL0 + .3)) +
                .12 * col,
                pitch=-.18 - .32 * io3(seg(t, T_EXT0 - .2, T_EXT1 + .3)),
                dist=1300, f=1300, cx=lerp(760, 960, col), cy=500)


def scene_wave(cv, t):
    if t < .8 or t > T_FLY0 + 1.0:
        return
    A = smooth(seg(t, .8, 1.4))
    morph = smooth(seg(t, T_FLY0 - .1, T_FLY0 + .35))
    fa = A * (1 - morph)
    for k, (nm, y) in enumerate(WY.items()):
        cv.text(WX0 - 44, y + 9, nm, F_UI_M, 28, INK,
                fa * smooth(seg(t, .9 + k * .12, 1.5 + k * .12)), anchor="r")
        cv.line((WX0, y + WA), (WXE, y + WA), DIM,
                fa * .6 * smooth(seg(t, 1.0, 1.8)), 1, [2, 6])
    head, mod = wave_head(t)
    D = [(WXS[2], 1, "n")] + ([(WXS[5], 0, "n")] if mod else [])
    CK = [(WXS[0], 0, "n"), (WXS[1], 1, "n"), (WXS[3], 0, "n"),
          (WXS[4], 1, "n")] + ([] if mod else [(WXS[5], 0, "n")])
    Q = [(WXS[4] + 10, 1, "n")] + ([(WXS[5] + 10, 0, "c")] if mod else [])
    cm = {"n": INK, "c": CORAL}
    draw_signal(cv, "D", 0, D, head, fa, cm)
    draw_signal(cv, "CK", 1, CK, head, fa, cm)
    draw_signal(cv, "Q", 0, Q, head, fa, cm)
    if mod and head > WXS[5] + 10:
        cv.line((WXS[5] + 10, WY["Q"] - WA), (head, WY["Q"] - WA), BLUE,
                fa * .8, 2, [3, 7])
        la = fa * smooth(seg(t, T_MOD1 - .1, T_MOD1 + .2))
        cv.text(WXE + 16, WY["Q"] - WA + 6, "expected Q", F_UI_M, 20, BLUE, la)
        cv.text(WXE + 16, WY["Q"] + WA + 6, "SeGen-20 output", F_MONO_M, 19, CORAL, la)
    if T_HEAD0 - .1 < t < T_MOD1 + .1 and abs(head - WXE) > 1:
        pass   # v4: no glow at the playhead
    if head > WXS[4] and t < T_REW0:
        fl = math.exp(-max(0, t - T_CAP) * 3)
        cv.glow_dot((WXS[4], WY["CK"]), 60, AMBER, .55 * fl * fa)
        cv.glow_dot((WXS[4] + 10, WY["Q"]), 60, AMBER, .55 * fl * fa)
    for k, x in enumerate(WXS):
        on = head >= x - 2 or (t >= T_REW0 and k < 5)
        if not on:
            continue
        cv.line((x, 360), (x, 680), GRAPHITE, fa * .55, 1.2, [2, 5])
        bad = mod and k == 5 and head >= x
        marker(cv, (x, 330), k + 1, fa, CORAL if bad else DIM)
        if bad:
            xmark(cv, (x + 34, 330), 8, CORAL, fa, 3)
            cv.text(x + 58, 336, "D 1→0 replaces CK 1→0", F_MONO, 15, CORAL,
                    fa * smooth(seg(t, T_MOD6 + .05, T_MOD6 + .35)))
        elif not (k == 5 and t >= T_REW0):
            pr = seg(t, T_TRANS[k] + .05, T_TRANS[k] + .3) if t < T_REW0 \
                else 1
            check(cv, (x + 34, 331), 8, TEAL, fa, pr, 3)
    st = DATA["segen"]["modified"]["states"]
    xs = [WX0] + WXS + [WXE]
    sa = A * smooth(seg(t, T_ST0, T_ST0 + .3))
    cv.text(WX0 - 44, 725, "s0 s1", F_UI_M, 20, GRAPHITE, 0 * sa * (1 - morph),
            anchor="r")
    cam = cube_cam(max(t, T_FLY0))
    for k in range(7):
        cx = (xs[k] + xs[k + 1]) / 2
        tgt, scl, _ = cam.proj(vpos(st[k] << 1, 3, 0.0))
        f = io3(seg(t, T_FLY0 + k * .04, T_FLY0 + .5 + k * .04))
        p = lerp2((cx, 727), (tgt[0], tgt[1] + 7), f)
        la = sa * smooth(seg(t, T_ST0 + k * .04, T_ST0 + .25 + k * .04)) * \
            (1 - smooth(seg(t, T_FLY0 + .65, T_FLY0 + .8)))
        cv.text(p[0], p[1], bits(st[k], 2), F_MONO_M, lerp(20, 19 * scl, f),
                mix(INK if k < 6 else CORAL, INK, f), la, anchor="c")
    caption(cv, t, 1.4, T_REW0 + .05, "One test vector. Six transitions. "
            "All pass.",
            "A prior automated flip-flop search validates each candidate "
            "against a single fixed input sequence.")
    caption(cv, t, T_MOD0 + .05, T_PB1,
            "Reorder one transition, and the same design outputs the wrong Q.",
            "SeGen-20: a 2-bit-state FSM that passes its test vector, "
            "yet violates flip-flop behavior.")
    tag(cv, t, 1.4, T_PB1, "Fig. 2 · §2 · re-simulated")


def scene_cube(cv, t):
    if t < T_FLY0 - .1 or t > T_TTL + .3:
        return
    A = smooth(seg(t, T_FLY0, T_FLY0 + .5)) * \
        (1 - smooth(seg(t, T_TTL - .2, T_TTL)))
    ext = io3(seg(t, T_EXT0, T_EXT1))
    col = cube_col(t)
    cam = cube_cam(t)

    def P(s):
        x, y, z = vpos(s, 3, ext)
        k = 1 - col
        return cam.proj((x * k, y * k, z * k))

    for (a, b) in cube_edges(3):
        is_z = (a ^ b) == 1
        ea = A * (ext if (is_z or (a & 1)) else 1)
        pa, _, _ = P(a)
        pb, _, _ = P(b)
        if is_z:
            pb = lerp2(pa, pb, ext)
        cv.line(pa, pb, GRAPHITE if is_z else INK, ea * .8, 2.2)
    for s in range(8):
        if (s & 1) and ext <= 0.01:
            continue
        p, sc, _ = P(s)
        aa = A * (ext if (s & 1) else 1)
        cv.circle(p, 30 * sc, INK, aa, fill=BG_IN, fa=.95, w=2)
        lab = bits(s >> 1, 2) if ext < .5 else bits(s, 3)
        if col < .5:
            cv.text(p[0], p[1] + 7, lab, F_MONO_M, 19 * sc, INK,
                    aa * (1 - col * 2) * smooth(seg(t, T_FLY0 + .65,
                                                    T_FLY0 + .85)), anchor="c")
    if col > 0 and t < T_TTL + .3:
        cv.glow_dot((960, 500), 50 + 110 * col, INK,
                    .75 * smooth(seg(t, T_TTL - .32, T_TTL - .02)) *
                    (1 - smooth(seg(t, T_TTL, T_TTL + .28))))
    px = 1180
    for aa, lab, big, big2, sub in [
            (0.0 * window(t, T_SQ0, T_CB0 - .2, .4, .35), "2-bit state", "3^{16}",
             "≈ 4.3 × 10^{7}",
             "4 inputs × 4 states = 16 entries · hold or flip one bit"),
            (window(t, T_CB0, T_COL0 + .1, .4, .35), "3-bit state", "4^{32}",
             "≈ 1.8 × 10^{19}",
             "4 inputs × 8 states = 32 entries · hold or flip one bit")]:
        if aa <= 0:
            continue
        cv.text(px, 400, lab, F_MONO, 18, AMBER, aa, track=.18)
        cv.text(px, 490, big, F_TITLE_L, 84, INK, aa)
        cv.text(px + cv.measure(big, F_TITLE_L, 84) + 24, 490, big2,
                F_TITLE_L, 44, INK, aa)
        cv.text(px, 536, "candidate transition tables", F_UI_L, 24, GRAPHITE,
                aa)
        cv.text(px, 580, sub, F_MONO_L, 15, GRAPHITE, aa)
    fa3 = window(t, T_CB0 + .35, T_COL0 + .1, .4, .35)
    cv.text(px, 650, "Prior automated FF search stops at 2-bit states.",
            F_UI, 24, INK, fa3)
    cv.text(px, 686, "Brute force, 1 thread: ~10^{6} years "
            "(extrapolated, Table 1)", F_MONO, 16, CORAL, fa3)
    caption(cv, t, T_CB0 - .05, T_COL0 + .05,
            "Prior automated FF search stops at 2-bit states.",
            "Brute force at 3-bit state: ~10^{6} years "
            "(extrapolated, Table 1).")
    tag(cv, t, T_SQ0, T_COL0, "Table 1 footnote · §1")


def scene_title(cv, t):
    if t < T_TTL - .1 or t > T_STAGE + .3:
        return
    a = smooth(seg(t, T_TTL, T_TTL + .33)) * \
        (1 - smooth(seg(t, T_STAGE - .15, T_STAGE + .15)))
    cv.text(960, 520, "B-Flex", F_TITLE, 150, INK, a, anchor="c", track=-.01)
    cv.text(960, 600,
            "Validate every input order.   Prune while you generate.",
            F_UI_L, 30, mix(GRAPHITE, INK, .35),
            a * smooth(seg(t, T_TTL + .3, T_TTL + .65)), anchor="c")
    ring = seg(t, T_TTL, T_TTL + .8)
    if 0 < ring < 1:
        cv.circle((960, 500), 40 + 700 * ocub(ring), INK, (1 - ring) * .5,
                  w=1.5)


def _camA_early(t):
    w = smooth(seg(t, T_HEAD0 - .1, T_HEAD0 + .55))
    fx = lagged(lambda q: [min(wave_head(min(q, T_REW0 - .01))[0] + 170,
                               1330)], t, .22)[0]
    cx = lerp(470, fx, w)
    z = math.exp(lerp(math.log(2.4), math.log(1.75),
                      smooth(seg(t, T_HEAD0, T_HEAD1))))
    z += .16 * math.exp(-((t - T_CAP) / .22) ** 2)
    return [cx, 520 - 8 * smooth(seg(t, T_HEAD0, T_HEAD1)), z]


CAMA_KEYS = [
    (T_REW0, tuple(_camA_early(T_REW0)), "l"),
    (T_REW1, (1415, 515, 2.1), "io"),
    (T_PB0, (1430, 518, 2.2), "l"),
    (T_PB1, (960, 525, 1.0), "io"),
    (T_COL0, (960, 515, 1.1), "s"),
    (T_TTL - .02, (960, 500, 3.2), "i"),
    (T_TTL + .85, (960, 520, 1.0), "o"),
    (T_STAGE + .4, (960, 520, 1.03), "l"),
]


def camA(t):
    v = _camA_early(t) if t < T_REW0 else kfv(t, CAMA_KEYS, logi=(2,))
    return View2(*v)


def dot_grid(cv, t, cam):
    a = .06 * smooth(seg(t, .3, 2.0)) * (1 - smooth(seg(t, T_TTL - .4,
                                                         T_TTL)))
    if a <= 0:
        return
    c = cv.c
    cv.rgba(INK, a)
    sp = 48
    ox = (-cam.cx * cam.z * .35) % sp
    oy = (-cam.cy * cam.z * .35) % sp
    for gx in range(-1, DW // sp + 2):
        for gy in range(-1, DH // sp + 2):
            c.rectangle(gx * sp + ox, gy * sp + oy, 1.3, 1.3)
    c.fill()


# ====================================== ACT II/III: the 3-D stage ===========
H_E = 125.0                                   # height of the candidate plane
RCOLS = [600, 840, 1080, 1320]
RROWS = [460, 680]
RN = {(n["i"], n["o"]): (RCOLS[n["col"]], RROWS[n["row"]])
      for n in DATA["rbg"]["nodes"]}
RBG_EDGES = [(tuple(e["a"]), tuple(e["b"]), e["rising"], e["changes_q"])
             for e in DATA["rbg"]["edges"]]
EDGE_SET = {(a, b) for a, b, _, _ in RBG_EDGES}
NODE_ORDER = sorted(RN, key=lambda k: (RN[k][1], RN[k][0]))
T_NODE = {k: T_NODE0 + j * .07 for j, k in enumerate(NODE_ORDER)}
T_EDGE = [T_EDGE0 + j * .045 for j in range(len(RBG_EDGES))]
# Act I's failing (modified) test vector, as a path through the reference:
# (01,Q0) -CK↓-> (00,Q0) -CK↑-> (01,Q0) -D↑-> (11,Q0) -CK↓-> (10,Q0)
#         -CK↑, D=1-> (11,Q1) -D↓-> (01,Q1)
TOKEN_PATH = [(1, 0), (0, 0), (1, 0), (3, 0), (2, 0), (3, 1), (1, 1)]
for _a, _b in zip(TOKEN_PATH, TOKEN_PATH[1:]):
    assert (_a, _b) in EDGE_SET, (_a, _b)
assert [o for _, o in TOKEN_PATH[1:]] == DATA["segen"]["modified"]["expected"][1:]


def lam(s):
    return 1 - (s & 1)


def slot_uv(i, s):
    u, v = RN[(i, lam(s))]
    return (u + (44 if (s >> 1) else -44), v)


def edge_geom(a, b):
    pa, pb = RN[a], RN[b]
    ra = 54
    bidir = (b, a) in EDGE_SET
    if pa[1] == pb[1] and abs(pa[0] - pb[0]) < 300:
        dx = 1 if pb[0] > pa[0] else -1
        off = (-9 if dx > 0 else 9) if bidir else 0
        p0 = (pa[0] + dx * ra, pa[1] + off)
        p1 = (pb[0] - dx * ra, pb[1] + off)
        return p0, lerp2(p0, p1, .33), lerp2(p0, p1, .66), p1
    if pa[1] == pb[1]:
        up = -1 if pa[1] == RROWS[0] else 1
        h = 150 + (22 if pa[0] < pb[0] else 0)
        p0 = (pa[0] + (10 if pa[0] < pb[0] else -10), pa[1] + up * ra)
        p1 = (pb[0] + (-10 if pa[0] < pb[0] else 10), pb[1] + up * ra)
        return p0, (p0[0], p0[1] + up * h), (p1[0], p1[1] + up * h), p1
    ang = math.atan2(pb[1] - pa[1], pb[0] - pa[0])
    p0 = (pa[0] + ra * math.cos(ang), pa[1] + ra * math.sin(ang))
    p1 = (pb[0] - ra * math.cos(ang), pb[1] - ra * math.sin(ang))
    return p0, lerp2(p0, p1, .33), lerp2(p0, p1, .66), p1


def tok_state(t):
    """(edge index k, fraction f along it) of the replay token."""
    u = seg(t, T_TOK0, T_TOK1) * (len(TOKEN_PATH) - 1)
    k = min(int(u), len(TOKEN_PATH) - 2)
    return k, io3(u - k) if u < len(TOKEN_PATH) - 1 else 1.0


def tok_pos(t):
    k, f = tok_state(t)
    return bez(*edge_geom(TOKEN_PATH[k], TOKEN_PATH[k + 1]), f)


# ---- walkthrough data (all from the computed search tree) ----------------
WALK = DATA["walk"]
CONF = WALK["conflict"]
CHAIN = CONF["chain"]                 # X1, L1, L2, L3 (edges + inferred δ)
INIT = (1, 3)
CANDS = [(c["s2"], c["status"]) for c in WALK["candidates"]]


# ---- stage camera -------------------------------------------------------
OXP = -230.0                          # stage shifted left of the δ panel
STAGE_KEYS = [
    (T_STAGE, (720, 500, 0, 520, 0, 0, 0, 0), "l"),
    (T_STAGE + .25, (720, 500, 0, 520, 0, 0, 0, 0), "l"),
    (T_EDGE0 + .75, (960, 575, 0, 960, .04, 0, 0, 0), "io"),
    (T_TILT, (960, 572, 0, 930, .05, 0, 0, 0), "l"),
    (T_TILT + .7, (990, 585, 60, 980, .80, -.16, -150, 60), "io"),
    (T_PANEL, (990, 582, 60, 965, .82, -.18, -150, 60), "l"),
    (T_S1, (990, 582, 60, 965, .82, -.18, OXP, 60), "s"),
    (T_S1 + .5, (850, 470, H_E, 520, .36, -.08, OXP, 20), "io"),
    (T_S2, (845, 468, H_E, 505, .35, -.07, OXP, 20), "l"),
    (T_S2 + .5, (915, 575, 90, 1030, .48, -.08, OXP, 30), "io"),
    (T_S3, (918, 577, 90, 1010, .48, -.08, OXP, 30), "l"),
    (T_S3 + .45, (700, 466, H_E, 470, .34, -.06, OXP, 20), "io"),
    (T_S4, (695, 465, H_E, 455, .33, -.05, OXP, 20), "l"),
    (T_S4 + .25, (938, 540, 75, 1000, .55, -.14, OXP, 40), "io"),
    (T_S4B, (940, 540, 75, 990, .55, -.14, OXP, 40), "l"),
    (T_S4B + .6, (1100, 570, H_E, 690, .40, -.10, OXP, 0), "io"),
    (T_PIP, (1102, 570, H_E, 650, .38, -.08, OXP, 0), "l"),
    (T_PIP + .6, (1102, 570, H_E, 330, .38, -.08, OXP, 0), "i"),
]


def stage_cam(t):
    return StageCam(*kfv(t, STAGE_KEYS, logi=(3,)))


# ---- focus: simplify the picture while a finding is shown ------------------
FOCUS = [((T_REJ - .15, T_RETRACT + .6), {(1, 0), (0, 0), (0, 1)}),
         ((T_ANT4, T_CUT + .6), {(2, 0), (3, 0), (3, 1), (1, 0)})]


def pill_focus(k, t):
    f = 1.0
    for (a, b), keep in FOCUS:
        if k not in keep:
            f = min(f, 1 - .7 * window(t, a, b, .35, .4))
    return f


# ---- projected drawing helpers --------------------------------------------
def proj_path(cam, pts, h):
    out, ss = [], 0.0
    for (u, v) in pts:
        x, y, s, _ = cam.P((u, v, h))
        out.append((x, y))
        ss += s
    return out, ss / max(len(pts), 1)


def draw_proj_path(cv, cam, pts, h, col, a, w, prog=1.0, dash=False,
                   head=True):
    if a <= 0.002 or prog <= 0 or len(pts) < 2:
        return None
    n = max(2, int(round(len(pts) * clamp(prog))))
    P, sc = proj_path(cam, pts[:n], h)
    lw = sw(sc, w)
    if dash:
        for k in range(0, len(P) - 1, 2):
            cv.line(P[k], P[k + 1], col, a, lw)
    else:
        cv.poly(P, col, a, lw)
    if head and prog > .97:
        cv.arrowhead(P[-1], P[-2], col, a, 7 + 5 * max(sc, .3) ** .8)
    return P


def pill_outline(u, v, w, hgt, r, n=6):
    pts = []
    for (cx, cy, a0) in [(u + w / 2 - r, v - hgt / 2 + r, -90),
                         (u + w / 2 - r, v + hgt / 2 - r, 0),
                         (u - w / 2 + r, v + hgt / 2 - r, 90),
                         (u - w / 2 + r, v - hgt / 2 + r, 180)]:
        for j in range(n + 1):
            a = math.radians(a0 + 90 * j / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def est_pts(a, b, lift=0.0):
    """Plane curve between two ESTG slots, trimmed at the node rims."""
    p0, p1 = slot_uv(*a), slot_uv(*b)
    du, dv = p1[0] - p0[0], p1[1] - p0[1]
    if abs(dv) < 1 and a[0] == b[0]:
        c1, c2 = (p0[0], p0[1] - 50), (p1[0], p1[1] - 50)
    elif abs(dv) < 1 and abs(du) > 300:
        up = -1 if p0[1] < 570 else 1
        h = 150 + lift
        c1, c2 = (p0[0], p0[1] + up * h), (p1[0], p1[1] + up * h)
    else:
        L = math.hypot(du, dv)
        nx, ny = -dv / L, du / L
        b_ = -26 if abs(dv) < 1 else -34
        c1 = (p0[0] + du * .3 + nx * b_, p0[1] + dv * .3 + ny * b_)
        c2 = (p0[0] + du * .7 + nx * b_, p0[1] + dv * .7 + ny * b_)
    pts = [bez(p0, c1, c2, p1, k / 60) for k in range(61)]
    return [p for p in pts if math.dist(p, p0) > 29 and math.dist(p, p1) > 31]


def path_point(pts, f):
    if not pts:
        return None
    if len(pts) == 1:
        return pts[0]
    f = clamp(f) * (len(pts) - 1)
    k = min(int(f), len(pts) - 2)
    return lerp2(pts[k], pts[k + 1], f - k)


def bb_text(cv, cam, wp, dx, dy, s, font, size, col, a, anchor="c"):
    """Billboard text: anchored at a world point, offset in world-ish px."""
    if a <= 0.002:
        return
    x, y, sc, _ = cam.P(wp)
    cv.text(x + dx * sc, y + dy * sc, s, font, size * sc, col, a, anchor=anchor)


def chip(cv, cam, wp, dx, dy, s, col, a, size=13, fill=None):
    if a <= 0.002:
        return
    x, y, sc, _ = cam.P(wp)
    w = cv.measure(s, F_MONO_M, size * sc) + 18 * sc
    h = (size + 13) * sc
    x0, y0 = x + dx * sc, y + dy * sc
    cv.rrect(x0, y0 - h / 2, w, h, 6 * sc, col, a, fill=fill or BG_IN, fa=.94,
             lw=1.4)
    cv.text(x0 + 9 * sc, y0 + size * .36 * sc, s, F_MONO_M, size * sc, col, a)


def stable_mark(cv, cam, ij, col, a):
    """Self-loop: δ(i, s) = s (the pair is stable)."""
    if a <= 0.002:
        return
    u, v = slot_uv(*ij)
    x, y, sc, _ = cam.P((u, v, H_E))
    r = 9 * sc
    cx, cy = x, y - 27 * sc - r * .55
    c = cv.c
    c.new_path()
    c.arc(cx, cy, r, math.radians(130), math.radians(410))
    cv.rgba(col, a)
    c.set_line_width(sw(sc, 1.6))
    c.stroke()
    ex, ey = cx + r * math.cos(math.radians(410)), cy + r * math.sin(
        math.radians(410))
    cv.arrowhead((ex, ey), (ex - 3 * sc, ey - 3 * sc), col, a, 4 + 3 * sc ** .8)


# ---- ESTG node-state bookkeeping ------------------------------------------
def node_style(i, s, t):
    """(alpha, ring colour, label colour) of a discovered ESTG node, or None."""
    if (i, s) == INIT and t >= T_INIT:
        return 1.0, TEAL, INK
    if i == 0 and s in (0, 2):                 # proposed then pruned (step 2)
        ta = T_CAND[s] + .3
        if t < ta or t > T_RETRACT + .5:
            return None
        kill = seg(t, T_REJ, T_REJ + .35)
        gone = smooth(seg(t, T_RETRACT, T_RETRACT + .5))
        return (1 - gone) * smooth(seg(t, ta, ta + .2)), \
            mix(GRAPHITE, CORAL, kill), mix(INK, CORAL, kill)
    if (i, s) == (0, 3):
        if t >= T_X1 + .3:
            return 1.0, TEAL, INK
        if t >= T_CAND[3] + .3:
            return .8, GRAPHITE, INK
        return None
    if (i, s) == (0, 1):
        if t >= LINK_T[2] + .22:
            return 1.0, TEAL, INK
        if t >= T_X2 + .45:
            fade = 1 - .7 * smooth(seg(t, T_FOLLOW, T_FOLLOW + .3))
            return fade, AMBER, INK
        if t >= T_CAND[1] + .3:
            return .8 * (1 - smooth(seg(t, T_X1 - .1, T_X1 + .2))), \
                GRAPHITE, INK
        return None
    if (i, s) == (3, 3) and t >= LINK_T[0] + .22:
        return 1.0, TEAL, INK
    if (i, s) == (2, 3) and t >= LINK_T[1] + .1:
        return .65, GRAPHITE, INK                  # transient of L2
    if (i, s) == (2, 1) and t >= LINK_T[1] + .22:
        return 1.0, TEAL, INK
    if (i, s) == (3, 1) and t >= T_CPATH + .4:      # transient of conflict
        return .95 * (1 - smooth(seg(t, T_CUT + .1, T_CUT + .4))), AMBER, INK
    if (i, s) == (3, 2) and t >= T_CPATH + 1.45:    # the unreachable target
        return .9 * (1 - smooth(seg(t, T_CUT + .1, T_CUT + .4))), CORAL, CORAL
    return None


def table_entries(t):
    """(i, s) -> (value, t_set, colour) for the δ panel."""
    ent = {}

    def put(i, s, v, ts, col=TEAL):
        if t >= ts:
            ent[(i, s)] = (v, ts, col)
    put(1, 3, 3, T_ROW7)
    put(0, 3, 3, T_X1 + .45)                                    # X1 (kept)
    if t < T_FOLLOW + .3:
        put(0, 1, 1, T_X2 + .55, AMBER)                         # X2 only
    for L, lt in zip(CHAIN[1:], LINK_T):
        for k, (i, s, v) in enumerate(L["inferred"]):
            put(i, s, v, lt + .2 + .04 * k)
    if t < T_CUT + .4:
        put(3, 1, 3, T_CPATH + .45, AMBER)                      # inferred
    return ent


# tethers: (node, row, start, end, colour) — node and its δ row light together
TETHERS = [(INIT, 7, T_ROW7 - .05, T_ROW7 + 1.05, TEAL),
           ((0, 3), 3, T_X1 + .4, T_X1 + 1.25, TEAL),
           ((0, 1), 1, T_X2 + .5, T_X2 + 1.35, AMBER),
           ((0, 3), 3, T_X2 + .5, T_X2 + 1.35, AMBER),
           ((3, 3), 15, LINK_T[0] + .18, LINK_T[0] + .5, TEAL),
           ((2, 1), 9, LINK_T[1] + .18, LINK_T[1] + .5, TEAL),
           ((0, 1), 1, LINK_T[2] + .18, LINK_T[2] + .5, TEAL),
           ((3, 1), 13, T_CPATH + .4, T_CPATH + 1.3, AMBER),
           ((3, 3), 15, T_CONF + .1, T_CUT + .55, CORAL)]

PX, PY, PROW = 1478.0, 232.0, 27.0


def prow_y(r):
    return PY + 96 + r * PROW


@overlay
def draw_panel(cv, t, node_px):
    a = smooth(seg(t, T_PANEL, T_PANEL + .4)) * (1 - smooth(seg(t, T_PIP - .1,
                                                                T_PIP + .3)))
    if a <= 0.002:
        return
    slide = (1 - ocub(seg(t, T_PANEL, T_PANEL + .5))) * 60
    x0, y0 = PX + slide, PY
    cv.shadow(x0 - 26, y0 - 18, 392, 96 + 16 * PROW + 12, 14, a)
    cv.rrect(x0 - 26, y0 - 18, 392, 96 + 16 * PROW + 12, 14, DIM,
             a, fill=PAPER, fa=.97, lw=1.2)
    cv.text(x0 - 8, y0 + 14, "Partial transition table", F_UI_M, 17, INK, a)
    cv.text(x0 - 8, y0 + 38, "δ(i, s) → s'   ·   · = not yet assigned",
            F_MONO, 12, GRAPHITE, a)
    cols = [0, 40, 98, 138, 236, 276]
    for k, h in enumerate(["D", "CK", "s0", "s1", "s0'", "s1'"]):
        cv.text(x0 + cols[k], y0 + 68, h, F_MONO, 13, GRAPHITE, a, anchor="c")
    cv.text(x0 + 187, y0 + 68, "→", F_MONO, 13, GRAPHITE, a, anchor="c")
    cv.line((x0 - 16, y0 + 78), (x0 + 330, y0 + 78), DIM, a, 1)
    ent = table_entries(t)
    for r in range(16):
        i, s = r >> 2, r & 3
        y = prow_y(r)
        e = ent.get((i, s))
        if e:
            hl = math.exp(-(t - e[1]) * 2.2)
            cv.rrect(x0 - 18, y - 18, 342, 24, 5, None, a,
                     fill=mix(BG_IN, e[2], .30 * hl + .10), fa=.95)
        for k, v in enumerate([i >> 1, i & 1, s >> 1, s & 1]):
            cv.text(x0 + cols[k], y, str(v), F_MONO, 15,
                    INK if e else GRAPHITE, a * (1 if e else .75), anchor="c")
        if e:
            v = e[0]
            col = mix(e[2], AMBER, math.exp(-(t - e[1]) * 2.2))
            for k, bv in ((4, v >> 1), (5, v & 1)):
                cv.text(x0 + cols[k], y, str(bv), F_MONO_M, 15, col, a,
                        anchor="c")
        else:
            for k in (4, 5):
                cv.text(x0 + cols[k], y, "·", F_MONO, 15, DIM, a * 1.5,
                        anchor="c")
    # step 3: the two branches write different values into the same row
    aa = 0.0   # v4: X1/X2 tags removed (too brief); the step marker carries it
    if aa > 0:
        cv.text(x0 + 306, prow_y(3), "X1", F_MONO_M, 13, TEAL, aa)
        cv.text(x0 + 306, prow_y(3) + 13, "X2→01", F_MONO_M, 11, AMBER,
                aa * smooth(seg(t, T_X2 + .55, T_X2 + .8)))
        cv.text(x0 + 306, prow_y(1), "X2", F_MONO_M, 13, AMBER,
                aa * smooth(seg(t, T_X2 + .55, T_X2 + .8)))
    ia = a * window(t, T_CPATH + .45, T_CUT + .4, .2, .3)
    if ia > 0:
        cv.text(x0 + 306, prow_y(13), "infer", F_MONO_M, 12, AMBER, ia)
    ca = a * window(t, T_CONF + .1, T_PIP + .2, .15, .35)
    if ca > 0:
        y = prow_y(15)
        cv.rrect(x0 - 18, y - 18, 342, 24, 5, CORAL, ca, fill=CORAL, fa=.16,
                 lw=2)
        xmark(cv, (x0 + 256, y - 5), 13, CORAL, ca * .95, 2.2)
        cv.text(x0 + 140, y + 28, "needs 10 · entry conflict", F_MONO_M, 14,
                CORAL, ca, anchor="c")
    # tethers: the node and the row it writes
    for (ij, r, ta, tb, col) in TETHERS:
        ta_ = a * window(t, ta, tb, .12, .3)
        if ta_ <= 0 or ij not in node_px:
            continue
        p0 = node_px[ij]
        p1 = (x0 - 22, prow_y(r) - 6)
        pr = ocub(seg(t, ta, ta + .3))
        mid = ((p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 40)
        pts = [bez(p0, lerp2(p0, mid, .8), lerp2(p1, mid, .6), p1, j / 40 * pr)
               for j in range(41)]
        cv.poly(pts, col, ta_ * .85, 1.6)
        cv.circle(p0, 4, None, ta_, fill=col)
        if pr > .95:
            cv.circle(p1, 4, None, ta_, fill=col)


def scene_stage(cv, t):
    if t < T_STAGE - .05 or t > T_PIP + .7:
        return
    cam = stage_cam(t)
    A = smooth(seg(t, T_STAGE - .05, T_STAGE + .3)) * \
        (1 - smooth(seg(t, T_PIP - .05, T_PIP + .45)))
    lift = io3(seg(t, T_LIFT0, T_LIFT1))
    floor_a = A * lerp(1.0, .34, smooth(seg(t, T_LIFT0 - .3, T_LIFT1)))
    c = cv.c
    # ---------------- floor: the Reference Behavior Graph -----------------
    hl_edges = {}
    if T_TOK0 - .05 < t < T_TILT + .3:            # replay path stays lit
        k, f = tok_state(t)
        hold = 1 - smooth(seg(t, T_TILT, T_TILT + .3))
        for j in range(k + 1):
            if j < k or f > .02:
                hl_edges[(TOKEN_PATH[j], TOKEN_PATH[j + 1])] = (TEAL, hold)
    if T_ANT2 - .05 < t < T_RETRACT + .6:
        hl_edges[((1, 0), (0, 0))] = (TEAL, window(t, T_ANT2, T_RETRACT + .6,
                                                   .3, .3))
    for lt, e in zip(LINK_T, [((1, 0), (3, 0)), ((0, 0), (2, 0)),
                              ((2, 0), (0, 0))]):
        if lt - .05 < t < lt + .5:
            hl_edges[e] = (TEAL, window(t, lt - .05, lt + .5, .08, .25))
    if T_ANT4 - .1 < t < T_CUT + .5:
        hl_edges[((2, 0), (3, 1))] = (AMBER, window(t, T_ANT4, T_CUT + .5,
                                                    .3, .3))
    for k, (a, b, rising, chq) in enumerate(RBG_EDGES):
        prog = io3(seg(t, T_EDGE[k], T_EDGE[k] + .3))
        if prog <= 0:
            continue
        g = edge_geom(a, b)
        pts = [bez(*g, j / 40) for j in range(41)]
        col = AMBER if rising else GRAPHITE
        foc = min(pill_focus(a, t), pill_focus(b, t))
        al = floor_a * (.95 if rising else .75) * foc
        hcol = hl_edges.get((a, b))
        w = 2.6 if chq else 1.8
        if hcol:
            col = mix(col, hcol[0], hcol[1])
            al = max(al, A * hcol[1])
            w += 1.6 * hcol[1]
        draw_proj_path(cv, cam, pts, 0.0, col, al, w, prog)
    # replay markers (same identity as Act I's transition markers)
    if T_TOK0 < t < T_TILT + .3:
        k, f = tok_state(t)
        ma = A * (1 - smooth(seg(t, T_TILT, T_TILT + .3)))
        for j in range(6):
            if j > k or (j == k and f < .55):
                continue
            a_, b_ = TOKEN_PATH[j], TOKEN_PATH[j + 1]
            g = edge_geom(a_, b_)
            mp = bez(*g, .5)
            if (b_, a_) in EDGE_SET and RN[a_][1] == RN[b_][1]:
                mp = (mp[0], mp[1] + (-24 if RN[b_][0] > RN[a_][0] else 24))
            x, y, sc, _ = cam.P((mp[0], mp[1], 0))
            pop = oback(seg(t, T_TOK0 + (j + .55) * T_TOKD,
                            T_TOK0 + (j + .9) * T_TOKD))
            marker(cv, (x, y - (0 if (b_, a_) in EDGE_SET and RN[a_][1] ==
                                 RN[b_][1] else 22) * sc), j + 1,
                   ma * clamp(pop),
                   AMBER if j == 4 else DIM, BG_OUT if j == 4 else INK,
                   r=14 * sc * pop, size=15 * sc)
    # ghost edge for the rejected candidates: (01,Q0) -> (00,Q1) is not in A×R
    ga = A * window(t, T_REJ, T_S3 + .05, .3, .3)
    if ga > 0:
        p0, p1 = RN[(1, 0)], RN[(0, 1)]
        pts = [lerp2(p0, p1, j / 30) for j in range(31)]
        pts = [p for p in pts if math.dist(p, p0) > 54 and math.dist(p, p1) > 56]
        P = draw_proj_path(cv, cam, pts, 0.0, CORAL, ga * .85, 1.8, dash=True)
        if P:
            m = P[len(P) // 2]
            sc = cam.P((*lerp2(p0, p1, .5), 0))[2]
            xmark(cv, m, 9 * sc ** .8, CORAL, ga, 2.2)
            cv.text(m[0] - 16 * sc, m[1] + 24 * sc, "no reference edge",
                    F_UI_M, 12 * sc, CORAL, ga, anchor="r")
    # floor nodes
    for k in NODE_ORDER:
        pop = oback(seg(t, T_NODE[k], T_NODE[k] + .4))
        if pop <= 0:
            continue
        u, v = RN[k]
        x, y, sc, _ = cam.P((u, v, 0))
        r = lerp(52, 38, lift) * sc * pop
        fa_ = floor_a * pill_focus(k, t)
        cv.circle((x, y), r, INK, fa_, fill=BG_IN, fa=.96, w=sw(sc, 2))
        la = fa_ * clamp(pop) * (1 - smooth(seg(t, T_LIFT0 - .3, T_LIFT1)))
        cv.text(x, y - 12 * sc, "D CK Q", F_UI, 11 * sc, GRAPHITE, la,
                anchor="c")
        cv.text(x, y + 14 * sc, f"{k[0] >> 1} {k[0] & 1} {k[1]}",
                F_MONO_M, 19 * sc, INK, la, anchor="c")
    # the replay token and its consequence
    if T_TOK0 - .05 < t < T_TILT + .3:
        tp = tok_pos(t)
        x, y, sc, _ = cam.P((tp[0], tp[1], 0))
        ta = window(t, T_TOK0 - .05, T_TILT + .3, .15, .3) * A
        cv.glow_dot((x, y), 40 * sc, TEAL, .8 * ta)
        cv.circle((x, y), 7 * sc, None, ta, fill=TEAL)
        ea = A * window(t, T_TOK1 - .05, T_TILT + .3, .2, .3)
        if ea > 0:
            u, v = RN[(1, 1)]
            x, y, sc, _ = cam.P((u, v, 0))
            cv.circle((x, y), 60 * sc, BLUE, ea, w=sw(sc, 2.4))
            cv.text(x, y + 96 * sc, "reference: Q = 1", F_MONO_M, 22 * sc,
                    BLUE, ea, anchor="c")
            cv.text(x, y + 126 * sc, "SeGen-20 output: Q = 0", F_MONO_M,
                    22 * sc, CORAL, ea * smooth(seg(t, T_TOK1 + .2,
                                                    T_TOK1 + .45)),
                    anchor="c")
    # ---------------- lift: each reference node splits into its states ----
    node_px = {}
    if lift > 0:
        pa = A * smooth(seg(t, T_LIFT0, T_LIFT0 + .25))
        for k in NODE_ORDER:
            u, v = RN[k]
            fk = pill_focus(k, t)
            h = H_E * lift
            w = lerp(104, 182, lift)
            hh = lerp(104, 80, lift)
            r = lerp(52, 40, lift)
            pr = A * lerp(.55, .2, smooth(seg(t, T_CALL, T_PANEL + .5))) * fk
            for du in (-w / 2 + r * .6, w / 2 - r * .6):
                P0 = cam.P((u + du, v, 0))
                P1 = cam.P((u + du, v, h))
                cv.line(P0[:2], P1[:2], GRAPHITE, pr * lift, 1.0, [3, 4])
            P, sc = proj_path(cam, pill_outline(u, v, w, hh, r), h)
            cv.poly(P, mix(INK, GRAPHITE, lift), pa * .9 * fk, sw(sc, 1.6),
                    close=True, fill=BG_IN, fa=.95)
            la = pa * smooth(seg(t, T_SLOT - .1, T_SLOT + .3)) * fk
            bb_text(cv, cam, (u - w / 2 + 12, v - hh / 2 - 12, h), 0, 0,
                    f"(D,CK)={k[0] >> 1}{k[0] & 1}  Q={k[1]}", F_MONO, 12,
                    GRAPHITE, la, anchor="l")
        sa = A * smooth(seg(t, T_SLOT, T_SLOT + .45))
        for k in NODE_ORDER:
            i, o = k
            fk = pill_focus(k, t)
            for s in range(4):
                if lam(s) != o:
                    continue
                u, v = slot_uv(i, s)
                x, y, sc, _ = cam.P((u, v, H_E * lift))
                node_px[(i, s)] = (x, y)
                st = node_style(i, s, t)
                if st is None or st[0] < .99:
                    c.new_path()
                    c.arc(x, y, 25 * sc, 0, 2 * math.pi)
                    cv.rgba(GRAPHITE, sa * .7 * fk)
                    c.set_line_width(sw(sc, 1.2))
                    c.set_dash([3 * sc, 4 * sc])
                    c.stroke()
                    c.set_dash([])
                    cv.text(x, y + 6 * sc, bits(s, 2), F_MONO, 16 * sc,
                            GRAPHITE, sa * .8 * fk, anchor="c")
        # callout: what the split means, on one node
        ca = A * window(t, T_CALL, T_S1 + .2, .3, .3)
        if ca > 0:
            wp = (RN[(1, 0)][0], RN[(1, 0)][1], H_E)
            chip(cv, cam, wp, -88, -84, "Q = 0  →  states with ¬s1 = 0 : "
                 "01, 11", TEAL, ca, size=13)
            wp = (RN[(1, 1)][0], RN[(1, 1)][1], H_E)
            chip(cv, cam, wp, -88, 76, "Q = 1  →  states with ¬s1 = 1 : "
                 "00, 10", TEAL, ca * smooth(seg(t, T_CALL + .2,
                                                 T_CALL + .45)), size=13)
    if t < T_S1:
        draw_panel(cv, t, node_px)
        stage_hud(cv, t)
        return

    ia = A
    # ---------------- step 2: the four proposed destinations ---------------
    for k, (s2, status) in enumerate(CANDS):
        tp = T_CAND[k]
        pr = io3(seg(t, tp, tp + .35))
        bad = status == "wrong output"
        if bad:
            kill = seg(t, T_REJ, T_REJ + .35)
            ret = io3(seg(t, T_RETRACT, T_RETRACT + .5))
            a_ = ia * (1 - smooth(seg(t, T_RETRACT + .35, T_RETRACT + .55)))
            col = mix(INK, CORAL, kill)
            pr = pr * (1 - ret)
        else:
            a_ = ia * (1 - smooth(seg(t, T_X1 - .2, T_X1 + .1)))
            col = INK
        if t > T_X1 + .2 and not bad:
            continue
        draw_proj_path(cv, cam, est_pts(INIT, (0, s2)), H_E, col, a_ * .9,
                       1.8, pr, dash=True)
    # ---------------- step 3: X1 / X2 --------------------------------------
    if t > T_X1:
        x1 = io3(seg(t, T_X1, T_X1 + .45))
        dimc = 1 - .6 * window(t, T_ANT4, T_CUT + .6, .3, .3)
        draw_proj_path(cv, cam, est_pts(INIT, (0, 3)), H_E, TEAL, ia * dimc,
                       2.4, x1)
    if T_X2 < t < LINK_T[2] + .2:
        x2a = ia * (1 - .7 * smooth(seg(t, T_FOLLOW, T_FOLLOW + .3)))
        pts = est_pts((0, 3), (0, 1))
        pr = io3(seg(t, T_X2, T_X2 + .55))
        draw_proj_path(cv, cam, pts, H_E, AMBER, x2a, 2.2, pr)
        if 0 < pr < .99:
            dp = path_point(pts, pr)
            x, y, sc, _ = cam.P((dp[0], dp[1], H_E))
            cv.glow_dot((x, y), 30 * sc, AMBER, .7 * x2a)
    # ---------------- step 4a: X1 branch, fast-forwarded -------------------
    for idx, (L, lt) in enumerate(zip(CHAIN[1:], LINK_T)):
        if t < lt:
            continue
        i, s, j, s2 = L["edge"]
        path = L["path"]
        lift_arc = 0 if idx == 1 else -30
        if idx == 0:          # L1 fixed δ(11,11) = 11: re-lit at the conflict
            glow = window(t, T_CONF, T_CUT + .5, .15, .35)
            dim = 1 - .5 * window(t, T_ANT4, T_CUT + .6, .3, .3) * (1 - glow)
            col = mix(INK, TEAL, glow)
            P = draw_proj_path(cv, cam, est_pts((i, s), (j, s2), lift_arc),
                               H_E, col, ia * .9 * dim, 2.0 + 1.2 * glow,
                               io3(seg(t, lt, lt + .28)))
            if glow > 0 and P:
                cv.glow_dot(P[len(P) // 2], 40 * cam.P((*slot_uv(j, s2),
                                                        H_E))[2] ** .7,
                            TEAL, .45 * glow)
            continue
        dim = 1 - .7 * window(t, T_ANT4, T_CUT + .6, .3, .3)
        if len(path) == 1:
            draw_proj_path(cv, cam, est_pts((i, s), (j, s2), lift_arc), H_E,
                           INK, ia * .9 * dim, 2.0, io3(seg(t, lt, lt + .28)))
        else:
            draw_proj_path(cv, cam, est_pts((i, s), (j, path[0]), lift_arc),
                           H_E, INK, ia * .7 * dim, 1.8,
                           io3(seg(t, lt, lt + .2)), dash=True)
            draw_proj_path(cv, cam, est_pts((j, path[0]), (j, s2)), H_E, INK,
                           ia * .9 * dim, 2.0, io3(seg(t, lt + .15, lt + .3)))
    # ---------------- step 4b: the contradiction (slow) ---------------------
    if t > T_CPATH:
        i, s, j, s2 = CONF["edge"]
        cp = CONF["path"]                       # 01 -> 11 -> 10 under (1, 1)
        ret = io3(seg(t, T_CUT, T_CUT + .45))
        ca = ia * (1 - smooth(seg(t, T_CUT + .3, T_CUT + .55)))
        segs = [((i, s), (j, cp[0]), T_CPATH, .45, True),
                ((j, cp[0]), (j, cp[1]), T_CPATH + .5, .45, False),
                ((j, cp[1]), (j, cp[2]), T_CPATH + 1.0, .5, True)]
        for k, (a_, b_, ts, du, dash) in enumerate(segs):
            pr = io3(seg(t, ts, ts + du)) * (1 - ret)
            col = CORAL if k == 2 else AMBER
            pts = est_pts(a_, b_)
            draw_proj_path(cv, cam, pts, H_E, col, ca, 2.4, pr, dash=dash)
            if 0 < pr < .99:
                dp = path_point(pts, pr)
                x, y, sc, _ = cam.P((dp[0], dp[1], H_E))
                cv.glow_dot((x, y), 34 * sc, col, .8 * ca)

    # ---------------- ESTG nodes -------------------------------------------
    for k in NODE_ORDER:
        i, o = k
        fk = pill_focus(k, t)
        for s in range(4):
            if lam(s) != o:
                continue
            st = node_style(i, s, t)
            if st is None:
                continue
            al, ring, lc = st
            u, v = slot_uv(i, s)
            x, y, sc, _ = cam.P((u, v, H_E))
            pop = oback(seg(t, T_INIT, T_INIT + .4)) if (i, s) == INIT else 1.0
            cv.circle((x, y), 25 * sc * pop, ring, ia * al * fk, fill=BG_IN,
                      fa=.97, w=sw(sc, 2.4))
            cv.text(x, y + 6 * sc, bits(s, 2), F_MONO_M, 17 * sc, lc,
                    ia * al * fk, anchor="c")
    sf = pill_focus((1, 0), t)
    stable_mark(cv, cam, INIT, TEAL, ia * sf * smooth(seg(t, T_INIT + .3,
                                                         T_INIT + .6)))
    stable_mark(cv, cam, (0, 3), TEAL,
                ia * pill_focus((0, 0), t) *
                smooth(seg(t, T_X1 + .4, T_X1 + .7)) *
                (1 - smooth(seg(t, LINK_T[1], LINK_T[1] + .15))))
    stable_mark(cv, cam, (3, 3), TEAL,
                ia * smooth(seg(t, LINK_T[0] + .25, LINK_T[0] + .45)))
    stable_mark(cv, cam, (2, 1), TEAL,
                ia * smooth(seg(t, LINK_T[1] + .3, LINK_T[1] + .45)))
    stable_mark(cv, cam, (0, 1), TEAL, ia * pill_focus((0, 0), t) *
                smooth(seg(t, LINK_T[2] + .3, LINK_T[2] + .45)))
    if t >= T_INIT:
        g = math.exp(-max(0, t - T_INIT - .1) * 1.6)
        x, y, sc, _ = cam.P((*slot_uv(*INIT), H_E))
        cv.glow_dot((x, y), 70 * sc, TEAL, .4 * g * ia)
    # ---------------- in-world annotations --------------------------------
    la = ia * window(t, T_INIT + .25, T_S2 + .45, .3, .25)
    bb_text(cv, cam, (*slot_uv(*INIT), H_E), 0, -94, "s = 11 · Q = ¬s1 = 0",
            F_MONO_M, 13, INK, la)
    bb_text(cv, cam, (*slot_uv(*INIT), H_E), 0, -74, "stable: δ(01, 11) = 11",
            F_MONO, 12, TEAL, la)
    aa2 = ia * window(t, T_ANT2, T_RETRACT + .5, .3, .3)
    fp = lerp2(RN[(1, 0)], RN[(0, 0)], .5)
    bb_text(cv, cam, (fp[0], fp[1] + 34, 0), 0, 0, "CK falls → Q must stay 0",
            F_UI_M, 17, TEAL, aa2)
    ra = ia * window(t, T_REJ, T_S3 + .05, .2, .25)
    for s2 in (0, 2):
        bb_text(cv, cam, (*slot_uv(0, s2), H_E), 0, 50, "Q = 1", F_MONO_M, 13,
                CORAL, ra)
    bb_text(cv, cam, (*RN[(0, 1)], H_E), -10, 92,
            "wrong output → branch pruned", F_UI_M, 17, CORAL, ra)
    xa = 0.0 * window(t, T_X1 + .3, T_S4 + .3, .2, .3)
    bb_text(cv, cam, (*slot_uv(0, 3), H_E), 0, -62, "X1  stays at 11",
            F_MONO_M, 13, TEAL, xa)
    xa2 = 0.0 * window(t, T_X2 + .45, T_S4 + .3, .2, .3)
    bb_text(cv, cam, (*slot_uv(0, 1), H_E), -30, 64, "X2  11 → 01",
            F_MONO_M, 13, AMBER, xa2)
    ka = 0.0   # v4: carried by the step marker (readable for the whole step)
    bb_text(cv, cam, (*RN[(0, 0)], H_E), 0, 96,
            "no contradiction → both branches kept", F_UI_M, 13, TEAL, ka)
    # conflict: anticipation, then the two δ values that cannot both hold
    aa4 = ia * window(t, T_ANT4, T_CUT + .5, .3, .3)
    fp = lerp2(RN[(2, 0)], RN[(3, 1)], .42)
    bb_text(cv, cam, (fp[0] + 20, fp[1], 0), 0, 0,
            "CK rises with D = 1 → Q must become 1", F_UI_M, 13, AMBER, aa4,
            anchor="l")
    wp = (*slot_uv(3, 3), H_E)
    cn = ia * window(t, T_CPATH + 1.15, T_PIP, .2, .3)
    chip(cv, cam, wp, -150, -66, "path needs δ(11,11) = 10", CORAL, cn,
         size=12)
    cs = ia * window(t, T_CONF, T_PIP, .2, .3)
    chip(cv, cam, wp, -150, -108, "earlier edge fixed δ(11,11) = 11", TEAL,
         cs, size=12)
    if cs > 0:
        x, y, sc, _ = cam.P(wp)
        fl = math.exp(-max(0, t - T_CONF - .2) * 3.0)
        cv.glow_dot((x, y), 90 * sc, CORAL, .5 * fl * cs + .12 * cs)
        cv.text(x - 166 * sc, y - 80 * sc, "≠", F_UI_M, 22 * sc, CORAL, cs,
                anchor="c")
    ia2 = ia * window(t, T_CPATH + .45, T_CUT + .3, .2, .3)
    bb_text(cv, cam, (*slot_uv(3, 1), H_E), 0, 50, "infer δ(11,01) = 11",
            F_MONO, 12, AMBER, ia2)
    da = ia * window(t, T_CUT, T_PIP, .2, .3)
    bb_text(cv, cam, (*slot_uv(3, 2), H_E), 0, -72, "branch pruned",
            F_UI_M, 15, CORAL, da)
    draw_panel(cv, t, node_px if t < T_PIP else {})
    stage_hud(cv, t)


@overlay
def stage_hud(cv, t):
    a = window(t, T_STAGE + .2, T_TILT + .1, .4, .4)
    a2k = window(t, T_TILT + .3, T_S1 + .1, .4, .4)
    cv.rrect(100, 120, 1120, 146, 10, fill=PAPER, fa=.88 * max(a, a2k))
    cv.text(120, 172, "Reference Behavior Graph", F_TITLE_L, 44, INK, a)
    cv.text(120, 210, "the complete specification of a positive-edge "
            "D flip-flop", F_UI_L, 22, GRAPHITE, a)
    al = window(t, T_STAGE + 1.0, T_TILT + .1, .4, .4)
    cv.text(120, 248, "node = (D, CK, Q)   ·   edge = one input pin changes   "
            "·   amber = rising clock edge, the only edge that may change Q",
            F_MONO, 15, GRAPHITE, al)
    a2 = window(t, T_TILT + .3, T_S1 + .1, .4, .4)
    cv.text(120, 172, "Candidate ESTG, lifted above the reference", F_TITLE_L,
            40, INK, a2)
    cv.text(120, 208, "slots for stable input–state pairs (i, s), each over the "
            "reference node (i, λ(s)), with λ(s) = ¬s1", F_UI_L, 21, GRAPHITE,
            a2)
    caption(cv, t, T_STAGE + .2, T_TOK0 - .05,
            "The reference: every admissible input change, and the Q it must "
            "produce.",
            "Nodes: (D, CK, Q).  Edges: one input pin changes.  Q may change "
            "only on a rising clock edge (amber).")
    caption(cv, t, T_TOK0, T_TILT + .1,
            "Act I's test vector is just one path through this graph.",
            "Replayed here, the graph demands Q = 1 where SeGen-20 output 0. "
            "Every admissible input order is a path.")
    caption(cv, t, T_TILT + .45, T_S1 + .05,
            "A candidate edge is valid only if a reference edge lies beneath "
            "it.",
            "B-Flex grows the candidate's state graph (ESTG) one stable edge at "
            "a time and checks each edge against the floor.")
    caption(cv, t, T_S1 + .3, T_S2 + .05, "Start from a stable input–state pair.",
            "(D, CK) = (0, 1), s = 11, Q = 0.  Its table entry "
            "δ(01, 11) = 11 says: stay.", step="STEP 1")
    caption(cv, t, T_ANT2, T_S3 + .05,
            "Destination discovery: CK falls, so the reference demands Q "
            "stays 0.",
            "All four states are proposed. The two that output Q = 1 have no "
            "reference edge beneath them: those branches are pruned.",
            step="STEP 2")
    caption(cv, t, T_S3 + .4, T_S4B + .1,
            "Transition instantiation: infer the δ entries for each choice.",
            "X1 stays at 11.  X2 passes 11 and settles at 01.  Neither "
            "contradicts δ, so both branches continue.", step="STEPS 3–4")
    caption(cv, t, T_S4 + .25, T_S4B + .1,
            "The same check repeats, edge after edge.",
            "Following X1: three more stable edges, each over a reference "
            "edge (fast-forward).")
    caption(cv, t, T_ANT4, T_PIP + .05,
            "Entry conflict: a contradiction prunes the branch and everything "
            "beneath it.",
            "Depth 5: CK rises with D = 1. The path 01 → 11 → 10 must leave "
            "(11, 11), but an earlier edge fixed δ(11, 11) = 11.",
            step="STEP 5")
    tag(cv, t, T_STAGE + .2, T_S1, "§3.1 · Fig. 1A, 1B · Fig. 2 vector")
    tag(cv, t, T_S1 + .5, T_PIP, "§3.2 · steps 1–3 as in Fig. 4 · steps 4–5 "
        "recomputed with the method")
    act_label(cv, t, T_STAGE, T_S1, "02", "THE IDEA")
    act_label(cv, t, T_S1, T_CELLS0, "03", "INSIDE THE ALGORITHM")


# ============================================== the real search tree ========
TREE = DATA["tree"]
TN = TREE["nodes"]
TBY = {n["id"]: n for n in TN}
NT = len(TN)
WID = TREE["walk_ids"]
WALK_IDS = set([WID["root"], WID["conflict"]] + WID["cands"] + WID["chain"])
_rest = [n for n in TN if n["id"] not in WALK_IDS]
GROW_T = {n["id"]: T_GROW0 + (T_GROW1 - T_GROW0) * (j / len(_rest)) ** .9
          for j, n in enumerate(_rest)}
PIP_C, PIP_RU = (1640.0, 902.0), 22.0


def walk_node_state(nid, t):
    """(appear time, colour) for the walkthrough nodes, mirroring the stage."""
    if nid == WID["root"]:
        return T_ANT2 - .2, INK
    if nid in WID["cands"]:
        k = WID["cands"].index(nid)
        bad = CANDS[k][1] == "wrong output"
        col = GRAPHITE
        if bad and t > T_REJ:
            col = CORAL
        if not bad and t > (T_X1 if k == 3 else T_X2):
            col = TEAL
        return T_CAND[k] + .1, col
    if nid in WID["chain"]:
        k = WID["chain"].index(nid)
        if k == 0:
            return T_CAND[3] + .1, TEAL if t > T_X1 else GRAPHITE
        return LINK_T[k - 1] + .2, TEAL
    if nid == WID["conflict"]:
        return T_CPATH + .3, CORAL if t > T_CONF else AMBER
    return 1e9, INK


def tree_geom(t):
    """centre, radial unit, rotation, alpha, mode."""
    if t < T_PIP:
        return PIP_C, PIP_RU, 0.0, smooth(seg(t, T_ANT2 - .4, T_ANT2)), "pip"
    e = ocub(seg(t, T_PIP - .1, T_PIP + .6))
    C = lerp2(PIP_C, (930, 530), e)
    RU = math.exp(lerp(math.log(PIP_RU), math.log(64), e))
    e2 = io3(seg(t, T_PIP + .6, T_GROW1 + .3))
    RU = math.exp(lerp(math.log(RU), math.log(31.5), e2))
    rot = .045 * max(0, t - T_PIP - .6)
    a = 1 - smooth(seg(t, T_CELLS0 + .1, T_CELLS0 + .6))
    return C, RU, rot, a, "full"


def tree_xy(n, C, RU, rot):
    r = n["depth"] * RU
    a = n["theta"] + rot
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


@overlay
def scene_tree_hud(cv, t):
    scene_tree(cv, t)


def scene_tree(cv, t):
    if t < T_ANT2 - .45 or t > T_CELLS0 + 1.0:
        return
    C, RU, rot, A, mode = tree_geom(t)
    if mode == "pip":
        cv.shadow(PIP_C[0] - 150, PIP_C[1] - 120, 300, 222, 14, A)
        cv.rrect(PIP_C[0] - 150, PIP_C[1] - 120, 300, 222, 14, DIM,
                 A, fill=PAPER, fa=.97, lw=1.1)
        cv.text(PIP_C[0] - 136, PIP_C[1] - 97, "SEARCH TREE", F_MONO, 12,
                GRAPHITE, A, track=.16)
    else:
        pa = A * (1 - smooth(seg(t, T_PIP, T_PIP + .4)))
        if pa > 0:
            cv.rrect(PIP_C[0] - 150, PIP_C[1] - 120, 300, 222, 14, GRAPHITE,
                     pa * .5, lw=1.1)
    vcount = pruned = 0
    dots = []
    for n in TN:
        if n["parent"] is None:
            continue
        nid = n["id"]
        if nid in WALK_IDS:
            ta, wcol = walk_node_state(nid, t)
        else:
            if mode == "pip":
                continue
            ta, wcol = GROW_T[nid], None
        if t < ta:
            continue
        p = TBY[n["parent"]]
        P0, P1 = tree_xy(p, C, RU, rot), tree_xy(n, C, RU, rot)
        pr = ocub(seg(t, ta, ta + .22))
        st = n["status"]
        if wcol is not None:
            cut = nid == WID["conflict"] and t > T_CUT
            ln = .55 if wcol == CORAL else 1.0
            al = A * (.5 if cut else 1.0)
            cv.line(P0, lerp2(P0, P1, pr * ln), wcol, al,
                    2.0 if mode == "pip" else 1.6)
            if pr > .9:
                dots.append((lerp2(P0, P1, ln), wcol, al))
            if nid == WID["conflict"] and t > T_CONF:
                q = lerp2(P0, P1, ln)
                fl = math.exp(-max(0, t - T_CONF) * 2)
                cv.glow_dot(q, 26, CORAL, (.3 + .5 * fl) * A)
                if mode == "full":
                    cv.circle(q, 10, CORAL, A * window(t, T_PIP, T_GROW1, .3,
                                                       .5), w=1.6)
            if st in ("wrong output", "entry conflict"):
                pruned += 1
            continue
        if st in ("wrong output", "entry conflict"):
            pruned += 1
            fade = seg(t, ta + .22, ta + .8)
            cv.line(P0, lerp2(P0, P1, pr * (1 - .55 * fade)), CORAL,
                    A * (.75 - .55 * fade), 1.1)
        else:
            col = TEAL if st == "valid" else INK
            cv.line(P0, lerp2(P0, P1, pr), col,
                    A * (.85 if st == "valid" else .42), 1.3)
            if st == "valid" and pr > .9:
                vcount += 1
                if t < T_CELLS0:
                    cv.glow_dot(P1, 26, TEAL, .55 * A)
                    cv.circle(P1, 4, None, A, fill=TEAL)
    for (q, col, al) in dots:
        cv.circle(q, 3.4, None, al, fill=col)
    cv.circle(C, 4.5, None, A, fill=INK)
    if mode == "full":
        ca = A * smooth(seg(t, T_PIP + .5, T_PIP + .9))
        cv.text(1500, 420, f"{vcount:>2d}", F_TITLE_L, 120, TEAL, ca)
        cv.text(1500, 462, "valid 2-bit-state FSMs", F_UI_L, 24, INK, ca)
        cv.text(1500, 530, f"{pruned:>3d}", F_MONO_L, 40, CORAL, ca * .9)
        cv.text(1590, 530, "pruned branches", F_UI_L, 20, GRAPHITE, ca)
        st = TREE["stats"]
        cv.text(1500, 558, f"{st['wrong output']} wrong output · "
                f"{st['entry conflict']} entry conflict", F_MONO, 14,
                GRAPHITE, ca)
        cv.text(1500, 582, f"{st['non-convergence']} non-convergence · "
                f"{NT} nodes · depth {TREE['max_depth']}", F_MONO, 14,
                GRAPHITE, ca)
        cv.text(1500, 610, "circled: the step-5 conflict", F_UI_L, 15,
                CORAL, ca * window(t, T_PIP + .5, T_GROW1 + .8, .3, .5))
        sa = A * smooth(seg(t, T_GROW1 - .1, T_GROW1 + .3))
        cv.text(1500, 660, "2-bit runtime (Table 1)", F_MONO, 15, GRAPHITE, sa)
        cv.text(1500, 700, "brute force 162 s  →  B-Flex 0.00784 s", F_UI, 22,
                INK, sa)
        cv.text(1500, 748, "2.07 × 10^{4}× faster", F_UI_M, 30, TEAL, sa)
        caption(cv, t, T_PIP + .6, T_CELLS0 + .1,
                "Repeated over the whole space: the complete 2-bit search.",
                "18 valid FSMs.  Brute force 162 s → B-Flex 0.00784 s "
                "(2.07 × 10^{4}×, Table 1).")
        tag(cv, t, T_PIP + .6, T_CELLS0, "Table 1 · tree recomputed with the "
            "method")


# ================================ ACT IV: 1 cell = 1 valid FSM ==============
SQ_W, SQ_R, SQ_LAST = 23850, 23850, 9554
N3 = SQ_W * SQ_R + SQ_LAST
assert N3 == 568832054
FILL = .80
_IY = np.arange(SQ_R + 1, dtype=np.float64)
_WROW = np.full(SQ_R + 1, SQ_W, dtype=np.float64)
_WROW[-1] = SQ_LAST
BLOCK = [(-8 + (j % 6), j // 6) for j in range(18)]     # 2-bit block cells


def count_R(R):
    r2 = R * R - (_IY + .5) ** 2
    n = np.where(r2 >= .25, np.floor(np.sqrt(np.maximum(r2, 0)) - .5) + 1, 0)
    return int(np.minimum(n, _WROW).sum())


def fill_R(t):
    g = seg(t, T_FILL0, T_FILL1)
    if g <= 0:
        return 0.0
    return .6 * math.exp(math.log(34000 / .6) * g ** 2.6)


def unit_cam(t):
    R = fill_R(t)
    Rc = min(R, 23851.0)
    s = 470.0 / (.5 * Rc + 10.2) * \
        lerp(1, 400 / 470, smooth(clamp(Rc / 23851.0) ** .5))
    w = clamp(Rc / 14.0) ** .8
    ux, uy = lerp(-5.0, Rc * .5, w), lerp(1.5, Rc * .5, w)
    e1 = smooth(seg(t, T_FILL1 - 1.6, T_FILL1))
    ax, ay = lerp(960, 1250, e1), lerp(540, 545, e1)
    if t > T_FILL1:                                    # impact kick
        s *= 1 + .018 * math.exp(-(t - T_FILL1) * 7) * math.cos(
            (t - T_FILL1) * 30)
    e = io3(seg(t, T_HIST0, T_HIST0 + .8))
    if e > 0:
        s = math.exp(lerp(math.log(s), math.log(.0235), e))
        ax, ay = lerp(ax, 480, e), lerp(ay, 560, e)
    return ux, uy, s, ax, ay


def unit_S(t, u, v):
    ux, uy, s, ax, ay = unit_cam(t)
    return (ax + (u - ux) * s, ay + (v - uy) * s), s


def _F(x):
    fl = np.floor(x)
    return fl * FILL + np.clip(x - fl, 0, FILL)


def unit_layer(cv, t, alpha):
    """Exact, box-filtered rendering of the unit chart (numpy)."""
    if alpha <= 0.002:
        return None
    ux, uy, s, ax, ay = unit_cam(t)
    R = fill_R(t)
    k, W, H = cv.k, cv.W, cv.H

    def pxu(u):
        return (ax + (u - ux) * s) * k

    def pyv(v):
        return (ay + (v - uy) * s) * k
    x0, x1 = int(max(0, math.floor(pxu(-8.5)))), \
        int(min(W, math.ceil(pxu(SQ_W + 1))))
    y0, y1 = int(max(0, math.floor(pyv(-.5)))), \
        int(min(H, math.ceil(pyv(SQ_R + 1.5))))
    if x1 <= x0 or y1 <= y0:
        return None
    px = np.arange(x0, x1, dtype=np.float64)
    py = np.arange(y0, y1, dtype=np.float64)
    u0 = ux + (px / k - ax) / s
    u1 = ux + ((px + 1) / k - ax) / s
    v0 = uy + (py / k - ay) / s
    v1 = uy + ((py + 1) / k - ay) / s
    covx = ((_F(u1) - _F(u0)) / (u1 - u0)).astype(np.float32)
    covy = ((_F(v1) - _F(v0)) / (v1 - v0)).astype(np.float32)
    uc, vc = np.floor((u0 + u1) / 2), np.floor((v0 + v1) / 2)
    inx = (uc >= 0) & (uc < SQ_W)
    inx_last = (uc >= 0) & (uc < SQ_LAST)
    iny = (vc >= 0) & (vc < SQ_R)
    lastrow = vc == SQ_R
    A2 = (uc + .5) ** 2
    B2 = (vc + .5) ** 2
    d2 = B2[:, None] + A2[None, :]
    m = ((iny[:, None] & inx[None, :]) | (lastrow[:, None] & inx_last[None, :]))
    m &= d2 <= R * R
    cov = covy[:, None] * covx[None, :]
    band = max(R * .05, 1.2)
    fresh = np.exp(-np.clip(R - np.sqrt(d2), 0, None) / band).astype(np.float32)
    dimf = 1 - .45 * smooth(seg(t, T_FILL1 + .6, T_FILL1 + 1.1))
    inten = np.where(m, cov * (.46 + .5 * fresh), 0).astype(np.float32) * dimf
    bx = (uc >= -8) & (uc < -2)
    by = (vc >= 0) & (vc < 3)
    blk = (by[:, None] & bx[None, :]).astype(np.float32) * cov
    ba = smooth(seg(t, T_CELLS0 + .7, T_CELLS0 + .8))   # handover from leaves
    # v4: alpha-over on white (older cells light teal, the fresh front full)
    A = np.clip(inten + blk * ba, 0, 1) * alpha
    return A, x0, y0


def composite_region(cv, res):
    if res is None:
        return
    lay, x0, y0 = res
    cv.surf.flush()
    buf = np.ndarray((cv.H, cv.W, 4), np.uint8, cv.surf.get_data())
    h, w = lay.shape[:2]
    sub = buf[y0:y0 + h, x0:x0 + w]
    tc = [c * 255 for c in TEAL]
    for ch, src in ((2, 0), (1, 1), (0, 2)):
        v = sub[..., ch].astype(np.float32) * (1 - lay) + tc[src] * lay
        sub[..., ch] = np.clip(v + .5, 0, 255).astype(np.uint8)
    cv.surf.mark_dirty()


def unit_alpha(t):
    return smooth(seg(t, T_CELLS0 + .65, T_CELLS0 + .8)) * \
        (1 - smooth(seg(t, T_BLK0 + .1, T_BLK0 + .7)))


LEAVES = sorted([n for n in TN if n["status"] == "valid"],
                key=lambda n: n["theta"])
assert len(LEAVES) == 18


# breadcrumb: valid FSMs (behaviour) -> ... -> circuits (SPICE)
CRUMBS = [("valid FSMs", "behavior", TEAL, T_CELLS0 + .6, T_HIST0),
          ("468 simplest · C_FF ≤ 20", "behavior", TEAL, T_HIST0, T_BLK0),
          ("20 transistor-level circuits", "circuit", AMBER, T_BLK0,
           T_RACE_IN),
          ("FF1 vs. TGFF in SPICE", "circuit", AMBER, T_RACE_IN, T_FINAL)]


@overlay
def breadcrumb(cv, t):
    A = window(t, T_CELLS0 + .6, T_FINAL - .1, .5, .5)
    if A <= 0:
        return
    x = 420
    for k, (lab, kind, col, a, b) in enumerate(CRUMBS):
        on = window(t, a, b, .3, .3)
        past = t >= b
        c_ = mix(GRAPHITE, col, on)
        al = A * (1.0 if on > .01 else (.75 if past else .4))
        c_ = mix(mix(GRAPHITE, INK, .35), col, on)
        cv.text(x, 92, lab, F_MONO_M if on > .5 else F_MONO, 16, c_, al)
        cv.text(x, 114, kind, F_MONO, 12, mix(GRAPHITE, col, .6 * on),
                al * .95, track=.14)
        x += cv.measure(lab, F_MONO, 16) + 30
        if k < 3:
            cv.text(x - 21, 92, "▸", F_MONO, 16, GRAPHITE, A * .7)


def scene_unit(cv, t):
    if t < T_CELLS0 or t > T_BLK0 + .8:
        return
    if t < T_CELLS0 + .8:
        C, RU, rot, _, _ = tree_geom(T_CELLS0)
        for j, n in enumerate(LEAVES):
            f = io3(seg(t, T_CELLS0 + j * .02, T_CELLS0 + .62 + j * .02))
            p0 = tree_xy(n, C, RU, rot)
            u, v = BLOCK[j]
            p1, s = unit_S(t, u + FILL / 2, v + FILL / 2)
            p = lerp2(p0, p1, f)
            half = lerp(4, s * FILL / 2, f)
            cv.glow_dot(p, 26, TEAL, .5 * (1 - f * .6))
            cv.rrect(p[0] - half, p[1] - half, 2 * half, 2 * half,
                     lerp(half, 2, f), None, 1.0, fill=TEAL, fa=1)
    ua = unit_alpha(t)
    R = fill_R(t)
    bp, s = unit_S(t, -8, 0)
    la = window(t, T_CELLS0 + .6, T_FILL0 + 2.3, .3, .4)
    cv.text(bp[0], bp[1] - 22, "2-bit state", F_MONO, 16, AMBER, la,
            track=.16)
    cv.text(bp[0], bp[1] + 3 * s + 40, "18 valid FSMs", F_UI_L, 22, INK, la)
    cv.text(bp[0], bp[1] + 3 * s + 68, "1 cell = 1 valid FSM", F_MONO, 15,
            GRAPHITE, la)
    sq0, _ = unit_S(t, 0, 0)
    ta3 = window(t, T_FILL0 + .15, T_FILL0 + 1.6, .3, .4)
    cv.text(sq0[0], sq0[1] - 22, "3-bit state", F_MONO, 16, AMBER, ta3,
            track=.16)
    ca = ua * smooth(seg(t, T_FILL0 + .1, T_FILL0 + .4)) * \
        (1 - smooth(seg(t, T_HIST0, T_HIST0 + .4)))
    if ca > 0:
        n = count_R(R) if t < T_FILL1 else N3
        hit = math.exp(-max(0, t - T_FILL1) * 2.2) if t >= T_FILL1 else 0
        k = 1 + .08 * hit
        c = cv.c
        c.save()
        c.translate(120, 520)
        c.scale(k, k)
        cv.text(0, 0, f"{n:,}", F_MONO_L, 92, mix(INK, AMBER, hit), ca)
        c.restore()
        cv.text(120, 572, "valid 3-bit-state FF FSMs", F_UI_L, 26, INK, ca)
        cv.text(120, 610, "vs. 18 at 2-bit state", F_MONO, 17, TEAL,
                ca * smooth(seg(t, T_FILL1 + .5, T_FILL1 + .8)))
        cv.text(120, 662, "exhaustive search · 787 s · 16 threads (Table 1)",
                F_MONO, 16, GRAPHITE, ca * smooth(seg(t, T_FILL1 + .6,
                                                     T_FILL1 + .85)))
        cv.text(120, 688, "average of 5 runs · cell order is arbitrary",
                F_MONO, 14, GRAPHITE, ca * .8 * smooth(seg(t, T_FILL1 + .7,
                                                          T_FILL1 + .95)))
        cv.text(120, 714, "§4.1 search space: Q = ¬s2 · initial state 011 · "
                "≤ 1 bit flip per transition", F_MONO, 14, GRAPHITE,
                ca * .8 * smooth(seg(t, T_FILL1 + .7, T_FILL1 + .95)))
    if t > T_FILL0 + 1.5:
        p, s = unit_S(t, -5, 1.5)
        ma = ua * smooth(seg(t, T_FILL1 - 1.0, T_FILL1 - .2)) * \
            (1 - smooth(seg(t, T_HIST0, T_HIST0 + .4)))
        if s < 6 and ma > 0:
            cv.circle(p, 9, TEAL, ma, w=1.6)
            cv.line((p[0] - 12, p[1]), (p[0] - 46, p[1]), TEAL, ma * .8, 1.2)
            cv.text(p[0] - 54, p[1] + 6, "18", F_MONO_M, 18, TEAL, ma,
                    anchor="r")
    if t > T_FILL1 - .05:
        p0, _ = unit_S(t, 0, 0)
        p1, _ = unit_S(t, SQ_W, SQ_R + 1)
        pa = math.exp(-(t - T_FILL1) * 2.2) * \
            (1 - smooth(seg(t, T_HIST0, T_HIST0 + .4)))
        g = 1 + .04 * (1 - math.exp(-(t - T_FILL1) * 4))
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        w, h = (p1[0] - p0[0]) * g, (p1[1] - p0[1]) * g
        cv.rrect(cx - w / 2, cy - h / 2, w, h, 4, AMBER, pa, lw=2.5)
    tag(cv, t, T_CELLS0 + .6, T_HIST0, "§4.1 · Table 1 · 1 cell = 1 valid FSM "
        "(exact)")
    act_label(cv, t, T_CELLS0, T_FINAL, "04", "IMPACT")


# ---- 468 candidates (Fig. 5) -> 20 synthesized circuits -> FF1 -------------
H_CFF = DATA["hist"]["cff"]
H_CNT = DATA["hist"]["count"]
assert sum(H_CNT) == 468
HX0, HBP, HY0, HCP = 880, 104, 834, 12
_rng = random.Random(21)
CELLS468 = []
for _k, _c in enumerate(H_CNT):
    for _j in range(_c):
        CELLS468.append({"bar": _k, "j": _j,
                         "u": _rng.uniform(0, SQ_W), "v": _rng.uniform(0, SQ_R),
                         "te": T_HIST0 + .1 + _rng.random() * .4,
                         "tf": T_HIST0 + .35 + _rng.random() * .7})
_perm = list(range(468))
_rng.shuffle(_perm)
BLK_C = (1330.0, 520.0)
BCP = 13.0


def block_xy(p):
    return (BLK_C[0] + ((p % 18) - 8.5) * BCP,
            BLK_C[1] + ((p // 18) - 12.5) * BCP)


SAMPLE20 = _rng.sample(range(468), 20)
FF1_POS = min(SAMPLE20, key=lambda p: math.dist(block_xy(p), BLK_C))
DIVE_TGT = (960.0, 520.0)


def hist_xy(k, j):
    return (HX0 + k * HBP + (j % 7) * HCP + HCP / 2,
            HY0 - (j // 7) * HCP - HCP / 2)


def dive_xf(t, p):
    g = seg(t, T_DIVE0, T_DIVE1)
    if g <= 0:
        return p, 1.0
    pf = block_xy(FF1_POS)
    Z = math.exp(math.log(46.0) * g ** 2.2)
    c = lerp2(pf, DIVE_TGT, io3(g))
    return (c[0] + (p[0] - pf[0]) * Z, c[1] + (p[1] - pf[1]) * Z), Z


def scene_hist(cv, t):
    if t < T_HIST0 + .05 or t > T_DIVE1 + .3:
        return
    fade_rest = 1 - smooth(seg(t, T_DIVE0 + .3, T_DIVE1))
    ha = window(t, T_HIST0 + .85, T_BLK0 + .5, .4, .3)
    if ha > 0:
        cv.line((HX0 - 16, HY0 + 4), (HX0 + 9 * HBP - 10, HY0 + 4), GRAPHITE,
                ha, 1.2)
        for k in range(9):
            cv.text(HX0 + k * HBP + 42, HY0 + 32, str(H_CFF[k]), F_MONO, 16,
                    GRAPHITE, ha, anchor="c")
            top = HY0 - math.ceil(H_CNT[k] / 7) * HCP
            cv.text(HX0 + k * HBP + 42, top - 10, str(H_CNT[k]), F_MONO_M, 16,
                    INK, ha * smooth(seg(t, T_HIST0 + 1.3 + k * .04,
                                         T_HIST0 + 1.55 + k * .04)),
                    anchor="c")
        cv.text(HX0 + 4.5 * HBP - 10, HY0 + 70,
                "logic complexity C_FF (literals + product terms, min. SOP)",
                F_UI_L, 19, GRAPHITE, ha, anchor="c")
        cv.text(HX0, 330, "468", F_TITLE_L, 96, TEAL, ha)
        cv.text(HX0 + 190, 300, "valid FSMs with C_FF ≤ 20", F_UI_L, 24, INK,
                ha)
        cv.text(HX0 + 190, 330, "1 cell = 1 FSM", F_MONO, 15, GRAPHITE, ha)
    for idx, cel in enumerate(CELLS468):
        if t < cel["te"]:
            continue
        p_sq, _ = unit_S(t, cel["u"], cel["v"])
        ph = hist_xy(cel["bar"], cel["j"])
        f = io3(seg(t, cel["tf"], cel["tf"] + .7))
        mid = ((p_sq[0] + ph[0]) / 2, min(p_sq[1], ph[1]) - 160)
        p = bez(p_sq, lerp2(p_sq, mid, .7), lerp2(ph, mid, .7), ph, f) \
            if f < 1 else ph
        fb = io3(seg(t, T_BLK0 + (idx % 37) * .006,
                     T_BLK0 + .4 + (idx % 37) * .006))
        p = lerp2(p, block_xy(_perm[idx]), fb)
        p, Z = dive_xf(t, p)
        grow = smooth(seg(t, cel["te"], cel["te"] + .2))
        pos = _perm[idx]
        is20 = pos in SAMPLE20
        isff1 = pos == FF1_POS
        am = 0.0
        if is20:
            j20 = SAMPLE20.index(pos)
            am = smooth(seg(t, T_AMB0 + j20 * .012, T_AMB0 + .2 + j20 * .012))
        col = mix(TEAL, AMBER, am)
        a = (1.0 if isff1 else fade_rest) * \
            (1 - (smooth(seg(t, T_DIVE1 - .15, T_DIVE1 + .15)) if isff1
                  else 0))
        half = 5.2 * grow * Z
        if a <= 0.002 or half <= 0:
            continue
        if f < 1:
            cv.glow_dot(p, 16, TEAL, .35 * a * (1 - f))
        if am > 0:
            cv.glow_dot(p, 22 * max(1, Z ** .5), AMBER, .6 * am * a)
        cv.rrect(p[0] - half, p[1] - half, 2 * half, 2 * half,
                 min(1.5 * Z, half), None, a, fill=col, fa=.95 if am else .8)
    sa = window(t, T_AMB0 - .1, T_DIVE0 + .2, .25, .2)
    if sa > 0:
        bx, by = BLK_C
        cv.text(bx - 130, by + 200, "20 sampled → transistor-level schematics",
                F_UI_L, 20, INK, sa)
        cv.text(bx - 130, by + 226, "known 2-bit-state FFs excluded · 28 nm "
                "CMOS · SPICE", F_MONO, 14, GRAPHITE, sa)
        pf = block_xy(FF1_POS)
        cv.text(pf[0] + 14, pf[1] - 12, "FF1", F_MONO_M, 16, AMBER,
                sa * smooth(seg(t, T_AMB0 + .3, T_AMB0 + .5)))
    caption(cv, t, T_HIST0 + .35, T_BLK0,
            "Rank the valid FSMs by logic complexity; keep the simplest.",
            "C_FF counts literals and product terms of the minimum "
            "sum-of-products.  468 FSMs have C_FF ≤ 20.")
    caption(cv, t, T_BLK0 + .1, T_DIVE0 + .25,
            "20 of them become circuits.",
            "Sampled from the 468 (excluding known 2-bit-state FFs), "
            "synthesized to transistor-level schematics, simulated in SPICE.")
    tag(cv, t, T_HIST0 + .35, T_BLK0 + .4, "§4.2 · Fig. 5")
    tag(cv, t, T_BLK0 + .1, T_DIVE0 + .2, "§4.2 · §4.3")


# ---- FF1: the published transition table, replayed on its state cube -------
FF1 = DATA["ff1"]
TRAJ = FF1["traj"][:5]                      # ends on the capture (CK rises, D=1)


def ff1_state_at(t):
    s0 = 3
    for k, st in enumerate(TRAJ):
        ts, du = T_FF[k], D_FF[k]
        path = st["path"]
        if t < ts:
            return s0, s0, 0.0, k - 1
        hops = len(path) - 1
        if hops == 0 or t >= ts + du:
            s0 = path[-1]
            continue
        u = (t - ts) / du * hops
        h = min(int(u), hops - 1)
        return path[h], path[h + 1], io3(u - h), k
    return s0, s0, 0.0, len(TRAJ) - 1


def ff1_cam(t):
    e = io3(seg(t, T_DIVE1 + .05, T_DIVE1 + .6))
    L = lerp(478, 270, e)
    push = 1 + .2 * io3(seg(t, T_FF[4] - .05, T_FF[4] + .6))
    cam = Cam3(yaw=.55 * e + .09 * max(0, t - T_DIVE1 - .6), pitch=-.42 * e,
               dist=1300, f=1300 * push, cx=960, cy=520)
    return cam, L, e


def ff1_dot(t):
    cam, L, e = ff1_cam(t)
    sa, sb, f, k = ff1_state_at(t)
    pa = cam.proj(vpos(sa, 3, e, L))[0]
    pb = cam.proj(vpos(sb, 3, e, L))[0]
    return lerp2(pa, pb, f)


def ff1_view(t):
    """2-D follow on top of the 3-D orbit: keep the state dot near centre."""
    t0 = T_DIVE1 + .6
    if t < t0:
        return 0.0, 0.0

    def tgt(q):
        d = ff1_dot(max(q, t0))
        return [-(d[0] - 960) * .3, -(d[1] - 520) * .3]
    off = lagged(tgt, t, .25, 7)
    w = smooth(seg(t, t0, t0 + .4))
    return off[0] * w, off[1] * w


def scene_ff1(cv, t):
    if t < T_DIVE1 - .1 or t > T_RACE_IN + .3:
        return
    A = smooth(seg(t, T_DIVE1 - .02, T_DIVE1 + .1)) * \
        (1 - smooth(seg(t, T_RACE_IN - .15, T_RACE_IN + .15)))
    cam, L, e = ff1_cam(t)
    ox, oy = ff1_view(t)
    cam.cx, cam.cy = 960 + ox, 520 + oy

    def P(s):
        return cam.proj(vpos(s, 3, e, L))[0]
    sa, sb, f, k = ff1_state_at(t)
    used = set()
    for st in TRAJ[:max(k, 0) + 1]:
        p = st["path"]
        for a_, b_ in zip(p, p[1:]):
            used.add((min(a_, b_), max(a_, b_)))
    for (a, b) in cube_edges(3):
        if (a ^ b) == 1 and e < .02:
            continue
        hot = (a, b) in used
        cv.line(P(a), P(b), TEAL if hot else mix(GRAPHITE, AMBER, 1 - e),
                A * (.95 if hot else .6 + .4 * (1 - e)), 2.6 if hot else 1.8)
    for s in range(8):
        if (s & 1) and e < .02:
            continue
        p = P(s)
        qv = 1 - (s & 1)
        na = A * smooth(seg(t, T_DIVE1, T_DIVE1 + .2)) * (e if (s & 1) else 1)
        cv.circle(p, 26, AMBER if (qv and e > .5) else INK, na, fill=BG_IN,
                  fa=.95, w=2)
        cv.text(p[0], p[1] + 6, bits(s, 3) if e > .5 else bits(s >> 1, 2),
                F_MONO_M, 15, INK, na, anchor="c")
    dot = lerp2(P(sa), P(sb), f)
    da = A * smooth(seg(t, T_FF[0] - .15, T_FF[0]))
    cv.glow_dot(dot, 70, TEAL, .7 * da)
    cv.circle(dot, 9, None, da, fill=TEAL)
    tq = T_FF[4] + D_FF[4] / 2           # Q flips at 101 -> 100 (λ = ¬s2)
    if t > tq:
        fl = math.exp(-(t - tq) * 1.6)
        cv.glow_dot(dot, 140, AMBER, (.35 + .45 * fl) * A)
    hud_ff1(cv, t, A, sa, sb, f, k)


@overlay
def hud_ff1(cv, t, A, sa, sb, f, k):
    ra = A * smooth(seg(t, T_DIVE1 + .3, T_DIVE1 + .6))
    cv.text(140, 380, "FF1", F_TITLE, 64, INK, ra)
    cv.text(140, 418, "its FSM — published transition table (Fig. 8f)",
            F_UI_L, 21, GRAPHITE, ra)
    inp = TRAJ[k]["input"] if k >= 0 else 1
    cur = sb if f > .5 else sa
    cv.text(140, 500, f"(D, CK) = {inp >> 1} {inp & 1}", F_MONO, 22, INK, ra)
    cv.text(140, 540, f"s0 s1 s2 = {bits(cur, 3)}", F_MONO, 22, INK, ra)
    q = 1 - (cur & 1)
    cv.text(140, 580, f"Q = ¬s2 = {q}", F_MONO_M, 22, AMBER if q else INK, ra)
    cv.text(1500, 400, "amber ring:  Q = 1", F_UI_L, 18, AMBER, ra * .9)
    cv.text(1500, 428, "teal edges:  settling paths taken", F_UI_L, 18, TEAL,
            ra * .9)
    wx0, wy = 1500, 500
    seq = [1] + [s["input"] for s in TRAJ]
    for row, (nm, fn) in enumerate((("D", lambda i: i >> 1),
                                    ("CK", lambda i: i & 1))):
        y = wy + row * 46
        cv.text(wx0 - 12, y + 6, nm, F_MONO, 15, GRAPHITE, ra, anchor="r")
        pts = []
        for j, iv in enumerate(seq):
            x = wx0 + j * 46
            if j > 0 and T_FF[j - 1] > t:
                break
            yy = y + (10 if fn(iv) == 0 else -10)
            if pts:
                pts.append((x, pts[-1][1]))
            pts.append((x, yy))
            pts.append((x + 46, yy))
        cv.poly(pts, INK, ra * .9, 2)
    caption(cv, t, T_DIVE1 + .4, T_RACE_IN - .05,
            "FF1's FSM: an extra internal state settles in steps before Q "
            "captures D.",
            "Replayed from its table: on the rising edge with D = 1 the state "
            "walks 101 → 100 → 000.")
    tag(cv, t, T_DIVE1 - .05, T_RACE_IN - .05,
        "Fig. 8f · validated against the RBG")


# ---- the race: two circuits, sequencing overhead on a picosecond axis -----
RPX = 30.0                 # world px per ps
LANE_Y = {"FF1": -62.0, "TGFF": 62.0}
EY = 300.0                 # scatter: world px per fJ
RZ = .85                   # static race framing
RACE_C = ((960 - 400) / RZ, -(585 - 540) / RZ)


def race_ps(t):
    return clamp((t - T_R0) * V_PS, 0, 1e9)


def race_flash_pt():
    cam, L, e = ff1_cam(T_RACE_IN)
    ox, oy = ff1_view(T_RACE_IN)
    cam.cx, cam.cy = 960 + ox, 520 + oy
    sa, sb, f, k = ff1_state_at(T_RACE_IN)
    return cam.proj(vpos(sb, 3, e, L))[0]


_PF = race_flash_pt()
RACE_KEYS = [
    (T_RACE_IN, (-(_PF[0] - 960) / RZ, -(_PF[1] - 540) / RZ, RZ), "l"),
    (T_RACE_IN + .55, (RACE_C[0], RACE_C[1], RZ), "io"),
    (T_SCAT, (RACE_C[0] + 8, RACE_C[1], RZ * 1.012), "l"),
    (T_SCAT + .75, (1240, -425, .62), "io"),
]


def race_view(t):
    return View2(*kfv(t, RACE_KEYS, logi=(2,)))


T2 = DATA["table2"]


def scene_race(cv, t):
    if t < T_RACE_IN - .05 or t > T_FINAL + .2:
        return
    S = race_view(t).S
    A = smooth(seg(t, T_RACE_IN - .1, T_RACE_IN + .15)) * \
        (1 - smooth(seg(t, T_FINAL - .45, T_FINAL)))
    ps = race_ps(t)
    sc_t = smooth(seg(t, T_SCAT, T_SCAT + .6))
    up = io3(seg(t, T_SCAT + .25, T_SCAT + .9))
    o = S((0, 0))
    fa = math.exp(-max(0, t - T_RACE_IN) * 2.2) * (1 - sc_t)
    cv.glow_dot(o, 140, AMBER, .6 * fa)
    lay = A * smooth(seg(t, T_RACE_IN + .05, T_RACE_IN + .4))
    sl_a = lay * (1 - sc_t)
    cv.line(S((0, -110)), S((0, 110)), AMBER, sl_a * .8, 1.6)
    ay_w = lerp(140, 0, up)
    xmax = lerp(52, 80, sc_t)
    cv.line(S((0, ay_w)), S((xmax * RPX, ay_w)), GRAPHITE, lay, 1.3)
    for v in range(0, int(xmax) + 1, 5):
        p = S((v * RPX, ay_w))
        major = v % 10 == 0
        cv.line(p, (p[0], p[1] + (9 if major else 5)), GRAPHITE, lay, 1.1)
        if major:
            cv.text(p[0], p[1] + 30, str(v), F_MONO, 15, GRAPHITE, lay,
                    anchor="c")
    p = S((xmax * RPX, ay_w))
    cv.text(p[0], p[1] + 56, "ps", F_MONO, 15, GRAPHITE, lay * (1 - sc_t),
            anchor="r")
    ga = lay * (1 - sc_t)
    if ga > 0:
        for v in range(5, 50, 5):
            cv.line(S((v * RPX, -120)), S((v * RPX, ay_w)), DIM, ga * .5, 1,
                    [2, 6])
    ya = A * sc_t
    if ya > 0:
        cv.line(S((0, 0)), S((0, -3.1 * EY)), GRAPHITE, ya, 1.3)
        for v in (1, 2, 3):
            p = S((0, -v * EY))
            cv.text(p[0] - 14, p[1] + 5, str(v), F_MONO, 15, GRAPHITE, ya,
                    anchor="r")
            cv.line(p, S((80 * RPX, -v * EY)), DIM, ya * .6, 1, [2, 6])
        p = S((0, -3.1 * EY))
        cv.text(p[0], p[1] - 20, "energy  [fJ]", F_UI_L, 18, GRAPHITE, ya)
        p = S((40 * RPX, 0))
        cv.text(p[0], p[1] + 58, "sequencing overhead  T_setup + T_CK→Q  [ps]",
                F_UI_L, 18, GRAPHITE, ya, anchor="c")
    for name, val, col, energy in (("FF1", 19.1, AMBER, 2.26),
                                   ("TGFF", 48.2, INK, 1.53)):
        y_lane = LANE_Y[name]
        end = min(ps, val)
        x_end = end * RPX
        x_start = lerp(0, x_end, smooth(seg(t, T_SCAT, T_SCAT + .4)))
        y = lerp(y_lane, -energy * EY, up)
        th = lerp(22, 0, smooth(seg(t, T_SCAT, T_SCAT + .4)))
        if x_end > x_start + .5 and th > .3:
            p0, p1 = S((x_start, y - th / 2)), S((x_end, y + th / 2))
            cv.rrect(p0[0], p0[1], p1[0] - p0[0], p1[1] - p0[1],
                     min(4, (p1[1] - p0[1]) / 2), None, A, fill=col, fa=.9)
        head = S((x_end, y))
        stopped = ps >= val
        if not stopped and ps > 0:
            cv.glow_dot(head, 46, col, .75 * A)
        if stopped:
            ts = T_R0 + val / V_PS
            fl = math.exp(-(t - ts) * 2.5)
            cv.glow_dot(head, 60 + 50 * fl, col, (.25 + .6 * fl) * A *
                        (1 - .7 * sc_t))
            if sc_t > 0:
                if name == "FF1":
                    d = 10
                    shp = [(head[0], head[1] - d), (head[0] + d, head[1]),
                           (head[0], head[1] + d), (head[0] - d, head[1])]
                else:
                    shp = [(head[0], head[1] - 9), (head[0] + 8, head[1] + 6),
                           (head[0] - 8, head[1] + 6)]
                cv.poly(shp, col, A * sc_t, 2, close=True, fill=col)
            lab = f"{val} ps" if sc_t < .5 else f"{name}  {energy} fJ"
            cv.text(head[0] + 16, head[1] - 20, lab, F_MONO_M, 26, col,
                    A * smooth(seg(t, ts, ts + .2)))
        lp = S((0, y_lane))
        cv.text(lp[0] - 20, lp[1] - 2, "FF1" if name == "FF1" else "TGFF",
                F_MONO_M, 26, col, lay * (1 - sc_t), anchor="r")
        cv.text(lp[0] - 20, lp[1] + 22, "B-Flex · 32 T" if name == "FF1"
                else "baseline · 24 T", F_MONO, 15, GRAPHITE,
                lay * (1 - sc_t), anchor="r")
    if ps > 19.1 and sc_t < 1:
        g0 = S((19.1 * RPX, LANE_Y["FF1"]))
        g1 = S((min(ps, 48.2) * RPX, LANE_Y["FF1"]))
        cv.line(g0, g1, AMBER, A * .6 * (1 - sc_t), 1.6, [5, 7])
    ba = A * (1 - sc_t)
    if ba > 0 and t > T_BRK:
        pr = io3(seg(t, T_BRK, T_BRK + .4))
        y = -135
        p0, p1 = S((48.2 * RPX, y)), S((19.1 * RPX, y))
        pm = lerp2(p0, p1, pr)
        cv.line(p0, pm, AMBER, ba, 2)
        cv.line((p0[0], p0[1] - 8), (p0[0], p0[1] + 8), AMBER, ba, 2)
        if pr > .97:
            cv.line((p1[0], p1[1] - 8), (p1[0], p1[1] + 8), AMBER, ba, 2)
    sl = A * smooth(seg(t, T_SLAM, T_SLAM + .45)) * (1 - sc_t)
    if sl > 0:
        kk = 1 + .06 * (1 - ocub(seg(t, T_SLAM, T_SLAM + .6)))
        c = cv.c
        c.save()
        c.translate(960, 360)
        c.scale(kk, kk)
        cv.text(0, 0, "2.53×", F_MONO_L, 120, AMBER, sl, anchor="c")
        c.restore()
        cv.text(960, 412, "lower sequencing overhead than TGFF", F_UI, 28, INK,
                sl, anchor="c")
        cv.text(960, 446, "19.1 ps vs. 48.2 ps", F_MONO, 18, GRAPHITE,
                sl * smooth(seg(t, T_SLAM + .35, T_SLAM + .6)), anchor="c")
    oa = A * smooth(seg(t, T_SCAT + .4, T_SCAT + .75))
    if oa > 0:
        for k, (nm, grp, so, en) in enumerate(T2):
            if nm in ("FF1", "TGFF"):
                continue
            p = S((so * RPX, -en * EY))
            ap = oa * smooth(seg(t, T_SCAT + .65 + k * .025,
                                 T_SCAT + .85 + k * .025))
            if grp == "prior":
                cv.circle(p, 6.5, GRAPHITE, ap, w=1.8)
            elif grp == "auto":
                cv.rrect(p[0] - 6, p[1] - 6, 12, 12, 1.5, GRAPHITE, ap, lw=1.8)
            else:
                cv.poly([(p[0], p[1] - 7), (p[0] + 7, p[1]), (p[0], p[1] + 7),
                         (p[0] - 7, p[1])], TEAL, ap, 2, close=True, fill=TEAL)
                if nm == "FF6":
                    cv.text(p[0] + 12, p[1] + 20, "FF6", F_MONO, 14, TEAL, ap)
        lx, ly = 1250, 300
        cv.poly([(lx, ly - 7), (lx + 7, ly), (lx, ly + 7), (lx - 7, ly)],
                TEAL, oa, 2, close=True, fill=TEAL)
        cv.text(lx + 18, ly + 6, "B-Flex circuits (5 of 20 reported, Table 2)",
                F_UI_L, 16, INK, oa)
        cv.circle((lx, ly + 30), 6, GRAPHITE, oa, w=1.8)
        cv.text(lx + 18, ly + 36, "recent flip-flops [2,5,7,9,12,14,16,23,24]",
                F_UI_L, 16, GRAPHITE, oa)
        cv.rrect(lx - 6, ly + 54, 12, 12, 1.5, GRAPHITE, oa, lw=1.8)
        cv.text(lx + 18, ly + 66, "automated search, SeGen [10]", F_UI_L, 16,
                GRAPHITE, oa)
    hud_race(cv, t, A)


@overlay
def hud_race(cv, t, A):
    ha = A * window(t, T_RACE_IN + .3, T_SCAT + .2, .3, .3)
    cv.text(120, 172, "Sequencing overhead  =  T_setup + T_CK→Q", F_TITLE_L,
            36, INK, ha)
    cv.text(120, 208, "two circuits · 28 nm CMOS · 0.9 V · FO4 load · SPICE · "
            "worst-case D transition", F_UI_L, 20, GRAPHITE,
            ha * smooth(seg(t, T_RACE_IN + .5, T_RACE_IN + .8)))
    cv.text(120, 240, "bars grow at the same rate: 20 ps per second of film",
            F_MONO, 15, GRAPHITE, ha * smooth(seg(t, T_R0 - .3, T_R0)))
    sa = A * smooth(seg(t, T_SCAT + .5, T_SCAT + .9))
    cv.text(1250, 176, "The cost: energy vs. sequencing overhead", F_TITLE_L,
            30, INK, sa)
    cv.text(1250, 210, "all 18 flip-flops of Table 2 · 0.9 V · energy at "
            "10% data activity", F_UI_L, 18,
            GRAPHITE, sa)
    cv.text(1250, 240, "FF1 2.26 fJ  vs.  TGFF 1.53 fJ", F_UI_M, 18, INK, sa)
    cv.text(1250, 268, "at 0.4 V: FF6 is 1.71× faster than TGFF, with a "
            "3.00× narrower metastability window", F_UI_L, 15, GRAPHITE,
            A * smooth(seg(t, T_SCAT + .6, T_SCAT + .9)))
    caption(cv, t, T_R0 - .1, T_SCAT,
            "FF1's circuit vs. the transmission-gate flip-flop (TGFF).",
            "Both measured the same way (Table 2).  Bars grow at the same "
            "rate: 20 ps per second of film.")
    caption(cv, t, T_SCAT + .3, T_FINAL - .1,
            "The speed has a cost: FF1 draws 2.26 fJ vs. TGFF's 1.53 fJ.",
            "All 18 flip-flops of Table 2 at 0.9 V.  FF6 at 0.4 V: 1.71× "
            "faster than TGFF, 3.00× narrower metastability window.")
    tag(cv, t, T_RACE_IN + .3, T_FINAL, "Table 2 · §4.3–4.4 · Abstract")


# ============================================================ ACT V =========
def scene_final(cv, t):
    if t < T_FINAL - .1:
        return
    ta = smooth(seg(t, T_FINAL + .05, T_FINAL + .45)) * \
        (1 - smooth(seg(t, DUR3 - .6, DUR3)))
    if ta <= 0:
        return
    z = lerp(.965, 1.0, ocub(seg(t, T_FINAL, DUR3)))
    c = cv.c
    c.save()
    c.translate(960, 540)
    c.scale(z, z)
    c.translate(-960, -540)
    cv.text(960, 410, "B-Flex", F_TITLE, 132, INK, ta, anchor="c", track=-.01)
    cv.line((920, 452), (1000, 452), AMBER,
            ta * smooth(seg(t, T_FINAL + .35, T_FINAL + .9)), 2)
    a2 = ta * smooth(seg(t, T_FINAL + .4, T_FINAL + 1.0))
    cv.text(960, 516, "Exploration of Broader Flip-Flop Design Space",
            F_TITLE_L, 40, INK, a2, anchor="c")
    cv.text(960, 564, "Based on FSM Exhaustive Search", F_TITLE_L, 40, INK, a2,
            anchor="c")
    a3 = ta * smooth(seg(t, T_FINAL + .8, T_FINAL + 1.4))
    cv.text(960, 640, "DAC 2026  ·  63rd ACM/IEEE Design Automation "
            "Conference  ·  Long Beach, CA", F_MONO, 17, AMBER, a3,
            anchor="c", track=.04)
    a4 = ta * smooth(seg(t, T_FINAL + 1.1, T_FINAL + 1.7))
    cv.text(960, 724, "Hyunsung Jeong†    Kyounghun Kang†    "
            "Wanyeong Jung    Jongeun Lee", F_UI, 24, INK, a4, anchor="c")
    cv.text(960, 760, "UNIST  ·  KAIST          † equal contribution",
            F_UI_L, 19, GRAPHITE, a4, anchor="c")
    cv.text(960, 836, "doi.org/10.1145/3770743.3804333", F_MONO, 16, GRAPHITE,
            ta * smooth(seg(t, T_FINAL + 1.0, T_FINAL + 1.4)), anchor="c")
    c.restore()


# ======================================================= timing exports =====
CUES = {
    "trans": T_TRANS, "cap": T_CAP, "rew": T_REW0, "mod6": T_MOD6,
    "mod_end": T_MOD1, "pull": T_PB0, "states": T_ST0, "fly": T_FLY0,
    "extrude": T_EXT0, "collapse": T_COL0, "title": T_TTL, "stage": T_STAGE,
    "rbg_nodes": sorted(T_NODE.values()), "rbg_edges": T_EDGE,
    "token": [T_TOK0 + T_TOKD * k for k in range(1, 7)],
    "token_amber": [4], "token_end": T_TOK1,
    "tilt": T_TILT, "lift": T_LIFT0, "slots": T_SLOT, "call": T_CALL,
    "panel": T_PANEL, "moves": [T_S1, T_S2, T_S3, T_S4, T_S4B],
    "init": T_INIT, "row7": T_ROW7, "ant2": T_ANT2,
    "cands": T_CAND, "reject": T_REJ, "retract": T_RETRACT,
    "x1": T_X1, "x2": T_X2, "keep": T_KEEP, "follow": T_FOLLOW,
    "links": LINK_T, "ant4": T_ANT4, "cpath": T_CPATH, "conflict": T_CONF,
    "cut": T_CUT, "pip": T_PIP, "grow": (T_GROW0, T_GROW1),
    "cells": T_CELLS0, "fill": (T_FILL0, T_FILL1), "hist": T_HIST0,
    "block": T_BLK0, "sample20": T_AMB0, "dive": (T_DIVE0, T_DIVE1),
    "ff1_steps": T_FF, "ff1_dur": D_FF, "race_in": T_RACE_IN, "race0": T_R0,
    "ff1_stop": T_FF1_STOP, "tg_stop": T_TG_STOP, "bracket": T_BRK,
    "slam": T_SLAM, "scatter": T_SCAT, "final": T_FINAL,
}

# motion-blur shutter windows (only where the camera moves fast)
BLUR = [(T_COL0 + .25, T_TTL + .35, 6), (T_S1, T_S1 + .5, 3),
        (T_S2, T_S2 + .5, 3), (T_S3, T_S3 + .45, 3), (T_S4, T_S4 + .25, 3),
        (T_S4B, T_S4B + .6, 3), (T_PIP - .1, T_PIP + .65, 5),
        (T_CELLS0, T_CELLS0 + .8, 5), (T_DIVE0, T_DIVE1 + .55, 6),
        (T_RACE_IN, T_RACE_IN + .55, 5), (T_SCAT, T_SCAT + .75, 5)]


def blur_n(t):
    for a, b, n in BLUR:
        if a <= t <= b:
            return n
    return 1


# ============================================================ compose =======
def draw3(cv, t):
    OVERLAY.clear()
    cv.begin()
    if t < T_STAGE + .4:
        camv = camA(t)
        camv.push(cv)
        act_label(cv, t, .9, T_COL0 + .3, "01", "THE CHALLENGE")
        scene_wave(cv, t)
        scene_cube(cv, t)
        scene_title(cv, t)
        camv.pop(cv)
    if T_CELLS0 < t < T_BLK0 + .8:
        composite_region(cv, unit_layer(cv, t, unit_alpha(t)))
    scene_stage(cv, t)
    if T_ANT2 - .45 < t < T_PIP:
        scene_tree_hud(cv, t)
    elif t >= T_PIP:
        scene_tree(cv, t)
    scene_unit(cv, t)
    scene_hist(cv, t)
    scene_ff1(cv, t)
    scene_race(cv, t)
    scene_final(cv, t)
    breadcrumb(cv, t)
    for fn in OVERLAY:
        fn()


# ====================================================== v4: narration clock ==
import edl
DURATION = edl.DURATION
CUES3 = CUES
CUES = {k: ([edl.inv(x) for x in v] if isinstance(v, (list, tuple)) else
            edl.inv(v)) for k, v in CUES3.items()}
_blur_n3 = blur_n


def blur_n(t4):
    return _blur_n3(edl.warp(t4))


def draw(cv, t4):
    """v4 entry point: the narration-aligned clock drives the v3 animation."""
    draw3(cv, edl.warp(t4))
    g = smooth(seg(t4, 0, .5)) * (1 - smooth(seg(t4, DURATION - .8, DURATION)))
    if g < 1:
        cv.c.identity_matrix()
        cv.c.set_source_rgba(*PAPER, 1 - g)
        cv.c.paint()
        cv.c.scale(cv.k, cv.k)
