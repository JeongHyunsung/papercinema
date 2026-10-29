"""SRT subtitles from the placed narration (word-level film times).

Cue = sentence; long sentences split at clause punctuation; wrap to <= 42
chars x 2 lines. Cue times come from the aligned words, counted by SPOKEN
words (the script's SPOKEN table maps printed tokens such as '568' to spoken
words); the counts are asserted, so a cue boundary can never fall
mid-sentence. Min 1 s per cue, no overlaps.
  python3 subtitles.py out/final/NAME.en.srt
"""
import importlib, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "narration"))
import edl                                                     # noqa: E402
from textnorm import n_spoken                                   # noqa: E402

sys.path.insert(0, edl.NAR)
script = importlib.import_module(os.environ.get("SCRIPT", "script"))
TABLE = getattr(script, "SPOKEN", [])
MAXC = 42


def chunks(text):
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
        if cur:
            out.append(cur)
    return out


def wrap(s):
    if len(s) <= MAXC:
        return s
    w, best = s.split(), None
    for k in range(1, len(w)):
        if "=" in (w[k], w[k - 1]):
            continue
        a, b = " ".join(w[:k]), " ".join(w[k:])
        if best is None or max(len(a), len(b)) < best[0]:
            best = (max(len(a), len(b)), a + "\n" + b)
    return best[1] if best else s


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build():
    words = {}
    for c in edl.clips():
        words.setdefault(c["line"], []).extend(c["words"])
    cues = []
    for L in script.LINES:
        ws = words[L["id"]]
        ch = chunks(L["sub"])
        counts = [n_spoken(c, TABLE) for c in ch]
        assert sum(counts) == len(ws), (L["id"], counts, len(ws),
                                        "add the missing print->spoken pair to SPOKEN")
        k = 0
        for c, m in zip(ch, counts):
            cues.append([ws[k]["t0"] - .05, ws[k + m - 1]["t1"] + .12, wrap(c)])
            k += m
    for a, b in zip(cues, cues[1:]):
        a[1] = min(max(a[1], a[0] + 1.0), b[0] - .04)
    return cues


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/film.en.srt"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cues = build()
    with open(out, "w") as f:
        for k, (a, b, s) in enumerate(cues, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
    print(out, len(cues), "cues")
