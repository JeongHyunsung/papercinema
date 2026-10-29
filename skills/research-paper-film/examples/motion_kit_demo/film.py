"""motion_kit demo: one mechanism beat choreographed the way the case study did it.

A toy validation search (3 reference nodes, 2 candidate states each). It shows,
in 12 s:
  - pills: the full candidate space above each reference node (ghost slots),
  - a living camera: beat_keys() pushes in to each beat and pulls back,
  - focus: non-participating pills dim while a finding is shown,
  - proposals (dashed arcs) -> a tracer runs the accepted settling path,
  - an AddressTable written in place, each write tethered to its node,
  - findings pinned with callout_at() and concrete values,
  - an entry conflict: the earlier fact and the needed fact side by side.

  cd examples/motion_kit_demo
  PYTHONPATH=../../scripts python3 ../../scripts/render.py stills --w 1280 --times 2 4.6 7.6 10
  PYTHONPATH=../../scripts python3 ../../scripts/render.py video --w 640 --fps 30 --out out/demo.mkv
  PYTHONPATH=../../scripts python3 ../../scripts/linkage_audit.py film
  python3 ../../scripts/motion_audit.py out/demo.mkv --json out/motion.json
Toy data, not from any paper.
"""
import math
from engine import (seg, smooth, io3, ocub, oback, window, lerp, DW, DH, INK, GRAPHITE, DIM,
                    TEAL, CORAL, AMBER, BLUE, PAPER)
from scene_kit import OVERLAY, overlay, sw
from motion_kit import (begin_frame, beat_keys, stage_cam, focus, tracer, proposal, pulse,
                        callout_at, tether, AddressTable, pill, slot_node, stable_loop,
                        breadcrumb)

DURATION = 12.0
NODES = {"A": (-420, 0), "B": (0, 0), "C": (420, 0)}     # reference nodes (floor)
H = 260                                                   # candidate layer height
SLOT = {0: -60, 1: 60}                                    # slot offsets inside a pill

# camera: (tx, ty, th, D, tau, psi, ox, oy); distance (index 3) is log-interpolated
WIDE = (0, 0, 130, 1650, .92, -.12, -250, 60)
CLOSE_A = (-330, 0, H, 1150, .70, -.10, -240, 30)
CLOSE_B = (-140, 0, H, 1250, .72, -.14, -250, 30)
CLOSE_C = (-60, 0, H, 1350, .78, -.18, -250, 20)
KEYS = beat_keys(0.0, WIDE, [(2.2, 3.6, CLOSE_A), (5.0, 6.9, CLOSE_B), (8.4, 10.4, CLOSE_C)],
                 push=.7, pull=.7)

# timings
T_START, T_PROP, T_PRUNE, T_RUN, T_WRITE_B = 1.9, 4.4, 5.3, 6.0, 6.7
T_CPROP, T_CONF = 8.4, 9.1
FOCUS = [((T_PROP - .2, 7.0), {"A", "B"}), ((T_CPROP - .2, 10.6), {"A", "C"})]

TABLE = AddressTable(keys=[(n, s) for n in "ABC" for s in (0, 1)], x=1350, y=170, w=470,
                     head=["in", "s", "→ s'"], key_fmt=lambda k: [k[0], str(k[1])],
                     val_fmt=lambda v: [str(v)], col_x=[70, 150, 300], val_x=[300],
                     title="transition table δ (toy)")
CELLS = {("A", 0): dict(v=0, t=T_START + .3, style="write"),
         ("B", 0): dict(v=0, t=T_WRITE_B, style="infer", note="infer"),
         ("A", 0, "c"): None}


def slot_world(n, s):
    return (NODES[n][0] + SLOT[s], NODES[n][1], H)


def draw(cv, t):
    begin_frame()
    cv.begin()
    cam = stage_cam(t, KEYS, f=1500)
    P = lambda w: cam.P(w)                                       # noqa: E731
    # reference floor: nodes and edges
    for (a, b) in (("A", "B"), ("B", "C")):
        pa, pb = P((*NODES[a], 0)), P((*NODES[b], 0))
        cv.line(pa[:2], pb[:2], BLUE, .55, sw(pa[2], 2.2))
    for n, (u, v) in NODES.items():
        x, y, sc, _ = P((u, v, 0))
        cv.circle((x, y), 46 * sc, BLUE, focus(t, FOCUS, n), fill=PAPER, w=sw(sc, 2.4))
        cv.text(x, y + 9 * sc, n, MONO_(), 26 * sc, INK, focus(t, FOCUS, n), anchor="c")
    # pills with all candidate states (ghost until reached)
    for n, (u, v) in NODES.items():
        fa = focus(t, FOCUS, n)
        sc = pill(cv, cam, u, v, H, 250, 110, fa * smooth(seg(t, .2, .9)))
        bx, by = P((u, v, 0))[:2]
        tx, ty, ts, _ = P((u, v, H))
        cv.line((tx, ty + 55 * ts), (bx, by - 46 * P((u, v, 0))[2]), GRAPHITE, fa * .4, 1.2,
                dash=[4, 5])
        for s in (0, 1):
            x, y, ss, _ = P(slot_world(n, s))
            state = "ghost"
            if (n, s) == ("A", 0) and t >= T_START:
                state = "start"
            if (n, s) == ("B", 0) and t >= T_WRITE_B:
                state = "live"
            if (n, s) == ("B", 1) and T_PRUNE <= t:
                state = "pruned"
            al = fa * (1 - .65 * smooth(seg(t, T_PRUNE + 1.2, T_PRUNE + 1.8)) if state == "pruned" else fa)
            slot_node(cv, (x, y), 38 * ss, str(s), state, al, size=24 * ss)
    a0 = P(slot_world("A", 0))
    if t >= T_START:
        stable_loop(cv, a0[:2], 38 * a0[2], TEAL, 1)
        pulse(cv, a0[:2], 38 * a0[2], TEAL, t, T_START)
        callout_at(cv, a0[:2], (0, -110), "start: δ(A, 0) = 0 (stable)", TEAL,
                   window(t, T_START + .1, 4.2, .3, .4), anchor_r=40 * a0[2])
    # step 2: proposals A0 -> B0, A0 -> B1
    b0, b1 = P(slot_world("B", 0)), P(slot_world("B", 1))
    for q, col in ((b0, AMBER), (b1, CORAL if t >= T_PRUNE else AMBER)):
        proposal(cv, a0[:2], q[:2], io3(seg(t, T_PROP, T_PROP + .6)), col,
                 window(t, T_PROP, 7.2, .2, .4), bend=-.25)
    callout_at(cv, b1[:2], (40, -120), "Q = 1 ≠ required 0 → pruned", CORAL,
               window(t, T_PRUNE, 7.4, .3, .4), anchor_r=40 * b1[2])
    # step 3: tracer runs the accepted settling path A0 -> B0
    if T_RUN <= t < T_WRITE_B + .5:
        pts = [(a0[0] + (b0[0] - a0[0]) * k / 30, a0[1] + (b0[1] - a0[1]) * k / 30
                - math.sin(math.pi * k / 30) * 60) for k in range(31)]
        tracer(cv, pts, io3(seg(t, T_RUN, T_WRITE_B)), TEAL, 1, r=8)
    pulse(cv, b0[:2], 38 * b0[2], AMBER, t, T_WRITE_B)
    # step 4: C proposal needs δ(A, 0) = 1, but it was fixed to 0
    c0 = P(slot_world("C", 0))
    proposal(cv, c0[:2], a0[:2], io3(seg(t, T_CPROP, T_CPROP + .6)), CORAL,
             window(t, T_CPROP, 11.2, .2, .4), bend=.22)
    ca = window(t, T_CONF, 11.4, .3, .4)
    callout_at(cv, a0[:2], (-30, -190), "earlier step fixed δ(A, 0) = 0", TEAL, ca)
    callout_at(cv, a0[:2], (-30, -140), "path needs δ(A, 0) = 1  ≠", CORAL, ca, leader=False)
    # table (overlay) with tethers from the node to the written row
    cells = dict(CELLS)
    cells.pop(("A", 0, "c"))
    if t >= T_CONF:
        cells[("A", 0)] = dict(v=0, t=T_CONF, style="conflict", note="needs 1")
    hud(cv, t, cells, a0, b0)
    for fn in OVERLAY:
        fn()


def MONO_():
    return "JetBrains Mono Medium"


@overlay
def hud(cv, t, cells, a0, b0):
    TABLE.draw(cv, t, cells, a=smooth(seg(t, .4, 1.0)))
    for key, node, t0, t1, col in ((("A", 0), a0, T_START + .3, 4.0, TEAL),
                                   (("B", 0), b0, T_WRITE_B, 8.0, AMBER),
                                   (("A", 0), a0, T_CONF, 11.4, CORAL)):
        ta = window(t, t0, t1, .25, .4)
        tether(cv, (node[0] + 40 * node[2], node[1]), TABLE.row_anchor(key), col, ta,
               prog=io3(seg(t, t0, t0 + .5)))
    steps = [(0, "STEP 1", "start from a stable pair"), (4.2, "STEP 2", "destination discovery · wrong output"),
             (5.9, "STEP 3", "settle and infer δ"), (8.2, "STEP 4", "entry conflict")]
    for k, (t0, s, txt) in enumerate(steps):
        t1 = steps[k + 1][0] if k + 1 < len(steps) else DURATION + 1
        breadcrumb(cv, s, txt, window(t, max(t0, .3), t1, .25, .25))
