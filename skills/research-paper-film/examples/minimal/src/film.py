"""Minimal demo film (~10 s): the pipeline end to end on a toy "paper".

Toy claim: "a search tree of 4 candidates; 2 violate the reference output and
are pruned; 2 survive". Everything on screen is driven by DATA below (in a
real project: data/scene_data.json from your re-implementation).
Animation clock = t_anim (timing constants); film clock = edl.warp.
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
from engine import *                                            # noqa: F401,F403
from scene_kit import OVERLAY, overlay, marker, check, xmark    # noqa: E402
os.environ.setdefault("NARRATION_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "narration"))
import edl                                                      # noqa: E402

DATA = {"candidates": [("00", 1, "pruned"), ("01", 0, "kept"),
                       ("10", 1, "pruned"), ("11", 0, "kept")],
        "reference_q": 0}
assert sum(c[2] == "kept" for c in DATA["candidates"]) == 2

# ---- timing sheet (animation clock) ----
T_ROOT, T_CAND, T_JUDGE, T_DONE = .2, .9, 2.0, 2.8
CUES = {"cand": T_CAND, "judge": T_JUDGE, "done": T_DONE}
ROOT = (560, 540)
POS = [(1060, 300 + 160 * k) for k in range(4)]


@overlay
def tag(cv, t, s):
    cv.text(1840, 70, s, F_UI, 18, GRAPHITE, window(t, .2, 3.5), anchor="r")


def draw_anim(cv, t):
    OVERLAY.clear()
    cv.begin()
    a = smooth(seg(t, T_ROOT, T_ROOT + .4))
    cv.circle(ROOT, 46, INK, a, fill=PAPER, w=2.4)
    cv.text(ROOT[0], ROOT[1] + 9, "s", F_UI_M, 26, INK, a, anchor="c")
    cv.text(ROOT[0], ROOT[1] - 70, f"reference: Q = {DATA['reference_q']}", F_UI_M, 24, BLUE, a, anchor="c")
    for k, (lab, q, st) in enumerate(DATA["candidates"]):
        g = io3(seg(t, T_CAND + .12 * k, T_CAND + .5 + .12 * k))
        if g <= 0:
            continue
        p = POS[k]
        judged = smooth(seg(t, T_JUDGE + .1 * k, T_JUDGE + .35 + .1 * k))
        col = mix(INK, CORAL if st == "pruned" else TEAL, judged)
        cv.line((ROOT[0] + 46, ROOT[1]), lerp2((ROOT[0] + 46, ROOT[1]), (p[0] - 40, p[1]), g), col, 1, 2.2)
        cv.circle(p, 38, col, g, fill=PAPER, w=2.4)
        cv.text(p[0], p[1] + 8, lab, F_UI_M, 24, col, g, anchor="c")
        cv.text(p[0] + 70, p[1] + 8, f"Q = {q}", F_UI, 22, col, g)
        if judged > 0:
            if st == "pruned":
                xmark(cv, (p[0] + 170, p[1]), 10, CORAL, judged)
            else:
                check(cv, (p[0] + 170, p[1] + 2), 10, TEAL, judged, judged)
    da = smooth(seg(t, T_DONE, T_DONE + .4))
    cv.text(1400, 960, "2 of 4 survive", F_UI_M, 34, TEAL, da, anchor="c")
    marker(cv, (100, 70), 1, a)
    tag(cv, t, "toy example")
    for fn in OVERLAY:
        fn()


DURATION = edl.DURATION


def draw(cv, t):
    draw_anim(cv, edl.warp(t))


def blur_n(t):
    return 1
