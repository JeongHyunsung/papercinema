"""Procedural score and sound design (licence-clean: nothing is sampled).

    from synth import Track, bell, tick, thump, whoosh, stab, pad, reverb, hp
    music, sfx = Track(dur), Track(dur)
    music.add(0.0, pad(["D3", "A3", "F4"], 8.0), gain=.5)    # stereo pad
    sfx.add(3.63, tick(), gain=.4, pan=-.2)                  # a check passes
    sfx.add(5.0, thump(), gain=.6)                           # a pruning decision
    music.write("out/audio/music.wav", room=(4.0, 2200, .8))
    sfx.write("out/audio/sfx.wav", room=(2.6, 3000, .5))
Cue sounds from film.CUES (map animation-time cues with edl.inv).
Semantics used in the case study: tick = check, low thump = prune decision,
bell = result, swell (pad + stab) = scale climax, whoosh = camera move.

Peaks (references/15): every planned peak gets one sound shape, landing on the
reveal frame:
    music.add(t_rev - 2.4, riser(2.4), gain=.5)          # tension into the reveal
    music.duck(t_rev - .35, t_rev, db=-18)               # pre-hit silence (the "breath")
    sfx.add(t_rev, hit("D2", ["D3", "A3", "F4"]), gain=.8)  # the reveal itself
Use at most one riser per peak and no hit outside a peak, or the hits stop meaning
anything. wow_audit.py checks that a cue lands within 80 ms of each reveal.
"""
import math
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
rng = np.random.default_rng(42)


def tt(d):
    return np.arange(int(d * SR)) / SR


def hz(note):
    """'D2' -> Hz (A4 = 440)."""
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
             "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10,
             "Bb": 10, "B": 11}
    m = 12 * (int(note[-1]) + 1) + names[note[:-1]]
    return 440 * 2 ** ((m - 69) / 12)


def lp(sig, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * .45), "low", fs=SR, output="sos"), sig, axis=0)


def hp(sig, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), sig, axis=0)


def bp(sig, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), sig, axis=0)


def bell(f, d=2.2, bright=1.0):
    t = tt(d)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
         + .35 * bright * np.sin(2 * np.pi * f * 2.756 * t) * np.exp(-t * 5)
         + .18 * bright * np.sin(2 * np.pi * f * 5.404 * t) * np.exp(-t * 9))
    return s * np.minimum(t / .004, 1)


def tick(f=3200, d=.035, noise=.3):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 140) + \
        noise * rng.normal(size=len(t)) * np.exp(-t * 300)


def thump(f0=55, d=1.6, drop=2.2):
    t = tt(d)
    f = f0 * (1 + drop * np.exp(-t * 18))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6) * np.minimum(t / .003, 1)


def whoosh(d=1.2, lo=300, hi=4000, rise=True):
    t = tt(d)
    n = rng.normal(size=len(t))
    a = t / d if rise else 1 - t / d
    b1, b2, b3 = bp(n, lo, lo * 2), bp(n, lo * 2, hi / 2), bp(n, hi / 2, hi)
    s = b1 * np.clip(1 - 2 * a, 0, 1) + b2 * (1 - abs(2 * a - 1)) + b3 * np.clip(2 * a - 1, 0, 1)
    env = (t / d) ** 2.2 * np.exp(-np.maximum(t - d * .92, 0) * 40) if rise else \
        np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return s * env


def stab(freqs, d=1.0):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in freqs)
    s = s / len(freqs) * np.exp(-t * 3.5) * np.minimum(t / .006, 1)
    return s + .25 * hp(rng.normal(size=len(t)), 2500) * np.exp(-t * 20)


def riser(d=2.4, lo=180, hi=2600, tone="D3"):
    """Tension into a reveal: noise band sweeping up plus a rising tone, ending
    exactly at d (place it at t_reveal - d)."""
    t = tt(d)
    f = lo * (hi / lo) ** (t / d)
    n = rng.normal(size=len(t))
    band = sum(bp(n, max(30, fc * .8), fc * 1.25) * ((t // (d / 8)) == k)
               for k, fc in enumerate(np.geomspace(lo, hi, 8)))
    ft = hz(tone) * (1 + .5 * (t / d) ** 2)
    sweep = np.sin(2 * np.pi * np.cumsum(ft) / SR)
    env = (t / d) ** 2.4
    return (.6 * band + .4 * sweep) * env * np.minimum((d - t) / .02, 1)


def hit(root="D2", chord=("D3", "A3", "F4"), d=2.6):
    """The reveal: a sub thump, a chord stab and a bell partial, one transient."""
    th = thump(hz(root), d=min(d, 1.8), drop=1.6)
    st = stab([hz(n) for n in chord], d=min(d, 1.4))
    be = bell(hz(chord[-1]) * 2, d=d, bright=.6)
    n = len(tt(d))
    out = np.zeros(n)
    for s_, g in ((th, .9), (st, .55), (be, .35)):
        out[:len(s_)] += g * s_[:n]
    return out


def pad(notes, d, fade_in=1.5, fade_out=1.5, cutoff=1400):
    """Stereo pad chord (detuned soft saws, slow LFO, low-passed) -> (n, 2)."""
    t = tt(d)
    L, R = np.zeros(len(t)), np.zeros(len(t))
    for k, n in enumerate(notes):
        f = hz(n)
        for det, pan in ((-.0035, -.6), (0, 0), (.0035, .6)):
            ff, ph = f * (1 + det), rng.random() * 6.28
            s = sum(np.sin(2 * np.pi * ff * h * t + ph * h) / h ** 1.35
                    for h in range(1, 7) if ff * h <= 6000)
            s = s * (1 + .12 * np.sin(2 * np.pi * (.07 + .013 * k) * t + k))
            L += s * math.cos((pan + 1) * math.pi / 4)
            R += s * math.sin((pan + 1) * math.pi / 4)
    env = np.clip(np.minimum(t / fade_in, 1) * np.minimum((d - t) / fade_out, 1), 0, 1) ** 1.5
    return np.stack([lp(L, cutoff), lp(R, cutoff)], 1) * env[:, None] / len(notes)


def reverb(x, secs=2.8, damp=3000, seed=1):
    """Convolution with a decaying, low-passed noise impulse response."""
    r = np.random.default_rng(seed)
    t = tt(secs)
    ir = lp(r.normal(size=len(t)) * np.exp(-t * 6.9 / secs), damp)
    ir[:int(.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    return fftconvolve(x, ir)[:len(x)]


class Track:
    """A stereo bus of fixed duration."""

    def __init__(self, dur):
        self.x = np.zeros((int(dur * SR), 2))

    def add(self, t0, sig, gain=1.0, pan=0.0):
        sig = np.asarray(sig, float)
        if sig.ndim == 1:
            sig = np.stack([sig * math.cos((pan + 1) * math.pi / 4),
                            sig * math.sin((pan + 1) * math.pi / 4)], 1)
        i0 = int(t0 * SR)
        if i0 >= len(self.x) or i0 < 0:
            return
        n = min(len(sig), len(self.x) - i0)
        self.x[i0:i0 + n] += sig[:n] * gain

    def duck(self, t0, t1, db=-18, ramp=.06):
        """Pull the bus down between t0 and t1 (pre-hit silence before a reveal)."""
        n = len(self.x)
        t = np.arange(n) / SR
        g = 10 ** (db / 20)
        w = np.clip(np.minimum((t - (t0 - ramp)) / ramp, (t1 + ramp - t) / ramp), 0, 1)
        self.x *= (1 - (1 - g) * w)[:, None]

    def render(self, room=None):
        x = self.x
        if room:
            secs, damp, wet = room
            x = x + np.stack([reverb(x[:, 0], secs, damp, 3),
                              reverb(x[:, 1], secs, damp, 4)], 1) * wet
        return hp(x, 30)

    def write(self, path, room=None):
        import soundfile as sf
        sf.write(path, self.render(room).astype(np.float32), SR, subtype="FLOAT")
