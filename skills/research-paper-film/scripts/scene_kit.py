"""Reusable scene helpers distilled from the case-study film.

  overlay        defer HUD drawing (labels, captions, panels) until after
                 camera-space content; figure mode can drop or move them
  kfv            keyframed values with per-key easing; log-interpolate e.g.
                 camera distance
  StageCam       look-at camera for a "graph above a graph" 3-D stage
  sw             projected stroke width (sub-linear in depth scale)
  bb_text, chip  billboard text / chip anchored at a world point
  marker, check, xmark   numbered markers and pass/fail glyphs

The motion/camera/linkage layer (beat_keys, lagged, focus, tracer, callout_at,
tether, AddressTable, pills, breadcrumb) lives in motion_kit.py; see
references/14-motion-camera-linkage.md.

Usage in film.py:
    from engine import *
    from scene_kit import *
    def draw(cv, t):
        OVERLAY.clear(); cv.begin()
        ...scenes...
        for fn in OVERLAY: fn()
"""
import math
from engine import (seg, smooth, io3, oexpo, ocub, clamp, lerp, DW, DH, INK,
                    DIM, PAPER, F_MONO_M)

OVERLAY = []


def overlay(fn):
    """Decorator: calls are queued and run after all camera-space drawing."""
    def wrap(*a, **k):
        OVERLAY.append(lambda: fn(*a, **k))
    wrap.__wrapped__ = fn
    return wrap


EASE = {"io": io3, "o": oexpo, "oc": ocub, "s": smooth, "l": clamp,
        "i": lambda x: clamp(x) ** 3}


def kfv(t, keys, logi=()):
    """Keyframes [(t, values, ease)] -> interpolated list.
    Indices in `logi` interpolate logarithmically (distances, zooms)."""
    if t <= keys[0][0]:
        return list(keys[0][1])
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = EASE[b[2]](seg(t, a[0], b[0]))
            return [math.exp(lerp(math.log(x), math.log(y), u)) if k in logi
                    else lerp(x, y, u)
                    for k, (x, y) in enumerate(zip(a[1], b[1]))]
    return list(keys[-1][1])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


class StageCam:
    """Look-at camera. World: x right, y 'down the layout', z up (height).
    tau = tilt from straight-down, psi = azimuth, D = distance, f = focal.
    ox, oy shift the projected stage in screen space.

    Near-orthographic oblique view (uniform sizes, ideal for slide figures):
        StageCam(tx, ty, th, D=40000, tau=.6, psi=-.1, ox, oy, f=1.4 * 40000)
    """

    def __init__(self, tx, ty, th, D, tau, psi, ox=0.0, oy=0.0, f=1400.0):
        st, ct, sp, cp = math.sin(tau), math.cos(tau), math.sin(psi), \
            math.cos(psi)
        self.eye = (tx + D * sp * st, ty + D * cp * st, th + D * ct)
        self.fwd = (-sp * st, -cp * st, -ct)
        self.up = (-sp * ct, -cp * ct, st)
        self.right = _cross(self.up, self.fwd)
        self.f, self.ox, self.oy, self.D = f, ox, oy, D

    def P(self, p):
        """World (x, y, h) -> (screen x, screen y, scale, depth)."""
        d = (p[0] - self.eye[0], p[1] - self.eye[1], p[2] - self.eye[2])
        xc = sum(d[k] * self.right[k] for k in range(3))
        yc = sum(d[k] * self.up[k] for k in range(3))
        zc = max(sum(d[k] * self.fwd[k] for k in range(3)), 1.0)
        s = self.f / zc
        return (DW / 2 + self.ox + xc * s, DH / 2 + self.oy - yc * s, s, zc)


def sw(sc, w):
    """Projected stroke width: grows with proximity, sub-linearly."""
    return w * max(sc, .25) ** .8 * .85


def bb_text(cv, cam, wp, dx, dy, s, font, size, col, a, anchor="c"):
    """Billboard text anchored at world point wp, offset (dx, dy) * scale."""
    if a <= 0.002:
        return
    x, y, sc, _ = cam.P(wp)
    cv.text(x + dx * sc, y + dy * sc, s, font, size * sc, col, a, anchor=anchor)


def chip(cv, cam, wp, dx, dy, s, col, a, size=13, fill=None, font=None):
    """Rounded label chip (left edge at wp + dx) - reads over busy geometry."""
    if a <= 0.002:
        return
    font = font or F_MONO_M
    x, y, sc, _ = cam.P(wp)
    w = cv.measure(s, font, size * sc) + 18 * sc
    h = (size + 13) * sc
    x0, y0 = x + dx * sc, y + dy * sc
    cv.rrect(x0, y0 - h / 2, w, h, 6 * sc, col, a, fill=fill or PAPER, fa=.94,
             lw=1.4)
    cv.text(x0 + 9 * sc, y0 + size * .36 * sc, s, font, size * sc, col, a)


def xmark(cv, p, r, col, a, w=3):
    cv.line((p[0] - r, p[1] - r), (p[0] + r, p[1] + r), col, a, w)
    cv.line((p[0] - r, p[1] + r), (p[0] + r, p[1] - r), col, a, w)


def check(cv, p, r, col, a, prog=1.0, w=3):
    """Check mark; prog in [0, 1] draws it progressively."""
    pts = [(p[0] - r, p[1]), (p[0] - r * .3, p[1] + r * .7),
           (p[0] + r, p[1] - r * .8)]
    l2 = lambda u, v, f: (u[0] + (v[0] - u[0]) * f, u[1] + (v[1] - u[1]) * f)  # noqa
    if prog < .5:
        cv.poly([pts[0], l2(pts[0], pts[1], prog * 2)], col, a, w)
    else:
        cv.poly([pts[0], pts[1], l2(pts[1], pts[2], (prog - .5) * 2)], col, a, w)


def marker(cv, p, n, a, col=DIM, txt=INK, r=15, size=16, font=None):
    """Numbered marker - reuse the same identity across acts."""
    if a <= 0.002:
        return
    cv.circle(p, r, None, a, fill=col, fa=1)
    cv.text(p[0], p[1] + size * .37, str(n), font or F_MONO_M, size, txt, a,
            anchor="c")
