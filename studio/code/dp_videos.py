# -*- coding: utf-8 -*-
"""Parfum Lattafa : « Le détecteur de bobards » (Black Friday, 27/11/2026).
   Mini Inès (Leda) sort son détecteur : « Tu crois encore aux promos du Black Friday ? » sur le vrai flacon.
   Mini David (Puck), vendeur de foire dessiné : « -90 % sur tout ! » BIIP rouge ; « sur presque tout ? » BIIP ;
   « c'était le prix normal » : le détecteur fume, tampon BOBARD. Retour au vrai flacon : détecteur VERT,
   « Sauf lui » ; pas de pourcentage magique : moins de 25 € ; question « tu y crois encore ? » ; panier orange."""
import math
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, ease_out, kf, FL2, EDP, GOLDC, REDX
from tb_videos import comment_bubble, zoom_about
from sl_videos import stamp, dark
import dp_data as DP

WORDS = {c: DP.words_for(c) for c in DP.CUTS}
for w in ('PROMOS', 'BLACK', 'FRIDAY ?', 'FRIDAY !', '90 %', 'PRESQUE', 'NORMAL.', 'SAUF', 'LUI.', 'CONFIDENTIAL', 'PRIVATE',
          'GOLD', 'LATTAFA.', 'MAGIQUE :', 'VINGT-CINQ', 'PROMOS ?', 'COMMENTAIRE.'):
    if w not in S.HL: S.HL = S.HL + (w,)
GREENL = hexc('#2ee66b'); AMBER = hexc('#ffb020'); NIGHT = hexc('#0d0d12'); BFY = hexc('#ffe600')
BAN = "BLACK FRIDAY : LE DÉTECTEUR DE BOBARDS"
ORDER = [('xp_i1', 'I'), ('xp_d1', 'D'), ('xp_d2', 'D'), ('xp_d3', 'D'), ('xp_i2', 'I'), ('xp_i3', 'I'), ('xp_i5', 'I'), ('xp_i4', 'I')]
PAUSE = {'xp_d1': 0.04, 'xp_d2': 0.05, 'xp_d3': 0.04, 'xp_i2': 0.38, 'xp_i3': 0.06, 'xp_i5': 0.06, 'xp_i4': 0.08}
RCTA = 0.5
IK = dict(); DK = dict(outfit='chic')

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

# ---------------------------------------------------------------- accessoires
def detector(c, x, y, s, t, state='scan', rot=0.0, smoke=0.0):
    """détecteur de bobards tenu à la main : boîtier, écran, cadran, antenne + ampoule"""
    col = {'scan': AMBER, 'red': REDX, 'green': GREENL}[state]
    blink = 0.5 + 0.5 * math.sin(t * (22 if state == 'red' else 9))
    c.save(); c.translate(x, y); c.rotate(rot + (0.08 * math.sin(t * 40) if state == 'red' else 0)); c.scale(s, s)
    ink_line(c, [(40, -120), (70, -250)], boil_seed(t), 9)
    c.new_path(); c.arc(72, -262, 30 + 14 * blink, 0, 7); c.set_source_rgba(*col, 0.35); c.fill()
    ink_fill(c, lambda k: k.arc(72, -262, 26, 0, 7), col, lw=6)
    ink_fill(c, lambda k: rrect(k, -40, 60, 80, 150, 22), hexc('#3a3a44'), lw=7)
    ink_fill(c, lambda k: rrect(k, -110, -130, 220, 210, 34), hexc('#5b5f6e'), lw=8)
    ink_fill(c, lambda k: rrect(k, -82, -104, 164, 92, 16), hexc('#101418'), lw=5)
    lab = {'scan': '. . .', 'red': 'BOBARD', 'green': 'VRAI'}[state]
    text(c, lab, 0, -52, 44, fill=col, stroke=None, shadow=False)
    # cadran
    c.new_path(); c.arc(0, 40, 34, math.pi, 2 * math.pi); c.set_source_rgb(1, 1, 1); c.fill()
    a = {'scan': math.pi * (1.5 + 0.35 * math.sin(t * 5)), 'red': math.pi * (1.92 + 0.05 * math.sin(t * 50)), 'green': math.pi * 1.08}[state]
    c.move_to(0, 40); c.line_to(30 * math.cos(a), 40 + 30 * math.sin(a)); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    c.restore()
    if smoke > 0:
        for i in range(5):
            u = (t * 0.9 + i * 0.21) % 1.0
            c.new_path(); c.arc(x + 60 * s + 40 * math.sin(u * 6 + i), y - 300 * s - 260 * u, (30 + 60 * u) * s, 0, 7)
            c.set_source_rgba(0.35, 0.35, 0.38, 0.6 * (1 - u) * smoke); c.fill()

def beam(c, x0, y0, x1, y1, t, col):
    """faisceau de scan du détecteur vers la cible"""
    c.save(); a = 0.18 + 0.1 * math.sin(t * 14)
    c.new_path(); c.move_to(x0, y0); c.line_to(x1 - 140, y1 - 60); c.line_to(x1 + 140, y1 + 60); c.close_path()
    c.set_source_rgba(*col, a); c.fill()
    ly = y1 + 120 * math.sin(t * 6)
    c.move_to(x1 - 180, ly); c.line_to(x1 + 180, ly); c.set_source_rgba(*col, 0.8); c.set_line_width(8); c.stroke()
    c.restore()

def hand_xy(x, feet_y, sc, face, pose='point_side'):
    hx, hy = {'point_side': (420, 200), 'hold_high': (220, 80), 'grab': (430, 250)}[pose]
    return x + face * hx * sc, feet_y - 770 * sc + hy * sc

def sign(c, x, y, s, t, top, big, small=None, rot=0.0, flip=0.0, col=BFY):
    """grande pancarte de vendeur (texte rouge sur jaune)"""
    c.save(); c.translate(x, y); c.rotate(rot + 0.04 * math.sin(t * 7)); c.scale(s * (1 - 2 * flip) if flip < 0.5 else s * (2 * flip - 1), s)
    ink_fill(c, lambda k: rrect(k, -12, 150, 24, 230, 8), hexc('#7a4f27'), lw=6)
    ink_fill(c, lambda k: rrect(k, -250, -170, 500, 340, 22), col, lw=9)
    text(c, top, 0, -100, 64, fill=INK, stroke=None, shadow=False)
    text(c, big, 0, 40, 170, fill=REDX, stroke=INK, shadow=False)
    if small: text(c, small, 120, 135, 40, font='Patrick Hand', fill=INK, stroke=None, shadow=False)
    c.restore()

def bg_foire(c, t):
    """décor dessiné du vendeur : boutique + guirlande d'étiquettes « % »"""
    S.bg_boutique(c, t)
    c.set_source_rgba(0.05, 0.02, 0.08, 0.35); c.paint()
    for i in range(7):
        x = 80 + i * 135; y = 250 + 30 * math.sin(i * 1.3 + t * 2)
        badge(c, ['-70%', '-90%', '-50%', '-80%', '-99%', '-60%', '-90%'][i], x, y, 46, REDX if i % 2 else BFY,
              fg=(1, 1, 1) if i % 2 else INK, rot=0.2 * math.sin(i * 2.1), scale=1)
    speed_lines(c, t, 480, 820, col=(1, 1, 1), n=30, alpha=0.18)

def counter(c, t):
    """comptoir du vendeur au premier plan (cache les pieds, remplit le bas)"""
    sd = boil_seed(t)
    ink_fill(c, lambda k: blob(k, [(40, 1060), (620, 1060), (630, 1440), (30, 1440)], sd + 5, 0.6), REDX, lw=8)
    for i in range(5):
        x0 = 60 + i * 115
        ink_fill(c, lambda k, x0=x0: k.rectangle(x0, 1060, 55, 380), BFY, lw=0)
    ink_line(c, [(40, 1060), (630, 1060)], sd, 10)
    badge(c, 'PROMOS !!!', 330, 1110, 52, (1, 1, 1), fg=REDX, rot=-0.04)

def pip_ines(c, t, sh, state, k=1.0, smoke=0.0):
    """mini Inès + détecteur dans le coin bas droit (pendant le vendeur)"""
    if k <= 0.01: return
    x = 790; fy = 1110; sc = 0.3 * k
    mini(c, 'ines', 'I', x, fy, t, sh, sc=sc, eyes='half' if state != 'red' else 'wide', brows=-0.6 if state == 'red' else 0.8,
         smile=-0.2 if state == 'red' else 0.3, look=(-1, -0.3), arms=('hip', 'point_side'), face=-1, **IK)
    hx, hy = hand_xy(x, fy, sc, -1)
    detector(c, hx - 30, hy - 40, 0.62 * k, t, state, rot=-0.25, smoke=smoke)

# ---------------------------------------------------------------- dessin
def draw_dp(ctx, t, sh):
    TL = sh.tl; T = TL.T; i1, d1, d2, d3, i2, i3, i5, i4 = (T[c] for c, _ in ORDER)
    cap_y = 1210; ban = True
    ctx.save()
    if t < d1:                                       # 1. accroche : le vrai flacon scanné par Inès
        footage(ctx, 'nom', t * 0.6, 1.08, 1.16, 2, 520, 760, offset=40)
        x, fy, sc = 220, 1120, 0.4
        mini(ctx, 'ines', 'I', x, fy, t, sh, sc=sc, eyes='half', brows=0.9, smile=0.5, look=(1, -0.5),
             arms=('hip', 'point_side'), tilt=0.03 * math.sin(t * 5), **IK)
        hx, hy = hand_xy(x, fy, sc, 1)
        beam(ctx, hx + 60, hy - 120, 560, 720, t, AMBER)
        detector(ctx, hx + 20, hy - 30, 0.75, t, 'scan', rot=0.35)
        kq = pop(t, wt('xp_i1', 'PROMOS', 0.7))
        text(ctx, 'TU Y CROIS ENCORE ?', SAFE_CX + 10, 470, 104, fill=BFY, scale=kq, rot=-0.05 + 0.02 * math.sin(t * 8))
        if t < 0.22: flash(ctx, t, 0.22)
    elif t < d2:                                     # 2. le vendeur : « BLACK FRIDAY ! -90 % SUR TOUT ! »
        u = t - d1; km = d1 + wt('xp_d1', 'MOINS', 1.6)
        bg_foire(ctx, t)
        z = 1.0 + 0.06 * min(1, u / 3)
        ctx.save(); zoom_about(ctx, z, 420, 900)
        mini(ctx, 'david', 'D', 290, 1290, t, sh, sc=0.64, eyes='wide', brows=1.0, smile=1.0, look=(1, -0.2),
             arms=('hold_high', 'cheer'), jump=24 * abs(math.sin(u * 7)), tilt=0.05 * math.sin(t * 10), **DK)
        counter(ctx, t)
        if t < km:
            text(ctx, 'BLACK FRIDAY !', SAFE_CX + 120, 470, 130, fill=BFY, scale=pop(t, d1 + 0.05), rot=-0.07 + 0.03 * math.sin(t * 11))
        else:
            sign(ctx, 660, 500, 0.78 * pop(t, km, 0.3), t, 'SUR TOUT !', '-90 %', rot=0.06)
        ctx.restore()
        kb = pop(t, d1 + wt('xp_d1', 'TOUT', 2.9) + 0.15)
        pip_ines(ctx, t, sh, 'red' if kb > 0.5 else 'scan')
        if kb > 0.01: stamp(ctx, 'BIIIP !', 760, 760, kb, rot=0.15, size=80)
        flash(ctx, u, 0.14)
    elif t < d3:                                     # 3. « Euh… sur presque tout ? »
        u = t - d2
        bg_foire(ctx, t)
        mini(ctx, 'david', 'D', 270, 1310, t, sh, sc=0.72, eyes='tiny', brows=-0.4, smile=-0.3, look=(1, 0),
             arms=('hold_high', 'chin'), tilt=-0.04, **DK)
        sweat(ctx, 360, 640, t, 1.6)
        counter(ctx, t)
        sign(ctx, 660, 500, 0.78, t, 'SUR TOUT !', '-90 %', rot=0.06)
        if u > 0.5:
            text(ctx, '*SUR PRESQUE TOUT', 660, 680, 58, fill=(1, 1, 1), stroke=INK, rot=-0.06, scale=pop(t, d2 + 0.5))
        kb = pop(t, d2 + wt('xp_d2', 'TOUT', 1.6) + 0.1)
        pip_ines(ctx, t, sh, 'red' if kb > 0.5 else 'scan')
        if kb > 0.01: stamp(ctx, 'BIIIP !', 760, 760, kb, rot=-0.12, size=80)
        flash(ctx, u)
    elif t < i2:                                     # 4. « c'était le prix normal » : le détecteur fume
        u = t - d3; kn = d3 + wt('xp_d3', 'PRIX', 1.7)
        bg_foire(ctx, t)
        dark(ctx, 0.25)
        fall = ease_out((t - kn) / 0.5) if t > kn else 0
        mini(ctx, 'david', 'D', 290, 1290, t, sh, sc=0.64, eyes='closed', brows=-0.8, smile=-0.8, look=(0, 0.6),
             arms=('down', 'face'), **DK)
        counter(ctx, t)
        sign(ctx, 660 + 100 * fall, 500 + 620 * fall, 0.78 * (1 - 0.4 * fall), t, 'SUR TOUT !', '-90 %', rot=0.06 + 1.2 * fall)
        badge(ctx, 'PRIX NORMAL', SAFE_CX + 100, 440, 96, (1, 1, 1), fg=INK, scale=pop(t, kn), rot=-0.04)
        pip_ines(ctx, t, sh, 'red', smoke=min(1, u / 0.6))
        stamp(ctx, 'BOBARD', 330, 900, pop(t, kn + 0.25, 0.25), rot=-0.16, size=120)
        flash(ctx, u)
    elif t < i3:                                     # 5. « Sauf lui » : retour au vrai flacon, détecteur VERT
        u = t - i2
        f = min(72, 30 + int(u * 0.5 * 30))
        footage(ctx, 'fl2', (f - 30) / 30, 1.0, 1.0, 1, offset=30)
        rays(ctx, 760, 760, t, GOLDC, alpha=0.2 * ease_out(u / 0.4))
        x, fy, sc = 210, 1130, 0.38
        mini(ctx, 'ines', 'I', x, fy, t, sh, sc=sc, eyes='happy', brows=0.5, smile=1.0, blush=0.8, look=(1, -0.4),
             arms=('cheer', 'point_side'), **IK)
        hx, hy = hand_xy(x, fy, sc, 1)
        beam(ctx, hx + 60, hy - 120, 760, 760, t, GREENL)
        detector(ctx, hx + 20, hy - 30, 0.72, t, 'green', rot=0.35)
        text(ctx, 'SAUF LUI.', SAFE_CX, 420, 120, fill=GREENL, scale=pop(t, i2 + 0.05), rot=-0.05)
        kn = pop(t, i2 + wt('xp_i2', 'CONFIDENTIAL', 0.9))
        badge(ctx, 'CONFIDENTIAL PRIVATE GOLD', SAFE_CX, 560, 56, GOLDC, fg=INK, scale=kn, rot=0.03)
        badge(ctx, 'LATTAFA', 640, 680, 72, hexc('#141414'), fg=GOLDC, scale=pop(t, i2 + wt('xp_i2', 'LATTAFA', 2.4)), rot=-0.05)
        if kn > 0.5:
            for i in range(5): sparkle(ctx, 620 + (i * 67) % 260, 760 + (i * 113) % 420, 30, t, ph=i)
        flash(ctx, u, 0.18)
    elif t < i5:                                     # 6. pas de pourcentage magique : le prix
        u = t - i3
        footage(ctx, 'edp', u * 0.4, 1.0, 1.06, 2.5)
        x, y, s = kf(EDP, min(60, int(u * 0.4 * 30)))
        # le badge « % » barré
        tm = i3 + wt('xp_i3', 'MOINS', 1.6)
        kpct = pop(t, i3 + 0.05)
        if t < tm:
            badge(ctx, '%', SAFE_CX, 640, 170, REDX, fg=(1, 1, 1), scale=kpct, rot=-0.1)
            if kpct > 0.5:
                ctx.save(); ctx.set_source_rgb(*INK); ctx.set_line_width(22)
                ctx.move_to(SAFE_CX - 110, 530); ctx.line_to(SAFE_CX + 110, 750); ctx.stroke(); ctx.restore()
        text(ctx, 'PAS DE % MAGIQUE', SAFE_CX, 420, 92, fill=(1, 1, 1), scale=pop(t, i3 + wt('xp_i3', 'POURCENTAGE', 0.3)), rot=-0.03)
        kp = pop(t, tm)
        if kp > 0.01: price_tag(ctx, SAFE_CX + 20, 640, 0.8 * kp, t, 'MOINS DE 25 €', sub=None)
        mini(ctx, 'ines', 'I', 790, 1130, t, sh, sc=0.34, eyes='happy', brows=0.5, smile=1.0, look=(-1, -0.3),
             arms=('hip', 'cheer'), face=-1, jump=30 * abs(math.sin(u * 6)) if t > tm else 0, **IK)
        mini(ctx, 'david', 'D', 170, 1130, t, sh, sc=0.3, eyes='wide', brows=0.9, smile=0.3, look=(1, -0.4),
             arms=('face', 'face'), **DK)
        flash(ctx, u)
    elif t < i4:                                     # 7. question au spectateur
        u = t - i5
        footage(ctx, 'nom', 1.5 + u * 0.5, 1.06, 1.12, 3, 600, 600, offset=40)
        dark(ctx, 0.35)
        badge(ctx, 'ET TOI, TU CROIS ENCORE', SAFE_CX, 400, 62, (1, 1, 1), fg=INK, scale=pop(t, i5 + 0.05), rot=-0.03)
        badge(ctx, 'AUX PROMOS ?', SAFE_CX, 510, 90, BFY, fg=INK, scale=pop(t, i5 + wt('xp_i5', 'AUX', 0.6)), rot=0.02)
        ko = pop(t, i5 + wt('xp_i5', 'PROMOS', 0.8))
        badge(ctx, 'OUI', 300, 700, 90, GREENL, fg=INK, scale=ko, rot=-0.08)
        badge(ctx, 'JAMAIS', 640, 700, 90, REDX, fg=(1, 1, 1), scale=ko, rot=0.06)
        mini(ctx, 'ines', 'I', SAFE_CX - 30, 1110, t, sh, sc=0.34, eyes='open', brows=0.7, smile=1.0, look=(0, 0.7),
             arms=('point_side', 'chin'), face=-1, **IK)
        comment_bubble(ctx, 780, 900, pop(t, i5 + wt('xp_i5', 'DIS', 1.3)) * 0.85, t)
        ban = False; cap_y = 1240
        flash(ctx, u)
    else:                                            # 8. prix + appel à l'action
        v = t - i4
        footage(ctx, 'fl1', 1.0 + min(v, 0.9) * 0.4, 1.0, 1.0, 1)
        mini(ctx, 'david', 'D', 800, 870, t, sh, sc=0.28, eyes='happy', brows=0.4, smile=1.0, look=(-1, 0.4), arms=('hip', 'wave'), face=-1, **DK)
        mini(ctx, 'ines', 'I', 640, 870, t, sh, sc=0.32, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
             look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1, **IK)
        price_tag(ctx, 330, 520, 0.62, t, 'MOINS DE 25 €', sub=None)
        ctx.restore(); L.banner(ctx, t, BAN, bg=BFY, fg=INK); L.cta(ctx, t, i4 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=BFY, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_dp():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.8); T = TL.T; i1, d1, d2, d3, i2, i3, i5, i4 = (T[c] for c, _ in ORDER)
    km = d1 + wt('xp_d1', 'MOINS', 1.6); kn = d3 + wt('xp_d3', 'PRIX', 1.7)
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.08, 0.5), ('buzz', 0.3, 0.25), ('pop', wt('xp_i1', 'PROMOS', 0.7), 0.5),
           ('scratch', d1 - 0.03, 0.5), ('bells', d1 + 0.05, 0.35), ('stamp', km, 0.7),
           ('buzz', d1 + wt('xp_d1', 'TOUT', 2.9) + 0.15, 0.8),
           ('swipe', d2 - 0.03, 0.4), ('wah', d2 + 0.6, 0.4), ('buzz', d2 + wt('xp_d2', 'TOUT', 1.6) + 0.1, 0.8),
           ('swipe', d3 - 0.03, 0.4), ('boing', kn + 0.1, 0.5), ('buzz', kn + 0.2, 0.9), ('stamp', kn + 0.25, 0.9),
           ('pschht', d3 + 0.3, 0.4),
           ('ding', i2 - 0.62, 0.5), ('sparkle', i2 + wt('xp_i2', 'GOLD', 1.6), 0.4),
           ('pop', i2 + wt('xp_i2', 'LATTAFA', 2.4), 0.6),
           ('swipe', i3 - 0.03, 0.5), ('scratch', i3 + 0.05, 0.4), ('coins', i3 + wt('xp_i3', 'MOINS', 1.6), 0.6),
           ('whoosh', i5 - 0.03, 0.5), ('pop', i5 + wt('xp_i5', 'PROMOS', 0.8), 0.6), ('sparkle', i5 + wt('xp_i5', 'DIS', 1.3), 0.5),
           ('bells', i4 + 0.05, 0.4), ('ding', i4 + RCTA + 0.05, 0.7)]
    sh = Shot('detecteur_promos', TL.dur, draw_dp, TL.voices(), sfx, []); sh.tl = TL
    return [sh], (i2 - 0.32, i2 + 0.6)
