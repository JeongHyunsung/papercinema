"""Peak kit: designed "wow" moments that stay faithful to the paper (references/15).

A film that is accurate, legible and alive (A-F, G, L gates) can still have no
moment anyone remembers. A *peak* is one planned moment per key idea or result
where setup, tension, a single reveal, sound and camera land together. This
module plans peaks, enforces their budget, and gives fidelity-safe devices.

    from peak_kit import Peak, PeakPlan, cascade, ripple_order, count_at, collapse,
                         wipe, breath, land, log_zoom, accent_glow, flood, spotlight_rgb,
                         night_rgb

Plan (one per film, exported for wow_audit.py)
  PLAN = PeakPlan([
      Peak("one rule removes every bad branch", kind="concept", t_setup=31.0,
           t_reveal=34.2, t_hold=38.0, key_word="pruned", claim="L12",
           device="cascade", signature="night"),
      Peak("10,000 checks, 0 violations", kind="evidence", ...,
           device="invariant_counter"),
      Peak("2.4× lower p99 latency vs Baseline A", kind="result", ..., tradeoff_t=63.5,
           signature="accent"),
  ])
  PLAN.export("out/peaks.json")      # wow_audit.py --peaks out/peaks.json

  Budgets (asserted at construction): 3-6 peaks; at most MAX_SIGNATURES = 2
  signature breaks per film, each <= 6 s and inside its peak's [setup, hold]
  window; peaks >= 8 s apart; every result peak names the trade-off time.

Fidelity-safe devices (motion with meaning; never change a value)
  ripple_order(points, src)          order items by distance from the decision
  cascade(t, t0, order, stagger, dur) per-item progress 0..1: one cause, many effects
  count_at(t, times)                 a counter that only moves when a real event lands
  collapse(t, t0, dur, pts, target)  many -> one morph (positions), no cut
  wipe(t, t0, dur)                   before / after split position 0..1
  breath(t, t_reveal, pre=.45)       0..1 hush just before the reveal (dim, slow drift)
  land(t, t0, dur, v0, v1)           data value easing to its exact value, no overshoot
  log_zoom(t, t0, t1, z0, z1)        scale reveal: zoom interpolated in log space

Signature breaks (style departures; budget MAX_SIGNATURES per film)
  "night"   whole stage flips to a dark tone, hue preserved     -> night_rgb(rgb, d)
  "spot"    everything outside one referent darkens            -> spotlight_rgb(rgb, c, r, d)
  "accent"  a light halo on the headline element only           -> accent_glow(cv, p, r, col, a)
  "flood"   a semantic colour floods the frame behind a number  -> flood(cv, col, a, origin, prog)
  Apply post-raster breaks from the film's  post(rgb, t)  hook (render.py calls it).
  PLAN.signature_level(t, name) gives the eased 0..1 level inside its window.
"""
import json
import math

import numpy as np

from engine import DW, DH, clamp, seg, smooth, io3

MAX_SIGNATURES = 2
MAX_SIGNATURE_S = 6.0
MIN_PEAKS, MAX_PEAKS = 3, 6
MIN_GAP_S = 8.0
KINDS = ("hook", "concept", "evidence", "twist", "result")
DEVICES = ("scale_reveal", "cascade", "collapse", "invariant_counter", "race",
           "reversal", "before_after", "number_land", "other")
SIGNATURES = ("night", "spot", "accent", "flood")


class Peak:
    """One designed moment.

    t_setup   the expectation is established (camera, context, question)
    t_reveal  the single change (<= 0.6 s) the peak is about; sound hit and key word here
    t_hold    end of the quiet hold that lets it land (>= readability budget)
    kind      hook | concept | evidence | twist | result
    claim     claim-ledger id the peak dramatises (every peak shows a verified fact)
    tradeoff_t  for kind="result": when the reported trade-off appears (<= 12 s later)
    signature None or one of SIGNATURES, with sig_in / sig_out (default: around reveal)
    """

    def __init__(self, name, kind, t_setup, t_reveal, t_hold, key_word, claim,
                 device="other", signature=None, sig_in=None, sig_out=None,
                 tradeoff_t=None, sound="hit"):
        assert kind in KINDS, kind
        assert device in DEVICES, device
        assert signature in (None, *SIGNATURES), signature
        assert t_setup < t_reveal < t_hold, (name, t_setup, t_reveal, t_hold)
        assert t_reveal - t_setup >= 1.5, f"{name}: setup shorter than 1.5 s"
        assert t_hold - t_reveal >= 2.5, f"{name}: hold shorter than 2.5 s (B1)"
        self.name, self.kind, self.device = name, kind, device
        self.t_setup, self.t_reveal, self.t_hold = t_setup, t_reveal, t_hold
        self.key_word, self.claim, self.sound = key_word, claim, sound
        self.signature = signature
        self.sig_in = sig_in if sig_in is not None else t_reveal - .6
        self.sig_out = sig_out if sig_out is not None else min(t_hold, t_reveal + 4.0)
        self.tradeoff_t = tradeoff_t
        if signature:
            assert t_setup <= self.sig_in < self.sig_out <= t_hold + .8, \
                f"{name}: signature window outside its peak"
            assert self.sig_out - self.sig_in <= MAX_SIGNATURE_S, \
                f"{name}: signature longer than {MAX_SIGNATURE_S} s"
        if kind == "result":
            assert tradeoff_t is not None and 0 < tradeoff_t - t_reveal <= 12.0, \
                f"{name}: a result peak must show its trade-off within 12 s (A5)"

    def as_dict(self):
        return dict(self.__dict__)


class PeakPlan:
    def __init__(self, peaks, strict=True):
        self.peaks = sorted(peaks, key=lambda p: p.t_reveal)
        n = len(self.peaks)
        sig = [p for p in self.peaks if p.signature]
        assert len(sig) <= MAX_SIGNATURES, \
            f"{len(sig)} signature breaks; the budget is {MAX_SIGNATURES} per film"
        if strict:
            assert MIN_PEAKS <= n <= MAX_PEAKS, f"{n} peaks; plan {MIN_PEAKS}-{MAX_PEAKS}"
            kinds = {p.kind for p in self.peaks}
            assert "concept" in kinds and "result" in kinds, \
                "at least one concept peak and one result peak"
            for a, b in zip(self.peaks, self.peaks[1:]):
                assert b.t_reveal - a.t_reveal >= MIN_GAP_S, \
                    f"peaks '{a.name}' and '{b.name}' closer than {MIN_GAP_S} s"

    def signature_level(self, t, name, fin=.5, fout=.7):
        """Eased 0..1 level of signature `name` at time t (0 outside its windows)."""
        lv = 0.0
        for p in self.peaks:
            if p.signature == name:
                lv = max(lv, smooth(seg(t, p.sig_in, p.sig_in + fin))
                         * (1 - smooth(seg(t, p.sig_out - fout, p.sig_out))))
        return lv

    def peak_at(self, t):
        for p in self.peaks:
            if p.t_setup <= t <= p.t_hold:
                return p
        return None

    def export(self, path, duration=None):
        json.dump(dict(duration=duration, max_signatures=MAX_SIGNATURES,
                       peaks=[p.as_dict() for p in self.peaks]),
                  open(path, "w"), indent=1)


# ================================================= fidelity-safe devices =====
def ripple_order(points, src):
    """Indices of points sorted by distance from src, with normalised distances
    (0 = nearest). Use as the order of a cascade so effects spread from the cause."""
    d = [math.hypot(p[0] - src[0], p[1] - src[1]) for p in points]
    m = max(d) or 1.0
    return [d_ / m for d_ in d]


def cascade(t, t0, order, stagger=.9, dur=.35):
    """Per-item progress 0..1. order: list of 0..1 ranks (ripple_order, or k/(n-1)).
    Item i starts at t0 + order[i] * stagger and completes over dur."""
    return [smooth(seg(t, t0 + o * stagger, t0 + o * stagger + dur)) for o in order]


def count_at(t, times):
    """Exact counter: number of real events (sorted times) that have landed by t."""
    return int(np.searchsorted(np.asarray(times), t, side="right"))


def collapse(t, t0, dur, pts, target, stagger=.25):
    """Many -> one: each point travels to target (staggered by index)."""
    n = max(len(pts) - 1, 1)
    out = []
    for k, p in enumerate(pts):
        f = io3(seg(t, t0 + stagger * k / n, t0 + stagger * k / n + dur))
        out.append((p[0] + (target[0] - p[0]) * f, p[1] + (target[1] - p[1]) * f))
    return out


def wipe(t, t0, dur):
    return io3(seg(t, t0, t0 + dur))


def breath(t, t_reveal, pre=.45, post=.15):
    """0..1 hush just before a reveal: dim non-participants a little more, slow
    the camera drift, duck the score. Peaks at the reveal frame, then releases."""
    return smooth(seg(t, t_reveal - pre, t_reveal)) * (1 - smooth(seg(t, t_reveal, t_reveal + post)))


def land(t, t0, dur, v0, v1):
    """A data value easing to its exact value. Monotone ease-out, no overshoot,
    so no frame ever shows a value the paper did not report beyond v1."""
    f = seg(t, t0, t0 + dur)
    f = 1 - (1 - f) ** 3
    return v0 + (v1 - v0) * f


def log_zoom(t, t0, t1, z0, z1, ease=io3):
    f = ease(seg(t, t0, t1))
    return math.exp(math.log(z0) + (math.log(z1) - math.log(z0)) * f)


# ================================================ signature breaks (budget) ==
def night_rgb(rgb, d):
    """Hue-preserving lightness inversion, blended by d (0..1).
    White paper -> near-black stage; ink -> near-white; semantic hues keep their hue.
    c' = c + (1 - max - min) per pixel (HSL: L' = 1 - L, H and S kept)."""
    if d <= 0.003:
        return rgb
    x = rgb.astype(np.float32) / 255.0
    mx, mn = x.max(-1, keepdims=True), x.min(-1, keepdims=True)
    inv = np.clip(x + (1.0 - mx - mn), 0, 1)
    inv = inv * .93 + .035                      # stage black #090B0E-ish, never pure
    out = x * (1 - d) + inv * d
    return (out * 255 + .5).astype(np.uint8)


def spotlight_rgb(rgb, centre, radius, d, floor=.28):
    """Darken everything outside a soft circle around the referent (design units)."""
    if d <= 0.003:
        return rgb
    H, W = rgb.shape[:2]
    k = W / DW
    cx, cy, r = centre[0] * k, centre[1] * k, radius * k
    yy, xx = np.ogrid[:H, :W]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    m = np.clip((dist - r) / (r * .6), 0, 1)[..., None]
    g = 1 - (1 - floor) * m * d
    return (rgb.astype(np.float32) * g).astype(np.uint8)


def accent_glow(cv, p, r, col, a=1.0):
    """Light halo behind the headline element only (C2 exception, budgeted)."""
    import cairo
    if a <= .003:
        return
    c = cv.c
    g = cairo.RadialGradient(p[0], p[1], r * .15, p[0], p[1], r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], .34 * a)
    g.add_color_stop_rgba(.45, col[0], col[1], col[2], .16 * a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g)
    c.new_path()
    c.arc(p[0], p[1], r, 0, 2 * math.pi)
    c.fill()


def flood(cv, col, a, origin=(DW / 2, DH / 2), prog=1.0, tint=.12):
    """A semantic colour floods the frame from origin (circle reveal) as a flat tint."""
    if a <= .003 or prog <= 0:
        return
    R = math.hypot(max(origin[0], DW - origin[0]), max(origin[1], DH - origin[1]))
    cv.circle(origin, R * clamp(prog), None, 1, fill=col, fa=tint * a)
