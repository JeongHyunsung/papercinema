"""Word-level alignment of each narration line.

The ASR (sherpa-onnx zipformer transducer) gives a start time for every BPE
token. Hypothesis words are matched to the script's spoken words (tts text)
with an edit-distance alignment; script words the ASR misspelled inherit the
time of the hypothesis word they align to; any unmatched word is interpolated.
Word end = next word start (or the line's speech end).
"""
import json, re, difflib, numpy as np, soundfile as sf, script
from asr import transcribe
def words_of(s):
    return [w for w in re.findall(r"[A-Za-z0-9'\-]+", s)]
def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())
def speech_end(a, sr):
    e = np.convolve(a**2, np.ones(240)/240, "same"); db = 10*np.log10(e+1e-12)
    return np.where(db > db.max()-40)[0][-1]/sr
out = {}
for L in script.LINES:
    a, sr = sf.read(f"lines/{L['id']}.wav", dtype="float32")
    txt, toks, ts = transcribe(a, sr)
    hw, ht = [], []
    for tk, t0 in zip(toks, ts):
        if tk.startswith((" ", "▁")) or not hw:
            hw.append(tk.replace("▁", "").strip()); ht.append(t0)
        else:
            hw[-1] += tk
    # script words: split hyphenated words for matching, keep display word groups
    sw = words_of(L["tts"])
    parts = [(i, p) for i, w in enumerate(sw) for p in w.split("-") if p]
    sm = difflib.SequenceMatcher(a=[norm(p) for _, p in parts], b=[norm(w) for w in hw], autojunk=False)
    pt = [None]*len(parts)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2-i1 == j2-j1):
            for k in range(i2-i1): pt[i1+k] = ht[j1+k]
        elif tag == "replace":
            for k in range(i2-i1): pt[i1+k] = ht[j1 + min(k*(j2-j1)//(i2-i1), j2-j1-1)] if k == 0 else None
    # word start = first part's time; interpolate gaps
    st = [None]*len(sw)
    for (i, _), t in zip(parts, pt):
        if st[i] is None and t is not None: st[i] = t
    end = speech_end(a, sr)
    known = [(i, t) for i, t in enumerate(st) if t is not None]
    if st[0] is None: st[0] = 0.0; known.insert(0, (0, 0.0))
    for i in range(len(sw)):
        if st[i] is None:
            lo = max((k for k in known if k[0] < i), key=lambda k: k[0])
            hi = min((k for k in known if k[0] > i), key=lambda k: k[0], default=(len(sw), end))
            st[i] = lo[1] + (hi[1]-lo[1])*(i-lo[0])/(hi[0]-lo[0])
    st = list(np.maximum.accumulate(np.array(st, float)))
    words = [dict(w=w, t0=round(st[i], 3), t1=round(st[i+1] if i+1 < len(sw) else end, 3)) for i, w in enumerate(sw)]
    out[L["id"]] = dict(asr=txt.lower(), matched=sum(t is not None for t in pt), parts=len(parts), words=words, speech_end=round(end, 3))
    print(L["id"], f"{out[L['id']]['matched']}/{len(parts)}", "|", txt.lower())
json.dump(out, open("words.json", "w"), indent=1)
