"""Generate the narration line by line, trim, assemble with edited gaps, align words."""
import json, re, sys, numpy as np, soundfile as sf, script
from tts_kokoro import synth
from asr import transcribe
import os
VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "0.9"))
SR = 24000
LEAD = 1.0                                     # silence before L01 (s); film retimes around it
def trim(a, thr_db=-45):
    e = np.convolve(a**2, np.ones(240)/240, "same"); db = 10*np.log10(e+1e-12)
    idx = np.where(db > db.max() + thr_db)[0]
    s, t = max(idx[0]-240, 0), min(idx[-1]+480, len(a))
    return a[s:t]
def main():
    parts, lines, t = [np.zeros(int(LEAD*SR), np.float32)], [], LEAD
    for L in script.LINES:
        a, sr = synth(L["tts"], VOICE, SPEED); assert sr == SR
        a = trim(a)
        sf.write(f"lines/{L['id']}.wav", a, SR)
        d = len(a)/SR
        lines.append(dict(id=L["id"], start=round(t, 3), end=round(t+d, 3), sub=L["sub"], tts=L["tts"]))
        parts += [a, np.zeros(int(L["gap"]*SR), np.float32)]
        t += d + L["gap"]
        print(L["id"], round(d, 2), file=sys.stderr)
    full = np.concatenate(parts + [np.zeros(int(.5*SR), np.float32)])
    sf.write("narration_raw.wav", full, SR)
    json.dump(dict(voice=VOICE, speed=SPEED, engine="Kokoro-82M v1.0 (kokoro-onnx 0.6.1)", sr=SR,
                   duration=round(len(full)/SR, 3), lines=lines), open("lines.json", "w"), indent=1)
    print("total", round(len(full)/SR, 2))
if __name__ == "__main__":
    import os; os.makedirs("lines", exist_ok=True); main()
