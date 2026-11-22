# -*- coding: utf-8 -*-
"""Dentifrice Dabur Miswak : 1) sketch « L'haleine »  2) présentation dynamique."""
import math, random, cairo
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash, shake_at, speed_lines
import sklib as L
from sklib import SAFE_CX, CAP_Y, view, actor
import dent_data as DD

W_ = {c: DD.words_for(c) for c in DD.CUTS}
W_['xd_p3'] = W_['xd_p3'] + [('FRAÎCHE.', 3.12)]
W_['xd_d4'] = [('MOINS', 0.13), ('DE', 0.37), ('5 EUROS.', 0.55)]
IX, DX, CY = 330, 770, 700
GREEN = hexc('#0f4a2a'); GOLDT = hexc('#e6b84a')

# ------------------------------------------------------------------ accessoires
def tube(ctx, x, y, s, t, rot=0.0, squeeze=0.0):
    """tube de dentifrice vert « MISWAK »"""
    sd = boil_seed(t) + 1200
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    body = [(-60, -150), (60, -150), (58 - 10 * squeeze, 120), (70, 150), (-70, 150), (-58 + 10 * squeeze, 120)]
    ink_fill(ctx, lambda c: blob(c, body, sd, 0.8), GREEN, lw=6, shade=lambda c: c.rectangle(-75, -160, 40, 330), seed=sd)
    ink_fill(ctx, lambda c: c.rectangle(-70, 140, 140, 18), (0.95, 0.95, 0.95), lw=4)
    ink_fill(ctx, lambda c: rrect(c, -42, -215, 84, 68, 12), (1, 1, 1), lw=6)
    ink_fill(ctx, lambda c: blob(c, [(-50, 70), (50, 70), (50, 130), (-50, 130)], sd + 1, 0.5), hexc('#ffd23f'), lw=3)
    ctx.save(); ctx.translate(0, -20); ctx.rotate(-math.pi / 2)
    text(ctx, 'MISWAK', 0, 0, 58, fill=GOLDT, stroke=INK, sw=4, shadow=False); ctx.restore()
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, -125, 24, 14, 8), sd + 2, 0.4), hexc('#c8102e'), lw=3)
    ctx.restore()

def toothbrush(ctx, x, y, s, rot, t, foam=False):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -10, -20, 230, 26, 12), hexc('#2f63b5'), lw=5)
    ink_fill(ctx, lambda c: rrect(c, -50, -50, 60, 34, 6), (1, 1, 1), lw=4)
    if foam:
        for i in range(4):
            ink_fill(ctx, lambda c, i=i: c.arc(-40 + i * 16, -58 - 6 * (i % 2), 14, 0, 7), (1, 1, 1), lw=3)
    ctx.restore()

def plant(ctx, x, y, s, t, droop=0.0, bloom=0.0):
    sd = boil_seed(t) + 1300
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: blob(c, [(-70, 0), (70, 0), (52, 120), (-52, 120)], sd, 1.0), hexc('#c0643a'), lw=6,
             shade=lambda c: c.rectangle(-80, 0, 50, 130), seed=sd)
    ink_fill(ctx, lambda c: c.rectangle(-80, -16, 160, 22), hexc('#d9774a'), lw=5)
    for i, a0 in enumerate((-0.5, -0.15, 0.2, 0.55)):
        a = a0 + droop * (1.6 if a0 > 0 else -1.6) + 0.04 * math.sin(t * 2 + i)
        L1 = 180 - 40 * droop
        mx, my = math.sin(a) * L1 * 0.5, -math.cos(a) * L1 * 0.5
        ex, ey = math.sin(a) * L1 + droop * 30 * (1 if a0 > 0 else -1), -math.cos(a) * L1 + droop * 140
        col = tuple(c0 * (1 - droop) + c1 * droop for c0, c1 in zip(hexc('#3e8a3a'), hexc('#8a7a3a')))
        ink_line(ctx, [(0, -10), (mx, my), (ex, ey)], sd + i, 7, color=INK)
        ink_fill(ctx, lambda c, ex=ex, ey=ey, a=a: blob(c, ellipse_pts(ex, ey, 26, 50, 9, a), sd + 5 + i, 1.0), col, lw=5)
        if bloom > 0:
            k = ease_out_back(min(1, bloom * 1.2 - i * 0.08))
            if k > 0:
                ink_fill(ctx, lambda c, ex=ex, ey=ey: star(c, ex, ey - 40, 34 * k, 16 * k, 6, t), hexc('#ff7fb0'), lw=4)
                ink_fill(ctx, lambda c, ex=ex, ey=ey: c.arc(ex, ey - 40, 10 * k, 0, 7), YEL, lw=3)
    ctx.restore()

def stink(ctx, x0, y0, x1, y1, t, t0, dur=2.2):
    """nuage d'haleine vert + mouches, de la bouche de David vers Inès"""
    if not (t0 <= t < t0 + dur): return
    u = t - t0
    for i in range(10):
        p = ((u * 0.9 + i * 0.1) % 1.0)
        x = x0 + (x1 - x0) * p; y = y0 + (y1 - y0) * p + 40 * math.sin(p * 8 + i)
        r = 30 + 50 * p
        ctx.new_path(); ctx.arc(x, y, r, 0, 7); ctx.set_source_rgba(0.45, 0.75, 0.2, 0.55 * (1 - p * 0.6)); ctx.fill_preserve()
        ctx.set_source_rgba(*INK, 0.5 * (1 - p)); ctx.set_line_width(4); ctx.stroke()
    for k in range(3):
        moth(ctx, x0 + (x1 - x0) * (0.3 + 0.25 * k) + 40 * math.sin(t * 9 + k), y0 - 60 + 50 * math.cos(t * 7 + k * 2), 0.8, t)
    for k in range(3):  # lignes d'odeur ondulées
        ctx.new_path()
        for j in range(20):
            p = j / 19; xx = x0 + (x1 - x0) * p; yy = y0 - 20 + k * 30 + 18 * math.sin(p * 12 + t * 8 + k)
            (ctx.move_to if j == 0 else ctx.line_to)(xx, yy)
        ctx.set_source_rgba(0.3, 0.55, 0.1, 0.9); ctx.set_line_width(7); ctx.stroke()

def fresh_breath(ctx, x0, y0, t, t0):
    if t < t0: return
    u = min(t - t0, 2.0)
    for k in range(3):
        ctx.new_path()
        for j in range(26):
            p = j / 25 * min(1, u * 1.5); xx = x0 - 500 * p; yy = y0 + k * 34 - 17 + 22 * math.sin(p * 9 + t * 6 + k)
            (ctx.move_to if j == 0 else ctx.line_to)(xx, yy)
        ctx.set_source_rgba(*INK, 0.8); ctx.set_line_width(12); ctx.stroke_preserve()
        ctx.set_source_rgba(0.55, 0.9, 1.0, 1); ctx.set_line_width(6); ctx.stroke()
    for i in range(7): sparkle(ctx, x0 - 60 - i * 60, y0 - 40 + 30 * math.sin(i * 1.7), 24, t, i, (0.75, 0.95, 1.0))

def bg_appart(ctx, t):
    sd = boil_seed(t)
    ctx.set_source_rgb(*hexc('#c9dde3')); ctx.rectangle(-1200, -800, 3500, 3600); ctx.fill()
    hatch_rect(ctx, -1200, -800, 3500, 3600, sd, False, 30, 0.08)
    ctx.set_source_rgb(*hexc('#b98a5e')); ctx.rectangle(-1200, 1260, 3500, 1400); ctx.fill()
    ink_line(ctx, [(-1200, 1260), (2300, 1262)], sd, 6)
    window_night(ctx, 400, 160, 320, 380, t, 3)
    ink_fill(ctx, lambda c: c.rectangle(-60, 1000, 260, 30), hexc('#7a4a2b'), lw=5)   # petit meuble de la plante
    ink_fill(ctx, lambda c: c.rectangle(-40, 1030, 30, 230), hexc('#7a4a2b'), lw=4)

# ================================================================== 1. SKETCH « L'HALEINE »
ORDER1 = [('xd_d1', 'D'), ('xd_i1', 'I'), ('xd_d2', 'D'), ('xd_i2', 'I'), ('xd_d3', 'D'), ('xd_i3', 'I'), ('xd_d4', 'D'), ('xd_d5', 'D')]
TL1 = L.Timeline(ORDER1, {'xd_i1': 0.1, 'xd_d3': 3.4, 'xd_d5': 0.15}, W_)
BAN1 = "ELLE A RECULÉ DE 3 MÈTRES…"

def draw1(ctx, t, sh):
    T = TL1.T
    d1, i1, d2, i2, d3, i3, d4, d5 = (T[c] for c, _ in ORDER1)
    brush0 = i2 + clip_len('xd_i2') + 0.05; brush_anim = brush0 + 1.7
    wprice = d4 + 0.55
    ctx.save()
    # -------- plan footage : il ouvre le dentifrice
    if brush0 <= t < brush_anim:
        u = t - brush0
        if u < 0.85: footage(ctx, 'd_sortie', u, 1.0, 1.1, 0.85, 560, 760)
        else: footage(ctx, 'd_bouchon', u - 0.85, 1.05, 1.18, 1.0, 560, 900)
        L.banner(ctx, t, BAN1); flash(ctx, u if u < 0.85 else u - 0.85)
        badge(ctx, 'DABUR MISWAK', SAFE_CX, 470, 80, GREEN, fg=GOLDT, scale=pop(t, brush0 + 0.1), rot=-0.04)
        ctx.restore(); return
    # -------- plan final : vraies images + arguments + panier
    if t >= d5 - 0.05:
        u = t - (d5 - 0.05)
        footage(ctx, 'd_hero', min(u, 1.3), 1.0, 1.1, 3.0, 540, 800)
        badge(ctx, 'À BASE DE PLANTES', SAFE_CX, 470, 70, hexc('#3e8a3a'), scale=pop(t, d5), rot=-0.04)
        badge(ctx, 'HALEINE FRAÎCHE', SAFE_CX, 600, 70, hexc('#4aa8d8'), scale=pop(t, d5 + 0.3), rot=0.04)
        price_tag(ctx, 690, 820, 0.62 * pop(t, d5 + 0.5), t, '5 €', sub='MOINS DE', rot=0.07)
        L.cta(ctx, t, d5 + 1.3)
        L.banner(ctx, t, BAN1); L.Timeline.captions(TL1, ctx, t, 990); flash(ctx, u)
        ctx.restore(); return

    # -------- caméra
    if t < i1: cam = (1.6 + 0.04 * t, DX, CY + 30, 0)
    elif t < d2: cam = (1.0, 560, CY + 60, shake_at(t, [i1 + 0.4], 10))
    elif t < i2: cam = (1.7, DX, CY + 30, 0)
    elif t < brush0: cam = (1.55, IX - 30, CY + 40, 0)
    elif t < d3: cam = (1.65, DX, CY + 30, 0)                      # brossage animé
    elif t < i3: cam = (1.6, DX, CY + 30, 0)
    elif t < d4: cam = (1.25, IX - 60, CY + 60, 0)
    else: cam = (1.7 + 0.12 * ease((t - d4) / 1.2), DX, CY + 30, shake_at(t, [wprice], 12))
    z, wx, wy, shk = cam
    view(ctx, z, wx, wy, shake=shk, t=t); bg_appart(ctx, t)

    # plante : se fane quand l'haleine passe, refleurit après le brossage
    droop = ease((t - (i1 + 0.3)) / 0.8) * (1 - ease((t - (i3 + 0.2)) / 0.6))
    bloom = ease((t - (i3 + 0.5)) / 0.8)
    plant(ctx, 70, 990, 0.9, t, droop, bloom)

    # -------- INÈS
    ik = dict(smile=0.4, eyes='open', brows=0.2, look=(1, 0), arms=('down', 'down'), blush=0.3)
    isq = 0.0; irot = 0.0; ix = IX
    if t < i1: ik.update(eyes='half', smile=0.3, look=(1, 0), arms=('down', 'chin'))
    elif t < d2:                                    # recule, dégoûtée
        u = t - i1
        ik.update(eyes='tiny' if u < 0.8 else 'closed', brows=-0.8, smile=-0.8, arms=('face', 'point_side') if u > 1.6 else ('face', 'down'),
                  look=(1, 0), tilt=-0.12, blush=0.0)
        ix = IX - 140 * ease(u / 0.5); irot = -0.10 * ease(u / 0.5); isq = spring(t, i1 + 0.05, 0.06)
    elif t < brush0:                                # lui tend le tube
        ik.update(eyes='half', brows=-0.4, smile=0.5, look=(1, 0), arms=('hip', ('down', 'give', (t - d2) / 0.4)), tilt=0.05)
        ix = IX - 80
    elif t < d4:                                    # charmée
        ik.update(eyes='heart' if t < i3 + 2.2 else 'open', brows=0.9, smile=1.0, blush=1.0, look=(1, 0), arms=('chin', 'down'),
                  tilt=0.12)
        isq = spring(t, i3, 0.06)
    else: ik.update(eyes='open', smile=0.8, look=(1, 0))
    if z < 1.3 or (i2 - 0.05 <= t < brush0) or (i3 <= t < d4) or t < i1:
        actor(ctx, 'ines', ix, CY, t, sh, 'I', sq=isq, rot=irot, **ik)
        if d2 <= t < brush0:
            kk = ease((t - d2) / 0.4); tube(ctx, ix + 190 + 50 * kk, CY + 230 - 40 * kk, 0.62, t, rot=-0.5 - 0.3 * kk)
        if i3 <= t < d4: L_hearts(ctx, t, ix, CY - 150)

    # -------- DAVID
    dk = dict(smile=0.8, eyes='open', brows=0.3, look=(-1, 0), arms=('down', 'down'))
    dsq = 0.0; drot = 0.0
    if t < i1:                                      # dragueur
        dk.update(eyes='half', smile=1.0, brows=0.4 + 0.5 * abs(math.sin(t * 6)), arms=('hip', 'chin'), tilt=-0.06)
        drot = -0.08 * ease(t / 0.8)
    elif t < d2:                                    # souffle sans le savoir
        dk.update(eyes='half', smile=0.9, brows=0.5, arms=('hip', 'chin')); drot = -0.08
    elif t < i2:                                    # vexé
        dk.update(eyes='open', brows=1.0, smile=-0.7, look=(-0.5, 0.6), arms=('down', 'down'), tilt=0.05)
    elif t < brush0: dk.update(eyes='open', brows=1.0, smile=-0.4)
    elif t < d3:                                    # se brosse les dents (animé)
        dk.update(eyes='closed', smile=0.2, brows=0.3, look=(0, 0), arms=('down', 'drink'), tilt=0.04 * math.sin(t * 20))
    elif t < i3:                                    # souffle frais, fier
        dk.update(eyes='wink' if t > d3 + 0.9 else 'half', smile=1.0, brows=0.6, arms=('hip', 'hip'), tilt=-0.05)
        dsq = spring(t, d3, 0.05)
    elif t < d4: dk.update(eyes='happy', smile=1.0)
    else:
        dk.update(eyes='half' if t < wprice else 'wink', smile=1.0, brows=0.6, look=(-0.3, 0.3), arms=('hip', 'hold_high'),
                  prop=lambda c, x, y, tt: tube(c, x + 10, y - 60, 0.42, tt, rot=0.2), prop_hand='R')
        dsq = spring(t, wprice, -0.05)
    if t < i1 or z < 1.3 or (d2 <= t < i2) or (brush_anim <= t < i3) or t >= d4:
        actor(ctx, 'david', DX, CY, t, sh, 'D', sq=dsq, rot=drot, **dk)
        if i1 <= t < d2: stink(ctx, DX - 60, CY + 70, IX - 40, CY + 60, t, i1 - 0.1)
        if t < i1: stink(ctx, DX - 60, CY + 70, DX - 260, CY + 30, t, 0.9, 5)
        if d2 <= t < i2: sweat(ctx, DX + 95, CY - 90, t, 1.2)
        if brush_anim <= t < d3:                    # brossage : brosse qui frotte + mousse
            bx = DX - 20 + 30 * math.sin(t * 28)
            toothbrush(ctx, bx, CY + 80, 0.9, 0.15, t, foam=True)
            for i in range(8):
                ink_fill(ctx, lambda c, i=i: c.arc(DX - 40 + 18 * math.cos(i * 1.3 + t * 5), CY + 95 + 14 * math.sin(i * 2.1 + t * 7),
                                                   12 + 4 * (i % 3), 0, 7), (1, 1, 1), lw=3)
        if d3 <= t < i3: fresh_breath(ctx, DX - 60, CY + 75, t, d3 + 0.15)
    ctx.restore()

    # -------- textes écran
    if brush_anim <= t < d3:
        text(ctx, 'FROTTE, FROTTE !', SAFE_CX, 470, 92, fill=(1, 1, 1), rot=-0.05 + 0.04 * math.sin(t * 10), scale=pop(t, brush_anim))
    if i1 <= t < d2:
        text(ctx, 'BEURK !', 250, 470, 140, fill=hexc('#7bc043'), scale=pop(t, i1 + 0.3), rot=-0.12)
    if d4 <= t:
        k = pop(t, wprice, 0.25)
        if k > 0:
            ctx.save(); s_ = 1 + 2.3 * (1 - min(1, (t - wprice) / 0.12)); ctx.translate(SAFE_CX + 160, 470); ctx.scale(s_, s_); ctx.translate(-SAFE_CX - 160, -470)
            price_tag(ctx, SAFE_CX + 160, 470, 0.7, t, '5 €', sub='MOINS DE', rot=-0.07); ctx.restore()
    L.banner(ctx, t, BAN1)
    TL1.captions(ctx, t, CAP_Y)
    cuts = [i1, d2, i2, brush_anim, d3, i3, d4]
    flash(ctx, min([t - c for c in cuts if c <= t] or [9]), 0.08)

def L_hearts(ctx, t, x, y):
    for i in range(5):
        u = ((t * 1.3 + i / 5) % 1.0)
        ctx.save(); ctx.translate(x - 140 + i * 70 + 20 * math.sin(t * 3 + i), y - 240 * u); ctx.scale(1.1 - 0.6 * u, 1.1 - 0.6 * u)
        ink_fill(ctx, lambda c: heart(c, 0, 0, 30), hexc('#e8455e'), lw=4); ctx.restore()

def build1():
    T = TL1.T; d1, i1, d2, i2, d3, i3, d4, d5 = (T[c] for c, _ in ORDER1)
    brush0 = i2 + clip_len('xd_i2') + 0.05
    sfx = [('ding', 0.05, 0.4), ('wink', 0.6, 0.5), ('boing', i1 + 0.05, 0.7), ('scratch', i1 + 0.3, 0.6), ('wah', i1 + 0.9, 0.5),
           ('whoosh', d2 - 0.03, 0.4), ('pop', d2 + 0.6, 0.5), ('whoosh', brush0 - 0.03, 0.6), ('pop', brush0 + 0.1, 0.5),
           ('pschht', brush0 + 0.9, 0.5), ('scratch', brush0 + 1.75, 0.35), ('scratch', brush0 + 2.3, 0.35), ('sparkle', d3 + 0.15, 0.9),
           ('wink', d3 + 0.9, 0.6), ('heart', i3 + 0.1, 0.8), ('sparkle', i3 + 0.5, 0.6), ('stamp', d4 + 0.55, 0.9),
           ('coins', d4 + 0.6, 0.4), ('whoosh', d5 - 0.05, 0.6), ('pop', d5, 0.5), ('pop', d5 + 0.3, 0.5), ('ding', d5 + 1.35, 0.7)]
    return [Shot('haleine', TL1.dur, draw1, TL1.voices(), sfx, [])], None

# ================================================================== 2. PRÉSENTATION DYNAMIQUE
ORDER2 = [('xd_p1', 'D'), ('xd_p2', 'D'), ('xd_p3', 'D'), ('xd_p4', 'D')]
TL2 = L.Timeline(ORDER2, {'xd_p2': 0.05, 'xd_p3': 0.05, 'xd_p4': 0.1}, W_)
BAN2 = "LE DENTIFRICE À MOINS DE 5 €"

def draw2(ctx, t, sh):
    T = TL2.T; p1, p2, p3, p4 = (T[c] for c, _ in ORDER2)
    ctx.save()
    if t < p2:                                           # présentateur animé + tube qui arrive
        view(ctx, 1.35 + 0.05 * t, DX - 120, CY + 60, t=t, shake=shake_at(t, [p1 + 1.42], 14))
        bg_appart(ctx, t)
        S.rays(ctx, DX - 120, CY, t, hexc('#ffffff'), 16, 0.25, 0.3)
        actor(ctx, 'david', DX - 120, CY, t, sh, 'D', sq=spring(t, p1 + 1.42, -0.05),
              smile=1.0, eyes='wide' if t > p1 + 1.42 else 'half', brows=0.8, look=(0, 0.2), arms=('hip', 'hold_high'),
              prop=lambda c, x, y, tt: tube(c, x + 10, y - 60, 0.45 * ease_out_back((tt - 0.3) / 0.5), tt, rot=0.25), prop_hand='R',
              tilt=-0.04 * math.sin(t * 4))
        ctx.restore()
        k = pop(t, p1 + 1.42, 0.25)
        if k > 0:
            ctx.save(); s_ = 1 + 2.3 * (1 - min(1, (t - p1 - 1.42) / 0.12)); ctx.translate(260, 520); ctx.scale(s_, s_); ctx.translate(-260, -520)
            price_tag(ctx, 260, 520, 0.6, t, '5 €', sub='MOINS DE', rot=-0.08); ctx.restore()
    elif t < p3:                                         # vraies images, coupes rythmées
        u = t - p2; segs = [('d_glisse', 0.0, 1.05), ('d_main', 1.05, 1.2), ('d_debout', 2.25, 1.2), ('d_face', 3.45, 1.2)]
        for name, a, d in segs:
            if a <= u < a + d or name == 'd_face' and u >= a:
                footage(ctx, name, u - a, 1.0, 1.12, d, 540, 860, offset=12 if name == 'd_glisse' else 0); flash(ctx, u - a); break
        badge(ctx, 'DABUR MISWAK', SAFE_CX, 470, 80, GREEN, fg=GOLDT, scale=pop(t, p2 + 0.42), rot=-0.04)
        badge(ctx, 'À BASE DE PLANTES', SAFE_CX, 610, 68, hexc('#3e8a3a'), scale=pop(t, p2 + 2.6), rot=0.04)
        badge(ctx, 'EXTRAIT DE MISWAK', SAFE_CX, 740, 68, hexc('#8a5a32'), scale=pop(t, p2 + 3.72), rot=-0.03)
        ctx.restore()
    elif t < p4:                                         # gros plan boîte + liste cochée
        u = t - p3
        footage(ctx, 'd_duo' if u < 1.8 else 'd_bouchon', u if u < 1.8 else u - 1.8, 1.05, 1.15, 1.8, 560, 900)
        flash(ctx, u if u < 1.8 else u - 1.8)
        ctx.new_path(); rrect(ctx, 90, 380, 760, 440, 36); ctx.set_source_rgba(0.05, 0.05, 0.05, 0.72); ctx.fill()
        text(ctx, 'ÉCRIT SUR LA BOÎTE :', SAFE_CX, 440, 56, font='Patrick Hand', fill=(1, 1, 1), stroke=None, shadow=False)
        for i, (lab, r) in enumerate((('DENTS SOLIDES', 1.1), ('GENCIVES SAINES', 1.94), ('HALEINE FRAÎCHE', 2.98))):
            k = pop(t, p3 + r, 0.3)
            if k > 0:
                L.check(ctx, 170, 540 + i * 110, 1.0, k)
                text(ctx, lab, 230, 540 + i * 110, 70, fill=(1, 1, 1), align='left', scale=k)
        ctx.restore()
    else:                                                # appel à l'action
        footage(ctx, 'd_hero', min(t - p4, 1.3), 1.0, 1.1, 3.0, 540, 800); flash(ctx, t - p4)
        price_tag(ctx, 690, 560, 0.62, t, '5 €', sub='MOINS DE', rot=0.07)
        L.cta(ctx, t, p4 + 1.0)
        ctx.restore()
        L.banner(ctx, t, BAN2, bg=GREEN, fg=GOLDT); TL2.captions(ctx, t, 990); return
    L.banner(ctx, t, BAN2, bg=GREEN, fg=GOLDT)
    TL2.captions(ctx, t, CAP_Y)

def build2():
    T = TL2.T; p1, p2, p3, p4 = (T[c] for c, _ in ORDER2)
    sfx = [('pop', 0.3, 0.6), ('sparkle', 0.4, 0.5), ('stamp', p1 + 1.42, 0.9), ('coins', p1 + 1.45, 0.4)]
    for a in (0.0, 1.05, 2.25, 3.45): sfx.append(('whoosh', p2 + a - 0.03, 0.5))
    sfx += [('pop', p2 + 0.42, 0.5), ('pop', p2 + 2.6, 0.5), ('pop', p2 + 3.72, 0.5), ('whoosh', p3 - 0.03, 0.5),
            ('ding', p3 + 1.1, 0.5), ('ding', p3 + 1.94, 0.5), ('ding', p3 + 2.98, 0.6), ('whoosh', p4 - 0.03, 0.5), ('ding', p4 + 1.05, 0.7)]
    return [Shot('promo', TL2.dur, draw2, TL2.voices(), sfx, [])], None
