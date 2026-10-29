"""EDL tables for the demo (see scripts/edl.py)."""
T_START = 0.0
SEGMENTS = [  # (t_anim reached, film seconds, note)
    (0.9, 1.6, "root + reference (L01)"),
    (0.9, 1.6, "HOLD reference"),
    (2.0, 1.6, "candidates appear"),
    (2.8, 2.2, "judge: 2 pruned, 2 kept (L02)"),
    (3.4, 1.0, "result"),
    (3.4, 3.2, "HOLD result"),
]
ANCHORS = {
    "L01": (0, None, .4),      # placed at film time 0.4 s
    "L02": (0, 2.0),           # "Two" lands as judging starts
}
SPLITS = {}
