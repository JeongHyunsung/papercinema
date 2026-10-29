"""QA: is every narration clip still intelligible in the final mix?
ASR of each clip cut from mix.wav vs the same window of narration.wav.
  python3 mix_check.py out/audio/mix.wav out/audio/narration.wav out/audio/placement.json
"""
import json, sys
import soundfile as sf
from asr import transcribe
from textnorm import words, edits

mix, sr = sf.read(sys.argv[1], dtype="float32")
nar, _ = sf.read(sys.argv[2], dtype="float32")
mix = mix.mean(1) if mix.ndim > 1 else mix
nar = nar.mean(1) if nar.ndim > 1 else nar
E = T = 0
for c in json.load(open(sys.argv[3]))["clips"]:
    a, b = int(max(0, c["start"] - .1) * sr), int((c["end"] + .1) * sr)
    tn, tm = transcribe(nar[a:b], sr)[0], transcribe(mix[a:b], sr)[0]
    e, n = edits(words(tn), words(tm)), len(words(tn))
    E += e; T += n
    print(f"{c['id']:6s} diff {e}/{n} | {tm.lower()}")
print(f"mix vs clean narration: {E}/{T} words differ ({100 * E / max(T, 1):.1f}%)")
