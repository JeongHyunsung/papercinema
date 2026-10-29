"""Word-level timestamps for each narration line.

ASR (sherpa-onnx zipformer) gives a start time per BPE token. Hypothesis words
are matched to the script's spoken (tts) words with difflib; words the ASR got
wrong inherit the time of the aligned hypothesis word; unmatched words are
interpolated. A word ends where the next starts (last: speech end).
  cd narration && python3 align.py      -> words.json ; prints matched/total
"""
import difflib, importlib, json, os, re, sys
import numpy as np, soundfile as sf
from asr import transcribe

sys.path.insert(0, os.getcwd())          # the project narration/ folder
script = importlib.import_module(os.environ.get("SCRIPT", "script"))


def words_of(s):
    return re.findall(r"[A-Za-z0-9'\-]+", s)


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def speech_end(a, sr):
    e = np.convolve(a ** 2, np.ones(240) / 240, "same")
    db = 10 * np.log10(e + 1e-12)
    return np.where(db > db.max() - 40)[0][-1] / sr


def align_line(a, sr, tts):
    txt, toks, ts = transcribe(a, sr)
    hw, ht = [], []
    for tk, t0 in zip(toks, ts):
        if tk.startswith((" ", "▁")) or not hw:
            hw.append(tk.replace("▁", "").strip()); ht.append(t0)
        else:
            hw[-1] += tk
    sw = words_of(tts)
    parts = [(i, p) for i, w in enumerate(sw) for p in w.split("-") if p]
    sm = difflib.SequenceMatcher(a=[norm(p) for _, p in parts],
                                 b=[norm(w) for w in hw], autojunk=False)
    pt = [None] * len(parts)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                pt[i1 + k] = ht[j1 + k]
        elif tag == "replace":
            pt[i1] = ht[j1]
    st = [None] * len(sw)
    for (i, _), t in zip(parts, pt):
        if st[i] is None and t is not None:
            st[i] = t
    end = speech_end(a, sr)
    if st[0] is None:
        st[0] = 0.0
    known = [(i, t) for i, t in enumerate(st) if t is not None]
    for i in range(len(sw)):
        if st[i] is None:
            lo = max((k for k in known if k[0] < i), key=lambda k: k[0])
            hi = min((k for k in known if k[0] > i), key=lambda k: k[0],
                     default=(len(sw), end))
            st[i] = lo[1] + (hi[1] - lo[1]) * (i - lo[0]) / (hi[0] - lo[0])
    st = list(np.maximum.accumulate(np.array(st, float)))
    words = [dict(w=w, t0=round(st[i], 3),
                  t1=round(st[i + 1] if i + 1 < len(sw) else end, 3))
             for i, w in enumerate(sw)]
    return dict(asr=txt.lower(), matched=sum(t is not None for t in pt),
                parts=len(parts), words=words, speech_end=round(end, 3))


if __name__ == "__main__":
    out = {}
    for L in script.LINES:
        a, sr = sf.read(f"lines/{L['id']}.wav", dtype="float32")
        out[L["id"]] = r = align_line(a, sr, L["tts"])
        print(L["id"], f"{r['matched']}/{r['parts']}", "|", r["asr"])
    json.dump(out, open("words.json", "w"), indent=1)
