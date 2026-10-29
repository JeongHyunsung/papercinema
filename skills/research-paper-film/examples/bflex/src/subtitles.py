"""SRT subtitles from the placed narration (word-level timings)."""
import re, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "narration"))
import edl, script
MAXC = 42                         # characters per subtitle line (2 lines max)


def chunks(text):
    """Sentences first; long sentences split at clause punctuation."""
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if len(sent) <= 2 * MAXC - 4:
            out.append(sent); continue
        cur = ""
        for p in re.split(r"(?<=[:;,])\s+", sent):
            if cur and len(cur) + 1 + len(p) > 2 * MAXC - 4:
                out.append(cur); cur = p
            else:
                cur = (cur + " " + p).strip()
        if cur: out.append(cur)
    return out


def wrap(s):
    if len(s) <= MAXC: return s
    w, best = s.split(), None
    for k in range(1, len(w)):
        if w[k] == "=" or w[k - 1] == "=":
            continue
        a, b = " ".join(w[:k]), " ".join(w[k:])
        sc = max(len(a), len(b))
        if best is None or sc < best[0]: best = (sc, a + "\n" + b)
    return best[1]


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


SPOKEN = [("SeGen-20", "See-Jen twenty"), ("SeGen", "See-Jen"), ("B-Flex", "Bee-Flex"),
          ("FF1", "F F one"), ("20,000", "twenty thousand"), ("468", "four hundred sixty-eight"),
          ("568", "five hundred sixty-eight"), ("0.9", "zero point nine"),
          ("2.53", "two point five three"), ("Q", "queue"), ("D", "dee")]


def n_spoken(text):
    """Number of spoken (TTS) words a piece of subtitle text corresponds to."""
    t = text
    for a, b in SPOKEN:
        t = re.sub(r"(?<![\w.,-])" + re.escape(a) + r"(?![\w-])", b, t)
    return len(re.findall(r"[A-Za-z0-9'\-]+", t))


def build():
    subs = {l["id"]: l["sub"] for l in script.LINES}
    words = {}
    for c in edl.clips():
        words.setdefault(c["line"], []).extend(c["words"])
    cues = []
    for lid, sub in subs.items():
        ws = words[lid]; n = len(ws)
        ch = chunks(sub)
        counts = [n_spoken(c) for c in ch]
        assert sum(counts) == n, (lid, counts, n, [w["w"] for w in ws])
        k = 0
        for c, m in zip(ch, counts):
            cues.append([ws[k]["t0"] - .05, ws[k + m - 1]["t1"] + .12, wrap(c)])
            k += m
    for a, b in zip(cues, cues[1:]):          # no overlaps, min duration 1 s
        a[1] = min(max(a[1], a[0] + 1.0), b[0] - .04)
    return cues


if __name__ == "__main__":
    cues = build()
    out = sys.argv[1] if len(sys.argv) > 1 else "../out/final_v4/BFlex_DAC2026_film_v4.en.srt"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        for k, (a, b, s) in enumerate(cues, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
    print(out, len(cues), "cues")
