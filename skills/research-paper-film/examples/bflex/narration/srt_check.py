"""QA: each subtitle cue vs ASR of the delivered film's own audio in that cue window."""
import sys, re, numpy as np, soundfile as sf
from asr import transcribe
wav, srt, out = sys.argv[1], sys.argv[2], sys.argv[3]
a, sr = sf.read(wav, dtype="float32")
def ts(s):
    h, m, r = s.split(":"); sec, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
cues = []
for b in open(srt).read().strip().split("\n\n"):
    ls = b.split("\n"); t0, t1 = [ts(x.strip()) for x in ls[1].split("-->")]; cues.append((t0, t1, " ".join(ls[2:])))
num = {"0": "zero", "1": "one", "20,000": "twenty thousand", "468": "four hundred sixty eight",
       "568": "five hundred sixty eight", "0.9": "zero point nine", "2.53": "two point five three"}
def norm(s):
    s = s.lower()
    for k, v in sorted(num.items(), key=lambda x: -len(x[0])):
        s = re.sub(r"(?<![\w.])" + re.escape(k) + r"(?![\w])", v, s)
    s = s.replace("segen-20", "see jen twenty").replace("segen", "see jen").replace("b-flex", "bee flex").replace("ff1", "f f one").replace("-", " ")
    return re.sub(r"[^a-z' ]", " ", s).split()
def wer(r, h):
    d = np.arange(len(h) + 1)
    for i, x in enumerate(r, 1):
        p = d.copy(); d[0] = i
        for j, y in enumerate(h, 1): d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (x != y))
    return d[-1]
E = N = 0; rows = []
for t0, t1, txt in cues:
    hyp = transcribe(a[int(max(0, t0 - .1) * sr):int((t1 + .1) * sr)], sr)[0].lower()
    r = norm(txt); e = wer(r, norm(hyp)); E += e; N += len(r)
    rows.append(f"{t0:7.2f}-{t1:6.2f} | {e:2d}/{len(r):2d} | SRT: {txt}\n{'':23s}ASR: {hyp}")
open(out, "w").write("\n".join(rows) + f"\nTOTAL word differences: {E}/{N}\n")
print("\n".join(rows)); print("TOTAL", E, N)
