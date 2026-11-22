# -*- coding: utf-8 -*-
"""Sketch duo parfum (format court, style davidplav2) : le sceptique (rose) contre le malin (noir)."""
import math, random, cairo
from ink import *
from chars import draw_char
from props import *
import scenes as S
from scenes import Shot, caps_from, clip_len, footage, flash, cam, shake_at

S1B, S2B, S3B = 2.9, 1.15, 1.7
M3 = [0.9, 2.6, 3.65, 5.3, 6.2, 6.9]
M4 = [2.35, 4.0]
BANNER = "ÇA EXISTE PAS À CE PRIX ??"

def banner(ctx, t):
    k = pop(t, 0.0, 0.3) if t < 0.4 else 1.0
    ctx.save(); ctx.translate(540, 290); ctx.scale(k, k)
    ctx.select_font_face('Bangers'); ctx.set_font_size(84)
    w = ctx.text_extents(BANNER).x_advance + 60
    ctx.new_path(); rrect(ctx, -w / 2 + 6, -56 + 8, w, 112, 22); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -56, w, 112, 22); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, BANNER, 0, 2, 84, fill=INK, stroke=None, shadow=False)
    ctx.restore()

def bg_room(ctx, t):
    sd = boil_seed(t)
    ctx.set_source_rgb(*hexc('#d9d2c7')); ctx.paint()
    rnd = random.Random(4)
    for r in range(22):  # briques
        y = r * 70; off = 0 if r % 2 else -90
        for c in range(8):
            x = off + c * 180
            g = rnd.uniform(-0.03, 0.03)
            ctx.new_path(); rrect(ctx, x + 5, y + 5, 170, 60, 8)
            ctx.set_source_rgb(0.80 + g, 0.77 + g, 0.72 + g); ctx.fill()
    hatch_rect(ctx, 0, 0, W, H, sd, False, 26, 0.10)
    # horloge murale + étagère
    ink_fill(ctx, lambda c: c.arc(880, 560, 95, 0, 7), hexc('#2a2a2e'), lw=7)
    ink_fill(ctx, lambda c: c.arc(880, 560, 78, 0, 7), hexc('#f4efe6'), lw=4)
    ink_line(ctx, [(880, 560), (880, 505)], sd, 6); ink_line(ctx, [(880, 560), (918, 575)], sd + 1, 6)
    g = cairo.RadialGradient(540, 900, 200, 540, 900, 1300)
    g.add_color_stop_rgba(0, 1, 0.95, 0.85, 0.25); g.add_color_stop_rgba(1, 0.2, 0.15, 0.1, 0.35)
    ctx.set_source(g); ctx.paint()

def duo(ctx, t, sh, left, right, z=1.0, zc=(540, 900), shake=0.0):
    ctx.save(); cam(ctx, t, z, *zc, shake)
    bg_room(ctx, t)
    draw_char(ctx, 'david', 800, 1030, 1.0, t + 0.7, outfit='rose', mouth=sh.mouth('d1', t), **right)
    draw_char(ctx, 'david', 290, 1030, 1.0, t, outfit='tee', mouth=sh.mouth('d2', t), **left)
    ctx.restore()

def build():
    shots = []
    bot = lambda c, x, y, tt: bottle(c, x + 20, y - 50, 0.5, tt, glow=0.5)

    # 1. « sens-moi ça » + réaction
    a = 0.15; b = a + clip_len('m1') + 0.1; d = b + clip_len('s1') + 0.15
    def d1(ctx, t, sh):
        sniff = t >= b - 0.2
        duo(ctx, t, sh,
            left=dict(smile=0.9, eyes='open', look=(1, 0), brows=0.4, arms=('down', 'give'), prop=bot, prop_hand='R', tilt=0.05),
            right=dict(smile=0.2 if not sniff else 0.7, eyes='wide' if sniff else 'open', look=(-1, 0.3), brows=1.0 if sniff else 0.0,
                       arms=('down', 'down') if not sniff else ('chin', 'down'), tilt=-0.08 if sniff else 0.0),
            z=1.0 + 0.05 * t, shake=shake_at(t, [b], 14))
        S.smell_swirl(ctx, 560, 880, t, 0.8)
        if sniff: text(ctx, 'OH !', 830, 520, 150, fill=YEL, scale=pop(t, b), rot=0.12)
        banner(ctx, t)
    caps = caps_from('m1', a, [('FRÉROT, SENS-MOI ÇA.', 0.0)], 0.05) + caps_from('s1', b, [('OH ! ÇA SENT LE PARFUM CHER, ÇA !', 0.0), ('T\'AS BRAQUÉ UNE PARFUMERIE OU QUOI ?', S1B)], 0.1)
    shots.append(Shot('k1', d, d1, [('m1', a, 'd2'), ('s1', b, 'd1')], [('pop', 0.0, 0.6), ('sparkle', a + 0.5, 0.5), ('boing', b, 0.7)], caps, 1480))

    # 2. « moins de 25 € » + « arrête de mentir »
    a = 0.1; tp = a + 0.15; b = a + clip_len('m2') + 0.25; d = b + clip_len('s2') + 0.15
    def d2(ctx, t, sh):
        angry = t >= b
        duo(ctx, t, sh,
            left=dict(smile=1.0, eyes='wink' if t < b else 'open', look=(0, 0), brows=0.5, arms=('hip', 'hold_high'), prop=bot, prop_hand='R'),
            right=dict(smile=-0.6 if angry else 0.0, eyes='open' if angry else 'wide', look=(-1, 0), brows=-1.0 if angry else 1.0,
                       arms=('point_side', 'hip') if angry else ('down', 'down'), tilt=0.06 if angry else 0, body_rot=-0.04 if angry else 0),
            shake=shake_at(t, [tp], 24))
        k = pop(t, tp, 0.25)
        if k > 0:
            ctx.save(); ctx.translate(540, 640); s = 1 + 2.2 * (1 - min(1, (t - tp) / 0.12)); ctx.scale(s, s); ctx.translate(-540, -640)
            price_tag(ctx, 540, 640, 0.95, t, '25 €', sub='MOINS DE', rot=-0.07); ctx.restore()
        if angry: text(ctx, 'MENTEUR !', 760, 470, 110, fill=hexc('#e8453c'), scale=pop(t, b + 0.1), rot=0.1)
        banner(ctx, 1)
    caps = caps_from('m2', a, [('MOINS DE 25 €.', 0.0)], 0.2) + caps_from('s2', b, [('ARRÊTE DE MENTIR.', 0.0), ('ÇA EXISTE PAS, À CE PRIX-LÀ.', S2B)], 0.1)
    shots.append(Shot('k2', d, d2, [('m2', a, 'd2'), ('s2', b, 'd1')], [('stamp', tp, 0.9), ('coins', tp, 0.5), ('scratch', b, 0.6)], caps, 1480))

    # 3. la preuve : vraies images
    a = 0.1; L = clip_len('m3'); d = a + L + 0.15; dn = min(d, 5.6)
    def d3(ctx, t, sh):
        if t < dn: footage(ctx, 'nom', t, 1.0, 1.12, dn, 600, 700)
        else: footage(ctx, 'fl1', t - dn, 1.0, 1.08, d - dn)
        for i, (s, r, bg, fg) in enumerate([('LATTAFA', M3[1], hexc('#141414'), GOLD), ('100 ML', M3[2], GOLD, INK),
                                            ('PÊCHE', M3[3], hexc('#ff8a3d'), (1, 1, 1)), ('VANILLE', M3[4], hexc('#f4c430'), INK), ('MUSC', M3[5], hexc('#8a6fb0'), (1, 1, 1))]):
            x = 540 if i < 2 else 200 + (i - 2) * 340; y = 470 + i * 130 if i < 2 else 1250
            badge(ctx, s, x, y, 80 if i < 2 else 66, bg, fg=fg, scale=pop(t, a + r), rot=-0.04 if i % 2 else 0.04)
        price_tag(ctx, 800, 1560, 0.5, t, '25 €', sub='MOINS DE', rot=0.08)
        banner(ctx, 1); flash(ctx, t)
    caps = caps_from('m3', a, [('REGARDE.', 0.0), ('CONFIDENTIAL PRIVATE GOLD', M3[0])], 0.0)
    caps[-1] = (caps[-1][0], caps[-1][1], a + M3[2])
    shots.append(Shot('k3', d, d3, [('m3', a, 'd2')], [('whoosh', 0.0, 0.6)] + [('pop', a + r, 0.5) for r in M3[1:]], caps, 1420))

    # 4. « 100 ml ?! » + appel à l'action
    a = 0.1; b = a + clip_len('s3') + 0.1; d = b + clip_len('m4') + 1.2
    def d4(ctx, t, sh):
        cta = t >= b
        duo(ctx, t, sh,
            left=dict(smile=0.9, eyes='open', look=(0, 0.6) if cta else (1, 0), brows=0.3, arms=('point_down', 'down') if cta else ('hip', 'down')),
            right=dict(smile=-0.2, eyes='wide', look=(-1, 0), brows=1.0, arms=('face', 'face'), tilt=0.05,
                       body_rot=0.03 * math.sin(t * 28) if not cta else 0),
            shake=shake_at(t, [a], 18))
        if not cta:
            speed_lines(ctx, t, 800, 800, seed=3); text(ctx, '100 ML ?!', 760, 480, 130, fill=YEL, scale=pop(t, a + 0.5), rot=0.08)
        else:
            k = pop(t, b + 0.2)
            badge(ctx, 'BLACK FRIDAY', 540, 440, 76, INK, fg=YEL, scale=pop(t, b + 0.05), rot=-0.04)
            badge(ctx, 'PANIER ORANGE', 470, 590, 92, ORANGE, scale=k, rot=-0.03); cart_icon(ctx, 850, 585, 1.05 * k)
            if k > 0:
                bob = 16 * math.sin(t * 6); arrow(ctx, 330, 680 + bob * 0.5, 130, 820 + bob * 0.5, t, w=56)
        banner(ctx, 1); flash(ctx, t)
    caps = caps_from('s3', a, [('ATTENDS… 100 ML ?', 0.0), ('POURQUOI TU ME L\'AS PAS DIT AVANT ?!', S3B)], 0.05) + \
        caps_from('m4', b, [('BLACK FRIDAY, NOËL QUI ARRIVE…', 0.0), ('LE LIEN EST JUSTE EN DESSOUS,', M4[0]), ('SUR LE PANIER ORANGE.', M4[1])], 1.0)
    shots.append(Shot('k4', d, d4, [('s3', a, 'd1'), ('m4', b, 'd2')], [('boing', a, 0.7), ('bells', b, 0.4), ('ding', b + 0.2, 0.7)], caps, 1480))
    return shots
