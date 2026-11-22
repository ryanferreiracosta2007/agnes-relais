# -*- coding: utf-8 -*-
"""Format « mini personnage dans la vraie vie » : un petit David dessiné vit sur la vraie table, à côté du vrai rasoir."""
import math, random, cairo
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash, shake_at
import sklib as L
from sklib import SAFE_CX, CAP_Y
from chars import draw_char
from rasoir_videos import fiche_band, coupon_note, bf_badge, LIME, WORDS, phone_ar
RCTA = 3.0
ORDER = [('xm_1', 'P'), ('xm_2', 'P'), ('xm_3', 'P'), ('xm_4', 'P'), ('xm_5', 'P'), ('xm_6', 'P')]
BAN = "LE PLUS PETIT VENDEUR DE TIKTOK"

def wt(clip, prefix, default):
    return next((rr for ww, rr in WORDS.get(clip, []) if ww.startswith(prefix)), default)

def tl():
    return L.Timeline(ORDER, {'xm_2': 0.1, 'xm_3': 0.1, 'xm_4': 0.45, 'xm_5': 0.1, 'xm_6': 0.1}, WORDS, start=0.05)

def mini(ctx, x, feet_y, t, sh, sc=0.5, walk=0.0, jump=0.0, face=1, **kw):
    """petit personnage en pied (jambes + chaussures) posé sur une surface réelle"""
    y = feet_y - 770 * sc - jump
    # ombre portée sur la table
    k = max(0.35, 1 - jump / 300)
    ctx.save(); ctx.translate(x, feet_y + 4); ctx.scale(70 * sc * 2.2 * k, 16 * sc * 2.2 * k)
    ctx.new_path(); ctx.arc(0, 0, 1, 0, 7); ctx.set_source_rgba(0, 0, 0, 0.45); ctx.fill(); ctx.restore()
    ctx.save(); ctx.translate(x, y); ctx.scale(sc * face, sc)
    sw = math.sin(walk) * 0.45
    for side, a in ((-1, sw), (1, -sw)):
        ctx.save(); ctx.translate(side * 55, 540); ctx.rotate(a)
        ink_fill(ctx, lambda c: rrect(c, -34, 0, 68, 200, 20), hexc('#2a2d35'), lw=7)
        ink_fill(ctx, lambda c: blob(c, [(-44, 190), (60, 190), (78, 236), (-44, 236)], 3, 0.6), (1, 1, 1), lw=7)
        ctx.restore()
    ctx.restore()
    ctx.save(); ctx.translate(x, 0); ctx.scale(face, 1); ctx.translate(-x, 0)
    kw.setdefault('outfit', 'tee')
    draw_char(ctx, 'david', x, y, sc, t, mouth=sh.mouth('P', t), **kw)
    ctx.restore()

def bubble(ctx, x, y, txt, k, size=54):
    if k <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    w = text_w(ctx, txt, size) + 50
    ctx.new_path(); rrect(ctx, -w / 2, -48, w, 96, 30); ctx.move_to(-20, 46); ctx.line_to(10, 90); ctx.line_to(20, 46)
    ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, txt, 0, 2, size, fill=INK, stroke=None, shadow=False); ctx.restore()

def draw(ctx, t, sh):
    TL = sh.tl; T = TL.T; l1, l2, l3, l4, l5, l6 = (T[c] for c, _ in ORDER)
    ctx.save()
    if t < l2:                                   # 1. il interpelle le spectateur
        footage(ctx, 'r_kit', t, 1.0, 1.06, l2, 600, 1100)
        fall = 900 * (1 - t / 0.35) ** 2 if t < 0.35 else 0
        hop = fall + (abs(math.sin((t - 0.35) * 7)) * 40 if 0.6 < t < 1.6 else 0)
        mini(ctx, 790, 1290, t, sh, jump=hop, eyes='wide' if t < 1.6 else 'half', brows=0.9, smile=1.0, look=(0, 0.2),
             arms=('wave', 'hip') if t < 1.6 else ('point_side', 'hip'))
        dust(ctx, 790, 1290, t, 0.33)
    elif t < l3:                                 # 2. il présente le rasoir (marche jusqu'à lui, toque dessus)
        u = t - l2
        footage(ctx, 'r_kit2', u, 1.0, 1.04, l3 - l2, 600, 1100)
        x = 800 - 90 * ease(u / 1.2)
        knock = u > 1.3 and (u % 0.5) < 0.2
        mini(ctx, x, 1290, t, sh, walk=u * 10 if u < 1.2 else 0, face=-1 if u < 1.2 else 1, eyes='open', smile=1.0, brows=0.5,
             look=(-1, 0), arms=('point_side', 'hip'))
        if knock: text(ctx, 'TOC', x - 150, 1000, 70, fill=(1, 1, 1), rot=-0.2)
        for i, (lab, pre) in enumerate((('TAILLE', 'TAILLE'), ('CONTOURS', 'CONTOURS'), ('RASE', 'RASE'))):
            badge(ctx, lab, 230 + i * 240, 470 + (i % 2) * 70, 66, LIME if i != 1 else hexc('#141414'), fg=INK if i != 1 else LIME,
                  scale=pop(t, l2 + wt('xm_2', pre, 2.0 + 0.5 * i)), rot=-0.05 + 0.05 * i)
        badge(ctx, 'PHILIPS ONEBLADE 360', SAFE_CX, 640, 60, hexc('#0b5ed7'), scale=pop(t, l2 + 0.6), rot=0.03)
    elif t < l4:                                 # 3. la main arrive : il saute de peur
        u = t - l3
        footage(ctx, 'r_prise', u * 1.15, 1.0, 1.05, l4 - l3, 600, 1100)
        jump = 260 * math.sin(min(1, u / 0.7) * math.pi) if u < 0.7 else 0
        x = 780 + 40 * ease(u / 0.7)
        mini(ctx, x, 1290, t, sh, jump=jump, eyes='tiny', brows=1.0, smile=-0.8, look=(-1, 0), arms=('face', 'face'),
             tilt=0.06 * math.sin(t * 40))
        shock_lines(ctx, x, 1290 - 770 * 0.5 - jump, t, 120)
        if u > 0.5: sweat(ctx, x + 50, 1290 - 800 * 0.5, t, 1.0)
        text(ctx, 'AAAAH !', 560, 900, 130, fill=hexc('#e8263d'), scale=pop(t, l3 + 0.05), rot=0.1 + 0.04 * math.sin(t * 30))
        flash(ctx, u)
    elif t < l5:                                 # 4. sur l'épaule pendant le rasage + son téléphone
        u = t - l4
        footage(ctx, 'r_rase', u, 1.0, 1.08, l5 - l4, 540, 900)
        mini(ctx, 750, 1330, t, sh, eyes='happy' if u > 1.2 else 'open', smile=1.0, brows=0.6, look=(-1, -0.3),
             arms=('cheer', 'hold_high'), prop=lambda c, x, y, tt: phone(c, x, y - 40, 0.9, tt, rot=0.1), prop_hand='R')
        k = pop(t, l4 + wt('xm_4', 'APPLICATION', 1.0))
        badge(ctx, 'APPLI GRATUITE', SAFE_CX - 60, 470, 70, LIME, fg=INK, scale=k, rot=-0.04)
        badge(ctx, 'ESSAI DE BARBES', SAFE_CX - 60, 600, 62, hexc('#141414'), fg=LIME, scale=pop(t, l4 + wt('xm_4', 'STYLES', 2.0)), rot=0.03)
        flash(ctx, u)
    elif t < l6:                                 # 5. debout sur la capture de la fiche, il montre le prix
        u = t - l5
        footage(ctx, 'r_kit', 2.9, 1.06, 1.06, 1, 600, 1100); ctx.set_source_rgba(0, 0, 0, 0.55); ctx.paint()
        r29 = wt('xm_5', '29', 3.2)
        fiche_band(ctx, t, l5 + 0.05, cy=900, circle_t=l5 + r29)
        top = 900 - 520 * 0.86 / 2
        x = 300 + 400 * ease((u - r29 + 0.6) / 0.6)
        mini(ctx, x, top + 6, t, sh, sc=0.42, walk=u * 10 if r29 - 0.6 < u < r29 else 0, eyes='open', smile=1.0, brows=0.5, look=(0, 1),
             arms=('down', 'point_down'))
        if t >= l5 + r29: coupon_note(ctx, 1165)
        flash(ctx, u)
    else:                                        # 6. appel à l'action
        u = t - l6
        footage(ctx, 'r_kit', min(u, 2.9), 1.0, 1.06, 3.0, 600, 1100)
        mini(ctx, 790, 1290, t, sh, eyes='open' if (u % 2.2) < 1.6 else 'wink', smile=1.0, brows=0.5, look=(-0.6, 0.8),
             arms=(('down', 'point_down', u / 0.3), 'hip'), face=-1)
        bf_badge(ctx, t, l6 + 0.05, 600); L.cta(ctx, t, l6 + RCTA)
        ctx.restore(); L.banner(ctx, t, BAN, bg=LIME, fg=INK); TL.captions(ctx, t, 990); return
    ctx.restore()
    L.banner(ctx, t, BAN, bg=LIME, fg=INK)
    TL.captions(ctx, t, 1180 if not (l5 <= t < l6) else 1310)

def build():
    TL = tl(); T = TL.T; l1, l2, l3, l4, l5, l6 = (T[c] for c, _ in ORDER)
    sfx = [('whoosh', 0.0, 0.6), ('stamp', 0.33, 0.8), ('boing', 0.36, 0.6), ('boing', 0.5, 0.4), ('boing', 0.95, 0.4), ('whoosh', l2 - 0.03, 0.5),
           ('pop', l2 + 0.6, 0.5), ('scratch', l3 - 0.05, 0.6), ('boing', l3 + 0.1, 0.8), ('whoosh', l3 + 0.2, 0.6),
           ('whoosh', l4 - 0.03, 0.5), ('buzz', l4 + 0.1, 0.6), ('ding', l4 + wt('xm_4', 'APPLICATION', 1.0), 0.5),
           ('whoosh', l5 - 0.03, 0.5), ('pop', l5 + 0.1, 0.6), ('ding', l5 + wt('xm_5', '29', 3.2), 0.7),
           ('whoosh', l6 - 0.03, 0.5), ('bells', l6 + 0.05, 0.4), ('ding', l6 + RCTA + 0.05, 0.7)]
    for i in range(6): sfx.append(('pop', l2 + 1.3 + i * 0.5, 0.3))
    sh = Shot('mini', TL.dur, draw, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
