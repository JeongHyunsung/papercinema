"""v4 sound: procedural score + sound design + narration, mixed with ducking.

Everything here is synthesized from code (no samples, no third-party
recordings), so the music and effects carry no licensing encumbrance.
Cue times come from film.CUES (the v4 narration clock); event times stored
in v3 units inside film.py are mapped with edl.inv.

Outputs (48 kHz, 24-bit WAV) in out/audio_v4/:
  narration.wav  music.wav  sfx.wav   (stems, at mix level, pre-limiter)
  mix.wav                               (-16 LUFS integrated, <= -1 dBTP)
"""
import math, os, sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
import film, edl, json
I = edl.inv
from engine import io3, seg

SR = 48000
DUR = film.DURATION + 1.5
N = int(SR * DUR)
rng = np.random.default_rng(42)
L = np.zeros(N)
R = np.zeros(N)
PADL = np.zeros(N)
PADR = np.zeros(N)


def hz(note):
    """MIDI-ish: 'D2' -> Hz."""
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
             "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9,
             "A#": 10, "Bb": 10, "B": 11}
    n, o = note[:-1], int(note[-1])
    m = 12 * (o + 1) + names[n]
    return 440 * 2 ** ((m - 69) / 12)


def add(buf_l, buf_r, t0, sig, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    sig = sig[:N - i0]
    gl = gain * math.cos((pan + 1) * math.pi / 4)
    gr = gain * math.sin((pan + 1) * math.pi / 4)
    buf_l[i0:i0 + len(sig)] += sig * gl
    buf_r[i0:i0 + len(sig)] += sig * gr


def tt(d):
    return np.arange(int(d * SR)) / SR


def bell(f, d=2.2, bright=1.0):
    t = tt(d)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
         + .35 * bright * np.sin(2 * np.pi * f * 2.756 * t) * np.exp(-t * 5)
         + .18 * bright * np.sin(2 * np.pi * f * 5.404 * t) * np.exp(-t * 9))
    att = np.minimum(t / .004, 1)
    return s * att


def tick(f=3200, d=.035, noise=.3):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 140)
    s += noise * rng.normal(size=len(t)) * np.exp(-t * 300)
    return s


def thump(f0=55, d=1.6, drop=2.2):
    t = tt(d)
    f = f0 * (1 + drop * np.exp(-t * 18))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 2.6) * np.minimum(t / .003, 1)


def lp(sig, fc, order=2):
    sos = butter(order, min(fc, SR * .45), "low", fs=SR, output="sos")
    return sosfilt(sos, sig)


def hp(sig, fc, order=2):
    sos = butter(order, fc, "high", fs=SR, output="sos")
    return sosfilt(sos, sig)


def bp(sig, lo, hi, order=2):
    sos = butter(order, [lo, hi], "band", fs=SR, output="sos")
    return sosfilt(sos, sig)


def whoosh(d=1.2, lo=300, hi=4000, rise=True):
    t = tt(d)
    n = rng.normal(size=len(t))
    # time-varying band: crossfade between three fixed bands
    a = t / d if rise else 1 - t / d
    b1, b2, b3 = bp(n, lo, lo * 2), bp(n, lo * 2, hi / 2), bp(n, hi / 2, hi)
    s = b1 * np.clip(1 - 2 * a, 0, 1) + b2 * (1 - abs(2 * a - 1)) + \
        b3 * np.clip(2 * a - 1, 0, 1)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 if not rise else \
        (t / d) ** 2.2 * np.exp(-np.maximum(t - d * .92, 0) * 40)
    return s * env


def stab(freqs, d=1.0):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in freqs)
    s = s / len(freqs) * np.exp(-t * 3.5) * np.minimum(t / .006, 1)
    s += .25 * hp(rng.normal(size=len(t)), 2500) * np.exp(-t * 20)
    return s


# ------------------------------------------------------------- pad bed ------
def pad_chord(notes, t0, t1, gain, fade_in=1.5, fade_out=1.5, cutoff=1400):
    d = t1 - t0
    t = tt(d)
    out_l = np.zeros(len(t))
    out_r = np.zeros(len(t))
    for k, n in enumerate(notes):
        f = hz(n)
        for det, pan in ((-.0035, -.6), (0, 0), (.0035, .6)):
            ff = f * (1 + det)
            ph = rng.random() * 6.28
            # band-limited soft saw: few harmonics
            s = np.zeros(len(t))
            for h in range(1, 7):
                if ff * h > 6000:
                    break
                s += np.sin(2 * np.pi * ff * h * t + ph * h) / h ** 1.35
            lfo = 1 + .12 * np.sin(2 * np.pi * (.07 + .013 * k) * t + k)
            s *= lfo
            out_l += s * math.cos((pan + 1) * math.pi / 4)
            out_r += s * math.sin((pan + 1) * math.pi / 4)
    env = np.minimum(t / fade_in, 1) * np.minimum((d - t) / fade_out, 1)
    env = np.clip(env, 0, 1) ** 1.5
    out_l = lp(out_l, cutoff) * env / len(notes)
    out_r = lp(out_r, cutoff) * env / len(notes)
    i0 = int(t0 * SR)
    PADL[i0:i0 + len(t)] += out_l[:N - i0] * gain
    PADR[i0:i0 + len(t)] += out_r[:N - i0] * gain


# chord plan (D minor; tension into the conflict; D major at both climaxes)
C = film.CUES
F0, F1 = C["fill"]
pad_chord(["D2", "A2", "E3", "F3"], 0.0, I(7.2), .55, 3.0, 1.6, 900)
pad_chord(["D2", "A2", "D3", "E3", "A3"], I(6.0), C["title"] + .2, .55, 1.4, .6,
          1300)
pad_chord(["Bb1", "F2", "D3", "A3", "C4"], C["title"] - .05, C["tilt"] + .4,
          .5, .4, 1.0, 1600)
pad_chord(["G1", "D2", "Bb2", "F3", "A3"], C["tilt"], C["ant2"], .45, .8, 1.0,
          1500)
pad_chord(["D2", "A2", "E3", "G3", "C4"], C["ant2"] - .4, C["follow"] + .2,
          .42, 1.0, 1.0, 1500)
pad_chord(["Bb1", "F2", "D3", "F3", "C4"], C["follow"], C["ant4"] + .2, .4,
          .6, .6, 1500)
pad_chord(["A1", "E2", "A2", "C#3", "G3"], C["ant4"] - .2, C["pip"] + .2, .5,
          .6, .6, 1900)
pad_chord(["D2", "A2", "F3", "C4", "E4"], C["pip"], C["cells"] + .6, .45, .4,
          .8, 1900)
pad_chord(["Bb1", "F2", "D3", "A3", "E4"], C["cells"] + .2, F1 + .05, .5, 1.0,
          .2, 2600)
pad_chord(["D2", "A2", "E3", "F#3", "A3"], F1, C["block"] + .4, .55, .05, 1.0,
          2600)
pad_chord(["G1", "D2", "A2", "D3", "B3"], C["block"], C["race_in"] + .3, .45,
          .8, .8, 1800)
pad_chord(["Bb1", "F2", "C3", "D3", "A3"], C["race_in"], C["slam"] + .05, .45,
          .6, .3, 2000)
pad_chord(["D1", "A1", "E2", "A2", "D3", "F#3", "A3"], C["slam"],
          C["final"] + .3, .55, .25, 1.0, 2400)
pad_chord(["D1", "A1", "E2", "A2", "D3", "F#3", "A3"], C["final"] - .2, DUR,
          .6, .4, 3.4, 2600)
t = tt(DUR)
sub = np.sin(2 * np.pi * hz("D1") * t) * .55
sub *= np.clip(np.minimum(t / 4, 1) * np.clip((C["cells"] - t) / 2, 0, 1), 0, 1)
PADL += sub
PADR += sub

# ------------------------------------------------------- event-driven fx ----
# ACT I: test vector, the reordered transition, the space ----------------------
for k, tc in enumerate(C["trans"]):
    add(L, R, tc, tick(2600 + 180 * k, .04, .25), .32, -.4 + .16 * k)
    add(L, R, tc + .14, bell(hz("A5") if k != 4 else hz("D6"), .9, .5), .07,
        -.3 + .12 * k)
add(L, R, C["cap"], bell(hz("F#5"), 2.4, .9), .16, .2)
add(L, R, C["rew"], whoosh(.5, 400, 3000, rise=False), .10)
add(L, R, C["mod6"], stab([hz("D4"), hz("Eb4"), hz("Ab4"), hz("A4")], 1.6), .32)
add(L, R, C["mod6"], thump(48, 1.0, 1.0), .35)
add(L, R, C["pull"], whoosh(.45, 200, 2500, rise=False), .08)
for k in range(7):
    add(L, R, C["states"] + k * .04, tick(1800, .03, .1), .10, -.5 + k * .15)
add(L, R, C["fly"], whoosh(.6, 250, 2500), .10)
add(L, R, C["extrude"], whoosh(.7, 120, 1800), .16)
add(L, R, C["extrude"], thump(41, 2.2, .6), .22)
add(L, R, C["collapse"], whoosh(.62, 300, 6000), .2)
add(L, R, C["title"], thump(44, 3.0, 2.5), .65)
add(L, R, C["title"], bell(hz("D5"), 4.0, 1.2), .18, -.2)
add(L, R, C["title"] + .02, bell(hz("A5"), 4.0, 1.0), .12, .2)
# ACT II: the reference, the replay, the lift ----------------------------------
for k, tn in enumerate(C["rbg_nodes"]):
    add(L, R, tn, bell(hz(["D5", "E5", "F5", "A5", "C6", "D6", "E6", "F6"][k]),
                       .6, .3), .045, -.6 + k * .17)
for k, te in enumerate(C["rbg_edges"]):
    add(L, R, te, tick(4200, .02, .4), .05, -.5 + k * .06)
for k, tk in enumerate(C["token"]):                 # same voice as Act I ticks
    add(L, R, tk - .05, tick(2600 + 180 * k, .04, .25), .26, -.4 + .16 * k)
    if k in C["token_amber"]:
        add(L, R, tk - .05, bell(hz("F#5"), 2.0, .9), .14, .1)
add(L, R, C["token_end"] + .05, bell(hz("A5"), 2.6, .9), .16, -.1)
add(L, R, C["token_end"] + .3, stab([hz("D4"), hz("Eb4")], .9), .12, .3)
add(L, R, C["tilt"], whoosh(.8, 150, 2000), .12)
add(L, R, C["lift"], whoosh(1.0, 120, 1600), .14)
add(L, R, C["lift"] + .9, bell(hz("A4"), 2.5, .6), .08)
for k in range(16):
    add(L, R, C["slots"] + k * .025, tick(3800, .015, .3), .025,
        -.7 + k * .09)
add(L, R, C["panel"], whoosh(.45, 500, 4000, rise=False), .07)
# ACT III: walkthrough ----------------------------------------------------------
for tm in C["moves"]:
    add(L, R, tm, whoosh(.5, 250, 3000), .07)
add(L, R, C["init"], bell(hz("A4"), 2.0, .6), .18)
for j in range(4):
    add(L, R, C["row7"] + j * .045, tick(3600, .015, .6), .07, .5)
add(L, R, C["ant2"], bell(hz("E5"), 1.6, .5), .08, -.2)          # anticipation
for k, tc in enumerate(C["cands"]):
    add(L, R, tc, tick(1900 + 150 * k, .035, .1), .14, .3)
for j in range(2):
    add(L, R, C["reject"] + j * .1, stab([hz("C5"), hz("Db5")], .5), .13, .4)
add(L, R, C["retract"], whoosh(.5, 300, 2500, rise=False), .1)
add(L, R, C["x1"], bell(hz("E5"), 1.4, .6), .12, -.1)
add(L, R, C["x2"], bell(hz("G5"), 1.4, .6), .1, .2)
for j in range(6):
    add(L, R, C["x2"] + .55 + j * .05, tick(3600, .015, .6), .05, .5)
add(L, R, C["keep"], bell(hz("A5"), 1.2, .4), .07)
add(L, R, C["follow"], whoosh(.4, 200, 2500, rise=False), .06)
for k, tl in enumerate(C["links"]):                  # fast: repetition
    add(L, R, tl + .2, tick(2600, .03, .2), .15, -.4 + .4 * k)
    add(L, R, tl + .2, bell(hz(["A5", "C6", "E6"][k]), .5, .4), .06)
add(L, R, C["ant4"], bell(hz("F#5"), 1.8, .8), .1, -.1)         # anticipation
tr = tt(1.6)
riser = np.sin(2 * np.pi * (55 + 40 * tr / 1.6) * tr) * (tr / 1.6) ** 2
add(L, R, C["cpath"], riser, .22)
for k, d in enumerate((0, .5, 1.0)):
    add(L, R, C["cpath"] + d, tick(1600 - 200 * k, .05, .1), .14)
add(L, R, C["conflict"], stab([hz("Bb3"), hz("B3"), hz("F4"), hz("E5")], 1.8),
    .36)
add(L, R, C["conflict"], thump(50, 1.4, 1.5), .35)
add(L, R, C["cut"], whoosh(.5, 300, 2500, rise=False), .14)
add(L, R, C["pip"] - .05, whoosh(.7, 200, 4000), .12)
scale = ["D5", "E5", "F5", "A5", "C6", "D6", "E6", "F6", "A6"]
vk = 0
for n in sorted(film.TN, key=lambda q: q["dfs"]):
    if n["parent"] is None or n["id"] in film.WALK_IDS:
        continue
    t0 = I(film.GROW_T[n["id"]])
    pan = math.cos(n["theta"]) * .8
    if n["status"] in ("wrong output", "entry conflict"):
        add(L, R, t0 + .02, tick(700 + rng.random() * 400, .03, .05), .03,
            pan)
    elif n["status"] == "valid":
        f = hz(scale[vk % len(scale)]) * (1 if vk < 9 else 2)
        add(L, R, t0 + .2, bell(f, 1.8, .8), .085, pan)
        vk += 1
    else:
        add(L, R, t0, tick(2600 + rng.random() * 1200, .02, .3), .026, pan)
# ACT IV ----------------------------------------------------------------------
add(L, R, C["cells"], whoosh(.8, 300, 4000, rise=False), .14)
add(L, R, F0, whoosh(F1 - F0 + .05, 120, 7000), .3)
tr = tt(F1 - F0)
rr = np.sin(2 * np.pi * np.cumsum(40 + 260 * (tr / (F1 - F0)) ** 3) / SR) * \
    (tr / (F1 - F0)) ** 2.5
add(L, R, F0, rr, .22)
prev = 0
for q in np.linspace(F0, F1, 90):              # ticks follow the real count
    n = film.count_R(film.fill_R(edl.warp(q)))
    if n > prev:
        add(L, R, q, tick(3000 + 1500 * rng.random(), .015, .5), .04,
            rng.uniform(-.5, .5))
    prev = n
add(L, R, F1, thump(36, 4.0, 3.0), .9)
add(L, R, F1, bell(hz("D5"), 3.8, 1.0), .2, -.3)
add(L, R, F1 + .02, bell(hz("A5"), 3.8, 1.0), .16, .3)
add(L, R, F1 + .04, bell(hz("F#6"), 3.2, .8), .09, 0)
add(L, R, C["hist"], whoosh(1.0, 200, 3000, rise=False), .12)
for cel in film.CELLS468[::6]:
    add(L, R, I(cel["tf"] + .7), tick(4200 + 800 * rng.random(), .012, .3), .025,
        rng.uniform(-.2, .8))
for k in range(9):
    add(L, R, C["hist"] + 1.3 + k * .04, bell(hz(scale[k]), .8, .4), .05,
        -.4 + .12 * k)
add(L, R, C["block"], whoosh(.5, 500, 5000, rise=False), .08)
for j in range(20):
    add(L, R, C["sample20"] + j * .012, tick(5200, .02, .2), .05,
        rng.uniform(-.3, .3))
d0, d1 = C["dive"]
add(L, R, d0, whoosh(d1 - d0 + .05, 150, 6000), .2)
add(L, R, d1, thump(48, 1.6, 1.0), .3)
for k, ts3 in enumerate(film.T_FF):
    add(L, R, I(ts3), tick(2000, .035, .1), .16, -.2)
    hops = len(film.TRAJ[k]["path"]) - 1
    for h in range(hops):
        add(L, R, I(ts3 + (h + .5) * film.D_FF[k] / hops), tick(3400, .02, .2),
            .08, .2)
tq = I(film.T_FF[4] + film.D_FF[4] / 2)
add(L, R, tq, bell(hz("F#5"), 2.6, .9), .22, .1)
add(L, R, tq, thump(55, .9, 1.0), .2)
add(L, R, C["race_in"], whoosh(.5, 300, 5000), .12)
for v in range(5, 50, 5):                      # a tick per 5 ps on the race
    add(L, R, I(film.T_R0 + v / 20.0), tick(2400, .02, .2), .07, -.3 + v / 80)
add(L, R, C["ff1_stop"], bell(hz("A5"), 2.4, 1.0), .2, -.2)
add(L, R, C["ff1_stop"], thump(60, .8, 1.0), .2)
add(L, R, C["tg_stop"], thump(42, 1.2, .8), .3)
add(L, R, C["bracket"], whoosh(.4, 400, 4000), .07)
add(L, R, C["slam"], thump(38, 3.6, 2.0), .6)          # controlled reveal
add(L, R, C["slam"], bell(hz("A5"), 3.2, 1.0), .18, .2)
add(L, R, C["slam"] + .03, bell(hz("D6"), 3.2, 1.0), .13, -.2)
add(L, R, C["scatter"], whoosh(.8, 200, 3000, rise=False), .12)
for k in range(16):
    add(L, R, C["scatter"] + .65 + k * .025, tick(2400 + 100 * k, .02, .1),
        .05, -.6 + k * .08)
# ACT V -----------------------------------------------------------------------
add(L, R, C["final"] - .35, whoosh(.4, 300, 7000), .12)
add(L, R, C["final"] + .05, thump(36, 5.0, 3.0), .85)
for k, nn in enumerate(["D5", "F#5", "A5", "E6"]):
    add(L, R, C["final"] + .05 + k * .05, bell(hz(nn), 5.0, 1.0), .12,
        -.4 + .27 * k)

# ------------------------------------------------------------- v4 mix -------
import soundfile as sf, pyloudnorm as pyln
from scipy.signal import resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d


def reverb(x, secs=2.8, seed=1, damp=3000):
    r = np.random.default_rng(seed)
    t = tt(secs)
    ir = r.normal(size=len(t)) * np.exp(-t * 6.9 / secs)
    ir = lp(ir, damp)
    ir[:int(.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    return fftconvolve(x, ir)[:len(x)]


METER = pyln.Meter(SR)


def lufs(st):
    return METER.integrated_loudness(st)


def gain_to(st, target):
    return st * 10 ** ((target - lufs(st)) / 20)


def true_peak_db(st):
    up = resample_poly(st, 4, 1, axis=0)
    return 20 * np.log10(np.max(np.abs(up)) + 1e-12)


# music stem (pads + sub, with its own room)
music = np.stack([PADL + reverb(PADL, 4.0, 3, 2200) * .8,
                  PADR + reverb(PADR, 4.0, 4, 2200) * .8], 1)
music = np.stack([hp(music[:, 0], 30), hp(music[:, 1], 30)], 1)
# sfx stem (dry + room), softened for a narrated film
sfx = np.stack([L + reverb(L, 2.6, 1) * .5, R + reverb(R, 2.6, 2) * .5], 1)
sfx = np.stack([hp(sfx[:, 0], 40), hp(sfx[:, 1], 40)], 1)

# narration stem: every clip placed at its natural speed (no time-stretch)
NAR = os.path.join(edl.NAR, "lines")
nar = np.zeros(N)
speech = np.zeros(N)
clips = edl.clips()
for c in clips:
    a, sr = sf.read(os.path.join(NAR, c["line"] + ".wav"), dtype="float64")
    a = a[int(c["src"] * sr):int(c["src_end"] * sr)]
    a = resample_poly(a, SR // math.gcd(SR, sr), sr // math.gcd(SR, sr))
    fade = np.minimum(1, np.minimum(np.arange(len(a)), len(a) - np.arange(len(a))) / (.006 * SR))
    a *= fade
    i0 = int(round(c["start"] * SR))
    nar[i0:i0 + len(a)] += a[:N - i0]
    for w in c["words"]:
        speech[int(w["t0"] * SR):int(w["t1"] * SR)] = 1
nar = hp(nar, 70)
nar_st = np.stack([nar, nar], 1)
nar_st = gain_to(nar_st, -17.0)
NAR_PEAK_BEFORE = true_peak_db(nar_st)

# ducking envelope: 150 ms pre-roll, 450 ms release, smoothed
pre = int(.15 * SR)
m = np.maximum(speech, np.r_[speech[pre:], np.zeros(pre)])
rel = int(.45 * SR)
m = np.maximum.accumulate(np.where(m > 0, np.arange(N), -10 ** 9))
m = np.clip(1 - (np.arange(N) - m) / rel, 0, 1)
duck = uniform_filter1d(m, int(.12 * SR))
music = gain_to(music, -26.0) * (10 ** (-9 * duck / 20))[:, None]
sfx = gain_to(sfx, -25.0) * (10 ** (-5 * duck / 20))[:, None]

FILM = edl.DURATION                       # picture length; audio ends with it
tail = np.clip((FILM - .05 - np.arange(N) / SR) / 1.6, 0, 1)[:, None]
music *= tail
sfx *= tail
mix = nar_st + music + sfx
g = 10 ** ((-16.0 - lufs(mix)) / 20)
mix *= g
stems_gain = g


def limit(st, ceil_db=-1.2):
    thr = 10 ** (ceil_db / 20)
    up = resample_poly(st, 4, 1, axis=0)
    pk = np.max(np.abs(up), 1).reshape(-1, 4).max(1)[:len(st)]
    pk = np.r_[pk, np.zeros(len(st) - len(pk))]
    gr = np.minimum(1, thr / np.maximum(pk, 1e-9))
    look = int(.004 * SR)
    gr = minimum_filter1d(gr, 2 * look + 1)
    # release smoothing (one-pole) after hold
    out = np.empty_like(gr)
    a = math.exp(-1 / (.08 * SR))
    cur = 1.0
    for i, v in enumerate(gr):
        cur = v if v < cur else a * cur + (1 - a) * v
        out[i] = cur
    return st * out[:, None]


# dialogue peak control: limit the voice alone first (gentle, then re-level),
# so the bus limiter only touches the rare remaining peaks
_nar_pre = nar_st.copy()
nar_st = limit(nar_st, -4.0)
nar_st *= 10 ** ((-17.0 - lufs(nar_st)) / 20)
nar_st = limit(nar_st, -3.0)
print(f"narration true peak {NAR_PEAK_BEFORE:.1f} -> {true_peak_db(nar_st):.1f} dBTP before bus")
_r = np.abs(nar_st[:, 0]) / np.maximum(np.abs(_nar_pre[:, 0]), 1e-9)
_sp = np.abs(_nar_pre[:, 0]) > 10 ** (-40 / 20)
_lev = 20 * np.log10(_r[_sp] / np.median(_r[_sp]))
print(f"voice limiter: share of speech samples reduced > 1 dB: {100 * np.mean(_lev < -1):.2f}%, > 3 dB: {100 * np.mean(_lev < -3):.2f}%")
mix = (nar_st + music + sfx)
g = 10 ** ((-16.0 - lufs(mix)) / 20)
mix *= g
stems_gain = g
_pre = mix.copy()
for _ in range(3):
    mix = limit(mix)
    mix *= 10 ** ((-16.0 - lufs(mix)) / 20)
mix = limit(mix, -1.2)
_gr = 20 * np.log10(np.maximum(np.abs(mix).max(1), 1e-9) / np.maximum(np.abs(_pre).max(1), 1e-9))
_act = np.abs(_pre).max(1) > 1e-3
print(f"bus limiter: gain change p50 {np.median(_gr[_act]):.2f} dB, p99 {np.percentile(_gr[_act], 1):.2f} dB, max {np.min(_gr[_act]):.2f} dB")
print(f"mix: {lufs(mix):.2f} LUFS, true peak {true_peak_db(mix):.2f} dBTP")
NF = int(round(FILM * SR))
nar_st, music, sfx, mix = (x[:NF] for x in (nar_st, music, sfx, mix))
OUT = "out/audio_v4"
os.makedirs(OUT, exist_ok=True)
for name, st in (("narration", nar_st * stems_gain), ("music", music * stems_gain),
                 ("sfx", sfx * stems_gain), ("mix", mix)):
    sf.write(f"{OUT}/{name}.wav", st.astype(np.float32), SR,
             subtype="PCM_24" if name == "mix" else "FLOAT")   # stems: float, no clipping
    print(name, f"{lufs(st):.1f} LUFS" if np.any(st) else "")
json.dump(dict(clips=clips, duration=edl.DURATION), open(f"{OUT}/placement.json", "w"), indent=1)
