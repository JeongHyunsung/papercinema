"""README hero for papercinema: the harness (orchestrator, generator, isolation wall,
reviewer, you) and one real run, drawn in the films' own visual identity.

  python3 harness_hero.py png   ../harness.png        # final state (SHIP), 2x
  python3 harness_hero.py video ../harness_loop.mp4   # 6 rounds, then hold; 1600x900, 30 fps

Pure pycairo; draw(cv, t) is a pure function of time, like every scene in the skill.
The round data are the first production with the review loop (46 findings in 6 rounds).
"""
import math, subprocess, sys
import cairo

W, H = 1600, 900
FPS = 30

# palette (the films' semantic colours, flat tints)
INK, MUTED, LINE = (0.10, 0.12, 0.15), (0.38, 0.42, 0.48), (0.70, 0.73, 0.77)
PAPER, FAINT = (1, 1, 1), (0.955, 0.962, 0.970)
TEAL, TEAL_T = (0.07, 0.47, 0.51), (0.89, 0.95, 0.95)
BLUE, BLUE_T = (0.22, 0.40, 0.76), (0.91, 0.93, 0.985)
AMBER, AMBER_T = (0.78, 0.50, 0.08), (0.995, 0.950, 0.875)
CORAL, CORAL_T = (0.79, 0.27, 0.25), (0.99, 0.915, 0.905)
GREY_T = (0.93, 0.94, 0.95)
SANS, MONO = "Inter", "JetBrains Mono"

# the real run (film rounds)
FINDINGS = [16, 10, 6, 8, 5, 1]
HUMAN = [False, True, False, True, False, True]
T0, DT = 0.6, 1.9                       # round r starts at T0 + (r-1)*DT
DUR = T0 + 6 * DT + 0.4
HOLD = 2.5


# ------------------------------------------------------------------ helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def seg(t, a, b): return ease((t - a) / (b - a))


def rr(cv, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cv.new_sub_path()
    cv.arc(x + w - r, y + r, r, -math.pi / 2, 0); cv.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cv.arc(x + r, y + h - r, r, math.pi / 2, math.pi); cv.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cv.close_path()


def card(cv, x, y, w, h, stroke=LINE, fill=PAPER, r=16, lw=1.6, shadow=True):
    if shadow:
        for i, a in enumerate((0.045, 0.03, 0.018)):
            rr(cv, x, y + 2 + 2 * i, w, h, r); cv.set_source_rgba(0, 0, 0, a); cv.fill()
    rr(cv, x, y, w, h, r); cv.set_source_rgb(*fill); cv.fill_preserve()
    cv.set_source_rgb(*stroke); cv.set_line_width(lw); cv.stroke()


def font(cv, size, bold=False, mono=False, italic=False):
    cv.select_font_face(MONO if mono else SANS,
                        cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    cv.set_font_size(size)


def tw(cv, s, size, bold=False, mono=False, italic=False):
    font(cv, size, bold, mono, italic); return cv.text_extents(s).x_advance


def text(cv, x, y, s, size=19, col=INK, bold=False, mono=False, italic=False, anchor="l", a=1.0):
    font(cv, size, bold, mono, italic)
    w = cv.text_extents(s).x_advance
    x0 = x - {"l": 0, "c": w / 2, "r": w}[anchor]
    cv.move_to(x0, y); cv.set_source_rgba(*col, a); cv.show_text(s)
    return w


def pill(cv, x, y, s, col, fill, size=17, bold=False, mono=False, anchor="l", a=1.0, check=False, strike=False):
    pad = 12; cw = 18 if check else 0
    w = tw(cv, s, size, bold, mono) + 2 * pad + cw; h = size + 15
    if anchor == "c": x -= w / 2
    cv.push_group()
    rr(cv, x, y - h / 2, w, h, h / 2); cv.set_source_rgb(*fill); cv.fill_preserve()
    cv.set_source_rgb(*col); cv.set_line_width(1.4); cv.stroke()
    if check:
        cx, cy = x + pad + 5, y
        cv.move_to(cx - 5, cy); cv.line_to(cx - 1, cy + 4); cv.line_to(cx + 6, cy - 5)
        cv.set_source_rgb(*col); cv.set_line_width(2.2); cv.stroke()
    text(cv, x + pad + cw, y + size * 0.36, s, size, col, bold=bold, mono=mono)
    if strike:
        cv.move_to(x + pad - 2, y + 1); cv.line_to(x + w - pad + 2, y + 1)
        cv.set_source_rgb(*col); cv.set_line_width(1.8); cv.stroke()
    cv.pop_group_to_source(); cv.paint_with_alpha(a)
    return w


def arrow(cv, x0, y0, x1, y1, col, lw=2.6, head=13, a=1.0):
    ang = math.atan2(y1 - y0, x1 - x0)
    cv.set_source_rgba(*col, a); cv.set_line_width(lw)
    cv.move_to(x0, y0); cv.line_to(x1 - math.cos(ang) * head * 0.7, y1 - math.sin(ang) * head * 0.7); cv.stroke()
    cv.move_to(x1, y1)
    for s in (-0.42, 0.42):
        cv.line_to(x1 - head * math.cos(ang + s), y1 - head * math.sin(ang + s))
    cv.close_path(); cv.fill()


def check_row(cv, x, y, s, on, col=TEAL):
    cv.arc(x + 11, y - 7, 11, 0, 2 * math.pi)
    cv.set_source_rgb(*(col if on else GREY_T)); cv.fill()
    if on:
        cv.move_to(x + 5, y - 7); cv.line_to(x + 9.5, y - 2.5); cv.line_to(x + 17, y - 12)
        cv.set_source_rgb(*PAPER); cv.set_line_width(2.4); cv.stroke()
    text(cv, x + 32, y, s, 19, INK if on else MUTED)


# ------------------------------------------------------------------ icons
def ic_doc(cv, x, y, w, h, col=INK):
    f = w * 0.22
    cv.move_to(x, y); cv.line_to(x + w - f, y); cv.line_to(x + w, y + f); cv.line_to(x + w, y + h)
    cv.line_to(x, y + h); cv.close_path()
    cv.set_source_rgb(*PAPER); cv.fill_preserve(); cv.set_source_rgb(*col); cv.set_line_width(1.8); cv.stroke()
    cv.move_to(x + w - f, y); cv.line_to(x + w - f, y + f); cv.line_to(x + w, y + f); cv.stroke()
    cv.set_line_width(2.0); cv.set_source_rgba(*col, 0.85)
    cv.move_to(x + w * 0.14, y + h * 0.17); cv.line_to(x + w * 0.62, y + h * 0.17); cv.stroke()
    cv.set_line_width(1.2); cv.set_source_rgba(*col, 0.45)
    for i in range(3):
        yy = y + h * (0.29 + 0.07 * i); cv.move_to(x + w * 0.14, yy); cv.line_to(x + w * 0.86, yy); cv.stroke()
    bx, by, bw, bh = x + w * 0.14, y + h * 0.53, w * 0.72, h * 0.30
    cv.set_source_rgb(*TEAL_T); cv.rectangle(bx, by, bw, bh); cv.fill()
    for i, v in enumerate((0.45, 0.8, 0.6, 0.95)):
        cv.set_source_rgb(*(AMBER if i == 3 else TEAL))
        cv.rectangle(bx + bw * (0.1 + 0.21 * i), by + bh * (1 - v * 0.85), bw * 0.13, bh * v * 0.85); cv.fill()
    cv.set_line_width(1.2); cv.set_source_rgba(*col, 0.45)
    for i in range(2):
        yy = y + h * (0.89 + 0.0 * i); cv.move_to(x + w * 0.14, yy); cv.line_to(x + w * 0.7, yy); cv.stroke()


def ic_grid(cv, cx, cy, s=64, n=4):
    c = s / n
    for i in range(n):
        for j in range(n):
            on = j < 3
            rr(cv, cx - s / 2 + i * c + 2, cy - s / 2 + j * c + 2, c - 4, c - 4, 3)
            cv.set_source_rgb(*(TEAL if on else GREY_T)); cv.fill()


def ic_wave(cv, cx, cy, w=70, h=44):
    vals = [0.25, 0.5, 0.9, 0.6, 0.35, 0.75, 1.0, 0.55, 0.3, 0.65, 0.45, 0.2]
    bw = w / len(vals)
    for i, v in enumerate(vals):
        rr(cv, cx - w / 2 + i * bw + 1.2, cy - h * v / 2, bw - 2.4, h * v, 2)
        cv.set_source_rgb(*TEAL); cv.fill()


def cloud(cv, x, y, w, h, n=70, seed=3, hi=True, pruned=False):
    import random
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * 2 * math.pi; r = math.sqrt(rnd.random())
        px, py = x + w / 2 + r * w * 0.46 * math.cos(a), y + h / 2 + r * h * 0.44 * math.sin(a)
        near = math.hypot(px - (x + w * 0.62), py - (y + h * 0.45)) < w * 0.17
        col = TEAL if near else (CORAL if (pruned and i % 7 == 0) else (0.72, 0.75, 0.79))
        cv.arc(px, py, 2.6 if near else 2.2, 0, 2 * math.pi); cv.set_source_rgb(*col); cv.fill()
    if hi:
        cv.arc(x + w * 0.62, y + h * 0.45, 5.5, 0, 2 * math.pi); cv.set_source_rgb(*AMBER); cv.fill()


def ic_frame(cv, x, y, w, h, play=True, col=TEAL):
    rr(cv, x, y, w, h, 8); cv.set_source_rgb(*PAPER); cv.fill_preserve()
    cv.set_source_rgb(*col); cv.set_line_width(1.8); cv.stroke()
    cloud(cv, x + 6, y + 6, w - 12, h - 18, n=int(w * h / 260) + 20, pruned=True)
    cv.set_source_rgb(*GREY_T); cv.rectangle(x + 8, y + h - 9, w - 16, 3); cv.fill()
    cv.set_source_rgb(*col); cv.rectangle(x + 8, y + h - 9, (w - 16) * 0.62, 3); cv.fill()
    if play:
        cx, cy, s = x + w / 2, y + h / 2 - 4, min(w, h) * 0.16
        cv.arc(cx, cy, s * 1.5, 0, 2 * math.pi); cv.set_source_rgba(*PAPER, 0.88); cv.fill()
        cv.move_to(cx - s * 0.55, cy - s * 0.8); cv.line_to(cx + s * 0.9, cy); cv.line_to(cx - s * 0.55, cy + s * 0.8)
        cv.close_path(); cv.set_source_rgb(*col); cv.fill()


def ic_stack(cv, x, y, w, h, col=BLUE):
    for i in range(3):
        rr(cv, x + i * 6, y + i * 6, w - 12, h - 12, 5); cv.set_source_rgb(*PAPER); cv.fill_preserve()
        cv.set_source_rgb(*col); cv.set_line_width(1.5); cv.stroke()
    cv.set_line_width(1.4); cv.set_source_rgba(*col, 0.55)
    for k in range(3):
        yy = y + 12 + 12 + k * 8; cv.move_to(x + 20, yy); cv.line_to(x + w - 12, yy); cv.stroke()


def ic_bubble(cv, x, y, w, h, col=AMBER, fill=AMBER_T):
    rr(cv, x, y, w, h - 10, 10); cv.set_source_rgb(*fill); cv.fill_preserve()
    cv.set_source_rgb(*col); cv.set_line_width(1.6); cv.stroke()
    cv.move_to(x + 16, y + h - 11); cv.line_to(x + 14, y + h); cv.line_to(x + 28, y + h - 11)
    cv.set_source_rgb(*fill); cv.fill_preserve(); cv.set_source_rgb(*col); cv.stroke()
    cv.set_source_rgb(*fill); cv.rectangle(x + 17, y + h - 13, 10, 3); cv.fill()
    cv.set_line_width(1.6); cv.set_source_rgba(*col, 0.7)
    for k in range(2):
        yy = y + 14 + k * 11; cv.move_to(x + 12, yy); cv.line_to(x + w - 12 - k * 14, yy); cv.stroke()


def ic_person(cv, cx, cy, s=30, col=AMBER):
    cv.arc(cx, cy - s * 0.42, s * 0.34, 0, 2 * math.pi); cv.set_source_rgb(*col); cv.fill()
    cv.arc(cx, cy + s * 0.62, s * 0.62, math.pi, 2 * math.pi); cv.close_path(); cv.fill()


def ic_figs(cv, x, y, w, h):
    for i in range(3):
        xx, yy = x + i * 16, y + i * 12
        rr(cv, xx, yy, w - 32, h - 24, 6); cv.set_source_rgb(*PAPER); cv.fill_preserve()
        cv.set_source_rgb(*TEAL); cv.set_line_width(1.6); cv.stroke()
    bx, by = x + 32 + 12, y + 24 + 12
    for k, v in enumerate((0.5, 0.85, 0.35, 0.7)):
        cv.set_source_rgb(*(AMBER if k == 1 else TEAL))
        cv.rectangle(bx + k * 18, by + (h - 64) * (1 - v), 11, (h - 64) * v); cv.fill()


# ------------------------------------------------------------------ the frame
M = 40
IN_X, IN_W = M, 200
G_X, G_W = 280, 400
WALL_C, WALL_W = 770, 56              # wall centre and width
R_X, R_W = 860, 400
O_X = 1296; O_W = W - M - O_X
TOP, MAIN_B = 104, 568                # main row
LOW, LOW_B = 596, 868                 # lower row
HEAD = 82                             # panel header band


def round_of(t):
    if t < T0: return 0, 0.0
    r = min(6, int((t - T0) // DT) + 1)
    return r, clamp((t - T0 - (r - 1) * DT) / DT)


def panel(cv, x, w, title, sub, col, tint, glow=0.0):
    card(cv, x, TOP, w, MAIN_B - TOP, col, lw=2.6)
    if glow > 0:
        rr(cv, x - 5, TOP - 5, w + 10, MAIN_B - TOP + 10, 20); cv.set_source_rgba(*col, 0.35 * glow)
        cv.set_line_width(4); cv.stroke()
    cv.save(); rr(cv, x, TOP, w, MAIN_B - TOP, 16); cv.clip()
    cv.rectangle(x, TOP, w, HEAD); cv.set_source_rgb(*tint); cv.fill(); cv.restore()
    rr(cv, x, TOP, w, MAIN_B - TOP, 16); cv.set_source_rgb(*col); cv.set_line_width(2.6); cv.stroke()
    text(cv, x + 24, TOP + 42, title, 27, col, bold=True)
    text(cv, x + 24, TOP + 68, sub, 18, col)


def draw(cv, t, final=False):
    if final: t = DUR + 1
    r, ph = round_of(t)
    shipped = t >= T0 + 6 * DT - 0.25
    cv.set_source_rgb(*PAPER); cv.paint()

    # orchestrator header
    rr(cv, M, 26, W - 2 * M, 52, 26); cv.set_source_rgb(*FAINT); cv.fill_preserve()
    cv.set_source_rgb(*LINE); cv.set_line_width(1.4); cv.stroke()
    w = text(cv, M + 30, 59, "ORCHESTRATOR", 20, MUTED, bold=True)
    text(cv, M + 30 + w + 18, 59, "the agent you talk to: asks once, routes files between the roles, keeps the round log. It never edits the film.", 19, MUTED)

    # ---- inputs
    card(cv, IN_X, TOP, IN_W, 214)
    ic_doc(cv, IN_X + 22, TOP + 24, 76, 100)
    text(cv, IN_X + 112, TOP + 62, "paper", 23, INK, bold=True)
    text(cv, IN_X + 112, TOP + 88, ".pdf", 19, MUTED, mono=True)
    text(cv, IN_X + 22, TOP + 178, "+ your data", 19, MUTED)
    card(cv, IN_X, TOP + 238, IN_W, MAIN_B - TOP - 238)
    text(cv, IN_X + 22, TOP + 280, "Asked once", 23, INK, bold=True)
    for i, s in enumerate(["length, voice", "example to walk", "figures needed", "review every K"]):
        cv.arc(IN_X + 28, TOP + 318 + i * 34 - 6, 4, 0, 2 * math.pi); cv.set_source_rgb(*MUTED); cv.fill()
        text(cv, IN_X + 42, TOP + 318 + i * 34, s, 19, INK)
    arrow(cv, IN_X + IN_W + 6, TOP + 107, G_X - 8, TOP + 107, LINE, lw=2.2)
    arrow(cv, IN_X + IN_W + 6, TOP + 350, G_X - 8, TOP + 350, LINE, lw=2.2)

    # ---- generator
    panel(cv, G_X, G_W, "GENERATOR", "one agent for every round", TEAL, TEAL_T)
    tiles = [("rebuild", ic_grid), ("narrate", ic_wave), ("render", None)]
    tws, th, gap = 112, 124, 12
    tx, ty = G_X + (G_W - 3 * tws - 2 * gap) / 2, TOP + HEAD + 18
    for i, (lab, ic) in enumerate(tiles):
        x = tx + i * (tws + gap)
        active = (not shipped) and r >= 1 and ph < 0.22 and int(ph / 0.0734) == i
        rr(cv, x, ty, tws, th, 12); cv.set_source_rgb(*(TEAL_T if active else FAINT)); cv.fill()
        if ic is ic_grid: ic_grid(cv, x + tws / 2, ty + 48, 58)
        elif ic is ic_wave: ic_wave(cv, x + tws / 2, ty + 48, 70, 44)
        else: ic_frame(cv, x + 12, ty + 16, tws - 24, 66, play=False)
        text(cv, x + tws / 2, ty + th - 14, lab, 18, TEAL if active else INK, bold=True, anchor="c")
    text(cv, G_X + 24, ty + th + 34, "frames drawn from the rebuilt method", 18, INK)
    text(cv, G_X + 24, ty + th + 78, "gates to pass before each hand-off", 18, MUTED)
    gate_lit = shipped or ((r >= 1) and 0.16 < ph < 0.26)
    for row, gs in enumerate((("motion", "linkage", "peaks"), ("argument", "readability", "sound"))):
        x = G_X + 24
        for g in gs:
            x += pill(cv, x, ty + th + 112 + row * 42, g, TEAL, TEAL_T if gate_lit else PAPER, 16, check=True) + 8
    text(cv, G_X + 24, MAIN_B - 20, "revises from review.md and nothing else", 18, MUTED)

    # ---- isolation wall
    wx = WALL_C - WALL_W / 2
    cv.save(); rr(cv, wx, TOP - 8, WALL_W, LOW_B - TOP + 8, 10); cv.clip()
    cv.set_source_rgb(*FAINT); cv.paint()
    cv.set_source_rgba(*INK, 0.10); cv.set_line_width(1.6)
    for k in range(-20, 70):
        y0 = TOP - 8 + k * 16; cv.move_to(wx, y0); cv.line_to(wx + WALL_W, y0 + 36); cv.stroke()
    cv.restore()
    cv.save(); cv.translate(WALL_C + 7, (TOP + 440 + LOW_B) / 2 + 14); cv.rotate(-math.pi / 2)
    s = "ISOLATION WALL"; w = tw(cv, s, 18, bold=True)
    cv.rectangle(-w / 2 - 12, -20, w + 24, 28); cv.set_source_rgb(*PAPER); cv.fill()
    text(cv, 0, 0, s, 18, INK, bold=True, anchor="c")
    cv.restore()

    YF, YB = TOP + 190, TOP + 392
    arrow(cv, G_X + G_W + 2, YF, R_X - 4, YF, INK, lw=2.8)
    arrow(cv, R_X - 2, YB, G_X + G_W + 4, YB, INK, lw=2.8)
    for y, s in ((YF - 22, "video + subtitles"), (YB - 22, "review.md only")):
        w = tw(cv, s, 18, bold=True)
        rr(cv, WALL_C - w / 2 - 10, y - 20, w + 20, 28, 8); cv.set_source_rgb(*PAPER); cv.fill()
        text(cv, WALL_C, y, s, 18, INK, bold=True, anchor="c")
    if not shipped and r >= 1:
        span = R_X - G_X - G_W
        if 0.24 < ph < 0.50:
            k = seg(ph, 0.24, 0.48); x = G_X + G_W + 48 + k * (span - 96)
            ic_frame(cv, x - 40, YF + 12, 80, 52, play=True)
        elif 0.72 < ph < 0.98:
            k = seg(ph, 0.72, 0.96); x = R_X - 64 - k * (span - 128)
            pill(cv, x, YB + 28, "review.md", BLUE, BLUE_T, 16, bold=True, anchor="c")

    # ---- reviewer
    reading = (not shipped) and r >= 1 and 0.48 < ph < 0.72
    panel(cv, R_X, R_W, "REVIEWER", "a fresh agent each round", BLUE, BLUE_T,
          glow=math.sin(math.pi * clamp((ph - 0.48) / 0.24)) if reading else 0.0)
    text(cv, R_X + 24, TOP + HEAD + 30, "sees only what an audience sees", 18, MUTED)
    sw, sh, sg = 80, 64, 10
    sx, sy = R_X + (R_W - 4 * sw - 3 * sg) / 2, TOP + HEAD + 44
    for i, lab in enumerate(["video", "paper", "history", "you"]):
        x = sx + i * (sw + sg)
        rr(cv, x, sy, sw, sh, 10); cv.set_source_rgb(*FAINT); cv.fill()
        if i == 0: ic_frame(cv, x + 9, sy + 9, sw - 18, sh - 18, play=True, col=BLUE)
        elif i == 1: ic_doc(cv, x + sw / 2 - 17, sy + 7, 34, 50, BLUE)
        elif i == 2: ic_stack(cv, x + 13, sy + 8, sw - 20, sh - 12)
        else: ic_bubble(cv, x + 12, sy + 12, sw - 24, sh - 22)
        text(cv, x + sw / 2, sy + sh + 22, lab, 18, INK, anchor="c")
    ny = sy + sh + 60
    x = R_X + 24
    x += text(cv, x, ny + 6, "never sees", 18, MUTED) + 12
    for s in ("code", "plan", "notes"):
        x += pill(cv, x, ny, s, CORAL, CORAL_T, 16, strike=True) + 8
    # review.md
    ry, rb = ny + 28, MAIN_B - 16
    rr(cv, R_X + 20, ry, R_W - 40, rb - ry, 12); cv.set_source_rgb(*PAPER); cv.fill_preserve()
    cv.set_source_rgb(*LINE); cv.set_line_width(1.4); cv.stroke()
    w = text(cv, R_X + 38, ry + 32, "review.md", 19, INK, bold=True, mono=True)
    verdict, vc, vf = ("SHIP", TEAL, TEAL_T) if shipped else ("REVISE", CORAL, CORAL_T)
    if shipped or (r >= 1 and ph > 0.62):
        pill(cv, R_X + 38 + w + 14, ry + 25, verdict, vc, vf, 16, bold=True)
    text(cv, R_X + R_W - 38, ry + 32, "done when", 15, MUTED, anchor="r")
    rows = [("MAJOR", AMBER, AMBER_T, "opening hard to follow"),
            ("MAJOR", AMBER, AMBER_T, "one chart for all cases"),
            ("MINOR", MUTED, GREY_T, "label hides a marker")]
    for i, (sev, c, f, s) in enumerate(rows):
        yy = ry + 70 + i * 38
        done = shipped
        w = pill(cv, R_X + 38, yy, sev, c, f, 14, bold=True, mono=True)
        text(cv, R_X + 38 + w + 12, yy + 6, s, 18, MUTED if done else INK)
        bx = R_X + R_W - 38 - 44
        rr(cv, bx + 11, yy - 11, 22, 22, 5); cv.set_source_rgb(*(TEAL if done else PAPER)); cv.fill_preserve()
        cv.set_source_rgb(*(TEAL if done else LINE)); cv.set_line_width(1.6); cv.stroke()
        if done:
            cv.move_to(bx + 16, yy); cv.line_to(bx + 20.5, yy + 5); cv.line_to(bx + 28, yy - 5)
            cv.set_source_rgb(*PAPER); cv.set_line_width(2.4); cv.stroke()

    # ---- output column
    card(cv, O_X, TOP, O_W, 182)
    text(cv, O_X + 22, TOP + 40, "Ships when", 23, INK, bold=True)
    check_row(cv, O_X + 22, TOP + 84, "reviewer: SHIP", shipped)
    check_row(cv, O_X + 22, TOP + 120, "all gates pass", shipped or r >= 1)
    check_row(cv, O_X + 22, TOP + 156, "you approve", shipped)
    oa = 1.0 if final else 0.30 + 0.70 * seg(t, T0 + 6 * DT - 0.25, T0 + 6 * DT + 0.5)
    cv.push_group()
    card(cv, O_X, TOP + 206, O_W, MAIN_B - TOP - 206, TEAL, lw=2.4)
    ic_frame(cv, O_X + 18, TOP + 224, O_W - 36, 148, play=True)
    text(cv, O_X + 22, TOP + 410, "Film", 23, INK, bold=True)
    text(cv, O_X + 22, TOP + 438, "4K60 · voice · subtitles", 18, MUTED)
    card(cv, O_X, LOW, O_W, LOW_B - LOW, TEAL, lw=2.4)
    ic_figs(cv, O_X + 26, LOW + 26, 170, 136)
    text(cv, O_X + 22, LOW + 218, "Slide figures", 23, INK, bold=True)
    text(cv, O_X + 22, LOW + 246, "PNG · SVG · PDF", 18, MUTED)
    cv.pop_group_to_source(); cv.paint_with_alpha(oa)
    arrow(cv, R_X + R_W + 4, TOP + 296, O_X - 6, TOP + 296, LINE, lw=2.2, a=oa)

    # ---- you
    you_on = shipped or ((r >= 1) and HUMAN[r - 1] and 0.30 < ph < 0.70)
    card(cv, R_X, LOW, R_W, LOW_B - LOW, AMBER, AMBER_T if you_on else PAPER, lw=2.4 if you_on else 1.8)
    ic_person(cv, R_X + 48, LOW + 58, 40)
    text(cv, R_X + 86, LOW + 52, "YOU", 27, AMBER, bold=True)
    text(cv, R_X + 86, LOW + 80, "review every K rounds", 19, AMBER)
    rr(cv, R_X + 20, LOW + 104, R_W - 40, 64, 12); cv.set_source_rgb(*PAPER); cv.fill_preserve()
    cv.set_source_rgb(*AMBER); cv.set_line_width(1.6); cv.stroke()
    text(cv, R_X + R_W / 2, LOW + 143, "“Too busy. Simplify the opening.”", 19, INK, italic=True, anchor="c")
    text(cv, R_X + 22, LOW + 212, "reaches the reviewer word for word;", 18, INK)
    text(cv, R_X + 22, LOW + 240, "if it contradicts the paper, you decide", 18, MUTED)
    arrow(cv, R_X + R_W / 2, LOW - 4, R_X + R_W / 2, MAIN_B + 6, AMBER, lw=2.8, a=1.0 if you_on else 0.4)

    # ---- one real run
    cw_ = G_X + G_W - IN_X
    card(cv, IN_X, LOW, cw_, LOW_B - LOW)
    w = text(cv, IN_X + 22, LOW + 40, "One real run", 23, INK, bold=True)
    x = IN_X + 22 + w + 16
    x += text(cv, x, LOW + 40, "findings per round  ·", 18, MUTED) + 12
    ic_person(cv, x + 8, LOW + 34, 15, AMBER)
    text(cv, x + 26, LOW + 40, "you reviewed", 18, MUTED)
    total = sum(FINDINGS) if shipped else (sum(FINDINGS[:max(0, r - 1)]) + (FINDINGS[r - 1] if (r >= 1 and ph > 0.62) else 0))
    msg = f"{total} findings, all closed before it shipped" if shipped else f"{total} findings so far"
    text(cv, IN_X + 22, LOW + 70, msg, 19, TEAL if shipped else INK, bold=True)
    cols = 6; cx0 = IN_X + 34; colw = (cw_ - 68) / cols
    base, hmax = LOW + 200, 92
    for i in range(cols):
        x = cx0 + i * colw + colw / 2
        live = shipped or (r > i + 1) or (r == i + 1 and ph > 0.62)
        cur = (not shipped) and r == i + 1
        v = FINDINGS[i]; hh = hmax * v / max(FINDINGS)
        if cur:
            rr(cv, x - colw / 2 + 8, LOW + 84, colw - 16, LOW_B - LOW - 92, 10); cv.set_source_rgb(*FAINT); cv.fill()
        if live:
            rr(cv, x - 22, base - hh, 44, hh, 5); cv.set_source_rgb(*(TEAL if i == 5 else CORAL)); cv.fill()
            text(cv, x, base - hh - 9, str(v), 19, INK, mono=True, anchor="c")
        text(cv, x, base + 28, f"r0{i + 1}", 18, INK if (live or cur) else MUTED, mono=True, anchor="c")
        if HUMAN[i]:
            ic_person(cv, x, base + 50, 14, AMBER if (live or cur) else LINE)
    cv.set_source_rgb(*LINE); cv.set_line_width(1.4); cv.move_to(cx0, base); cv.line_to(cx0 + cols * colw, base); cv.stroke()


# ------------------------------------------------------------------ output
def render_png(path, scale=2):
    sf = cairo.ImageSurface(cairo.FORMAT_RGB24, W * scale, H * scale)
    cv = cairo.Context(sf); cv.scale(scale, scale); draw(cv, 0, final=True); sf.write_to_png(path)


def render_video(path, scale=1):
    w, h = int(W * scale), int(H * scale)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    for i in range(int((DUR + HOLD) * FPS)):
        cv = cairo.Context(sf); cv.scale(scale, scale); draw(cv, min(i / FPS, DUR + 1))
        ff.stdin.write(bytes(sf.get_data()))
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    render_png(out) if mode == "png" else render_video(out)
