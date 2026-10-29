"""peak_kit demo: three planned peaks in 30 s (toy data, not from any paper).

  P1 hook     scale reveal   one candidate -> the whole toy space lights up   (no signature)
  P2 concept  cascade        one rule decision prunes cells in a ripple       (signature: night)
  P3 result   number land    the method's bar drops to its exact value,
                             trade-off pinned 2 s later                       (signature: accent)

Two signature breaks: the film's whole budget (peak_kit.MAX_SIGNATURES = 2).

  cd examples/peak_demo
  PYTHONPATH=../../scripts python3 ../../scripts/render.py video --w 640 --fps 30 --out out/demo.mkv
  PYTHONPATH=../../scripts python3 film.py               # writes out/peaks.json, out/cues.json, out/audio.wav
  python3 ../../scripts/wow_audit.py --peaks out/peaks.json --video out/demo.mkv \\
      --cues out/cues.json --ledger LEDGER.md --json out/wow.json
  python3 ../../scripts/motion_audit.py out/demo.mkv --json out/motion.json
  python3 ../../scripts/gate.py --no-edl --motion out/motion.json --wow out/wow.json
"""
import math
import random

from engine import (seg, smooth, io3, window, lerp, DW, DH, INK, GRAPHITE, DIM, TEAL, CORAL,
                    AMBER, BLUE, PAPER)
from scene_kit import OVERLAY, overlay
from motion_kit import begin_frame, View2, pulse, callout_at, breadcrumb
from peak_kit import (Peak, PeakPlan, ripple_order, cascade, count_at, breath, land, log_zoom,
                      accent_glow, night_rgb)

DURATION = 30.0
MONO, MED = "JetBrains Mono Medium", "Inter Medium"

PLAN = PeakPlan([
    Peak("whole toy space appears", kind="hook", device="scale_reveal",
         t_setup=.5, t_reveal=3.0, t_hold=8.0, key_word="candidates", claim="T1"),
    Peak("one rule prunes 60 % in a ripple", kind="concept", device="cascade",
         t_setup=9.0, t_reveal=12.0, t_hold=15.0, key_word="pruned", claim="T2",
         signature="night", sig_in=11.4, sig_out=15.6),
    Peak("64 % lower toy cost", kind="result", device="number_land",
         t_setup=20.5, t_reveal=24.0, t_hold=28.0, key_word="lower", claim="T3",
         signature="accent", sig_in=23.6, sig_out=28.4, tradeoff_t=26.0),
])
P1, P2, P3 = PLAN.peaks

# ---- toy grid: 32 x 32 candidates ------------------------------------------
N, CELL, GAP = 32, 21, 5
X0, Y0 = DW / 2 - N * (CELL + GAP) / 2, 140
CELLS = [(i, j) for j in range(N) for i in range(N)]
CENTRE = [(X0 + i * (CELL + GAP) + CELL / 2, Y0 + j * (CELL + GAP) + CELL / 2) for i, j in CELLS]
SEED_CELL = 17 * N + 9                                   # the candidate we start on
SRC = 12 * N + 20                                        # the cell where the rule fires
rnd = random.Random(3)
PRUNED = {k for k, (i, j) in enumerate(CELLS) if (i * 7 + j * 3) % 5 < 3 and k != SRC}
LIGHT = ripple_order(CENTRE, CENTRE[SEED_CELL])          # P1 reveal spreads from the seed
RIP = ripple_order(CENTRE, CENTRE[SRC])                  # P2 cascade spreads from the rule
PRUNE_STAGGER, PRUNE_DUR = .5, .3
PRUNE_T = sorted(P2.t_reveal + RIP[k] * PRUNE_STAGGER for k in PRUNED)


def cam(t):
    sx, sy = CENTRE[SEED_CELL]
    cx, cy = CENTRE[SRC]
    if t < P1.t_reveal + .1:                             # hold close on one candidate, then pull back
        z = log_zoom(t, 1.9, 2.9, 11.0, 1.0) * (1 + .03 * seg(t, 0, 1.9))
        f = io3(seg(t, 1.9, 2.9))
        return View2(lerp(sx, DW / 2, f), lerp(sy, Y0 + N * 13, f), z)
    base = (DW / 2, Y0 + N * 13)
    z = 1.0 + .03 * seg(t, P1.t_reveal, 8.6)             # drift during the hold
    if t >= 8.6:                                         # push in toward the rule source
        f = io3(seg(t, 8.6, 9.6)) - io3(seg(t, 15.4, 16.4))
        z = lerp(1.03, 1.4, f) * (1 - .015 * breath(t, P2.t_reveal))
        tx, ty = lerp(base[0], (cx + base[0]) / 2, f), lerp(base[1], (cy + base[1]) / 2, f)
        return View2(tx, ty, z * (1 + .02 * seg(t, 9.6, 15.4)))
    return View2(base[0], base[1], z)


def draw(cv, t):
    begin_frame()
    cv.begin()
    if t < 18.6:
        grid_scene(cv, t)
    if t > 17.4:
        bar_scene(cv, t)
    for fn in OVERLAY:
        fn()


def grid_scene(cv, t):
    fa = 1 - smooth(seg(t, 17.4, 18.6))
    v = cam(t)
    v.push(cv)
    lit = cascade(t, P1.t_reveal - .05, LIGHT, stagger=.35, dur=.25)
    pr = cascade(t, P2.t_reveal, RIP, stagger=PRUNE_STAGGER, dur=PRUNE_DUR)
    for k, (x, y) in enumerate(CENTRE):
        on = lit[k] if k != SEED_CELL else 1.0
        if k in PRUNED and pr[k] > 0:
            col, a = CORAL, fa * (1 - .78 * pr[k])
            dy = 10 * pr[k]
        else:
            col, a, dy = (TEAL if k != SRC else AMBER), fa, 0
        cv.rrect(x - CELL / 2, y - CELL / 2 + dy, CELL, CELL, 4, col=GRAPHITE, a=fa * .35 * (1 - on),
                 lw=1, dash=[3, 3])
        cv.rrect(x - CELL / 2, y - CELL / 2 + dy, CELL, CELL, 4, fill=col, fa=.85, a=a * on)
    v.pop(cv)
    sp = v.S(CENTRE[SEED_CELL])
    callout_at(cv, sp, (60, -90), "one candidate", INK, fa * window(t, .3, 2.2, .3, .3))
    pulse(cv, sp, 16 * v.z, TEAL, t, P1.t_reveal)
    s = v.S(CENTRE[SRC])
    callout_at(cv, s, (70, -110), "rule fires here: X = 0 ⇒ prune", AMBER,
               fa * window(t, 9.4, 16.0, .3, .4), anchor_r=12 * v.z)
    pulse(cv, s, 14 * v.z, AMBER, t, P2.t_reveal)
    hud(cv, t, fa)


@overlay
def hud(cv, t, fa):
    n_lit = 1 if t < P1.t_reveal else N * N
    cv.rrect(40, 950, DW - 80, 64, 10, fill=PAPER, fa=.92, a=fa)       # knockout band for the HUD
    cv.text(64, 990, f"{n_lit:,} candidate{'s' if n_lit > 1 else ''}  ·  toy space", MONO, 30, INK,
            fa * smooth(seg(t, .2, .8)))
    pruned = count_at(t, PRUNE_T)
    cv.text(DW - 64, 990, f"pruned {pruned:,} / {N * N:,}", MONO, 30, CORAL,
            fa * smooth(seg(t, P2.t_reveal - .3, P2.t_reveal + .1)), anchor="r")
    cv.rrect(40, 66, 560, 56, 10, fill=PAPER, fa=.92, a=fa)            # knockout behind the breadcrumb
    steps = [(0, "PEAK 1", "scale reveal"), (8.6, "PEAK 2", "one decision, many effects"),
             (18.8, "PEAK 3", "the result lands")]
    for k, (t0, s_, txt) in enumerate(steps):
        t1 = steps[k + 1][0] if k + 1 < len(steps) else DURATION + 1
        breadcrumb(cv, s_, txt, window(t, max(t0, .3), t1, .25, .25))


BASE, METHOD = 1.00, 0.36                                # toy, normalised cost
BX, BY, BH, BWD = 640, 900, 620, 230


def bar_scene(cv, t):
    fa = smooth(seg(t, 17.4, 18.6))
    z = 1.0 + .05 * seg(t, 18, 30) + .1 * io3(seg(t, 23.0, 24.4))
    v = View2(DW / 2 + 40 * seg(t, 18, 30), 560, z)
    v.push(cv)
    cv.line((BX - 120, BY), (BX + 760, BY), GRAPHITE, fa, 2)
    hb = BH * BASE * smooth(seg(t, 18.4, 19.4))
    cv.rrect(BX, BY - hb, BWD, hb, 6, fill=BLUE, fa=.85, a=fa)
    cv.text(BX + BWD / 2, BY + 48, "baseline", MED, 30, INK, fa, anchor="c")
    cv.text(BX + BWD / 2, BY - hb - 40, f"{BASE:.2f}", MONO, 48, INK, fa * smooth(seg(t, 19.2, 19.8)),
            anchor="c")
    hm = BH * (land(t, P3.t_reveal, .5, BASE, METHOD) if t >= P3.t_reveal else BASE) \
        * smooth(seg(t, 20.6, 21.6))
    mx = BX + 420
    br = breath(t, P3.t_reveal)
    cv.rrect(mx, BY - hm, BWD, hm, 6, fill=AMBER, fa=.9, a=fa * (1 - .3 * br))
    cv.text(mx + BWD / 2, BY + 48, "method", MED, 30, INK, fa, anchor="c")
    v.pop(cv)
    top = v.S((mx + BWD / 2, BY - hm))
    ag = PLAN.signature_level(t, "accent")
    accent_glow(cv, (top[0], top[1] - 60), 260, AMBER, ag)
    val = METHOD if t >= P3.t_reveal + .5 else land(t, P3.t_reveal, .5, BASE, METHOD)
    cv.text(top[0], top[1] - 40, f"{val:.2f}", MONO, 64, INK,
            fa * smooth(seg(t, 21.0, 21.6)), anchor="c")
    callout_at(cv, (top[0] + 118, top[1]), (170, -60), "64 % lower toy cost (1.00 → 0.36)", AMBER,
               window(t, P3.t_reveal + .3, 30.5, .3, .3), anchor_r=8)
    callout_at(cv, v.S((mx + BWD, BY - BH * METHOD / 2)), (220, 40), "trade-off: area +4 % (toy)", CORAL,
               window(t, P3.tradeoff_t, 30.5, .3, .3), anchor_r=6)
    cv.text(DW - 64, 76, "toy data · not from any paper", MED, 22, GRAPHITE, fa, anchor="r")


def post(rgb, t):
    return night_rgb(rgb, PLAN.signature_level(t, "night"))


# ---- cues and audio (run this file directly) --------------------------------
CUES = {"P1_reveal": P1.t_reveal, "P2_reveal": P2.t_reveal, "P3_reveal": P3.t_reveal}

if __name__ == "__main__":
    import json, os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../scripts/audio"))
    from synth import Track, pad, riser, hit, tick, SR
    import numpy as np
    import soundfile as sf
    os.makedirs("out", exist_ok=True)
    PLAN.export("out/peaks.json", duration=DURATION)
    json.dump(CUES, open("out/cues.json", "w"), indent=1)
    music, sfx = Track(DURATION), Track(DURATION)
    music.add(0, pad(["D3", "A3", "F4"], DURATION, 2, 2), gain=.35)
    for p in PLAN.peaks:
        music.add(p.t_reveal - 2.0, riser(2.0), gain=.35)
        music.duck(p.t_reveal - .35, p.t_reveal, db=-18)
        sfx.add(p.t_reveal, hit(), gain=.7)
    for tp in PRUNE_T[::40]:
        sfx.add(tp, tick(), gain=.08)
    x = music.render(room=(3.0, 2400, .5)) + sfx.render(room=(2.0, 3000, .4))
    x = x / max(1e-9, np.abs(x).max()) * .7
    sf.write("out/audio.wav", x.astype(np.float32), SR)
    print("wrote out/peaks.json out/cues.json out/audio.wav")
