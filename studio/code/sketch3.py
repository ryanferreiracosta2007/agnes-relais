# -*- coding: utf-8 -*-
"""Sketch « Le cadeau de Noël » : Inès (I) / David (D). Zone sûre TikTok, sous-titres mot par mot, émotions."""
import math, random, json, cairo
from ink import *
from chars import draw_char
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash, shake_at, speed_lines

SAFE_CX, CAP_Y = 480, 1190
BANNER = "UN CADEAU À MOINS DE 25 € ?!"
IX, DX, CY = 330, 770, 700
G = 0.07

FIX = {'LATAFA': 'LATTAFA', 'LATAFA.': 'LATTAFA.', 'LATTAFA': 'LATTAFA', 'CONFIDENTIEL': 'CONFIDENTIAL'}

def load_words(clip):
    W_ = json.load(open('words_cadeau.json'))[f'clips/{clip}.wav']
    out = []
    for w_, a, b in W_:
        w_ = w_.strip().upper()
        if not w_: continue
        if out and (w_.startswith("'") or w_ in ('?', '!', '?!', ',', '.')):
            out[-1] = (out[-1][0] + ("" if w_.startswith("'") else " ") + w_, out[-1][1]); continue
        out.append((FIX.get(w_, w_), a))
    return out

ORDER = [('x4_i1', 'I'), ('x4_d1', 'D'), ('x4_i2', 'I'), ('x4_d2', 'D'), ('x4_i3', 'I'), ('x4_d3', 'D'), ('x4_i4', 'I'),
         ('x4_d4', 'D'), ('x4_d5', 'D')]
PAUSE_BEFORE = {'x4_i2': 1.35, 'x4_i4': 1.7, 'x4_d3': 0.25, 'x4_d5': 0.1}

def schedule():
    t = 0.12; T = {}
    for c, _ in ORDER:
        t += PAUSE_BEFORE.get(c, 0); T[c] = t; t += clip_len(c) + G
    return T, t + 1.3

T, DUR = schedule()
LINES = [(c, w, load_words(c)) for c, w in ORDER]

def page_cuts(words, maxw=780, size=104, gap=22, maxlines=2):
    """coupe automatiquement en pages de 2 lignes max"""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4); c = cairo.Context(surf)
    cuts = []; lines = 1; cur = 0
    for i, (w_, r) in enumerate(words):
        wd = text_w(c, w_, size)
        if cur and cur + gap + wd > maxw:
            lines += 1; cur = 0
            if lines > maxlines: cuts.append(i); lines = 1
        cur += (gap if cur else 0) + wd
        if w_.endswith(('.', '?', '!', '?!')) and i + 1 < len(words) and (not cuts or cuts[-1] != i + 1) and lines >= 1 and cur > 300:
            cuts.append(i + 1); lines = 1; cur = 0
    return sorted(set(cuts))

def captions(ctx, t, y=CAP_Y):
    for clip, who, words in LINES:
        if not words: continue
        a = T[clip]; L = clip_len(clip)
        later = [T[c] for c, _ in ORDER if T[c] > a]
        end = min([a + L + 0.25] + later)
        if not (a <= t < end): continue
        cuts = [0] + page_cuts(words) + [len(words)]
        page = None
        for i in range(len(cuts) - 1):
            if t - a >= words[cuts[i]][1] - 0.05: page = (cuts[i], cuts[i + 1])
        if page is None: return
        ws = words[page[0]:page[1]]; size = 104; gap = 22
        lines = [[]]; cur = 0
        for w_, r in ws:
            wd = text_w(ctx, w_, size)
            if lines[-1] and cur + gap + wd > 780: lines.append([]); cur = 0
            lines[-1].append((w_, r, wd)); cur += (gap if cur else 0) + wd
        for li, ln in enumerate(lines):
            tot = sum(wd for _, _, wd in ln) + gap * (len(ln) - 1)
            sc = min(1.0, 860 / tot)
            x = SAFE_CX - tot * sc / 2; yy = y + (li - (len(lines) - 1) / 2) * size * 1.08
            for w_, r, wd in ln:
                ta = a + r
                if t >= ta - 0.03:
                    k = ease_out_back((t - ta + 0.03) / 0.18, 2.6)
                    nxt = [rr for _, rr in ws if rr > r]
                    active = t < a + (min(nxt) if nxt else L + 0.25)
                    col = YEL if active else (1, 1, 1)
                    if 'PANIER' in w_ or 'ORANGE' in w_: col = ORANGE
                    ctx.save(); ctx.translate(x + wd * sc / 2, yy - (10 if active else 0)); ctx.rotate((-0.05 if len(w_) % 2 else 0.05) if active else 0)
                    text(ctx, w_, 0, 0, size * sc, fill=col, sw=15 * sc, scale=k * (1.12 if active else 1.0))
                    ctx.restore()
                x += (wd + gap) * sc

def banner(ctx, t):
    k = pop(t, 0.0, 0.3) if t < 0.4 else 1.0
    ctx.save(); ctx.translate(SAFE_CX, 275); ctx.scale(k, k); ctx.rotate(-0.02)
    size = 70; w = text_w(ctx, BANNER, size) + 60
    ctx.new_path(); rrect(ctx, -w / 2 + 7, -48 + 9, w, 96, 22); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -48, w, 96, 22); ctx.set_source_rgb(*hexc('#d7263d')); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, BANNER, 0, 2, size, fill=(1, 1, 1), stroke=None, shadow=False)
    ctx.restore()

def view(ctx, z, wx, wy, sx=SAFE_CX + 20, sy=760, shake=0.0, t=0.0):
    dx, dy = jit(boil_seed(t, 30), 5, shake) if shake else (0, 0)
    ctx.translate(sx + dx, sy + dy); ctx.scale(z, z); ctx.translate(-wx, -wy)

def steam(ctx, x, y, t):
    for s in (-1, 1):
        for i in range(3):
            u = (t * 2.2 + i / 3) % 1.0
            px = x + s * (120 + 40 * u); py = y - 20 - 160 * u
            ctx.new_path(); ctx.arc(px, py, 18 + 30 * u, 0, 7)
            ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - u)); ctx.fill_preserve(); ctx.set_source_rgba(*INK, 0.7 * (1 - u)); ctx.set_line_width(4); ctx.stroke()

def hearts_up(ctx, t, x, y, n=5, spread=140):
    for i in range(n):
        u = ((t * 1.3 + i / n) % 1.0)
        ctx.save(); ctx.translate(x - spread + i * (2 * spread / max(n - 1, 1)) + 20 * math.sin(t * 3 + i), y - 260 * u)
        ctx.scale(1.1 - 0.6 * u, 1.1 - 0.6 * u)
        ink_fill(ctx, lambda c: heart(c, 0, 0, 32), hexc('#e8455e'), lw=4); ctx.restore()

def bg_salon(ctx, t):
    sd = boil_seed(t)
    ctx.set_source_rgb(*hexc('#e9cba0')); ctx.rectangle(-1200, -800, 3500, 3600); ctx.fill()
    hatch_rect(ctx, -1200, -800, 3500, 3600, sd, False, 30, 0.09)
    ctx.set_source_rgb(*hexc('#9c5b3a')); ctx.rectangle(-1200, 1260, 3500, 1400); ctx.fill()
    ink_line(ctx, [(-1200, 1260), (2300, 1262)], sd, 6)
    window_night(ctx, 420, 180, 300, 360, t, 7)
    ctx.save(); ctx.rectangle(420, 180, 300, 360); ctx.clip(); snow(ctx, t, 18, 4); ctx.restore()
    string_lights(ctx, t, 110, 8, 7)
    xmas_tree(ctx, 1010, 900, 0.95, t, 2)
    xmas_tree(ctx, 30, 950, 0.8, t, 5)

BOT = lambda c, x, y, tt: bottle(c, x + 10, y - 45, 0.45, tt, glow=0.5)

def actor(ctx, who, x, y, t, sh, tag, sq=0.0, rot=0.0, sc=0.95, **kw):
    fy = y + 560 * sc
    ctx.save(); ctx.translate(x, fy); ctx.rotate(rot); ctx.scale(1 + sq, 1 - sq); ctx.translate(-x, -fy)
    if who == 'david': kw.setdefault('outfit', 'tee')
    draw_char(ctx, who, x, y, sc, t + (0.4 if tag == 'I' else 0), mouth=sh.mouth(tag, t), **kw)
    ctx.restore()

def draw(ctx, t, sh):
    i1, d1, i2, d2, i3, d3, i4, d4, d5 = (T[c] for c, _ in ORDER)
    unwrap = d1 + clip_len('x4_d1') + 0.15         # elle déchire le papier
    sniff = d3 + clip_len('x4_d3') + 0.1             # elle renifle
    melt = sniff + 0.9
    w_price = d2 + PRICE_AT                          # « vingt-cinq »
    ctx.save()
    # -------- vraies images (preuve) pendant d4
    if d4 - 0.05 <= t < d5 - 0.02:
        u = t - (d4 - 0.05); d = d5 - d4
        footage(ctx, 'fl2', u, 1.0, 1.1, d, 560, 700)
        badge(ctx, 'LATTAFA', SAFE_CX, 470, 82, hexc('#141414'), fg=GOLD, scale=pop(t, d4 + 1.6), rot=-0.04)
        badge(ctx, '100 ML', SAFE_CX - 190, 640, 78, GOLD, fg=INK, scale=pop(t, d4 + 0.4), rot=0.05)
        badge(ctx, 'MIXTE', SAFE_CX + 200, 640, 78, hexc('#9a6ad6'), fg=(1, 1, 1), scale=pop(t, d4 + MIXTE_AT), rot=-0.05)
        price_tag(ctx, 660, 920, 0.6, t, '25 €', sub='MOINS DE', rot=0.07)
        flash(ctx, u); ctx.restore(); banner(ctx, t); captions(ctx, t); return

    # -------- caméra
    if t < d1: cam = (1.65, IX, CY + 30, 0)
    elif t < unwrap: cam = (1.6, DX, CY + 30, 0)
    elif t < i2: cam = (1.08, 550, CY + 40, shake_at(t, [unwrap + 0.35], 10))
    elif t < d2: cam = (1.6 + 0.05 * (t - i2), IX, CY + 40, 0)
    elif t < i3: cam = (1.7 + 0.15 * ease((t - d2) / 1.5), DX, CY + 30, shake_at(t, [w_price], 12))
    elif t < d3: cam = (2.05, IX, CY + 20, 12 + shake_at(t, [i3], 30, 0.5))
    elif t < sniff: cam = (1.6, DX, CY + 40, 0)
    elif t < d4: cam = (1.5 + 0.12 * ease((t - sniff) / 1.5), IX, CY + 40, 0)
    else: cam = (1.08, 550, CY + 200, 0)
    z, wx, wy, shk = cam
    view(ctx, z, wx, wy, shake=shk, t=t)
    bg_salon(ctx, t)
    if i3 <= t < d3:
        S.rays(ctx, IX, CY, t, hexc('#e8263d'), 18, 0.55, 0.8)
        ctx.new_path(); ctx.arc(IX, CY, 2500, 0, 7); ctx.set_source_rgba(0.85, 0.1, 0.1, 0.22); ctx.fill()
    if sniff + 0.5 <= t < d4:
        g = cairo.RadialGradient(IX, CY, 50, IX, CY, 900)
        g.add_color_stop_rgba(0, 1, 0.6, 0.8, 0.6); g.add_color_stop_rgba(1, 1, 0.6, 0.8, 0)
        ctx.set_source(g); ctx.paint()

    # -------- INÈS
    ik = dict(smile=0.7, eyes='open', brows=0.3, look=(1, 0), arms=('hold', 'hold'), tilt=0.0, blush=0.4)
    isq = 0.0; holds_gift = t < unwrap + 0.3; holds_bottle = not holds_gift
    if t < d1:                                   # surexcitée
        ik.update(eyes='happy' if (t % 1.2) < 0.8 else 'open', smile=1.0, brows=0.8, look=(0.5, -0.3), blush=1.0)
        isq = 0.05 * math.sin(t * 14)
    elif t < unwrap:                             # attend
        ik.update(eyes='wide', smile=1.0, look=(1, 0))
    elif t < i2:                                 # ouvre : émerveillée
        u = t - unwrap
        ik.update(eyes='wide' if u > 0.35 else 'closed', smile=0.9, brows=1.0, look=(0, 0.4),
                  arms=('face', 'face') if u > 0.6 else ('hold', 'hold'), blush=1.0)
        isq = spring(t, unwrap + 0.35, -0.08)
    elif t < d2:                                 # admire puis soupçonne
        late = t > i2 + clip_len('x4_i2') * 0.55
        ik.update(eyes='half' if late else 'open', brows=-0.6 if late else 0.6, smile=0.0 if late else 0.9,
                  look=(1, 0) if late else (0.3, -0.5), arms=('down', 'hold_high'), prop=BOT, prop_hand='R', tilt=-0.08 if late else 0.05)
    elif t < i3:                                 # écoute la réponse
        ik.update(eyes='half', brows=-0.7, smile=-0.2, look=(1, 0), arms=('hip', 'hold_high'), prop=BOT, prop_hand='R')
    elif t < d3:                                 # FURIEUSE
        ik.update(eyes='open', brows=-1.0, smile=-0.8, look=(0.3, 0), arms=('hip', 'point_side'), tilt=0.05 * math.sin(t * 30), blush=0.0)
        isq = -0.08 * math.exp(-5 * max(0, t - i3)) + spring(t, i3, 0.04, 22)
    elif t < sniff:                              # boude
        ik.update(eyes='half', brows=-0.9, smile=-0.6, look=(1, 0), arms=('hip', 'hold'), prop=BOT, prop_hand='R', tilt=-0.1)
    elif t < melt:                               # renifle
        ik.update(eyes='closed', brows=0.2, smile=0.2, look=(0, 0), arms=('down', 'spray'), prop=BOT, prop_hand='R', tilt=0.12)
        isq = 0.03 * math.sin(t * 18)
    elif t < d4:                                 # fond d'amour
        ik.update(eyes='heart', brows=1.0, smile=1.0, arms=('chin', 'hold'), prop=BOT, prop_hand='R', blush=1.0,
                  tilt=0.15 + 0.05 * math.sin(t * 3))
        isq = 0.06 * min(1, (t - melt) / 0.4) + spring(t, melt, 0.05)
    else:                                        # final : collée à David
        ik.update(eyes='heart', smile=1.0, blush=1.0, look=(1, 0), arms=('down', 'hold'), tilt=0.12)
    ix = IX + (90 if t >= d5 else 0)
    if t >= unwrap - 0.05 or t < d1 or z < 1.3:
        actor(ctx, 'ines', ix, CY, t, sh, 'I', sq=isq, **ik)
        if holds_gift: gift(ctx, ix, CY + 400, 0.78, t, lid=ease((t - unwrap) / 0.3))
        if unwrap <= t < i2 + 0.5:
            u = t - unwrap
            if u > 0.25:
                kb = ease_out_back((u - 0.25) / 0.4)
                bottle(ctx, ix, CY + 330 - 210 * kb, 0.55 * kb, t, glow=1.0)
                for i in range(7): sparkle(ctx, ix + 200 * math.cos(i * 0.9), CY + 150 + 160 * math.sin(i * 1.7), 28, t, i)
        if i3 <= t < d3: steam(ctx, ix, CY - 40, t); vein(ctx, ix + 80, CY - 100, t, 1.1)
        if sniff <= t < melt: sniff_marks(ctx, ix + 60, CY + 30, t); S.smell_swirl(ctx, ix + 140, CY + 120, t, 0.6)
        if t >= melt: hearts_up(ctx, t, ix, CY - 140, 5)

    # -------- DAVID
    dk = dict(smile=0.8, eyes='open', brows=0.3, look=(-1, 0), arms=('down', 'down'), tilt=0.0)
    dsq = 0.0
    if t < d1: pass
    elif t < unwrap: dk.update(eyes='half', smile=1.0, brows=0.5, arms=('hip', 'point_side'), tilt=0.05)
    elif t < i2: dk.update(smile=1.0, eyes='happy', arms=('hip', 'hip'))
    elif t < i3:                                  # gêné puis fier
        late = t > w_price
        dk.update(eyes='open' if not late else 'half', look=(0.6, -0.6) if not late else (-1, 0), brows=1.0 if not late else 0.5,
                  smile=-0.2 if not late else 0.9, arms=('chin', 'down') if not late else ('hip', 'down'), tilt=0.06)
        dsq = spring(t, w_price, -0.05)
    elif t < d3: dk.update(eyes='tiny', brows=1.0, smile=-0.5, arms=('face', 'down'))
    elif t < sniff: dk.update(eyes='half', smile=0.6, brows=0.2, arms=(('down', 'cheer', 0.3), ('down', 'cheer', 0.3)), tilt=-0.04)
    elif t < d4: dk.update(eyes='half', smile=1.0, brows=0.6, arms=('hip', 'hip'))
    else:
        dk.update(look=(-0.4, 0.7), eyes='open' if ((t - d5) % 2.3) < 1.7 else 'wink', smile=1.0,
                  arms=(('down', 'point_down', (t - d5) / 0.3), 'hip'))
    if t >= d1 or z < 1.3:
        actor(ctx, 'david', DX, CY, t, sh, 'D', sq=dsq, **dk)
        if d2 <= t < w_price + 0.2: sweat(ctx, DX + 95, CY - 90, t, 1.2)
    ctx.restore()

    # -------- textes écran
    if d2 <= t < i3:
        k = pop(t, w_price, 0.25)
        if k > 0:
            ctx.save(); s_ = 1 + 2.3 * (1 - min(1, (t - w_price) / 0.12)); ctx.translate(SAFE_CX + 160, 470); ctx.scale(s_, s_); ctx.translate(-SAFE_CX - 160, -470)
            price_tag(ctx, SAFE_CX + 160, 470, 0.7, t, '25 €', sub='MOINS DE', rot=-0.07); ctx.restore()
    if i3 <= t < d3:
        k = pop(t, i3, 0.2)
        ctx.save(); ctx.translate(730, 460); ctx.scale(0.78 * k, 0.78 * k); ctx.rotate(0.08 + 0.03 * math.sin(t * 30))
        burst(ctx, 0, 0, 220, YEL, boil_seed(t), 14, 0.68); text(ctx, 'QUOI ?!', 0, 0, 140, fill=hexc('#e8263d'), sw=14); ctx.restore()
    if t >= d5:
        k = pop(t, d5 + CTA_AT - 0.2)
        badge(ctx, 'PANIER ORANGE', SAFE_CX - 30, 1150, 84, ORANGE, scale=k, rot=-0.03)
        cart_icon(ctx, SAFE_CX + 320, 1145, 0.9 * k)
        if k > 0:
            bob = 18 * math.sin(t * 7); arrow(ctx, 300, 1230 + bob * 0.5, 210, 1360 + bob * 0.5, t, w=54)
        price_tag(ctx, 210, 470, 0.45 * pop(t, d5 + 0.1), t, '25 €', sub='MOINS DE', rot=-0.08)
    banner(ctx, t)
    captions(ctx, t, 990 if t >= d5 else CAP_Y)
    cuts = [d1, unwrap, i2, d2, i3, d3, sniff, d4, d5]
    flash(ctx, min([t - c for c in cuts if c <= t] or [9]), 0.08)

PRICE_AT = 0.95; MIXTE_AT = 2.94; CTA_AT = 3.08

def build():
    i1, d1, i2, d2, i3, d3, i4, d4, d5 = (T[c] for c, _ in ORDER)
    unwrap = d1 + clip_len('x4_d1') + 0.15; sniff = d3 + clip_len('x4_d3') + 0.1
    voices = [(c, T[c], w) for c, w in ORDER]
    sfx = [('bells', 0.0, 0.5), ('pop', 0.1, 0.5), ('whoosh', d1 - 0.03, 0.4), ('scratch', unwrap, 0.4), ('pop', unwrap + 0.3, 0.8),
           ('sparkle', unwrap + 0.35, 0.9), ('heart', unwrap + 0.6, 0.5), ('whoosh', d2 - 0.03, 0.4), ('stamp', d2 + PRICE_AT, 0.9),
           ('scratch', i3 - 0.08, 1.0), ('boing', i3 + 0.05, 0.6), ('whoosh', d3 - 0.03, 0.4), ('sniff', sniff, 0.8),
           ('sniff', sniff + 0.4, 0.8), ('heart', sniff + 0.9, 0.8), ('sparkle', sniff + 0.95, 0.6), ('whoosh', d4 - 0.05, 0.6),
           ('pop', d4 + 0.4, 0.5), ('pop', d4 + 1.6, 0.5), ('pop', d4 + MIXTE_AT, 0.5), ('pop', d5 + CTA_AT - 0.2, 0.6),
           ('ding', d5 + CTA_AT - 0.1, 0.7)]
    return [Shot('cadeau', DUR, draw, voices, sfx, [])], (i3 - 0.1, d3)
