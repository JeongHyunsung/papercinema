"""Regenerate only the given narration lines with the V4 voice settings; keep the rest."""
import sys, json, numpy as np, soundfile as sf, script
from tts_kokoro import synth
from narrate import trim, VOICE, SPEED, SR
ids = sys.argv[1:]
L = {l["id"]: l for l in script.LINES}
for i in ids:
    a, sr = synth(L[i]["tts"], VOICE, SPEED); assert sr == SR
    a = trim(a); sf.write(f"lines/{i}.wav", a, SR); print(i, round(len(a) / SR, 2))
# rebuild lines.json durations from the files on disk
lines, t = [], 1.0
for l in script.LINES:
    d = sf.info(f"lines/{l['id']}.wav").duration
    lines.append(dict(id=l["id"], start=round(t, 3), end=round(t + d, 3), sub=l["sub"], tts=l["tts"])); t += d + l["gap"]
meta = json.load(open("lines.json")); meta["lines"] = lines
json.dump(meta, open("lines.json", "w"), indent=1)
