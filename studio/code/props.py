# -*- coding: utf-8 -*-
"""Accessoires et décors."""
import math, random
from ink import *

GOLD = hexc('#e2b33c'); GOLD_D = hexc('#a8781c'); ORANGE = hexc('#ff6a13')
RED = hexc('#d7263d'); YEL = hexc('#ffd23f'); CREAM = hexc('#fff4dc')

def bottle(ctx, x, y, s, t, rot=0.0, glow=0.0):
    if s <= 0.01: return
    """flacon doré stylisé (cylindre + étiquette noire + bouchon doré)"""
    sd = boil_seed(t) + 500
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    if glow > 0:
        for i in range(6, 0, -1):
            ctx.new_path(); ctx.arc(0, 0, 120 + i * 22, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.85, 0.35, 0.05 * glow); ctx.fill()
    # corps
    body = [(-95, -60), (-100, 0), (-98, 110), (-80, 130), (80, 130), (98, 110), (100, 0), (95, -60), (60, -75),
            (-60, -75)]
    ink_fill(ctx, lambda c: blob(c, body, sd, 1.0), GOLD, lw=6,
             shade=lambda c: c.rectangle(-110, -80, 50, 230), seed=sd)
    ctx.new_path(); ctx.rectangle(40, -55, 18, 170); ctx.set_source_rgba(1, 1, 0.9, 0.55); ctx.fill()
    # étiquette
    ink_fill(ctx, lambda c: blob(c, [(-70, -35), (70, -35), (70, 85), (-70, 85)], sd + 1, 0.6), hexc('#141414'), lw=4)
    ctx.new_path(); ctx.rectangle(-45, 0, 90, 18); ctx.set_source_rgb(*GOLD); ctx.fill()
    for i in range(5):
        ctx.new_path(); ctx.move_to(-48 + i * 22, -14); ctx.curve_to(-40 + i * 22, -24, -32 + i * 22, -6, -26 + i * 22, -16)
        ctx.set_source_rgb(*GOLD); ctx.set_line_width(3); ctx.stroke()
    ctx.new_path(); ctx.rectangle(-38, 34, 76, 6); ctx.rectangle(-28, 52, 56, 5); ctx.set_source_rgb(*GOLD); ctx.fill()
    # col + bouchon
    ink_fill(ctx, lambda c: blob(c, [(-28, -75), (28, -75), (28, -100), (-28, -100)], sd + 2, 0.5), GOLD_D, lw=5)
    ink_fill(ctx, lambda c: blob(c, [(-62, -100), (62, -100), (66, -170), (-66, -170)], sd + 3, 0.8), GOLD, lw=6,
             shade=lambda c: c.rectangle(-70, -175, 34, 80), seed=sd)
    ctx.new_path(); ctx.rectangle(30, -165, 12, 60); ctx.set_source_rgba(1, 1, 0.9, 0.55); ctx.fill()
    ctx.restore()

def sparkle(ctx, x, y, r, t, ph=0.0, col=(1, 0.95, 0.6)):
    k = 0.5 + 0.5 * math.sin(t * 7 + ph)
    if k < 0.1: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 1.5 + ph)
    ink_fill(ctx, lambda c: star(c, 0, 0, r * k, r * k * 0.28, 4), col, lw=3)
    ctx.restore()

def phone(ctx, x, y, s, t, screen=None, rot=0.0):
    sd = boil_seed(t) + 600
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -55, -100, 110, 200, 18), hexc('#202024'), lw=5)
    ctx.new_path(); rrect(ctx, -46, -88, 92, 176, 10); ctx.set_source_rgb(*hexc('#ffe9b8')); ctx.fill()
    if screen: screen(ctx, t)
    ctx.restore()

def wallet(ctx, x, y, s, t, open_k=0.0):
    sd = boil_seed(t) + 700
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: blob(c, [(-90, -50), (90, -50), (95, 55), (-95, 55)], sd, 1.2), hexc('#7a4b2a'), lw=6,
             shade=lambda c: c.rectangle(-100, 10, 200, 60), seed=sd)
    if open_k > 0:
        ctx.save(); ctx.translate(0, -50); ctx.scale(1, 1 - 1.6 * open_k)
        ink_fill(ctx, lambda c: blob(c, [(-90, 0), (90, 0), (85, -60), (-85, -60)], sd + 1, 1.2), hexc('#8d5a34'), lw=6)
        ctx.restore()
        ctx.new_path(); ctx.rectangle(-80, -50, 160, 14); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.restore()

def moth(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    f = abs(math.sin(t * 22))
    for sx in (-1, 1):
        ctx.save(); ctx.scale(sx, 1)
        ink_fill(ctx, lambda c: blob(c, [(0, 0), (40, -30 * f - 8), (55, 10), (10, 15)], boil_seed(t) + sx, 0.6),
                 hexc('#cfc2a6'), lw=3.5)
        ctx.restore()
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 5, 8, 20, 8), 3, 0.3), hexc('#6d5d48'), lw=3)
    ctx.restore()

def gift(ctx, x, y, s, t, lid=0.0, col=RED):
    if s <= 0.01: return
    sd = boil_seed(t) + 800
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: blob(c, [(-110, -60), (110, -60), (105, 110), (-105, 110)], sd, 1.2), col, lw=6,
             shade=lambda c: c.rectangle(-120, -60, 60, 180), seed=sd)
    ink_fill(ctx, lambda c: c.rectangle(-18, -60, 36, 170), GOLD, lw=4)
    ctx.save(); ctx.translate(0, -60 - lid * 140); ctx.rotate(-lid * 0.5)
    ink_fill(ctx, lambda c: blob(c, [(-125, -40), (125, -40), (125, 5), (-125, 5)], sd + 1, 1.0), col, lw=6)
    ink_fill(ctx, lambda c: c.rectangle(-18, -40, 36, 45), GOLD, lw=4)
    for sx in (-1, 1):
        ink_fill(ctx, lambda c, sx=sx: blob(c, [(0, -40), (sx * 70, -100), (sx * 80, -50)], sd + 2 + sx, 1.0), GOLD, lw=5)
    ctx.restore(); ctx.restore()

def price_tag(ctx, x, y, s, t, txt, sub=None, rot=-0.08, col=YEL, fg=INK):
    if s <= 0.01: return
    sd = boil_seed(t) + 900
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    w = max(text_w(ctx, txt, 150) + 120, 420)
    pts = [(-w / 2, -110), (w / 2 - 60, -110), (w / 2 + 20, 0), (w / 2 - 60, 110), (-w / 2, 110)]
    ctx.new_path(); [ctx.line_to(px + 10, py + 12) for px, py in pts]; ctx.close_path()
    ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ink_fill(ctx, lambda c: blob(c, pts, sd, 1.5), col, lw=8)
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(w / 2 - 50, 0, 18, 18, 8), sd + 1, 0.5), CREAM, lw=5)
    text(ctx, txt, -30, 6 if not sub else 22, 150, fill=fg, stroke=None, shadow=False)
    if sub: text(ctx, sub, -30, -68, 52, font='Patrick Hand', fill=fg, stroke=None, shadow=False)
    ctx.restore()

def cart_icon(ctx, x, y, s, col=ORANGE):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.new_path(); ctx.move_to(-60, -40); ctx.line_to(-40, -40); ctx.line_to(-20, 30); ctx.line_to(50, 30)
    ctx.line_to(62, -20); ctx.line_to(-30, -20)
    ctx.set_source_rgb(*INK); ctx.set_line_width(22); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve(); ctx.set_source_rgb(*col); ctx.set_line_width(12)
    ctx.stroke()
    for wx in (-10, 40):
        ink_fill(ctx, lambda c, wx=wx: c.arc(wx, 52, 11, 0, 2 * math.pi), col, lw=5)
    ctx.restore()

def arrow(ctx, x0, y0, x1, y1, t, col=ORANGE, w=60):
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0)
    ctx.save(); ctx.translate(x0, y0); ctx.rotate(ang)
    hl = w * 1.6
    pts = [(0, -w / 2), (L - hl, -w / 2), (L - hl, -w * 1.15), (L, 0), (L - hl, w * 1.15), (L - hl, w / 2), (0, w / 2)]
    ctx.new_path(); ctx.move_to(pts[0][0] + 8, pts[0][1] + 10)
    for p in pts[1:]: ctx.line_to(p[0] + 8, p[1] + 10)
    ctx.close_path(); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.set_source_rgb(*col); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.restore()

# ------------------------------------------------------------------ fruits & notes
def fruit(ctx, kind, x, y, s, t):
    sd = boil_seed(t) + hash(kind) % 777
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if kind == 'peche':
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 0, 70, 64, 12), sd, 1.2), hexc('#ffa36c'), lw=6,
                 shade=lambda c: c.rectangle(-80, 10, 160, 80), seed=sd)
        ctx.new_path(); ctx.arc(-18, -10, 40, 0, 2 * math.pi); ctx.set_source_rgba(0.95, 0.3, 0.3, 0.35); ctx.fill()
        ink_line(ctx, [(0, -64), (-6, -30)], sd, 4)
        ink_fill(ctx, lambda c: blob(c, [(0, -62), (45, -95), (60, -70)], sd + 1, 0.8), hexc('#5aa34a'), lw=4)
    elif kind == 'passion':
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 0, 66, 66, 12), sd, 1.2), hexc('#6d2a62'), lw=6)
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 6, 46, 40, 10), sd + 1, 1.0), hexc('#f2b51b'), lw=4)
        for i in range(9):
            a = i * 0.7; ctx.new_path(); ctx.arc(math.cos(a) * 24, 6 + math.sin(a) * 20, 5, 0, 7)
            ctx.set_source_rgb(*INK); ctx.fill()
    elif kind == 'poire':
        ink_fill(ctx, lambda c: blob(c, [(0, -80), (25, -60), (32, -20), (65, 30), (55, 75), (0, 88), (-55, 75),
                                          (-65, 30), (-32, -20), (-25, -60)], sd, 1.2), hexc('#c9d94a'), lw=6,
                 shade=lambda c: c.rectangle(-80, 20, 60, 80), seed=sd)
        ink_line(ctx, [(0, -80), (8, -105)], sd, 5)
    elif kind == 'framboise':
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 0, 52, 62, 10), sd, 1.0), hexc('#d8264e'), lw=6)
        for i in range(4):
            for j in range(3):
                ctx.new_path(); ctx.arc(-24 + j * 24 + (i % 2) * 12, -36 + i * 24, 13, 0, 7)
                ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
        ink_fill(ctx, lambda c: blob(c, [(-30, -58), (0, -80), (30, -58), (0, -66)], sd + 1, 0.6), hexc('#5aa34a'), lw=4)
    elif kind == 'cassis':
        for i, (bx, by) in enumerate([(-28, 10), (26, 18), (0, -26), (-6, 44), (40, -20)]):
            ink_fill(ctx, lambda c, bx=bx, by=by: blob(c, ellipse_pts(bx, by, 28, 28, 9), sd + i, 0.6),
                     hexc('#3b1f4f'), lw=5)
            ctx.new_path(); ctx.arc(bx + 8, by - 8, 6, 0, 7); ctx.set_source_rgba(1, 1, 1, 0.5); ctx.fill()
        ink_line(ctx, [(0, -26), (10, -70), (40, -20)], sd, 4)
    elif kind == 'muguet':
        ink_line(ctx, [(0, 110), (5, 20), (20, -60), (50, -100)], sd, 6, color=hexc('#3c7a33'))
        ink_fill(ctx, lambda c: blob(c, [(0, 110), (-60, 0), (-40, -80), (-10, 20)], sd + 1, 1.0), hexc('#5aa34a'), lw=5)
        for i, (bx, by) in enumerate([(5, 20), (12, -10), (20, -40), (35, -70)]):
            ink_fill(ctx, lambda c, bx=bx, by=by: blob(c, [(bx + 10, by), (bx + 36, by + 4), (bx + 40, by + 36),
                                                           (bx + 26, by + 28), (bx + 18, by + 40), (bx + 8, by + 28)],
                                                      sd + i, 0.5), (1, 1, 1), lw=4)
    elif kind == 'musc':
        for i in range(3):
            ctx.new_path(); blob(ctx, [(-60 + i * 10, 40 - i * 30), (-20, 10 - i * 30), (20, 40 - i * 30),
                                       (60 - i * 10, 10 - i * 30)], sd + i, 2, closed=False)
            ctx.set_source_rgba(*hexc('#8a6fb0'), 0.9); ctx.set_line_width(12); ctx.stroke()
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 60, 45, 18, 10), sd, 0.8), hexc('#efe6ff'), lw=4)
    elif kind == 'vanille':
        for k in (-1, 1):
            ink_line(ctx, [(-70 + k * 6, 60), (-10, 0), (60 + k * 6, -70)], sd + k, 18, color=INK)
            ink_line(ctx, [(-70 + k * 6, 60), (-10, 0), (60 + k * 6, -70)], sd + k, 10, color=hexc('#4a2a14'))
        ink_fill(ctx, lambda c: blob(c, [(10, 30), (60, 20), (75, 55), (35, 70)], sd + 3, 1), hexc('#fff3c8'), lw=4)
    elif kind == 'santal':
        ink_fill(ctx, lambda c: blob(c, [(-80, -25), (80, -40), (85, 25), (-78, 40)], sd, 1.0), hexc('#b9824e'), lw=6,
                 shade=lambda c: c.rectangle(-90, 10, 180, 40), seed=sd)
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(82, -8, 14, 32, 8), sd + 1, 0.5), hexc('#e3b98a'), lw=4)
        for i in range(3):
            ink_line(ctx, [(-60, -14 + i * 16), (0, -20 + i * 16), (60, -24 + i * 16)], sd + i, 2.5)
    elif kind == 'patchouli':
        for i, a in enumerate((-0.6, 0, 0.6)):
            ctx.save(); ctx.rotate(a)
            ink_fill(ctx, lambda c: blob(c, [(0, 60), (-34, 0), (-20, -55), (0, -75), (20, -55), (34, 0)], sd + i, 1),
                     hexc('#3e8a3a'), lw=5)
            ink_line(ctx, [(0, 55), (0, -60)], sd + i, 3)
            ctx.restore()
    ctx.restore()

# ------------------------------------------------------------------ décors
def bg_fill(ctx, col):
    ctx.set_source_rgb(*col); ctx.paint()

def bg_paper(ctx, paper, tint=None, alpha=0.0):
    ctx.set_source_surface(paper, 0, 0); ctx.paint()
    if tint:
        ctx.set_source_rgba(*tint, alpha); ctx.paint()

def floor_wall(ctx, t, wall, floor, horizon=1250, seed=0):
    sd = boil_seed(t) + seed
    ctx.set_source_rgb(*wall); ctx.rectangle(0, 0, W, horizon); ctx.fill()
    ctx.set_source_rgb(*floor); ctx.rectangle(0, horizon, W, H - horizon); ctx.fill()
    hatch_rect(ctx, 0, horizon, W, H - horizon, sd, False, 16, 0.25)
    ink_line(ctx, [(-10, horizon), (W / 2, horizon + 4), (W + 10, horizon)], sd, 6)

def window_night(ctx, x, y, w, h, t, seed=0):
    sd = boil_seed(t) + seed
    ink_fill(ctx, lambda c: c.rectangle(x, y, w, h), hexc('#1c2647'), lw=8)
    rnd = random.Random(seed)
    for i in range(14):
        sx, sy = x + rnd.uniform(10, w - 10), y + rnd.uniform(10, h * 0.6)
        sparkle(ctx, sx, sy, 9, t, i, (1, 1, 0.85))
    ctx.new_path(); ctx.arc(x + w * 0.75, y + h * 0.25, 34, 0, 7); ctx.set_source_rgb(*hexc('#fff3c4')); ctx.fill()
    ink_line(ctx, [(x + w / 2, y), (x + w / 2, y + h)], sd, 7)
    ink_line(ctx, [(x, y + h / 2), (x + w, y + h / 2)], sd + 1, 7)

def string_lights(ctx, t, y=330, seed=0, n=9):
    sd = boil_seed(t) + seed
    pts = [(i * W / (n - 1), y + 60 * math.sin(math.pi * (i % 3) / 2)) for i in range(n)]
    ink_line(ctx, [(-20, y)] + [(px, y + 55 * math.sin(px / W * math.pi * 2.0)) for px, _ in pts] + [(W + 20, y)],
             sd, 4)
    for i in range(n):
        px = i * W / (n - 1); py = y + 55 * math.sin(px / W * math.pi * 2.0) + 18
        k = 0.6 + 0.4 * math.sin(t * 4 + i)
        ctx.new_path(); ctx.arc(px, py, 34, 0, 7); ctx.set_source_rgba(1, 0.85, 0.4, 0.22 * k); ctx.fill()
        ink_fill(ctx, lambda c: blob(c, ellipse_pts(px, py, 11, 15, 8), sd + i, 0.4), (1, 0.88, 0.45), lw=3)

def xmas_tree(ctx, x, y, s, t, seed=0):
    sd = boil_seed(t) + seed
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: c.rectangle(-25, 260, 50, 70), hexc('#6b4226'), lw=5)
    for i, (w_, y_) in enumerate([(230, 280), (190, 160), (140, 40)]):
        ink_fill(ctx, lambda c, w_=w_, y_=y_: blob(c, [(-w_, y_), (0, y_ - 210), (w_, y_)], sd + i, 2),
                 hexc('#2f7a3a'), lw=6, shade=lambda c: c.rectangle(-260, -200, 200, 500), seed=sd)
    rnd = random.Random(seed)
    cols = [hexc('#e23b52'), GOLD, hexc('#4a8fe7'), (1, 1, 1)]
    for i in range(16):
        bx = rnd.uniform(-150, 150); by = rnd.uniform(-120, 260)
        if abs(bx) > (by + 170) * 0.62: continue
        ink_fill(ctx, lambda c, bx=bx, by=by: c.arc(bx, by, 13, 0, 7), cols[i % 4], lw=3)
    ink_fill(ctx, lambda c: star(c, 0, -175, 48, 20, 5, t * 0.3), GOLD, lw=5)
    ctx.restore()

def snow(ctx, t, n=60, seed=3, alpha=0.9):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W); sp = rnd.uniform(60, 160); r = rnd.uniform(4, 10); ph = rnd.uniform(0, 100)
        y = (ph * 37 + t * sp) % (H + 40) - 20
        x = x0 + 30 * math.sin(t * 1.3 + ph)
        ctx.new_path(); ctx.arc(x, y, r, 0, 7); ctx.set_source_rgba(1, 1, 1, alpha); ctx.fill()

def speed_lines(ctx, t, cx, cy, col=INK, n=40, alpha=0.35, seed=0):
    rnd = random.Random(seed + boil_seed(t, 12))
    ctx.set_source_rgba(*col, alpha)
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi); r0 = rnd.uniform(380, 520); r1 = r0 + rnd.uniform(300, 900)
        ctx.new_path(); ctx.move_to(cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        ctx.line_to(cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        ctx.set_line_width(rnd.uniform(3, 9)); ctx.stroke()

def rays(ctx, cx, cy, t, col, n=16, alpha=0.25, rot_speed=0.15):
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(t * rot_speed)
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = a0 + math.pi / n
        ctx.new_path(); ctx.move_to(0, 0); ctx.arc(0, 0, 2200, a0, a1); ctx.close_path()
        ctx.set_source_rgba(*col, alpha); ctx.fill()
    ctx.restore()

def smell_swirl(ctx, x, y, t, s=1.0, col=(1, 0.8, 0.3), ph=0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    for k in range(3):
        ctx.new_path()
        for i in range(30):
            u = i / 29; yy = -u * 260; xx = 40 * math.sin(u * 7 + t * 3 + k * 2 + ph) + (k - 1) * 40
            (ctx.move_to if i == 0 else ctx.line_to)(xx, yy)
        ctx.set_source_rgba(*INK, 0.8); ctx.set_line_width(12); ctx.stroke_preserve()
        ctx.set_source_rgba(*col, 0.95); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()
