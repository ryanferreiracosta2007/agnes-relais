# -*- coding: utf-8 -*-
"""Dentifrice Miswak : « Tu savais que le miswak, c'est d'abord un bâton ? »
   Faux tuto raté : mini Sarah veut montrer le vrai bâton de miswak, mais il est plus grand qu'elle et lui tombe dessus.
   Mini Léa lui montre que le miswak existe aussi en dentifrice (vraies images du tube), puis question au spectateur."""
import math, random
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, leaf, ease_out, stars_dizzy
import mb_data as MB

WORDS = {c: MB.words_for(c) for c in MB.CUTS}
for w in ('MISWAK,', 'BÂTON ?', 'CINQ', 'EUROS !', 'DENTIFRICE !', "D'AL-ARAK.", 'PLANTES,', 'COMMENTAIRE !', 'GRAND'):
    if w not in S.HL: S.HL = S.HL + (w,)
MINT = hexc('#3ddc97'); GREEN_D = hexc('#0f5132'); REDX = hexc('#e8263d'); WOOD = hexc('#c9a26b'); WOOD_D = hexc('#8a6238')
YELC = hexc('#ffd23f')
BAN = "LE MISWAK, C'EST UN BÂTON ?!"
ORDER = [('mbs_1', 'S'), ('mbs_2', 'S'), ('mbs_3', 'S'), ('mbl_1', 'L'), ('mbl_2', 'L'),
         ('mbs_4', 'S'), ('mbs_5', 'S'), ('mbl_3', 'L'), ('mbl_4', 'L')]
PAUSE = {'mbs_2': 0.0, 'mbs_3': 0.25, 'mbl_1': 0.1, 'mbl_2': 0.05, 'mbs_4': 0.05, 'mbs_5': 0.05, 'mbl_3': 0.05, 'mbl_4': 0.05}
RCTA = 0.5

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def big_stick(ctx, x, y, length, rot, t, fib=1.0):
    """bâton de miswak : (x, y) = point tenu, le bâton part vers l'angle rot ; la pointe effilochée est au bout"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    w = max(18, length * 0.075); back = length * 0.3
    ink_fill(ctx, lambda c: rrect(c, -back, -w / 2, length, w, w / 2.2), WOOD, lw=7)
    for k in range(4):  # nœuds et stries du bois
        xx = -back + length * (0.12 + 0.2 * k)
        ctx.new_path(); ctx.move_to(xx, -w / 2 + 5); ctx.curve_to(xx + 10, -w / 6, xx - 6, w / 6, xx + 4, w / 2 - 5)
        ctx.set_source_rgb(*WOOD_D); ctx.set_line_width(4); ctx.stroke()
    tip = length - back
    for k in range(7):  # fibres du bout
        a = (k - 3) * 0.16 + 0.05 * math.sin(t * 9 + k)
        ctx.new_path(); ctx.move_to(tip - 6, (k - 3) * w / 8)
        ctx.line_to(tip + w * 1.1 * fib * math.cos(a), (k - 3) * w / 8 + w * 1.1 * fib * math.sin(a))
        ctx.set_source_rgb(*hexc('#f2e2b8')); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()

def hand_pos(x, feet_y, sc, face=1, pose='hold_high', side='R'):
    from chars import ARM
    hx, hy = ARM[pose][2]; s = 1 if side == 'R' else -1
    return x + s * face * hx * 0.88 * sc, feet_y - 770 * sc + hy * sc

def zoom_about(ctx, z, cx, cy):
    ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)

def stamp_txt(ctx, txt, x, y, size, col, t, t0, rot=-0.12):
    k = pop(t, t0, 0.25)
    if k <= 0.01: return
    s = 1 + 1.4 * max(0, 1 - (t - t0) / 0.18)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * k, s * k)
    w = text_w(ctx, txt, size) + 50
    ctx.new_path(); rrect(ctx, -w / 2, -size * 0.62, w, size * 1.24, 16); ctx.set_source_rgba(1, 1, 1, 0.85); ctx.fill_preserve()
    ctx.set_source_rgb(*col); ctx.set_line_width(10); ctx.stroke()
    text(ctx, txt, 0, 4, size, fill=col, stroke=None, shadow=False)
    ctx.restore()

def comment_bubble(ctx, x, y, s, t):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(0.06 * math.sin(t * 5))
    ink_fill(ctx, lambda c: (rrect(c, -110, -80, 220, 140, 40), c.move_to(-40, 58), c.line_to(-70, 110), c.line_to(10, 58)), (1, 1, 1), lw=7)
    for i in range(3):
        ctx.new_path(); ctx.arc(-50 + 50 * i, -10, 14, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.restore()

def draw_mb(ctx, t, sh):
    TL = sh.tl; T = TL.T; s1, s2, s3, l1, l2, s4, s5, l3, l4 = (T[c] for c, _ in ORDER)
    cap_y = 1220; ban = True
    ctx.save()
    if t < s2:                                     # 1. Sarah « prof » avec un bâton plus grand qu'elle, à côté du vrai tube
        tb = s1 + wt('mbs_1', 'BÂTON', 2.1)
        zin = ease_out((t - tb + 0.1) / 0.25)
        footage(ctx, 'd_hero', t, 1.0, 1.06, s2, 540, 800)
        ctx.save(); zoom_about(ctx, 1 + 0.18 * zin, 720, 900)
        x, fy, sc = 740, 1120, 0.5
        mini(ctx, 'sarah', 'S', x, fy, t, sh, sc=sc, eyes='open', brows=0.7, smile=1.0, look=(-1, -0.3),
             arms=('point_side', 'hold_high'), face=-1, tilt=0.03 * math.sin(t * 4))
        hx, hy = hand_pos(x, fy, sc, face=-1, pose='hold_high', side='R')
        big_stick(ctx, hx, hy + 30, 800, -1.48 + 0.04 * math.sin(t * 3), t)
        ctx.restore()
        badge(ctx, 'TUTO', 250, 470, 80, (1, 1, 1), fg=INK, scale=pop(t, 0.05), rot=0.06)
        if zin > 0: stamp_txt(ctx, 'UN BÂTON ?!', 420, 640, 110, WOOD_D, t, tb, rot=-0.1)
        if t < 0.22: ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - t / 0.22)); ctx.paint()
    elif t < s3:                                   # 2. elle essaie de le soulever vers sa bouche : ça vacille
        u = t - s2
        footage(ctx, 'd_hero', 0.8 + u, 1.12, 1.2, s3 - s2, 600, 900)
        x, fy, sc = 640, 1130, 0.52
        wob = math.sin(u * 7) * 0.12
        mini(ctx, 'sarah', 'S', x + 20 * math.sin(u * 7), fy, t, sh, sc=sc, eyes='wide', brows=0.9, smile=0.2, look=(1, -0.8),
             arms=('hold_high', 'hold_high'), face=1, tilt=wob)
        sweat(ctx, x - 90, fy - 380, t, 0.9)
        hx, hy = hand_pos(x + 20 * math.sin(u * 7), fy, sc, face=1, pose='hold_high', side='R')
        big_stick(ctx, hx, hy + 30, 800, -1.48 + min(1.0, u * 0.9) + wob, t)
        badge(ctx, 'ÉTAPE 1', 300, 360, 70, YELC, fg=INK, scale=pop(t, s2 + 0.05), rot=-0.05)
        flash(ctx, u)
    elif t < l1:                                   # 3. le bâton lui tombe dessus : tuto raté
        u = t - s3
        footage(ctx, 'd_bouchon', 0.4 + u * 0.5, 1.0, 1.06, l1 - s3, 540, 900)
        fall = ease_out(u / 0.25)
        x, fy, sc = 540, 1000, 0.5
        sq = 0.55 * fall
        mini(ctx, 'sarah', 'S', x, fy, t, sh, sc=sc, sq=sq, eyes='closed' if u < 0.6 else 'half', brows=-0.6, smile=-0.4,
             look=(0, 0), arms=('down', 'down'))
        big_stick(ctx, x - 300, fy - 60, 900, -1.5 * (1 - fall) + 0.03 * math.sin(t * 20) * (u < 0.5), t)
        if fall >= 1:
            stars_dizzy(ctx, x, fy - 190, t, 90)
            dust(ctx, x, fy - 30, t, s3 + 0.25)
        stamp_txt(ctx, 'TUTO RATÉ', SAFE_CX, 560, 120, REDX, t, s3 + 0.25)
    elif t < l2:                                   # 4. Léa : le miswak existe aussi en dentifrice (vraie main, vrai tube)
        u = t - l1
        footage(ctx, 'd_main', u * 0.9, 1.0, 1.05, l2 - l1, 540, 900, offset=10)
        mini(ctx, 'lea', 'L', 800, 1300, t, sh, sc=0.46, eyes='half' if u < 1.0 else 'open', brows=0.4, smile=0.8, look=(-1, -0.6),
             arms=('hip', 'point_side'), face=-1)
        mini(ctx, 'sarah', 'S', 250, 1330, t, sh, sc=0.3, eyes='tiny', brows=-0.5, smile=-0.3, look=(1, -0.5), arms=('down', 'down'), sit=True)
        stars_dizzy(ctx, 250, 1180, t, 60)
        badge(ctx, 'EN DENTIFRICE !', SAFE_CX, 400, 82, MINT, fg=INK, scale=pop(t, l1 + wt('mbl_1', 'DENTIFRICE', 2.0)), rot=-0.04)
        cap_y = 1080
        flash(ctx, u)
    elif t < s4:                                   # 5. Dabur Miswak : aux plantes, extrait pur d'Al-Arak
        u = t - l2
        footage(ctx, 'd_boite', u * 0.6, 1.0, 1.1, s4 - l2, 540, 900)
        for j in range(5): leaf(ctx, 120 + j * 190, (t * 120 + j * 260) % 1700 + 200, 1.1, t * 2 + j)
        badge(ctx, 'DABUR MISWAK', SAFE_CX, 380, 84, GREEN_D, fg=YELC, scale=pop(t, l2 + wt('mbl_2', 'MISWAK', 0.2)), rot=-0.04)
        badge(ctx, 'AUX PLANTES', 330, 520, 74, MINT, fg=INK, scale=pop(t, l2 + wt('mbl_2', 'AUX', 1.5)), rot=-0.05)
        ka = pop(t, l2 + wt('mbl_2', "L'EXTRAIT", 2.5))
        badge(ctx, "EXTRAIT PUR D'AL-ARAK", SAFE_CX, 650, 60, GREEN_D, fg=YELC, scale=ka, rot=0.03)
        x, fy, sc = 760, 1110, 0.42
        mini(ctx, 'lea', 'L', x, fy, t, sh, sc=sc, jump=abs(math.sin(u * 5)) * 14, eyes='happy' if ka > 0.9 else 'open',
             brows=0.6, smile=1.0, look=(-1, -0.2), arms=('hip', 'hold_high'), face=-1)
        hx, hy = hand_pos(x, fy - abs(math.sin(u * 5)) * 14, sc, face=-1, pose='hold_high', side='R')
        if ka > 0.01:
            big_stick(ctx, hx, hy + 10, 170 * ka, -1.35, t)
            text(ctx, '= LE BÂTON', hx - 230, hy + 60, 58, fill=YELC, scale=ka, rot=-0.06)
        flash(ctx, u)
    elif t < s5:                                   # 6. ce qui est écrit sur la boîte
        u = t - s4
        footage(ctx, 'd_face', 0.4 + u * 0.6, 1.0, 1.08, s5 - s4, 540, 960)
        ctx.set_source_rgba(0, 0, 0, 0.28); ctx.paint()
        mini(ctx, 'sarah', 'S', 810, 1370, t, sh, sc=0.36, eyes='open', brows=0.5, smile=1.0, look=(-1, -1), arms=('point_side', 'hip'), face=-1)
        badge(ctx, 'SUR LA BOÎTE :', SAFE_CX, 420, 66, (1, 1, 1), fg=INK, scale=pop(t, s4 + 0.1), rot=-0.03)
        for j, (lab, pre) in enumerate((('DENTS FORTES', 'DENTS'), ('GENCIVES SAINES', 'GENCIVES'), ('HALEINE FRAÎCHE', 'HALEINE'))):
            k = pop(t, s4 + wt('mbs_4', pre, 1.5 + j))
            badge(ctx, lab, SAFE_CX - 40, 570 + j * 130, 70, MINT if j != 1 else hexc('#141414'), fg=INK if j != 1 else MINT, scale=k,
                  rot=(-0.04, 0.03, -0.02)[j])
            L.check(ctx, SAFE_CX + 330, 570 + j * 130, 0.8, k)
        flash(ctx, u)
    elif t < l3:                                   # 7. question au spectateur : le vrai bâton, tu as déjà essayé ?
        u = t - s5
        footage(ctx, 'd_duo', u * 0.8, 1.05, 1.12, l3 - s5, 540, 900)
        ctx.save(); ctx.rectangle(0, 0, W / 2, H); ctx.set_source_rgba(*WOOD_D, 0.42); ctx.fill()
        ctx.rectangle(W / 2, 0, W / 2, H); ctx.set_source_rgba(*MINT, 0.32); ctx.fill(); ctx.restore()
        kq = pop(t, s5 + 0.05)
        badge(ctx, 'TU AS DÉJÀ ESSAYÉ', SAFE_CX, 345, 70, (1, 1, 1), fg=INK, scale=kq, rot=-0.03)
        badge(ctx, 'LE VRAI BÂTON ?', SAFE_CX, 455, 82, YELC, fg=INK, scale=pop(t, s5 + wt('mbs_5', 'VRAI', 1.4)), rot=0.03)
        kL = pop(t, s5 + 0.4); kR = pop(t, s5 + 0.6)
        badge(ctx, 'OUI', 250, 600, 90, WOOD_D, fg=(1, 1, 1), scale=kL, rot=-0.06)
        badge(ctx, 'JAMAIS', 720, 600, 90, GREEN_D, fg=MINT, scale=kR, rot=0.06)
        text(ctx, 'OU', SAFE_CX, 600, 90, fill=YELC, scale=pop(t, s5 + 0.5), rot=0.08 * math.sin(t * 6))
        x, fy, sc = 300, 1110, 0.42
        mini(ctx, 'sarah', 'S', x, fy, t, sh, sc=sc, eyes='open', brows=0.6, smile=1.0, look=(0.4, 0.7),
             arms=('hip', 'cheer'), jump=30 * abs(math.sin(u * 5)), face=1)
        if kL > 0.01: big_stick(ctx, 250 - 110 * kL, 700, 240 * kL, 0.0, t)
        mini(ctx, 'lea', 'L', 740, 1110, t, sh, sc=0.42, eyes='open', brows=0.4, smile=1.0, look=(-0.4, 0.7),
             arms=('hip', 'cheer'), jump=30 * abs(math.sin(u * 5 + 1)), face=-1)
        kc = pop(t, s5 + wt('mbs_5', 'COMMENTAIRE', 2.4))
        if kc > 0.01:
            comment_bubble(ctx, 560, 820, kc * 0.9, t)
            badge(ctx, 'DIS-LE EN COMMENTAIRE', SAFE_CX, 232, 52, MINT, fg=INK, scale=kc, rot=0.02)
        cap_y = 1260; ban = False
        flash(ctx, u)
    else:                                          # 8-9. prix puis appel à l'action
        u = t - l3
        footage(ctx, 'd_sortie', 0.6 + min(u, 2.6) * 0.55, 1.0, 1.06, 3, 540, 1100)
        kp = pop(t, l3 + wt('mbl_3', 'CINQ', 0.8))
        if t < l4:
            mini(ctx, 'lea', 'L', 770, 1010, t, sh, sc=0.42, jump=50 * abs(math.sin(u * 6)), eyes='happy', brows=0.6, smile=1.0,
                 look=(-1, 0), arms=('cheer', 'cheer'), face=-1)
            if kp > 0.01: price_tag(ctx, SAFE_CX, 650, 0.95 * kp, t, 'MOINS DE 5 €', sub=None)
            flash(ctx, u)
        else:
            v = t - l4
            mini(ctx, 'sarah', 'S', 840, 1010, t, sh, sc=0.36, eyes='happy', brows=0.5, smile=1.0, look=(-1, 0.5), arms=('hip', 'wave'), face=-1)
            mini(ctx, 'lea', 'L', 650, 1010, t, sh, sc=0.38, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
                 look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1)
            price_tag(ctx, SAFE_CX, 560, 0.85, t, 'MOINS DE 5 €', sub=None)
            ctx.restore(); L.banner(ctx, t, BAN, bg=YELC, fg=INK); L.cta(ctx, t, l4 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=YELC, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_mb():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.8); T = TL.T; s1, s2, s3, l1, l2, s4, s5, l3, l4 = (T[c] for c, _ in ORDER)
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.05, 0.5), ('stamp', s1 + wt('mbs_1', 'BÂTON', 2.1), 0.6),
           ('swipe', s2 - 0.03, 0.5), ('pop', s2 + 0.05, 0.4), ('wah', s2 + 0.4, 0.3),
           ('boing', s3 + 0.22, 0.7), ('stamp', s3 + 0.25, 0.6),
           ('whoosh', l1 - 0.03, 0.5), ('pop', l1 + wt('mbl_1', 'DENTIFRICE', 2.0), 0.6),
           ('swipe', l2 - 0.03, 0.6), ('pop', l2 + wt('mbl_2', 'MISWAK', 0.2), 0.5), ('pop', l2 + wt('mbl_2', 'AUX', 1.5), 0.5),
           ('sparkle', l2 + wt('mbl_2', "L'EXTRAIT", 2.5), 0.5),
           ('whoosh', s4 - 0.03, 0.5), ('ding', s4 + wt('mbs_4', 'DENTS', 1.5), 0.5), ('ding', s4 + wt('mbs_4', 'GENCIVES', 2.5), 0.5),
           ('ding', s4 + wt('mbs_4', 'HALEINE', 3.5), 0.5),
           ('drumroll', s5 + 0.1, 0.3), ('pop', s5 + 0.4, 0.5), ('pop', s5 + 0.6, 0.5),
           ('sparkle', s5 + wt('mbs_5', 'COMMENTAIRE', 2.4), 0.6),
           ('swipe', l3 - 0.03, 0.7), ('coins', l3 + wt('mbl_3', 'CINQ', 0.8), 0.6),
           ('bells', l4 + 0.05, 0.4), ('ding', l4 + RCTA + 0.05, 0.7)]
    sh = Shot('miswak_baton', TL.dur, draw_mb, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
