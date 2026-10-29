"""QA: each subtitle cue vs ASR of the delivered file's own audio in that window.
  ffmpeg -i film.mp4 -ac 1 -ar 16000 audio.wav
  python3 srt_check.py audio.wav film.en.srt report.txt
Printed tokens are normalized with SPOKEN from the narration script.
"""
import importlib, os, sys
import soundfile as sf
from asr import transcribe
from textnorm import spoken, words, edits

sys.path.insert(0, os.getcwd())          # the project narration/ folder
script = importlib.import_module(os.environ.get("SCRIPT", "script"))
TABLE = getattr(script, "SPOKEN", [])
wav, srt, out = sys.argv[1:4]
a, sr = sf.read(wav, dtype="float32")
a = a.mean(1) if a.ndim > 1 else a


def ts(s):
    h, m, r = s.strip().split(":"); sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


rows, E, N = [], 0, 0
for b in open(srt).read().strip().split("\n\n"):
    ls = b.split("\n")
    t0, t1 = [ts(x) for x in ls[1].split("-->")]
    txt = " ".join(ls[2:])
    hyp = transcribe(a[int(max(0, t0 - .1) * sr):int((t1 + .1) * sr)], sr)[0]
    r, h = words(spoken(txt, TABLE)), words(hyp)
    e = edits(r, h); E += e; N += len(r)
    rows.append(f"{t0:7.2f}-{t1:6.2f} | {e:2d}/{len(r):2d} | SRT: {txt}\n"
                f"{'':23s}ASR: {hyp.lower()}")
rep = "\n".join(rows) + f"\nTOTAL word differences: {E}/{N}\n"
open(out, "w").write(rep)
print(rep)
