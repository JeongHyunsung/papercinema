"""Voice casting: synthesize one passage with many voices and score them.

  cd narration && python3 cast_eval.py af_heart af_bella am_michael bf_emma ...
Passage = the tts text of $CAST_LINES (comma-separated ids; default: first 5).
Metrics per voice (casting/metrics.json):
  wer        ASR word error rate vs the script (intelligibility)
  wpm        speaking rate
  f0_med     median pitch (Hz); pitch_range_st = 10-90 % range in semitones
  pause      share of low-energy frames
Choose with these numbers plus listening notes; record in VOICE_CASTING.md.
"""
import importlib, json, os, sys
import numpy as np, soundfile as sf
from tts_kokoro import synth
from asr import transcribe
from textnorm import words, edits

sys.path.insert(0, os.getcwd())          # the project narration/ folder
script = importlib.import_module(os.environ.get("SCRIPT", "script"))
L = {l["id"]: l for l in script.LINES}
ids = os.environ.get("CAST_LINES", ",".join(list(L)[:5])).split(",")
text = " ".join(L[i]["tts"] for i in ids)
os.makedirs("casting", exist_ok=True)
out = {}
for v in sys.argv[1:]:
    lang = "en-gb" if v[0] == "b" else "en-us"
    a, sr = synth(text, v, float(os.environ.get("SPEED", "1.0")), lang)
    sf.write(f"casting/{v}.wav", a, sr)
    hyp = transcribe(a, sr)[0]
    R, H = words(text), words(hyp)
    m = dict(dur=round(len(a) / sr, 1), wpm=round(len(R) / (len(a) / sr) * 60),
             wer=round(edits(R, H) / len(R), 3), hyp=hyp.lower())
    try:
        import librosa
        y = librosa.resample(a, orig_sr=sr, target_sr=16000)
        f0, vf, _ = librosa.pyin(y, fmin=60, fmax=400, sr=16000, frame_length=1024)
        f0 = f0[vf]
        st = 12 * np.log2(f0 / np.median(f0))
        rms = librosa.feature.rms(y=a, frame_length=1024, hop_length=240)[0]
        m.update(f0_med=round(float(np.median(f0))),
                 pitch_range_st=round(float(np.subtract(*np.percentile(st, [90, 10]))), 1),
                 pause=round(float((rms < .1 * np.median(rms)).mean()), 2))
    except ImportError:
        pass
    out[v] = m
    print(v, {k: x for k, x in m.items() if k != "hyp"})
json.dump(out, open("casting/metrics.json", "w"), indent=1)
