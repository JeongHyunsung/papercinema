"""QA: is every narration clip still intelligible in the final mix?
ASR transcript of the clip cut from mix.wav vs the same clip from narration.wav."""
import json, re, numpy as np, soundfile as sf
from asr import transcribe
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "out", "audio_v4") + "/"
mix, sr = sf.read(P + "mix.wav", dtype="float32"); mix = mix.mean(1)
nar, _ = sf.read(P + "narration.wav", dtype="float32"); nar = nar.mean(1)
clips = json.load(open(P + "placement.json"))["clips"]
def norm(s): return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()
def wer(r, h):
    d = np.arange(len(h) + 1)
    for i, x in enumerate(r, 1):
        p = d.copy(); d[0] = i
        for j, y in enumerate(h, 1): d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (x != y))
    return d[-1], len(r)
E = T = 0
rows = []
for c in clips:
    a, b = int((c["start"] - .1) * sr), int((c["end"] + .1) * sr)
    tn = transcribe(nar[a:b], sr)[0]; tm = transcribe(mix[a:b], sr)[0]
    e, n = wer(norm(tn), norm(tm)); E += e; T += n
    rows.append((c["id"], e, n, tm.lower()))
    print(f"{c['id']:5s} diff {e}/{n}  | {tm.lower()}")
print(f"mix-vs-narration word difference: {E}/{T} = {100*E/T:.1f}%")
