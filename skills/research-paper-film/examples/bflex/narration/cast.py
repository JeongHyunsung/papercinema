import sys, numpy as np, soundfile as sf, script
from tts_kokoro import synth
L = {l["id"]: l for l in script.LINES}
text = " ".join(L[i]["tts"] for i in ["L01", "L08", "L11", "L16", "L17"])
voices = sys.argv[1:]
for v in voices:
    lang = "en-gb" if v[0] == "b" else "en-us"
    a, sr = synth(text, v, 1.0, lang)
    sf.write(f"casting/{v}.wav", a, sr)
    print(v, sr, round(len(a)/sr, 2))
