"""v4 edit decision list: narration-first retiming.

The v3 animation is driven by its own clock t3 (the timing sheet in film.py).
The v4 film clock t4 drives it through a monotone piecewise-linear map
t3 = W(t4), authored here as SEGMENTS. A slope of 1 plays the v3 motion at its
designed speed; a small slope is a hold (the screen is already settled there,
so a label or result stays readable); a slope near 0.5 is a moderate move.
Narration is never stretched: every clip is placed at its natural speed and
anchored by one of its words to a v3 event, so the word lands on the event.

Narration clips are lines of narration/script.py (or a line split at a
sentence pause: "L04a" / "L04b").
"""
import json, os, bisect

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NAR = os.path.join(ROOT, "narration")

# (v3 end time, v4 duration, note).  Starts at t4 = 0, t3 = T3_START.
T3_START = 0.6
SEGMENTS = [
    # ---- Act I: the challenge
    (1.60, 2.3, "pin labels fade in (L01)"),
    (1.75, 1.3, "hold: D, CK, Q"),
    (4.00, 5.1, "test vector applied, checks 1-6 (L01-L02)"),
    (4.50, 2.15, "anticipation: rewind to transition 6"),
    (5.20, 1.9, "action: D falls instead of CK; Q goes wrong"),
    (5.95, 2.1, "HOLD consequence: expected Q vs SeGen-20 (L03)"),
    (7.45, 1.9, "pull back; SeGen-20's states fly into the square"),
    (8.20, 1.7, "square settles (2-bit count removed in v4: too brief)"),
    (8.85, .8, "extrude to 3 bits"),
    (9.95, 5.3, "HOLD 3-bit count, prior search stops, brute force"),
    (10.67, .8, "collapse into the wordmark"),
    (11.30, 1.2, "title"),
    (11.70, 2.0, "HOLD title + tagline (L06)"),
    (11.85, .3, "title out"),
    # ---- Act II: the idea
    (14.25, 3.6, "reference graph builds (L07)"),
    (14.30, 2.1, "hold full graph"),
    (16.40, 3.0, "Act I's vector replayed, markers 1-6 (L08)"),
    (16.90, .6, "consequence labels appear"),
    (17.00, 3.6, "HOLD reference: Q = 1 / SeGen-20 output: Q = 0"),
    (17.05, .4, "settle"),
    (19.00, 2.4, "tilt; nodes lift and split into states (L09)"),
    (19.45, .8, "second callout"),
    (19.55, 2.2, "HOLD callouts Q=0 -> 01,11 / Q=1 -> 00,10"),
    (19.95, .5, "delta panel arrives"),
    # ---- Act III: inside the algorithm
    (21.20, 1.4, "STEP 1 start pair + tether to row 7"),
    (21.55, 1.5, "HOLD start-pair annotations"),
    (21.85, .4, "settle"),
    (22.40, .55, "camera to step 2"),
    (23.00, 2.1, "anticipation: CK falls -> Q must stay 0 (L10)"),
    (23.95, 1.15, "four candidate destinations"),
    (24.70, 2.2, "consequence: Q=1 candidates, no reference edge"),
    (25.25, .55, "branches retract"),
    (25.95, 1.3, "HOLD wrong output -> branch pruned"),
    (28.00, 1.5, "STEP 3 X1 / X2"),
    (28.90, .8, "both branches kept"),
    (30.20, 1.1, "STEP 4 fast-forward (repetition)"),
    (30.85, .65, "camera push to the conflict (L11)"),
    (31.45, 1.1, "anticipation: CK rises with D = 1"),
    (32.95, 1.6, "path 01 -> 11, infer delta(11,01)"),
    (33.60, 2.0, "consequence: earlier edge fixed delta(11,11) = 11"),
    (34.05, .5, "branch retracts"),
    (34.60, 2.8, "HOLD conflict reasoning"),
    (36.70, 2.1, "PiP -> remaining 2-bit tree grows (L12)"),
    (37.60, 2.1, "HOLD 18 valid, 162 s -> 0.00784 s"),
    # ---- Act IV: impact
    (39.15, 2.3, "leaves become cells"),
    (42.55, 3.4, "CLIMAX 1 fill + pull-back (L13), slope 1"),
    (44.55, 4.2, "impact hold: number, vs 18, 786 s / 16 threads"),
    (46.65, 4.1, "468 with C_FF <= 20 (L14)"),
    (47.10, .6, "block"),
    (47.80, 2.8, "HOLD 20 synthesized to transistor level"),
    (48.45, .65, "dive into FF1"),
    (49.85, 1.05, "FF1 fast steps (L15)"),
    (51.35, 1.95, "capture 101 -> 100 -> 000"),
    (51.60, 3.45, "HOLD Q = not s2 = 1, then capture flash"),
    (52.40, 1.7, "race start line + conditions (L16)"),
    (55.35, 2.95, "race at slope 1 (20 ps per second), bracket"),
    (56.80, 4.0, "HOLD 2.53x lower sequencing overhead"),
    (59.00, 4.6, "scatter: energy cost, all 18 FFs (L17)"),
    # ---- Act V
    (62.20, 5.9, "title card (L18)"),
]

# clip id -> (anchor word index within the clip, v3 event time)
ANCHORS = {
    "L01": (0, None, .45),          # (word, None, absolute t4) : placed by time
    "L02": (7, 3.63),               # "passes" on the 6th check
    "L03": (6, 5.0),                # "zero" as Q goes wrong
    "L04a": (0, 6.1),               # "Every" as the pull-back starts
    "L04b": (1, 8.3),               # "three" as the cube extrudes
    "L05": (0, 9.78),               # "Beyond" with the brute-force line
    "L06": (0, 10.8),              # "Bee-Flex" on the wordmark
    "L07": (1, 12.1),               # "reference" as the graph starts
    "L08": (0, 14.3),               # "The failing vector" with marker 1
    "L09": (0, 17.25),              # "Candidates" as nodes lift
    "L10": (2, 22.45),              # "clock" at the anticipation
    "L11": (0, 30.25),              # "Deeper" on the push-in
    "L12": (0, 34.8),               # "Pruning" as the tree grows
    "L13": (10, 42.4),               # "million" as the counter lands
    "L14": (0, 44.75),              # "Twenty" over the histogram
    "L15": (4, 48.35),               # "F F one" as FF1 appears
    "L16": (1, 51.75),              # "spice" with the conditions
    "L17": (0, 57.2),               # "at a higher energy cost" with the scatter
    "L18": (0, 59.3),               # "Bee-Flex" on the title card
}
SPLITS = {"L04": ("L04a", "L04b", 9)}   # split before word 6 ("With")

# ------------------------------------------------------------------ warp ----
_K4, _K3 = [0.0], [T3_START]
for t3, d4, _ in SEGMENTS:
    _K4.append(_K4[-1] + d4)
    _K3.append(t3)
DURATION = _K4[-1]


def warp(t4):
    """v4 time -> v3 time."""
    if t4 <= 0:
        return T3_START + t4          # pre-roll (unused)
    if t4 >= DURATION:
        return _K3[-1] + (t4 - DURATION)
    j = bisect.bisect_right(_K4, t4) - 1
    a4, b4, a3, b3 = _K4[j], _K4[j + 1], _K3[j], _K3[j + 1]
    return a3 + (b3 - a3) * (t4 - a4) / (b4 - a4)


def inv(t3):
    """v3 time -> earliest v4 time showing it."""
    if t3 <= T3_START:
        return 0.0
    j = bisect.bisect_left(_K3, t3)
    if j >= len(_K3):
        return DURATION
    a4, b4, a3, b3 = _K4[j - 1], _K4[j], _K3[j - 1], _K3[j]
    return a4 + (b4 - a4) * (t3 - a3) / (b3 - a3)


def slope(t4):
    return (warp(t4 + .01) - warp(t4 - .01)) / .02


# ------------------------------------------------------------ narration ----
def clips():
    """Narration clips with v4 placement and per-word v4 times."""
    words = json.load(open(os.path.join(NAR, "words.json")))
    lines = json.load(open(os.path.join(NAR, "lines.json")))["lines"]
    out = []
    for L in lines:
        wl = words[L["id"]]["words"]
        dur = L["end"] - L["start"]
        if L["id"] in SPLITS:
            a, b, k = SPLITS[L["id"]]
            cut = (wl[k - 1]["t1"] + wl[k]["t0"]) / 2
            cut = wl[k]["t0"] - .08
            parts = [(a, 0.0, cut, wl[:k]), (b, cut, dur, wl[k:])]
        else:
            parts = [(L["id"], 0.0, dur, wl)]
        for cid, s0, s1, ws in parts:
            an = ANCHORS[cid]
            if an[1] is None:
                start = an[2]
            else:
                start = inv(an[1]) - (ws[an[0]]["t0"] - s0)
            out.append(dict(
                id=cid, line=L["id"], src=s0, src_end=s1, start=round(start, 3),
                end=round(start + s1 - s0, 3),
                text=" ".join(w["w"] for w in ws),
                words=[dict(w=w["w"], t0=round(start + w["t0"] - s0, 3),
                            t1=round(start + min(w["t1"], s1) - s0, 3))
                       for w in ws]))
    return out


def check():
    cs = clips()
    ok = True
    for a, b in zip(cs, cs[1:]):
        g = b["start"] - a["end"]
        flag = "  <-- OVERLAP" if g < .2 else ""
        ok &= g >= .2
        print(f"{a['id']:5s} {a['start']:7.2f}-{a['end']:7.2f}  gap {g:5.2f}{flag}")
    print(f"{cs[-1]['id']:5s} {cs[-1]['start']:7.2f}-{cs[-1]['end']:7.2f}  tail {DURATION - cs[-1]['end']:.2f}")
    print("DURATION", round(DURATION, 2), "ok" if ok else "FIX")
    return ok


if __name__ == "__main__":
    check()
