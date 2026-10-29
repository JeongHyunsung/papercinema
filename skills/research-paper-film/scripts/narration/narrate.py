"""Synthesize the narration line by line, trim silence, assemble with gaps.

  cd narration && VOICE=af_heart SPEED=0.9 python3 narrate.py
Outputs: lines/<id>.wav, lines.json (start/end of each line in the raw
assembly), narration_raw.wav (for listening). Script module: $SCRIPT (default
'script').
"""
import importlib, json, os, sys
import numpy as np, soundfile as sf
from tts_kokoro import synth

sys.path.insert(0, os.getcwd())          # the project narration/ folder
script = importlib.import_module(os.environ.get("SCRIPT", "script"))
VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "0.9"))
SR = 24000
LEAD = 1.0                       # silence before the first line in the raw file


def trim(a, thr_db=-45):
    e = np.convolve(a ** 2, np.ones(240) / 240, "same")
    db = 10 * np.log10(e + 1e-12)
    idx = np.where(db > db.max() + thr_db)[0]
    s, t = max(idx[0] - 240, 0), min(idx[-1] + 480, len(a))
    return a[s:t]


def layout(durs):
    """lines.json entries from per-line durations (same as narrate)."""
    out, t = [], LEAD
    for L, d in zip(script.LINES, durs):
        out.append(dict(id=L["id"], start=round(t, 3), end=round(t + d, 3),
                        sub=L["sub"], tts=L["tts"]))
        t += d + L["gap"]
    return out


def main():
    os.makedirs("lines", exist_ok=True)
    parts, durs = [np.zeros(int(LEAD * SR), np.float32)], []
    for L in script.LINES:
        a, sr = synth(L["tts"], VOICE, SPEED)
        assert sr == SR, sr
        a = trim(a)
        sf.write(f"lines/{L['id']}.wav", a, SR)
        durs.append(len(a) / SR)
        parts += [a, np.zeros(int(L["gap"] * SR), np.float32)]
        print(L["id"], round(durs[-1], 2), file=sys.stderr)
    full = np.concatenate(parts + [np.zeros(int(.5 * SR), np.float32)])
    sf.write("narration_raw.wav", full, SR)
    json.dump(dict(voice=VOICE, speed=SPEED, engine="Kokoro-82M v1.0 (kokoro-onnx)",
                   sr=SR, duration=round(len(full) / SR, 3), lines=layout(durs)),
              open("lines.json", "w"), indent=1)
    print("total", round(len(full) / SR, 2))


if __name__ == "__main__":
    main()
