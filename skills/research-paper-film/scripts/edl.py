"""Narration-first retiming (edit decision list).

Put your tables in an `edl_config.py` next to film.py (T_START, SEGMENTS,
ANCHORS, SPLITS); this module imports it. Without one, the example tables
below are used. Narration files are read from ../narration (override with
the NARRATION_DIR environment variable).

The animation keeps its own designed clock t_anim (timing constants in
film.py). The film clock t drives it through a monotone piecewise-linear map
t_anim = warp(t), authored as SEGMENTS:
  slope 1   designed speed (REQUIRED where duration encodes data)
  slope ~0  hold: the screen is settled, text stays readable
  slope .5  moderate move
Narration is never stretched: each clip is placed at natural speed, anchored
by one of its words to the animation event it names.

  python3 edl.py      -> clip table with gaps; flags overlaps (< 0.2 s)
Fix an overlap by lengthening the segment *before* the clip.
"""
import bisect, json, os, sys

NAR = os.environ.get("NARRATION_DIR", os.path.join(os.getcwd(), "..", "narration"))

# ---- EDIT: (t_anim reached, film seconds it takes, note); starts at T_START
T_START = 0.0
SEGMENTS = [
    (1.0, 1.5, "title builds (L01)"),
    (1.0, 1.2, "HOLD"),
    (3.0, 2.0, "mechanism at designed speed"),
    (3.0, 2.5, "HOLD result (L02)"),
]
# ---- EDIT: clip -> (anchor word index, t_anim event)  or  (idx, None, film t)
ANCHORS = {
    "L01": (0, None, .4),
    "L02": (2, 3.0),
}
# ---- EDIT: split a line into two clips before word k (a sentence pause)
SPLITS = {}          # e.g. {"L04": ("L04a", "L04b", 9)}

sys.path.insert(1, os.getcwd())         # run from the project's src/
try:                                    # project tables override the examples
    import edl_config as _cfg
except ImportError as _e:
    if _e.name != "edl_config":
        raise
    print("edl.py: no edl_config.py found - using the EXAMPLE tables", file=sys.stderr)
else:
    T_START = getattr(_cfg, "T_START", T_START)
    SEGMENTS = getattr(_cfg, "SEGMENTS", SEGMENTS)
    ANCHORS = getattr(_cfg, "ANCHORS", ANCHORS)
    SPLITS = getattr(_cfg, "SPLITS", SPLITS)

_KF, _KA = [0.0], [T_START]
for ta, df, _ in SEGMENTS:
    _KF.append(_KF[-1] + df)
    _KA.append(ta)
DURATION = _KF[-1]


def warp(t):
    """film time -> animation time."""
    if t <= 0:
        return T_START + t
    if t >= DURATION:
        return _KA[-1] + (t - DURATION)
    j = bisect.bisect_right(_KF, t) - 1
    a, b, A, B = _KF[j], _KF[j + 1], _KA[j], _KA[j + 1]
    return A + (B - A) * (t - a) / (b - a)


def inv(ta):
    """animation time -> earliest film time showing it."""
    if ta <= T_START:
        return 0.0
    j = bisect.bisect_left(_KA, ta)
    if j >= len(_KA):
        return DURATION
    a, b, A, B = _KF[j - 1], _KF[j], _KA[j - 1], _KA[j]
    return a + (b - a) * (ta - A) / (B - A) if B > A else a


def slope(t):
    return (warp(t + .01) - warp(t - .01)) / .02


def clips():
    """Narration clips with film-time placement and per-word film times."""
    words = json.load(open(os.path.join(NAR, "words.json")))
    lines = json.load(open(os.path.join(NAR, "lines.json")))["lines"]
    out = []
    for L in lines:
        wl = words[L["id"]]["words"]
        dur = L["end"] - L["start"]
        if L["id"] in SPLITS:
            a, b, k = SPLITS[L["id"]]
            cut = wl[k]["t0"] - .08
            parts = [(a, 0.0, cut, wl[:k]), (b, cut, dur, wl[k:])]
        else:
            parts = [(L["id"], 0.0, dur, wl)]
        for cid, s0, s1, ws in parts:
            an = ANCHORS[cid]
            start = an[2] if an[1] is None else inv(an[1]) - (ws[an[0]]["t0"] - s0)
            out.append(dict(
                id=cid, line=L["id"], src=s0, src_end=s1, start=round(start, 3),
                end=round(start + s1 - s0, 3), text=" ".join(w["w"] for w in ws),
                words=[dict(w=w["w"], t0=round(start + w["t0"] - s0, 3),
                            t1=round(start + min(w["t1"], s1) - s0, 3)) for w in ws]))
    return out


def timing_sheet():
    """Markdown: each segment with film-time range and slope."""
    rows = ["| film t | anim t | slope | note |", "|---|---|---|---|"]
    t = 0.0
    for (ta, df, note), a0 in zip(SEGMENTS, _KA):
        s = (ta - a0) / df if df else 0
        rows.append(f"| {t:6.2f}–{t + df:6.2f} | {a0:6.2f}→{ta:6.2f} | {s:4.2f} | {note} |")
        t += df
    return "\n".join(rows)


def check():
    cs = clips()
    ok = True
    for a, b in zip(cs, cs[1:]):
        g = b["start"] - a["end"]
        ok &= g >= .2
        print(f"{a['id']:6s} {a['start']:7.2f}-{a['end']:7.2f}  gap {g:5.2f}"
              + ("  <-- OVERLAP" if g < .2 else ""))
    c = cs[-1]
    print(f"{c['id']:6s} {c['start']:7.2f}-{c['end']:7.2f}  tail {DURATION - c['end']:.2f}")
    if cs[0]["start"] < 0 or c["end"] > DURATION:
        ok = False
        print("clip outside the film")
    print("DURATION", round(DURATION, 2), "ok" if ok else "FIX")
    return ok


if __name__ == "__main__":
    check()
