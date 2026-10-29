"""Figure-archetype gallery: five slide figures for five kinds of CS/EE paper,
built only from scripts/viz_kit.py. Data are TOY values - replace them with
your paper's numbers (and keep the conditions next to them).

  python3 gallery.py            -> out/*.png|svg|pdf  (+ run lint_figs.py)

  A_hw_architecture     dataflow / accelerator: blocks, buses, PE-array heat
                        + normalized speed-up bars (geomean)
  B_algorithm_step      search / pruning step: graph with pruned candidates
                        + the state table with the written row and a conflict
  C_systems_results     latency vs load curves with direct labels + breakdown
  D_scale_to_pareto     huge count (block + lens) -> histogram -> Pareto scatter
  E_circuit_timing      waveform with pass/fail transitions + pipeline schedule
"""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(here, "..", "..", "scripts")
sys.path[:0] = [S, os.path.join(S, "figures")]
import figkit as FK                                      # noqa: E402
FK.use_inter()
FK.use_contrast()
from engine import INK, GRAPHITE, TEAL, CORAL, AMBER, BLUE, DIM     # noqa: E402
from viz_kit import *                                    # noqa: E402,F401,F403
import viz_kit as V                                      # noqa: E402

OUT = os.path.join(here, "out")


def A(cv):
    cv.begin()
    p = block(cv, 60, 360, 150, 130, "DRAM", GRAPHITE, ports=[("r", .5, "o")])
    q = block(cv, 400, 330, 210, 190, "Global buffer", INK, sub="512 KB",
              ports=[("l", .5, "i"), ("r", .5, "o")])
    wire(cv, [p["o"], q["i"]], text="64 B/cycle", bus=True)
    grid_array(cv, 720, 250, 8, 8, 40, value=lambda i, j: ((i * 3 + j * 5) % 9) / 8)
    label(cv, 720 + 4 * 44, 228, "PE array 8 × 8", "axis", INK, "c")
    wire(cv, [q["o"], (712, q["o"][1])], col=TEAL)
    callout(cv, (720 + 2 * 44 + 20, 250 + 7 * 44 + 20), (620, 680), "weight-stationary reuse", AMBER)
    ax = Axes(cv, (1240, 250, 520, 440), (0, 4), (0, 4), yticks=[1, 2, 3, 4],
              ylabel="speed-up vs CPU (×)", draw=True)
    bars(cv, ax, ["CNN", "RNN", "GEOMEAN"], {"GPU": [2.1, 1.6, 1.8], "ours": [3.6, 2.9, 3.2]},
         colors={"GPU": GRAPHITE, "ours": TEAL}, value_fmt="{:.1f}×")


def B(cv):
    cv.begin()
    nodes = {"s": (200, 520, "11"), "a": (560, 280, "00"), "b": (560, 440, "01"),
             "c": (560, 600, "10"), "d": (560, 760, "11")}
    edges = [("s", k, dict(col=CORAL if k in "ac" else TEAL, w=2.4)) for k in "abcd"]
    graph(cv, nodes, edges, node_col={"a": CORAL, "c": CORAL, "b": TEAL, "d": TEAL})
    for k in "ac":
        V._xmark(cv, (640, nodes[k][1]), 10, CORAL, 1)
        label(cv, 670, nodes[k][1] + 7, "Q = 1 ≠ reference 0", "note", CORAL)
    chip2d(cv, 120, 400, "reference: Q = 0", BLUE)
    chip2d(cv, 300, 880, "wrong output → branch pruned", CORAL)
    table_panel(cv, 1180, 230, ["in", "s", "→", "s'"], [
        ("00", "00", "", "·"), ("00", "01", "", "11"), ("00", "10", "", "·"),
        ("00", "11", "", "01"), ("01", "11", "", "11"), ("11", "11", "", "11")],
        col_x=[0, 110, 220, 330], row_h=52, highlight={4: TEAL, 5: CORAL},
        strike={5: 3}, note=(5, "needs 10 · entry conflict", CORAL))


def C(cv):
    cv.begin()
    ax = Axes(cv, (140, 230, 760, 420), (0, 100), (0, 40), xticks=[0, 25, 50, 75, 100],
              yticks=[10, 20, 30, 40], xlabel="offered load (%)", ylabel="p99 latency (ms)")
    lines(cv, ax, {"baseline": [(10, 4), (30, 6), (50, 10), (70, 21), (85, 37)],
                   "ours": [(10, 3), (30, 4), (50, 5.5), (70, 8), (85, 12), (95, 19)]},
          colors={"baseline": GRAPHITE, "ours": TEAL})
    vspan(cv, ax.X(85) + 26, ax.Y(37), ax.Y(12), "3.1× lower at 85 %")
    ax2 = Axes(cv, (1180, 230, 620, 420), (0, 4), (0, 100), yticks=[25, 50, 75, 100],
               ylabel="time breakdown (%)")
    bars(cv, ax2, ["queue", "compute", "network"], {"baseline": [55, 30, 15], "ours": [18, 52, 30]},
         colors={"baseline": GRAPHITE, "ours": TEAL}, value_fmt="{:g} %")


def D(cv):
    cv.begin()
    S0, Sz = (80, 250), 380
    label(cv, S0[0], S0[1] - 74, "valid designs", "eyebrow", AMBER)
    label(cv, S0[0], S0[1] - 20, "1,048,576", "hero", INK)
    unit_block(cv, S0[0], S0[1], Sz)
    cell = unit_histogram(cv, 600, 640, [2, 5, 9, 21, 40, 63], [10, 11, 12, 13, 14, 15],
                          axis_sub=("C", "cost"))
    import random
    rnd = random.Random(3)
    k = 0
    for b, n in enumerate([2, 5, 9, 21, 40, 63]):
        for j in range(n):
            while True:
                u = (S0[0] + 20 + rnd.random() * (Sz - 40), S0[1] + 20 + rnd.random() * (Sz - 40))
                if (u[0] - S0[0] - 172) ** 2 + (u[1] - S0[1] - 165) ** 2 > 122 ** 2:
                    break
            h = cell(b, j)
            m = ((u[0] + h[0]) / 2, min(u[1], h[1]) - 60)
            cv.bezier(u, lerp2(u, m, .75), lerp2(h, m, .75), h, TEAL, .06, 1)
            cv.rrect(u[0] - 2.4, u[1] - 2.4, 4.8, 4.8, 1, None, 1, fill=TEAL, fa=.7)
            k += 1
    label(cv, 600, S0[1] - 20, "140", "hero", TEAL)
    lens(cv, (S0[0] + 3, S0[1] + 3), (S0[0] + 172, S0[1] + 165), 108,
         inner=lambda cv, c, r: (count_block(cv, c[0] - 39, c[1] + 14, 12, 6, 13, 10.5, INK, .9),
                                 label(cv, c[0], c[1] + 62, "12", "approx", INK, "c"),
                                 label(cv, c[0], c[1] - 38, "prior space", "eyebrow", AMBER, "c")))
    count_block(cv, 1100, 520, 12, 4, 14, 11, AMBER)
    label(cv, 1125, 430, "12", "approx", AMBER, "c")
    wire(cv, [(1040, 490), (1086, 490)])
    wire(cv, [(1170, 490), (1250, 490)])
    ax = Axes(cv, (1330, 250, 500, 390), (0, 80), (0, 3), xticks=[0, 20, 40, 60, 80],
              yticks=[1, 2, 3], xlabel="delay (ps)", ylabel="energy (fJ)")
    pts = [(19, 2.3, "headline", "ours-1"), (31, 2.2, "prior"), (33, 1.6, "ours"),
           (48, 1.5, "baseline", "baseline"), (57, .6, "prior"), (61, .6, "ours"),
           (63, 1.0, "prior"), (22, 2.7, "auto")]
    scatter(cv, ax, pts)
    pareto(cv, ax, [(x, y) for x, y, *_ in pts])


def E(cv):
    cv.begin()
    xs = [300 + 110 * k for k in range(6)]
    marker_row(cv, xs, 150, [True] * 5 + [False])
    for x in xs:
        cv.line((x, 190), (x, 560), GRAPHITE, .5, 1.3, [2, 6])
    waveform(cv, 230, 1000, 250, "D", 0, [(xs[2], 1), (xs[5], 0)])
    waveform(cv, 230, 1000, 385, "CK", 1, [(xs[0], 0), (xs[1], 1), (xs[3], 0), (xs[4], 1)])
    waveform(cv, 230, 1000, 520, "Q", 0, [(xs[4] + 10, 1), (xs[5] + 10, 0)],
             col_after=CORAL, after_x=xs[5] + 10)
    cv.line((xs[5] + 10, 488), (1000, 488), BLUE, .9, 2.4, [4, 8])
    label(cv, 1000, 474, "expected Q", "value", BLUE, "r")
    label(cv, 1000, 590, "observed Q", "value", CORAL, "r")
    pipeline(cv, 1260, 270, ["IF", "ID", "EX", "MEM", "WB"],
             [(i, s, i + s + (1 if (i == 2 and s >= 2) else 0), "busy") for i in range(4) for s in range(5)]
             + [(2, 2, 4, "stall")], cw=58, rh=46)


FIGS = {"A_hw_architecture": A, "B_algorithm_step": B, "C_systems_results": C,
        "D_scale_to_pareto": D, "E_circuit_timing": E}
if __name__ == "__main__":
    for nm, fn in FIGS.items():
        print(FK.export(nm, fn, OUT, k=2, pad=30)[0])
