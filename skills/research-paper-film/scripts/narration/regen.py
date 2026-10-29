"""Regenerate only the given lines with the same voice settings; keep the rest
byte-identical.   cd narration && python3 regen.py L04 L08
(VOICE/SPEED must match the original run; they are read from lines.json.)"""
import json, os, sys
import soundfile as sf
meta = json.load(open("lines.json"))
os.environ.setdefault("VOICE", meta["voice"])
os.environ.setdefault("SPEED", str(meta["speed"]))
import narrate                                   # noqa: E402
from tts_kokoro import synth                     # noqa: E402

L = {l["id"]: l for l in narrate.script.LINES}
for i in sys.argv[1:]:
    a, sr = synth(L[i]["tts"], narrate.VOICE, narrate.SPEED)
    a = narrate.trim(a)
    sf.write(f"lines/{i}.wav", a, sr)
    print(i, round(len(a) / sr, 2))
durs = [sf.info(f"lines/{l['id']}.wav").duration for l in narrate.script.LINES]
meta["lines"] = narrate.layout(durs)
json.dump(meta, open("lines.json", "w"), indent=1)
print("now re-run align.py and check edl.py for overlaps")
