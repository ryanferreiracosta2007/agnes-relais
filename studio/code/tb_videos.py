# -*- coding: utf-8 -*-
"""Dentifrice Miswak : « Team brosse mouillée ou team brosse sèche ? »
   Mini Hamza (team mouillée) et mini Inès (team sèche) se disputent sur les vraies images du tube,
   se réconcilient sur le dentifrice, puis demandent au spectateur de voter en commentaire."""
import math, random
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, leaf, miswak_stick, ease_out, kf
from dent_videos import toothbrush
import tb_data as TB

WORDS = {c: TB.words_for(c) for c in TB.CUTS}
for w in ('MISWAK', 'DABUR.', 'CINQ', 'EUROS !', 'SÈCHE ?', 'MOUILLÉE', 'TEAM', 'COMMENTAIRE.', "D'AL-ARAK.", 'PLANTES,'):
    if w not in S.HL: S.HL = S.HL + (w,)
MINT = hexc('#3ddc97'); GREEN_D = hexc('#0f5132'); REDX = hexc('#e8263d')
BLUE = hexc('#2f8de4'); BLUE_L = hexc('#9fd3ff'); ORG = hexc('#ff8a1f'); SAND = hexc('#ffd9a0')
BAN = "TEAM MOUILLÉE OU TEAM SÈCHE ?"
ORDER = [('xb_h1', 'H'), ('xb_i1', 'I'), ('xb_i2', 'I'), ('xb_h2', 'H'), ('xb_i3', 'I'), ('xb_i4', 'I'), ('xb_h3', 'H'), ('xb_i5', 'I')]
PAUSE = {'xb_i1': 0.0, 'xb_i2': 0.1, 'xb_h2': 0.05, 'xb_i3': 0.05, 'xb_i4': 0.05, 'xb_h3': 0.05, 'xb_i5': 0.05}
RCTA = 0.6
HK = dict(outfit='sweat')

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def drop(ctx, x, y, s, col=BLUE_L):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: (c.move_to(0, -34), c.curve_to(14, -10, 22, 4, 22, 14), c.curve_to(22, 30, -22, 30, -22, 14),
                             c.curve_to(-22, 4, -14, -10, 0, -34), c.close_path()), col, lw=4)
    ctx.new_path(); ctx.arc(-8, 10, 5, 0, 7); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()
    ctx.restore()

def _brush_at(c, x, y, s, rot, tt):
    """brosse tenue par le manche : la tête (poils) vers le haut ; renvoie la position des poils"""
    ox, oy = 110 * s, 0  # point du manche tenu dans la main
    ca, sa = math.cos(rot), math.sin(rot)
    bx0, by0 = x - (ox * ca - oy * sa), y - (ox * sa + oy * ca)
    toothbrush(c, bx0, by0, s, rot, tt)
    hx, hy = -20 * s, -50 * s
    return bx0 + hx * ca - hy * sa, by0 + hx * sa + hy * ca

def brush_wet(s=2.0, rot=1.45):
    """brosse mouillée : gouttes qui tombent des poils"""
    def f(c, x, y, tt):
        bx, by = _brush_at(c, x, y, s, rot, tt)
        for i in range(3):
            u = (tt * 1.6 + i / 3) % 1
            drop(c, bx - 30 + 26 * i, by + 20 + 160 * u, 1.0 * (1 - 0.4 * u))
    return f

def brush_dry(s=2.0, rot=1.45):
    """brosse sèche : petit nuage de poussière qui sort des poils"""
    def f(c, x, y, tt):
        bx, by = _brush_at(c, x, y, s, rot, tt)
        for i in range(3):
            u = (tt * 0.9 + i / 3) % 1
            c.new_path(); c.arc(bx - 30 + 40 * i + 50 * u, by - 40 - 100 * u, 18 + 30 * u, 0, 7)
            c.set_source_rgba(0.95, 0.85, 0.65, 0.7 * (1 - u)); c.fill()
    return f

def team_tag(ctx, txt, x, y, col, k, rot=0.0, wet=True):
    if k <= 0.01: return
    badge(ctx, txt, x, y, 62, col, fg=(1, 1, 1), scale=k, rot=rot)
    if wet: drop(ctx, x - text_w(ctx, txt, 62) / 2 * k - 34 * k, y, 0.8 * k)

def comment_bubble(ctx, x, y, s, t):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(0.06 * math.sin(t * 5))
    ink_fill(ctx, lambda c: (rrect(c, -110, -80, 220, 140, 40), c.move_to(-40, 58), c.line_to(-70, 110), c.line_to(10, 58)), (1, 1, 1), lw=7)
    for i in range(3):
        ctx.new_path(); ctx.arc(-50 + 50 * i, -10, 14, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.restore()

def vote_bar(ctx, t, t0, y=1010):
    """jauge de vote qui hésite entre les deux teams"""
    k = ease_out((t - t0) / 0.4)
    if k <= 0: return
    w = 760 * k; x0 = SAFE_CX - w / 2
    p = 0.5 + 0.16 * math.sin((t - t0) * 3.1) + 0.06 * math.sin((t - t0) * 7.3)
    ctx.new_path(); rrect(ctx, x0 + 6, y + 8, w, 70, 34); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.save(); ctx.new_path(); rrect(ctx, x0, y, w, 70, 34); ctx.clip()
    ctx.rectangle(x0, y, w * p, 70); ctx.set_source_rgb(*BLUE); ctx.fill()
    ctx.rectangle(x0 + w * p, y, w * (1 - p), 70); ctx.set_source_rgb(*ORG); ctx.fill()
    ctx.restore()
    ctx.new_path(); rrect(ctx, x0, y, w, 70, 34); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, f'{int(round(p * 100))} %', x0 + 90, y + 35, 52, fill=(1, 1, 1))
    text(ctx, f'{100 - int(round(p * 100))} %', x0 + w - 90, y + 35, 52, fill=(1, 1, 1))
    text(ctx, '?', x0 + w * p, y + 35, 80, fill=hexc('#ffd23f'), rot=0.1 * math.sin(t * 8))

def zoom_about(ctx, z, cx, cy):
    ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)

def draw_tb(ctx, t, sh):
    TL = sh.tl; T = TL.T; h1, i1, i2, h2, i3, i4, h3, i5 = (T[c] for c, _ in ORDER)
    cap_y = 1200; ban = True
    ctx.save()
    if t < i1:                                     # 1. Hamza découvre qu'Inès brosse à sec
        footage(ctx, 'd_hero', t, 1.0, 1.08, i1, 540, 700)
        zin = ease_out((t - (h1 + wt('xb_h1', 'BROSSE', 2.3) - 0.15)) / 0.3)
        ctx.save(); zoom_about(ctx, 1 + 0.32 * zin, 790, 900)
        mini(ctx, 'hamza', 'H', 210, 1060, t, sh, sc=0.56, eyes='wide', brows=1.0, smile=-0.8, look=(1, -0.2),
             arms=('point_side', 'hold_high'), tilt=0.05 * math.sin(t * 30), prop=brush_wet(), prop_hand='L', face=-1, **HK)
        shock_lines(ctx, 200, 700, t, 150)
        if t > 0.8: sweat(ctx, 260, 690, t, 1.0)
        mini(ctx, 'ines', 'I', 790, 1060, t, sh, sc=0.56, eyes='open', brows=0.2, smile=0.6, look=(-1, 0),
             arms=('hold_high', 'hip'), prop=brush_dry(), prop_hand='L', face=-1)
        ctx.restore()
        team_tag(ctx, 'MOUILLÉE', 230, 520, BLUE, pop(t, 0.1) * (1 - zin), rot=-0.05)
        team_tag(ctx, 'SÈCHE', 790, 520, ORG, pop(t, 0.25) * (1 - zin), rot=0.05, wet=False)
        if zin > 0: text(ctx, 'À SEC ?!', 420, 800, 130, fill=REDX, scale=pop(t, h1 + wt('xb_h1', 'SÈCHE', 2.8)), rot=-0.1)
        if t < 0.25: ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - t / 0.25)); ctx.paint()
    elif t < i2:                                   # 2. Inès, sûre d'elle, sur le bouchon du tube
        u = t - i1
        footage(ctx, 'd_bouchon', 0.8 + u * 0.6, 1.05, 1.15, i2 - i1, 540, 1100)
        mini(ctx, 'ines', 'I', 640, 1080, t, sh, sc=0.62, eyes='half', brows=-0.3, smile=0.8, look=(-1, 0.1),
             arms=('hip', 'hold_high'), prop=brush_dry(2.2), prop_hand='R', face=-1, tilt=-0.08)
        mini(ctx, 'hamza', 'H', 180, 1080, t, sh, sc=0.34, eyes='tiny', brows=-1.0, smile=-0.7, look=(1, 0), arms=('hip', 'hip'), **HK)
        vein(ctx, 230, 820, t, 0.7)
        team_tag(ctx, 'TEAM SÈCHE', 600, 470, ORG, pop(t, i1 + 0.05), rot=-0.04, wet=False)
        flash(ctx, u)
    elif t < h2:                                   # 3. réconciliation : d'accord sur le dentifrice
        u = t - i2
        footage(ctx, 'd_duo', u * 0.8, 1.0, 1.06, h2 - i2, 540, 900)
        agree = u > wt('xb_i2', "D'ACCORD", 0.9) - 0.1
        mini(ctx, 'hamza', 'H', 330, 1060, t, sh, sc=0.45, eyes='happy' if agree else 'half', brows=0.3, smile=0.9 if agree else -0.2,
             look=(1, 0), arms=('hip', 'give') if agree else ('hip', 'hip'), **HK)
        mini(ctx, 'ines', 'I', 660, 1060, t, sh, sc=0.45, eyes='happy' if agree else 'open', brows=0.3, smile=1.0, look=(-1, 0),
             arms=('hip', 'give') if agree else ('hip', 'hip'), face=-1)
        if agree:
            k = pop(t, i2 + wt('xb_i2', "D'ACCORD", 0.9))
            ink_fill(ctx, lambda c: heart(c, 495, 700 - 20 * math.sin(t * 6), 60 * k), REDX, lw=5)
            badge(ctx, 'ON EST D\'ACCORD', SAFE_CX, 480, 70, MINT, fg=INK, scale=k, rot=-0.03)
        flash(ctx, u)
    elif t < i3:                                   # 4. le produit : Miswak, aux plantes, Al-Arak
        u = t - h2
        tb = wt('xb_h2', 'AUX', 2.2)
        if u < tb:
            footage(ctx, 'd_main', u * 0.9, 1.0, 1.06, tb, 540, 900, offset=20)
            mini(ctx, 'hamza', 'H', 740, 1300, t, sh, sc=0.5, eyes='open', brows=0.6, smile=1.0, look=(-1, -0.6),
                 arms=('point_side', 'hip'), face=-1, **HK)
            badge(ctx, 'DABUR MISWAK', SAFE_CX, 470, 84, GREEN_D, fg=hexc('#ffd23f'), scale=pop(t, h2 + wt('xb_h2', 'MISWAK', 0.3)), rot=-0.04)
            cap_y = 1080
        else:
            v = u - tb
            footage(ctx, 'd_boite', v * 0.6, 1.0, 1.1, i3 - h2 - tb, 540, 900)
            for j in range(5): leaf(ctx, 120 + j * 190, (t * 120 + j * 260) % 1700 + 200, 1.1, t * 2 + j)
            mini(ctx, 'hamza', 'H', 780, 1080, t, sh, sc=0.42, jump=abs(math.sin(v * 6)) * 18, eyes='happy' if v > 1.2 else 'open',
                 brows=0.6, smile=1.0, look=(-1, -0.2), arms=('hold_high', 'point_side'), face=-1, **HK,
                 prop=lambda c, x, y, tt: miswak_stick(c, x, y - 60, 0.9, tt, rot=0.25), prop_hand='R')
            badge(ctx, 'AUX PLANTES', 330, 470, 74, MINT, fg=INK, scale=pop(t, h2 + tb), rot=-0.05)
            badge(ctx, "EXTRAIT PUR D'AL-ARAK", SAFE_CX, 600, 60, GREEN_D, fg=hexc('#ffd23f'), scale=pop(t, h2 + wt('xb_h2', "L'EXTRAIT", 3.0)), rot=0.03)
            flash(ctx, v)
    elif t < i4:                                   # 5. ce qui est écrit sur la boîte
        u = t - i3
        footage(ctx, 'd_face', 0.4 + u * 0.6, 1.0, 1.08, i4 - i3, 540, 960)
        ctx.set_source_rgba(0, 0, 0, 0.28); ctx.paint()
        mini(ctx, 'ines', 'I', 790, 1420, t, sh, sc=0.38, eyes='open', brows=0.5, smile=1.0, look=(-1, -1), arms=('point_side', 'hip'), face=-1)
        badge(ctx, 'SUR LA BOÎTE :', SAFE_CX, 440, 66, (1, 1, 1), fg=INK, scale=pop(t, i3 + 0.1), rot=-0.03)
        for j, (lab, pre) in enumerate((('DENTS FORTES', 'DENTS'), ('GENCIVES SAINES', 'GENCIVES'), ('HALEINE FRAÎCHE', 'HALEINE'))):
            k = pop(t, i3 + wt('xb_i3', pre, 1.5 + j))
            badge(ctx, lab, SAFE_CX - 40, 580 + j * 130, 70, MINT if j != 1 else hexc('#141414'), fg=INK if j != 1 else MINT, scale=k,
                  rot=(-0.04, 0.03, -0.02)[j])
            L.check(ctx, SAFE_CX + 330, 580 + j * 130, 0.8, k)
        flash(ctx, u)
    elif t < h3:                                   # 6. vote : écran partagé, question au spectateur
        u = t - i4
        footage(ctx, 'd_hero', 0.5 + u * 0.3, 1.1, 1.15, i4 - i3, 540, 700)
        ctx.save(); ctx.rectangle(0, 0, W / 2, H); ctx.set_source_rgba(*BLUE, 0.35); ctx.fill()
        ctx.rectangle(W / 2, 0, W / 2, H); ctx.set_source_rgba(*ORG, 0.35); ctx.fill(); ctx.restore()
        for j in range(7):
            drop(ctx, 60 + (j * 71) % 420, (t * 380 + j * 230) % 1500 + 300, 0.7)
        kL = pop(t, i4 + wt('xb_i4', 'MOUILLÉE', 1.0)); kR = pop(t, i4 + wt('xb_i4', 'SÈCHE', 1.9))
        mini(ctx, 'hamza', 'H', 250, 930, t, sh, sc=0.44, eyes='open', brows=0.6, smile=1.0, look=(0.5, 0.6),
             arms=('cheer', 'hold_high'), jump=40 * abs(math.sin(u * 5)) * (kL > 0.9), prop=brush_wet(1.8), prop_hand='L', face=-1, **HK)
        mini(ctx, 'ines', 'I', 730, 930, t, sh, sc=0.44, eyes='open', brows=0.6, smile=1.0, look=(-0.5, 0.6),
             arms=('hold_high', 'cheer'), jump=40 * abs(math.sin(u * 5 + 1)) * (kR > 0.9), prop=brush_dry(1.8), prop_hand='L', face=-1)
        team_tag(ctx, 'MOUILLÉE', 250, 520, BLUE, (1 + 0.25 * kL * max(0, 1 - (t - i4 - wt('xb_i4', 'MOUILLÉE', 1.0)) / 0.6)) * pop(t, i4 + 0.05), rot=-0.05)
        team_tag(ctx, 'SÈCHE', 740, 520, ORG, (1 + 0.25 * kR * max(0, 1 - (t - i4 - wt('xb_i4', 'SÈCHE', 1.9)) / 0.6)) * pop(t, i4 + 0.15), rot=0.05, wet=False)
        text(ctx, 'VS', SAFE_CX + 30, 600, 120, fill=hexc('#ffd23f'), scale=pop(t, i4 + 0.2), rot=0.08 * math.sin(t * 6))
        vote_bar(ctx, t, i4 + 0.3)
        kc = pop(t, i4 + wt('xb_i4', 'COMMENTAIRE', 3.2))
        if kc > 0.01:
            comment_bubble(ctx, 780, 740, kc * 0.9, t)
            badge(ctx, 'VOTE EN COMMENTAIRE', SAFE_CX, 330, 66, (1, 1, 1), fg=INK, scale=kc, rot=-0.02)
        cap_y = 1260; ban = False
        flash(ctx, u)
    else:                                          # 7-8. prix puis appel à l'action
        u = t - h3
        footage(ctx, 'd_sortie', 0.6 + min(u, 2.6) * 0.55, 1.0, 1.06, 3, 540, 1100)
        kp = pop(t, h3 + wt('xb_h3', 'CINQ', 0.8))
        if t < i5:
            mini(ctx, 'hamza', 'H', 760, 1000, t, sh, sc=0.42, jump=50 * abs(math.sin(u * 6)), eyes='happy', brows=0.6, smile=1.0,
                 look=(-1, 0), arms=('cheer', 'cheer'), face=-1, **HK)
            if kp > 0.01: price_tag(ctx, SAFE_CX - 60, 650, 1.1 * kp, t, 'MOINS DE 5 €', sub=None)
            cap_y = 1200
        else:
            v = t - i5
            mini(ctx, 'hamza', 'H', 830, 1010, t, sh, sc=0.36, eyes='happy', brows=0.5, smile=1.0, look=(-1, 0.5), arms=('hip', 'wave'), face=-1, **HK)
            mini(ctx, 'ines', 'I', 640, 1010, t, sh, sc=0.38, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
                 look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1)
            price_tag(ctx, SAFE_CX - 80, 560, 0.9, t, 'MOINS DE 5 €', sub=None)
            ctx.restore(); L.banner(ctx, t, BAN, bg=hexc('#ffd23f'), fg=INK); L.cta(ctx, t, i5 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=hexc('#ffd23f'), fg=INK)
    TL.captions(ctx, t, cap_y)

def build_tb():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.75); T = TL.T; h1, i1, i2, h2, i3, i4, h3, i5 = (T[c] for c, _ in ORDER)
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.1, 0.5), ('pop', 0.25, 0.5), ('scratch', h1 + wt('xb_h1', 'BROSSE', 2.3) - 0.15, 0.6),
           ('boing', h1 + wt('xb_h1', 'SÈCHE', 2.8), 0.6),
           ('whoosh', i1 - 0.03, 0.5), ('buzz', i1 + 0.1, 0.35),
           ('whoosh', i2 - 0.03, 0.5), ('heart', i2 + wt('xb_i2', "D'ACCORD", 0.9), 0.6),
           ('swipe', h2 - 0.03, 0.6), ('pop', h2 + wt('xb_h2', 'MISWAK', 0.3), 0.6),
           ('whoosh', h2 + wt('xb_h2', 'AUX', 2.2) - 0.03, 0.5), ('pop', h2 + wt('xb_h2', "L'EXTRAIT", 3.0), 0.5),
           ('whoosh', i3 - 0.03, 0.5), ('ding', i3 + wt('xb_i3', 'DENTS', 1.5), 0.5), ('ding', i3 + wt('xb_i3', 'GENCIVES', 2.5), 0.5),
           ('ding', i3 + wt('xb_i3', 'HALEINE', 3.5), 0.5),
           ('drumroll', i4 + 0.1, 0.35), ('pop', i4 + wt('xb_i4', 'MOUILLÉE', 1.0), 0.6), ('pop', i4 + wt('xb_i4', 'SÈCHE', 1.9), 0.6),
           ('sparkle', i4 + wt('xb_i4', 'COMMENTAIRE', 3.2), 0.6),
           ('swipe', h3 - 0.03, 0.7), ('coins', h3 + wt('xb_h3', 'CINQ', 0.8), 0.6),
           ('bells', i5 + 0.05, 0.4), ('ding', i5 + RCTA + 0.05, 0.7)]
    sh = Shot('team_brosse', TL.dur, draw_tb, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
