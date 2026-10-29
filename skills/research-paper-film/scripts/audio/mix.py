"""Narration placement, ducking, loudness and true-peak mastering.

  python3 mix.py --duration 119.1 --lines narration/lines \\
                 --music out/audio/music.wav --sfx out/audio/sfx.wav --out out/audio
  (clips come from edl.clips(); run from src/ or set PYTHONPATH so `import edl` works)

Steps: narration clips placed at natural speed (6 ms edge fades, HP 70 Hz,
-17 LUFS) -> speech mask from word times -> ducking envelope (150 ms pre-roll,
450 ms release) -> music -26 LUFS ducked 9 dB, SFX -25 LUFS ducked 5 dB ->
tail fade -> voice limiter (-4, re-level, -3 dBTP) -> bus at -16 LUFS with a
4x-oversampled look-ahead limiter at -1.2 dBTP (3 level/limit iterations).
Writes narration/music/sfx stems (float, at mix gain), mix.wav (24-bit),
placement.json. Prints measured LUFS / true peak - report these, and measure
the encoded deliverables again with ffmpeg ebur128.
"""
import argparse, json, math, os, sys
import numpy as np, soundfile as sf
import pyloudnorm as pyln
from scipy.ndimage import uniform_filter1d, minimum_filter1d
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth import hp, SR                                        # noqa: E402

METER = pyln.Meter(SR)


def lufs(st):
    return METER.integrated_loudness(st)


def gain_to(st, target):
    return st * 10 ** ((target - lufs(st)) / 20) if np.any(st) else st


def true_peak_db(st):
    return 20 * np.log10(np.max(np.abs(resample_poly(st, 4, 1, axis=0))) + 1e-12)


def limit(st, ceil_db=-1.2):
    thr = 10 ** (ceil_db / 20)
    up = resample_poly(st, 4, 1, axis=0)
    pk = np.max(np.abs(up), 1).reshape(-1, 4).max(1)[:len(st)]
    pk = np.r_[pk, np.zeros(len(st) - len(pk))]
    gr = minimum_filter1d(np.minimum(1, thr / np.maximum(pk, 1e-9)), 2 * int(.004 * SR) + 1)
    out, a, cur = np.empty_like(gr), math.exp(-1 / (.08 * SR)), 1.0
    for i, v in enumerate(gr):
        cur = v if v < cur else a * cur + (1 - a) * v
        out[i] = cur
    return st * out[:, None]


def load(path, n):
    if not path or not os.path.exists(path):
        return np.zeros((n, 2))
    x, sr = sf.read(path, dtype="float64", always_2d=True)
    if sr != SR:
        x = resample_poly(x, SR // math.gcd(SR, sr), sr // math.gcd(SR, sr), axis=0)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, 1)
    out = np.zeros((n, 2)); m = min(n, len(x)); out[:m] = x[:m]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--lines", required=True)
    ap.add_argument("--music"); ap.add_argument("--sfx")
    ap.add_argument("--out", default="out/audio")
    ap.add_argument("--duck-music", type=float, default=9.0)
    ap.add_argument("--duck-sfx", type=float, default=5.0)
    a = ap.parse_args()
    import edl
    N = int(round((a.duration + 1.5) * SR))
    nar, speech = np.zeros(N), np.zeros(N)
    clips = edl.clips()
    for c in clips:
        x, sr = sf.read(os.path.join(a.lines, c["line"] + ".wav"), dtype="float64")
        x = x[int(c["src"] * sr):int(c["src_end"] * sr)]
        x = resample_poly(x, SR // math.gcd(SR, sr), sr // math.gcd(SR, sr))
        x *= np.minimum(1, np.minimum(np.arange(len(x)), len(x) - np.arange(len(x))) / (.006 * SR))
        i0 = int(round(c["start"] * SR))
        nar[i0:i0 + len(x)] += x[:N - i0]
        for w in c["words"]:
            speech[int(w["t0"] * SR):int(w["t1"] * SR)] = 1
    nar_st = gain_to(np.stack([hp(nar, 70)] * 2, 1), -17.0)
    pre, rel = int(.15 * SR), int(.45 * SR)
    m = np.maximum(speech, np.r_[speech[pre:], np.zeros(pre)])
    m = np.maximum.accumulate(np.where(m > 0, np.arange(N), -10 ** 9))
    duck = uniform_filter1d(np.clip(1 - (np.arange(N) - m) / rel, 0, 1), int(.12 * SR))
    music = gain_to(load(a.music, N), -26.0) * (10 ** (-a.duck_music * duck / 20))[:, None]
    sfx = gain_to(load(a.sfx, N), -25.0) * (10 ** (-a.duck_sfx * duck / 20))[:, None]
    tail = np.clip((a.duration - .05 - np.arange(N) / SR) / 1.6, 0, 1)[:, None]
    music *= tail; sfx *= tail
    pre_v = nar_st.copy()
    nar_st = limit(nar_st, -4.0)
    nar_st *= 10 ** ((-17.0 - lufs(nar_st)) / 20)
    nar_st = limit(nar_st, -3.0)
    r = np.abs(nar_st[:, 0]) / np.maximum(np.abs(pre_v[:, 0]), 1e-9)
    sp = np.abs(pre_v[:, 0]) > 10 ** (-2)
    if sp.any():
        lev = 20 * np.log10(r[sp] / np.median(r[sp]))
        print(f"voice limiter: speech samples reduced >1 dB {100 * np.mean(lev < -1):.2f}%, "
              f">3 dB {100 * np.mean(lev < -3):.2f}%")
    mix = nar_st + music + sfx
    g = 10 ** ((-16.0 - lufs(mix)) / 20)
    mix *= g
    for _ in range(3):
        mix = limit(mix)
        mix *= 10 ** ((-16.0 - lufs(mix)) / 20)
    mix = limit(mix, -1.2)
    print(f"mix: {lufs(mix):.2f} LUFS integrated, true peak {true_peak_db(mix):.2f} dBTP")
    NF = int(round(a.duration * SR))
    os.makedirs(a.out, exist_ok=True)
    for name, st in (("narration", nar_st * g), ("music", music * g), ("sfx", sfx * g), ("mix", mix)):
        sf.write(f"{a.out}/{name}.wav", st[:NF].astype(np.float32), SR,
                 subtype="PCM_24" if name == "mix" else "FLOAT")
    json.dump(dict(clips=clips, duration=a.duration), open(f"{a.out}/placement.json", "w"), indent=1)


if __name__ == "__main__":
    main()
