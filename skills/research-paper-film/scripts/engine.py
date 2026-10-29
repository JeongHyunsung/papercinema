"""Minimal programmatic motion-graphics engine.

pycairo vector drawing in a fixed 1920x1080 design space, scaled to any output
size; easing and keyframe helpers; a small 3-D projection (Cam3); and a clean
white "paper" finish (no bloom, glow, grain or vignette).

Copy this file into your project's src/ and edit the palette and fonts at the
top. Scene helpers (overlays, keyframed values, a look-at stage camera,
billboard text, chips) are in scene_kit.py.
"""
import math
import cairo
import numpy as np
from PIL import Image, ImageFilter

DW, DH = 1920, 1080

# ---------------------------------------------------------------- palette ----
def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[k:k + 2], 16) / 255 for k in (0, 2, 4))

# White identity (semantic tokens; edit for your project):
#   INK      primary text / structure        #17212B
#   GRAPHITE secondary text                  #607080
#   DIM      inactive structure              #D9E0E5
#   TEAL     valid / accepted                #087F8C
#   BLUE     the reference (RBG, expected)   #2764C5
#   CORAL    pruned / failure (vermilion)    #C83F45
#   AMBER    rising clock edge / headline    #B7791F
INK = hexc("17212B")
GRAPHITE = hexc("607080")
DIM = hexc("D9E0E5")
TEAL = hexc("087F8C")
BLUE = hexc("2764C5")
CORAL = hexc("C83F45")
AMBER = hexc("B7791F")
PAPER = hexc("FFFFFF")
BG_IN = PAPER
BG_OUT = PAPER

# Fonts (cairo "toy" names, resolved by fontconfig). NOTE: on some systems the
# bare family "Inter" resolves to the *Medium* face; run
# scripts/figures/setup_fonts.py and use "Inter Regular" for true Regular.
# Check what a PDF really embeds with `pdffonts`.
F_TITLE = "Inter Display SemiBold"
F_TITLE_L = "Inter Display Light"
F_UI = "Inter"
F_UI_L = "Inter Light"
F_UI_M = "Inter Medium"
F_MONO = "JetBrains Mono"
F_MONO_M = "JetBrains Mono Medium"
F_MONO_L = "JetBrains Mono Light"


def mix(a, b, t):
    return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


# ---------------------------------------------------------------- easing -----
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def seg(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def io3(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def oexpo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ocub(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def oback(x, s=1.4):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def window(t, a, b, fin=0.4, fout=0.4):
    """1 inside [a,b] with smooth fades."""
    return smooth(seg(t, a, a + fin)) * (1 - smooth(seg(t, b - fout, b)))


# ---------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.k = W / DW
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.c = cairo.Context(self.surf)
        self.c.set_antialias(cairo.ANTIALIAS_BEST)
        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_GRAY)
        fo.set_hint_style(cairo.HINT_STYLE_NONE)
        fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
        self.c.set_font_options(fo)

    def begin(self):
        c = self.c
        c.identity_matrix()
        c.scale(self.k, self.k)
        c.set_source_rgb(*PAPER)
        c.paint()

    # --- primitives ---------------------------------------------------------
    def rgba(self, col, a=1.0):
        self.c.set_source_rgba(col[0], col[1], col[2], clamp(a))

    def line(self, p, q, col, a=1, w=2, dash=None, cap=cairo.LINE_CAP_ROUND):
        if a <= 0.002 or (abs(p[0] - q[0]) + abs(p[1] - q[1])) < 0.05:
            return
        c = self.c
        c.new_path()
        c.move_to(*p)
        c.line_to(*q)
        self.rgba(col, a)
        c.set_line_width(w)
        c.set_line_cap(cap)
        c.set_dash(dash or [])
        c.stroke()
        c.set_dash([])

    def poly(self, pts, col, a=1, w=2, close=False, fill=None, fa=1.0,
             join=cairo.LINE_JOIN_ROUND):
        if a <= 0.002 or len(pts) < 2:
            return
        c = self.c
        c.new_path()
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        if close:
            c.close_path()
        if fill is not None:
            self.rgba(fill, fa * a)
            c.fill_preserve()
        self.rgba(col, a)
        c.set_line_width(w)
        c.set_line_join(join)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.stroke()

    def circle(self, p, r, col=None, a=1, fill=None, fa=1.0, w=2):
        if a <= 0.002 or r <= 0:
            return
        c = self.c
        c.new_path()
        c.arc(p[0], p[1], r, 0, 2 * math.pi)
        if fill is not None:
            self.rgba(fill, fa * a)
            if col is not None:
                c.fill_preserve()
            else:
                c.fill()
        if col is not None:
            self.rgba(col, a)
            c.set_line_width(w)
            c.stroke()

    def rrect(self, x, y, w, h, r, col=None, a=1, fill=None, fa=1, lw=1.5,
              dash=None):
        if a <= 0.002:
            return
        c = self.c
        c.new_path()
        r = min(r, w / 2, h / 2)
        c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        c.close_path()
        if fill is not None:
            self.rgba(fill, fa * a)
            if col is not None:
                c.fill_preserve()
            else:
                c.fill()
        if col is not None:
            self.rgba(col, a)
            c.set_line_width(lw)
            c.set_dash(dash or [])
            c.stroke()
            c.set_dash([])

    def glow_dot(self, p, r, col, a=1):
        """A faint flat tint behind an emphasized element (no glow)."""
        a *= .13
        r *= .62
        if a <= 0.002:
            return
        c = self.c
        g = cairo.RadialGradient(p[0], p[1], 0, p[0], p[1], r)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
        g.add_color_stop_rgba(0.7, col[0], col[1], col[2], a * .8)
        g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        c.set_source(g)
        c.new_path()
        c.arc(p[0], p[1], r, 0, 2 * math.pi)
        c.fill()

    def shadow(self, x, y, w, h, r, a=1.0, dy=6, spread=14):
        """Selective soft drop shadow for cards/panels (stacked translucent
        rounded rects; reads as a diffuse shadow on white)."""
        if a <= 0.01:
            return
        n = 7
        for k in range(n):
            g = spread * (k + 1) / n
            self.rrect(x - g * .5, y - g * .5 + dy, w + g, h + g, r + g * .5,
                       fill=(0.09, 0.13, 0.17), fa=.022 * a)

    def bezier(self, p, c1, c2, q, col, a=1, w=2, t=1.0, dash=None):
        """Partial cubic bezier (0..t) drawn via subdivision."""
        if a <= 0.002 or t <= 0:
            return None
        pts = [bez(p, c1, c2, q, t * k / 40) for k in range(41)]
        self.poly(pts, col, a, w)
        if dash:
            pass
        return pts[-1], pts[-2]

    def arrowhead(self, tip, frm, col, a=1, size=11):
        if a <= 0.002:
            return
        ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
        pts = [tip,
               (tip[0] - size * math.cos(ang - .42),
                tip[1] - size * math.sin(ang - .42)),
               (tip[0] - size * .72 * math.cos(ang),
                tip[1] - size * .72 * math.sin(ang)),
               (tip[0] - size * math.cos(ang + .42),
                tip[1] - size * math.sin(ang + .42))]
        c = self.c
        c.new_path()
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.close_path()
        self.rgba(col, a)
        c.fill()

    # --- text ---------------------------------------------------------------
    def _runs(self, s):
        """Split on ^{...} superscripts."""
        out, k = [], 0
        while k < len(s):
            j = s.find("^{", k)
            if j < 0:
                out.append((s[k:], False))
                break
            if j > k:
                out.append((s[k:j], False))
            e = s.find("}", j)
            out.append((s[j + 2:e], True))
            k = e + 1
        return out

    def measure(self, s, font, size, track=0.0):
        c = self.c
        wsum = 0
        for txt, sup in self._runs(s):
            c.select_font_face(font)
            c.set_font_size(size * (0.62 if sup else 1))
            for ch in txt:
                wsum += c.text_extents(ch).x_advance + track * size
        return wsum

    def text(self, x, y, s, font=F_UI, size=28, col=INK, a=1.0, anchor="l",
             track=0.0, reveal=1.0):
        """Draw text; reveal<1 types it out character by character."""
        if a <= 0.002 or not s:
            return 0
        c = self.c
        W = self.measure(s, font, size, track)
        if anchor == "c":
            x -= W / 2
        elif anchor == "r":
            x -= W
        nchar = sum(len(t) for t, _ in self._runs(s))
        show = int(round(nchar * clamp(reveal)))
        k = 0
        self.rgba(col, a)
        for txt, sup in self._runs(s):
            sz = size * (0.62 if sup else 1)
            c.select_font_face(font)
            c.set_font_size(sz)
            dy = -size * 0.40 if sup else 0
            if track == 0 and k + len(txt) <= show:
                c.move_to(x, y + dy)
                c.show_text(txt)
                x += c.text_extents(txt).x_advance
                k += len(txt)
                continue
            for ch in txt:
                if k >= show:
                    break
                c.move_to(x, y + dy)
                c.show_text(ch)
                x += c.text_extents(ch).x_advance + track * size
                k += 1
        return W


def bez(p, c1, c2, q, t):
    u = 1 - t
    return (u ** 3 * p[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0]
            + t ** 3 * q[0],
            u ** 3 * p[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1]
            + t ** 3 * q[1])


# ------------------------------------------------------------ 3-D camera -----
class Cam3:
    def __init__(self, yaw=0.0, pitch=0.0, dist=1200.0, f=1100.0,
                 cx=DW / 2, cy=DH / 2):
        self.yaw, self.pitch, self.dist, self.f = yaw, pitch, dist, f
        self.cx, self.cy = cx, cy

    def proj(self, p):
        x, y, z = p
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x, z = x * cy + z * sy, -x * sy + z * cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y, z = y * cp - z * sp, y * sp + z * cp
        zz = z + self.dist
        s = self.f / max(zz, 1e-3)
        return (self.cx + x * s, self.cy + y * s), s, zz

    def proj_np(self, P):
        x, y, z = P[:, 0], P[:, 1], P[:, 2]
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x, z = x * cy + z * sy, -x * sy + z * cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y, z = y * cp - z * sp, y * sp + z * cp
        zz = z + self.dist
        s = self.f / np.maximum(zz, 1e-3)
        return self.cx + x * s, self.cy + y * s, s, zz


# ------------------------------------------------------------ post stack -----
class Post:
    def __init__(self, W, H, seed=7):
        self.W, self.H = W, H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2))
                    ** 2)
        self.vig = (1 - 0.30 * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None] \
            .astype(np.float32)
        rng = np.random.default_rng(seed)
        gs = (H // 2, W // 2)
        self.grain = [np.repeat(np.repeat(
            rng.normal(0, 1.0, gs).astype(np.float32), 2, 0), 2, 1)[..., None]
            for _ in range(6)]
        self.bw, self.bh = max(W // 8, 1), max(H // 8, 1)

    def grab(self, surf):
        """Surface -> RGB uint8 array (copy)."""
        surf.flush()
        a = np.ndarray((self.H, self.W, 4), np.uint8, surf.get_data())
        return np.ascontiguousarray(a[..., [2, 1, 0]])

    def process(self, surf, fidx, extra_add=None, bloom=0.85, grain=2.2):
        return self.process_rgb(self.grab(surf), fidx, extra_add, bloom, grain)

    def process_rgb(self, rgb, fidx, extra_add=None, bloom=0.0, grain=0.0):
        """Clean output: no bloom, vignette, grain or tone curve."""
        if extra_add is None:
            return rgb
        return np.clip(rgb.astype(np.float32) + extra_add, 0, 255).astype(np.uint8)
