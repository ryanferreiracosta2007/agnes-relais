# -*- coding: utf-8 -*-
"""Parfum Lattafa : « Soft launch » détourné (tendance de la semaine : indice puis révélation).
   Mini Léa fait le soft launch de son « nouveau crush » : on voit la main qui tient le vrai flacon, l'étiquette cachée
   par un autocollant cœur. Mini Inès veut voir « son visage ». Indices (doré, mystérieux), puis HARD LAUNCH :
   l'autocollant s'envole, c'est le Confidential Private Gold. Prix, question « tu ferais le soft launch de quoi ? », CTA."""
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
import sl_data as SL

WORDS = {c: SL.words_for(c) for c in SL.CUTS}
for w in ("QUELQU'UN.", 'QUI ?', 'VISAGE !', 'DORÉ…', 'MYSTÉRIEUX.', 'CONFIDENTIAL', 'PRIVATE', 'GOLD', 'LATTAFA.',
          'PARFUM ?!', 'VINGT-CINQ', 'SOFT', 'LAUNCH', 'COMMENTAIRE.'):
    if w not in S.HL: S.HL = S.HL + (w,)
PINK = hexc('#ff5c8a'); PINK_L = hexc('#ffb3c8'); NIGHT = hexc('#140a1e')
BAN = "SOFT LAUNCH DE MON NOUVEAU CRUSH"
ORDER = [('xl_l1', 'L'), ('xl_i1', 'I'), ('xl_l2', 'L'), ('xl_l3', 'L'), ('xl_i2', 'I'), ('xl_l4', 'L'), ('xl_i3', 'I'), ('xl_l5', 'L')]
PAUSE = {'xl_i1': 0.05, 'xl_l2': 0.05, 'xl_l3': 0.12, 'xl_i2': 0.05, 'xl_l4': 0.06, 'xl_i3': 0.06, 'xl_l5': 0.08}
RCTA = 0.55
LK = dict(); IK = dict()
# position de l'étiquette dans les images « nom » (image source, x, y) relevée sur planche quadrillée
NOMLAB = [(40, 685, 720), (48, 615, 700), (56, 570, 770), (64, 575, 770), (72, 675, 740), (80, 685, 700), (88, 690, 700), (96, 690, 700), (104, 630, 670), (112, 620, 650)]

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def lab_at(f):
    if f <= NOMLAB[0][0]: return NOMLAB[0][1:]
    for a, b in zip(NOMLAB, NOMLAB[1:]):
        if f <= b[0]:
            u = (f - a[0]) / (b[0] - a[0]); return (a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u)
    return NOMLAB[-1][1:]

# ---------------------------------------------------------------- accessoires dessinés
def heart_sticker(c, x, y, s, t, rot=0.0):
    """gros autocollant cœur (le code du soft launch : on cache le visage)"""
    c.save(); c.translate(x, y); c.rotate(rot + 0.05 * math.sin(t * 3)); c.scale(s, s)
    c.save(); c.translate(10, 14); c.new_path(); heart(c, 0, 0, 120); c.set_source_rgba(0, 0, 0, 0.35); c.fill(); c.restore()
    ink_fill(c, lambda k: heart(k, 0, 0, 128), (1, 1, 1), lw=4)
    ink_fill(c, lambda k: heart(k, 0, 0, 112), PINK, lw=6)
    c.new_path(); c.arc(-48, -38, 16, 0, 7); c.set_source_rgba(1, 1, 1, 0.7); c.fill()
    c.restore()

def story_bars(c, t, k_done):
    """barres de progression façon « story » (générique, sans logo)"""
    n = 3; w = (860 - 20 * (n - 1)) / n
    for i in range(n):
        x = 70 + i * (w + 20)
        c.new_path(); rrect(c, x, 112, w, 12, 6); c.set_source_rgba(1, 1, 1, 0.45); c.fill()
        f = max(0, min(1, k_done * n - i))
        if f > 0: c.new_path(); rrect(c, x, 112, w * f, 12, 6); c.set_source_rgb(1, 1, 1); c.fill()

def stamp(c, txt, x, y, k, rot=-0.18, col=REDX, size=120):
    if k <= 0.01: return
    s = 1 + 1.6 * (1 - min(1, k))
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    w = text_w(c, txt, size) + 70
    c.new_path(); rrect(c, -w / 2, -size * 0.72, w, size * 1.4, 18); c.set_source_rgba(1, 1, 1, 0.85); c.fill_preserve()
    c.set_source_rgb(*col); c.set_line_width(12); c.stroke()
    text(c, txt, 0, 6, size, fill=col, stroke=None, shadow=False)
    c.restore()

def magnifier(c, x, y, s, t):
    c.save(); c.translate(x, y); c.rotate(-0.6 + 0.15 * math.sin(t * 6)); c.scale(s, s)
    ink_fill(c, lambda k: rrect(k, -18, 70, 36, 150, 14), hexc('#7a4f27'), lw=6)
    c.new_path(); c.arc(0, 0, 80, 0, 7); c.set_source_rgba(0.8, 0.95, 1, 0.35); c.fill_preserve()
    c.set_source_rgb(*INK); c.set_line_width(22); c.stroke()
    c.new_path(); c.arc(0, 0, 80, 0, 7); c.set_source_rgb(*GOLD); c.set_line_width(10); c.stroke()
    c.restore()

def dark(c, a):
    c.set_source_rgba(0, 0, 0, a); c.paint()

def hint_card(c, num, txt, x, y, k, rot, t):
    if k <= 0.01: return
    badge(c, f'INDICE {num}', x, y - 70, 50, (1, 1, 1), fg=INK, scale=k, rot=rot)
    badge(c, txt, x, y + 20 * math.sin(t * 4) * 0.2, 80, PINK, fg=(1, 1, 1), scale=k, rot=rot)

# ---------------------------------------------------------------- dessin
def draw_sl(ctx, t, sh):
    TL = sh.tl; T = TL.T; l1, i1, l2, l3, i2, l4, i3, l5 = (T[c] for c, _ in ORDER)
    cap_y = 1200; ban = True
    ctx.save()
    if t < l2:                                       # 1-2. le soft launch : la main, le flacon, le cœur sur l'étiquette
        ft = t * 0.5
        footage(ctx, 'nom', ft, 1.0, 1.0, 4, offset=40)
        f = 40 + int(ft * 30)
        lx, ly = lab_at(f)
        story_bars(ctx, t, min(1, t / l2) * 0.34)
        heart_sticker(ctx, lx, ly + 55, 1.95 + 0.04 * math.sin(t * 7), t, rot=-0.08)
        for i in range(4): sparkle(ctx, lx - 230 + (i * 157) % 460, ly - 260 + (i * 211) % 520, 26, t, ph=i, col=(1, 0.9, 0.5))
        if t < i1:
            mini(ctx, 'lea', 'L', 210, 1090, t, sh, sc=0.42, eyes='heart', brows=0.6, smile=1.0, blush=1.0, look=(1, -0.6),
                 arms=('phone', 'hip'), tilt=0.05 * math.sin(t * 5), **LK)
            S.hearts_float(ctx, t, 210, 640, n=5, seed=3, start=0.1)
            if t < 0.25: flash(ctx, t, 0.25)
        else:
            u = t - i1
            mini(ctx, 'lea', 'L', 170, 1090, t, sh, sc=0.38, eyes='wink' if (u % 1.4) > 1.0 else 'happy', brows=0.4, smile=1.0, blush=0.8,
                 look=(1, 0), arms=('phone', 'lips'), **LK)
            jump = 30 * abs(math.sin(u * 9)) if u < 1.0 else 0
            mini(ctx, 'ines', 'I', 800, 1090, t, sh, sc=0.42, eyes='wide', brows=1.0, smile=0.6, look=(-1, -0.7),
                 arms=('point_side', 'hip'), face=-1, jump=jump, tilt=0.06 * math.sin(t * 14), **IK)
            shock_lines(ctx, 800, 820, t, 150)
            kq = pop(t, i1 + wt('xl_i1', 'QUI', 0.5))
            text(ctx, "C'EST QUI ?!", SAFE_CX, 470, 120, fill=hexc('#ffd23f'), scale=kq, rot=-0.06 + 0.03 * math.sin(t * 8))
            kv = pop(t, i1 + wt('xl_i1', 'MONTRE', 0.9))
            if kv > 0.01: magnifier(ctx, lx + 190, ly + 190, 1.3 * kv, t)
            flash(ctx, u)
    elif t < l3:                                     # 3. deux indices, un plan chacun
        u = t - l2; half = l2 + wt('xl_l2', 'ET', 1.35) - 0.08
        if t < half:
            footage(ctx, 'fl1', u * 0.5, 1.7, 1.85, 2, 440, 560)
            rays(ctx, 440, 560, t, GOLDC, alpha=0.2)
            heart_sticker(ctx, 440, 1120, 2.2, t, rot=0.08)
            for i in range(6): sparkle(ctx, 200 + (i * 97) % 520, 300 + (i * 131) % 500, 34, t, ph=i)
            hint_card(ctx, 1, 'IL EST TOUT DORÉ', SAFE_CX, 860, pop(t, l2 + 0.1), -0.04, t)
            mini(ctx, 'lea', 'L', 790, 1090, t, sh, sc=0.38, eyes='heart', brows=0.6, smile=1.0, blush=1.0, look=(-1, -0.6),
                 arms=('lips', 'hip'), face=-1, **LK)
            cap_y = 1250
        else:
            v = t - half
            footage(ctx, 'edp', 0.3 + v * 0.3, 1.25, 1.32, 2, 620, 760)
            dark(ctx, 0.62)
            g = cairo.RadialGradient(620, 760, 60, 620, 760, 420)
            g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.18); g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.set_source(g); ctx.paint()
            heart_sticker(ctx, 600, 820, 1.9, t, rot=-0.06)
            for i in range(3):
                a = t * 1.6 + i * 2.1
                text(ctx, '?', 600 + 300 * math.cos(a), 700 + 260 * math.sin(a), 120, fill=PINK_L, rot=0.2 * math.sin(t * 6 + i))
            hint_card(ctx, 2, 'UN PEU MYSTÉRIEUX', SAFE_CX, 470, pop(t, half + 0.05), 0.04, t)
            mini(ctx, 'lea', 'L', 200, 1090, t, sh, sc=0.36, eyes='half', brows=0.8, smile=0.8, look=(1, -0.3),
                 arms=('chin', 'hip'), **LK)
            flash(ctx, v)
    elif t < i2:                                     # 4. HARD LAUNCH : l'autocollant s'envole, le vrai flacon
        u = t - l3
        f = min(72, 30 + int(u * 0.45 * 30))
        footage(ctx, 'fl2', (f - 30) / 30, 1.0, 1.0, 1, offset=30)
        rays(ctx, 740, 760, t, GOLDC, alpha=0.22 * ease_out(u / 0.4))
        fly = ease_out(u / 0.55)
        if fly < 0.99: heart_sticker(ctx, 720 + 500 * fly, 900 - 900 * fly, 1.7 * (1 - 0.4 * fly), t, rot=fly * 3)
        x, y, s = kf(FL2, f)
        mini(ctx, 'lea', 'L', x, y, t, sh, sc=s, eyes='happy', brows=0.6, smile=1.0, blush=1.0, look=(-1, -0.3),
             arms=('cheer', 'cheer'), face=-1, jump=20 * abs(math.sin(u * 6)), **LK)
        stamp(ctx, 'HARD LAUNCH', SAFE_CX, 470, pop(t, l3 + 0.1, 0.25), rot=-0.12)
        kn = pop(t, l3 + wt('xl_l3', 'CONFIDENTIAL', 0.9))
        badge(ctx, 'CONFIDENTIAL PRIVATE GOLD', SAFE_CX, 640, 58, GOLDC, fg=INK, scale=kn, rot=0.03)
        badge(ctx, 'LATTAFA', 300, 780, 76, hexc('#141414'), fg=GOLDC, scale=pop(t, l3 + wt('xl_l3', 'LATTAFA', 2.6)), rot=-0.05)
        if kn > 0.5:
            for i in range(6): sparkle(ctx, 600 + (i * 67) % 300, 700 + (i * 113) % 480, 30, t, ph=i)
        flash(ctx, u, 0.18)
    elif t < l4:                                     # 5. Inès : « c'est un parfum ?! »
        u = t - i2
        f = min(60, int(u * 0.45 * 30))
        footage(ctx, 'edp', u * 0.45, 1.0, 1.0, 1)
        x, y, s = kf(EDP, f)
        laugh = t > i2 + wt('xl_i2', 'PARFUM', 0.9) + 0.4
        mini(ctx, 'ines', 'I', x, y, t, sh, sc=s, eyes='happy' if laugh else 'wide', brows=1.0, smile=1.0 if laugh else -0.3,
             look=(-1, -0.2), arms=('face', 'face') if not laugh else ('hip', 'cheer'), face=-1,
             tilt=0.08 * math.sin(t * 16) if laugh else 0, **IK)
        shock_lines(ctx, x, y - 200, t, 170)
        kp = pop(t, i2 + wt('xl_i2', 'PARFUM', 0.9))
        text(ctx, 'UN PARFUM ?!', SAFE_CX - 80, 520, 130, fill=PINK, scale=kp, rot=-0.08 + 0.03 * math.sin(t * 9))
        if laugh: text(ctx, 'MDR', 300, 760, 90, fill=(1, 1, 1), scale=pop(t, i2 + wt('xl_i2', 'PARFUM', 0.9) + 0.4), rot=0.1)
        flash(ctx, u)
    elif t < i3:                                     # 6. prix
        u = t - l4
        footage(ctx, 'fl1', 0.6 + u * 0.3, 1.0, 1.06, 2, 540, 900)
        snow(ctx, t, n=40, alpha=0.7)
        mini(ctx, 'lea', 'L', 190, 1090, t, sh, sc=0.38, jump=36 * abs(math.sin(u * 6)), eyes='happy', brows=0.6, smile=1.0,
             look=(1, 0), arms=('cheer', 'cheer'), **LK)
        mini(ctx, 'ines', 'I', 810, 1090, t, sh, sc=0.38, eyes='heart', brows=0.6, smile=1.0, look=(-1, 0), arms=('hip', 'cheer'), face=-1, **IK)
        kp = pop(t, l4 + wt('xl_l4', 'MOINS', 1.1))
        if kp > 0.01: price_tag(ctx, SAFE_CX, 620, 0.8 * kp, t, 'MOINS DE 25 €', sub=None)
        flash(ctx, u)
    elif t < l5:                                     # 7. question au spectateur
        u = t - i3
        footage(ctx, 'nom', 1.2 + u * 0.5, 1.06, 1.12, 3, 600, 600, offset=40)
        dark(ctx, 0.25)
        badge(ctx, 'ET TOI, TU FERAIS', SAFE_CX, 420, 64, (1, 1, 1), fg=INK, scale=pop(t, i3 + 0.05), rot=-0.03)
        badge(ctx, 'LE SOFT LAUNCH DE QUOI ?', SAFE_CX, 530, 64, PINK, fg=(1, 1, 1), scale=pop(t, i3 + wt('xl_i3', 'SOFT', 0.6)), rot=0.02)
        mini(ctx, 'ines', 'I', SAFE_CX + 40, 1090, t, sh, sc=0.42, eyes='open', brows=0.7, smile=1.0, look=(0, 0.7),
             arms=('point_side', 'chin'), face=-1, **IK)
        kc = pop(t, i3 + wt('xl_i3', 'DIS', 1.3))
        if kc > 0.01:
            comment_bubble(ctx, 790, 800, kc * 0.9, t)
            heart_sticker(ctx, 230, 800, 0.6 * kc, t)
        ban = False; cap_y = 1240
        flash(ctx, u)
    else:                                            # 8. appel à l'action
        v = t - l5
        footage(ctx, 'fl1', 1.0 + min(v, 0.9) * 0.4, 1.0, 1.0, 1)
        snow(ctx, t, n=40, alpha=0.6)
        mini(ctx, 'ines', 'I', 800, 870, t, sh, sc=0.3, eyes='heart', brows=0.5, smile=1.0, look=(-1, 0.4), arms=('hip', 'wave'), face=-1, **IK)
        mini(ctx, 'lea', 'L', 640, 870, t, sh, sc=0.32, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
             look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1, **LK)
        price_tag(ctx, 330, 520, 0.62, t, 'MOINS DE 25 €', sub=None)
        ctx.restore(); L.banner(ctx, t, BAN, bg=PINK, fg=(1, 1, 1)); L.cta(ctx, t, l5 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=PINK, fg=(1, 1, 1))
    TL.captions(ctx, t, cap_y)

def build_sl():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.75); T = TL.T; l1, i1, l2, l3, i2, l4, i3, l5 = (T[c] for c, _ in ORDER)
    half = l2 + wt('xl_l2', 'ET', 1.35) - 0.08
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.08, 0.5), ('heart', 0.2, 0.5), ('sparkle', 0.6, 0.3),
           ('whoosh', i1 - 0.03, 0.5), ('boing', i1 + wt('xl_i1', 'QUI', 0.5), 0.5), ('pop', i1 + wt('xl_i1', 'MONTRE', 0.9), 0.5),
           ('swipe', l2 - 0.03, 0.5), ('sparkle', l2 + 0.15, 0.4), ('swipe', half - 0.03, 0.5),
           ('drumroll', half + 0.1, 0.2),
           ('scratch', l3 - 0.02, 0.5), ('stamp', l3 + 0.12, 0.9), ('sparkle', l3 + wt('xl_l3', 'GOLD', 1.6), 0.35),
           ('pop', l3 + wt('xl_l3', 'LATTAFA', 2.6), 0.6),
           ('whoosh', i2 - 0.03, 0.5), ('boing', i2 + wt('xl_i2', 'PARFUM', 0.9), 0.5),
           ('swipe', l4 - 0.03, 0.6), ('coins', l4 + wt('xl_l4', 'MOINS', 1.1), 0.6),
           ('whoosh', i3 - 0.03, 0.5), ('pop', i3 + wt('xl_i3', 'SOFT', 0.6), 0.6), ('sparkle', i3 + wt('xl_i3', 'DIS', 1.3), 0.5),
           ('bells', l5 + 0.05, 0.4), ('ding', l5 + RCTA + 0.05, 0.7)]
    sh = Shot('soft_launch', TL.dur, draw_sl, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
