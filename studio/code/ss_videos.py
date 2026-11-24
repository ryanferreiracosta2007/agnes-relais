# -*- coding: utf-8 -*-
"""Parfum Lattafa : « Secret Santa au bureau, 25 € de budget, tu offres quoi ? »
   Mini David (bonnet de Père Noël) a tiré sa collègue Sarah au Secret Santa. Le mug et les chaussettes
   sont rejetés (« au fond du tiroir »), puis il dévoile le vrai flacon doré. Fin : débat « bonne idée ou trop perso ? »."""
import math
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, ease_out, kf, FL1, FL2, EDP, GOLDC, REDX
from tb_videos import comment_bubble, zoom_about
import ss_data as SS

WORDS = {c: SS.words_for(c) for c in SS.CUTS}
for w in ('SECRET', 'SANTA', 'SANTA :', 'VINGT-CINQ', 'MUG,', 'DOUZE.', 'CHAUSSETTES', 'TIROIR.', 'CONFIDENTIAL', 'PRIVATE',
          'LATTAFA.', 'DORÉ…', 'POINTS.', 'PERSO ?', 'COMMENTAIRE.', 'BONNE', 'IDÉE'):
    if w not in S.HL: S.HL = S.HL + (w,)
GREENC = hexc('#2fa84f'); NAVY = hexc('#1d2b53'); WOOD = hexc('#b07a45'); WOOD_D = hexc('#7a4f27')
BAN = "SECRET SANTA : 25 € DE BUDGET"
ORDER = [('xs_d1', 'D'), ('xs_s1', 'S'), ('xs_d2', 'D'), ('xs_s2', 'S'), ('xs_d3', 'D'), ('xs_s3', 'S'),
         ('xs_d4', 'D'), ('xs_s4', 'S'), ('xs_d5', 'D')]
PAUSE = {'xs_s1': 0.05, 'xs_d2': 0.05, 'xs_s2': 0.05, 'xs_d3': 0.1, 'xs_s3': 0.08, 'xs_d4': 0.05, 'xs_s4': 0.08, 'xs_d5': 0.08}
RCTA = 0.55
DK = dict(outfit='tee'); SK = dict()

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

# ---------------------------------------------------------------- accessoires dessinés
def mug_shape(c, x, y, s, t, col=hexc('#5aa9e6')):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.new_path(); c.arc(54, 0, 30, -1.5, 1.5); c.set_source_rgb(*INK); c.set_line_width(16); c.stroke()
    c.new_path(); c.arc(54, 0, 30, -1.5, 1.5); c.set_source_rgb(*col); c.set_line_width(8); c.stroke()
    ink_fill(c, lambda k: rrect(k, -50, -55, 100, 115, 14), col, lw=6)
    ink_fill(c, lambda k: heart(k, 0, 4, 22), (1, 1, 1), lw=3)
    c.restore()

def mug_prop(s=1.6):
    def f(c, x, y, tt): mug_shape(c, x + 20, y - 40, s, tt)
    return f

def sock_shape(c, x, y, s, t, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    ink_fill(c, lambda k: blob(k, [(-30, -90), (30, -90), (30, 30), (85, 55), (80, 95), (-10, 95), (-30, 60)], 11, 0.8), RED, lw=6)
    ink_fill(c, lambda k: rrect(k, -38, -110, 76, 34, 12), (1, 1, 1), lw=5)
    for j in range(3):
        ink_fill(c, lambda k, j=j: star(k, -2 + 8 * j, -40 + 28 * j, 10, 4), (1, 1, 1), lw=2)
    c.restore()

def sock_prop(s=1.3):
    def f(c, x, y, tt): sock_shape(c, x + 10, y - 30, s, tt, rot=0.15 * math.sin(tt * 4))
    return f

def name_note(c, x, y, tt):
    """petit papier du tirage au sort : « SARAH »"""
    c.save(); c.translate(x + 30, y - 70); c.rotate(-0.12 + 0.05 * math.sin(tt * 9)); c.scale(1.5, 1.5)
    ink_fill(c, lambda k: rrect(k, -60, -40, 120, 80, 6), CREAM, lw=5)
    text(c, 'SARAH', 0, 4, 34, fill=REDX, stroke=None, shadow=False)
    c.restore()

def red_x(c, x, y, s, k):
    if k <= 0.01: return
    c.save(); c.translate(x, y); c.scale(s * k, s * k); c.rotate(-0.1)
    for sgn in (1, -1):
        c.new_path(); c.move_to(-90, -90 * sgn); c.line_to(90, 90 * sgn)
        c.set_line_cap(1); c.set_source_rgb(*INK); c.set_line_width(46); c.stroke()
        c.new_path(); c.move_to(-90, -90 * sgn); c.line_to(90, 90 * sgn); c.set_source_rgb(*REDX); c.set_line_width(30); c.stroke()
    c.restore()

def drawer(c, x, y, open_k, t):
    """tiroir de bureau vu de face ; open_k 1 = ouvert (on voit l'intérieur), 0 = fermé"""
    w, h = 560, 260
    ink_fill(c, lambda k: rrect(k, x - w / 2 - 30, y - h / 2 - 30, w + 60, h + 60, 18), WOOD_D, lw=7)
    if open_k > 0.01:
        d = 120 * open_k
        ink_fill(c, lambda k: (k.move_to(x - w / 2, y - h / 2), k.line_to(x + w / 2, y - h / 2),
                               k.line_to(x + w / 2 + 40, y - h / 2 - d), k.line_to(x - w / 2 - 40, y - h / 2 - d), k.close_path()), hexc('#3b2412'), lw=6)
    ink_fill(c, lambda k: rrect(k, x - w / 2, y - h / 2 + 20 * open_k, w, h, 12), WOOD, lw=7)
    ink_fill(c, lambda k: rrect(k, x - 70, y - 14 + 20 * open_k, 140, 28, 12), GOLD, lw=5)

def choice_card(c, txt, x, y, col, k, rot, t):
    if k <= 0.01: return
    badge(c, txt, x, y + 6 * math.sin(t * 5 + x), 64, col, fg=(1, 1, 1), scale=k, rot=rot)

def dark(c, a):
    c.set_source_rgba(0, 0, 0, a); c.paint()

# ---------------------------------------------------------------- dessin
def draw_ss(ctx, t, sh):
    TL = sh.tl; T = TL.T; d1, s1, d2, s2, d3, s3, d4, s4, d5 = (T[c] for c, _ in ORDER)
    cap_y = 1200; ban = True
    ctx.save()
    if t < s1:                                       # 1. accroche : il a tiré Sarah, 25 € de budget, panique
        tz = d1 + wt('xs_d1', 'TU', 2.7) - 0.1
        zin = ease_out((t - tz) / 0.25)
        footage(ctx, 'nom', t * 0.8, 1.0, 1.06, s1, 600, 560, offset=40)
        ctx.save(); zoom_about(ctx, 1 + 0.18 * zin, 600, 560)
        for i in range(3):
            a = t * 1.8 + i * 2.1
            text(ctx, '?', 600 + 260 * math.cos(a), 560 + 200 * math.sin(a), 110, fill=hexc('#ffd23f'), rot=0.2 * math.sin(t * 6 + i))
        ctx.restore()
        mini(ctx, 'david', 'D', 250, 1070, t, sh, sc=0.44, hat=True, eyes='wide', brows=1.0, smile=-0.7, look=(1, -0.6),
             arms=('hold_high', 'face'), tilt=0.05 * math.sin(t * 28), prop=name_note, prop_hand='R', **DK)
        sweat(ctx, 330, 690, t, 1.0)
        shock_lines(ctx, 250, 760, t, 160)
        kb = pop(t, d1 + wt('xs_d1', 'VINGT', 1.8))
        badge(ctx, 'BUDGET : 25 €', 680, 1000, 72, hexc('#ffd23f'), fg=INK, scale=kb, rot=0.05)
        if t < 0.25: flash(ctx, t, 0.25)
    elif t < d3:                                     # 2-4. le mug, les chaussettes, le tiroir
        footage(ctx, 'fl1', 0.2 + (t - s1) * 0.15, 1.12, 1.18, d3 - s1, 540, 760)
        dark(ctx, 0.5)
        snow(ctx, t, n=30, alpha=0.5)
        if t < s2:
            socks = t >= d2
            u = t - (d2 if socks else s1)
            mini(ctx, 'david', 'D', 260, 1070, t, sh, sc=0.44, hat=True, eyes='wide' if socks else 'open', brows=0.8 if socks else 0.4,
                 smile=0.9, look=(1, -0.2), arms=('hip', 'give'), jump=20 * abs(math.sin(u * 8)) if socks else 0, **DK)
            ki = pop(t, (d2 if socks else s1) + 0.02)
            bob = 12 * math.sin(t * 5)
            if ki <= 0.01: pass
            elif socks: sock_shape(ctx, 480, 760 + bob, 1.7 * ki, t, rot=0.15 * math.sin(t * 4))
            else: mug_shape(ctx, 470, 770 + bob, 1.8 * ki, t)
            mini(ctx, 'sarah', 'S', 740, 1070, t, sh, sc=0.46, eyes='half', brows=-0.6, smile=-0.5, look=(-1, 0.1),
                 arms=('hip', 'hip'), face=-1, tilt=-0.06, **SK)
            if not socks:
                k12 = pop(t, s1 + wt('xs_s1', 'DOUZE', 2.5))
                if k12 > 0.01:
                    for j in range(12):
                        mug_shape(ctx, 150 + (j % 6) * 130, 470 + (j // 6) * 150, 0.75 * k12, t,
                                  col=(hexc('#5aa9e6'), hexc('#f4c430'), hexc('#ef7fae'), GREENC)[j % 4])
                    badge(ctx, 'DÉJÀ 12 MUGS', SAFE_CX, 790, 66, REDX, fg=(1, 1, 1), scale=k12, rot=-0.04)
                if k12 <= 0.01: red_x(ctx, 480, 770, 0.9, pop(t, s1 + wt('xs_s1', 'PAS', 0.0) + 0.35))
            else:
                for i in range(4): sparkle(ctx, 300 + 90 * i, 640 + 40 * math.sin(i), 26, t, ph=i)
                text(ctx, 'NOËL ?', 600, 560, 110, fill=(1, 1, 1), scale=pop(t, d2 + 0.1), rot=-0.08)
            flash(ctx, u)
        else:
            u = t - s2; D = d3 - s2
            slam = ease_out((u - (D - 0.55)) / 0.18)
            drawer(ctx, SAFE_CX, 1000, 1 - slam, t)
            fall = ease(min(1, u / 0.9))
            if slam < 0.99:
                mug_shape(ctx, SAFE_CX - 120, 420 + 520 * fall, 1.1, t)
                sock_shape(ctx, SAFE_CX + 120, 380 + 560 * fall, 1.0, t, rot=fall * 2.5)
            mini(ctx, 'sarah', 'S', 800, 1300, t, sh, sc=0.4, eyes='half', brows=-0.8, smile=-0.3, look=(-0.4, -1),
                 arms=('hip', 'point_side'), face=-1, **SK)
            mini(ctx, 'david', 'D', 160, 1300, t, sh, sc=0.32, hat=True, eyes='tiny', brows=-0.8, smile=-0.8, look=(1, 0), arms=('down', 'down'), **DK)
            if slam > 0.5: text(ctx, 'CLAC !', SAFE_CX, 760, 130, fill=REDX, scale=pop(t, s2 + D - 0.4), rot=-0.1)
            cap_y = 520
            flash(ctx, u)
    elif t < d4:                                     # 5-6. la révélation : le vrai flacon doré
        if t < s3:
            u = t - d3
            f = min(72, 30 + int(u * 0.5 * 30))
            footage(ctx, 'fl2', (f - 30) / 30, 1.0, 1.0, 1, offset=30)
            rays(ctx, 820, 640, t, GOLDC, alpha=0.18 * ease_out(u / 0.4))
            x, y, s = kf(FL2, f)
            mini(ctx, 'david', 'D', x, y, t, sh, sc=s, hat=True, eyes='happy' if u > 0.5 else 'half', brows=0.6, smile=1.0,
                 look=(-1, -0.3), arms=('point_side', 'cheer'), face=-1, **DK)
            kn = pop(t, d3 + wt('xs_d3', 'CONFIDENTIAL', 0.8))
            badge(ctx, 'CONFIDENTIAL PRIVATE GOLD', SAFE_CX, 470, 60, GOLDC, fg=INK, scale=kn, rot=-0.03)
            badge(ctx, 'LATTAFA', 300, 600, 78, hexc('#141414'), fg=GOLDC, scale=pop(t, d3 + wt('xs_d3', 'LATTAFA', 2.2)), rot=0.04)
            if kn > 0.5:
                for i in range(6): sparkle(ctx, 700 + (i * 67) % 260, 620 + (i * 113) % 520, 30, t, ph=i)
            flash(ctx, u)
        else:
            u = t - s3
            f = min(60, int(u * 0.4 * 30))
            footage(ctx, 'edp', u * 0.4, 1.0, 1.0, 1)
            string_lights(ctx, t, y=370, seed=2)
            snow(ctx, t, n=45, alpha=0.75)
            x, y, s = kf(EDP, f)
            mini(ctx, 'sarah', 'S', x, y, t, sh, sc=s, eyes='heart' if u > 0.4 else 'wide', brows=0.8, smile=1.0, blush=1.0,
                 look=(-1, -0.2), arms=('cheer', 'face') if u > 0.4 else ('face', 'face'), jump=30 * abs(math.sin(u * 5)) if u > 0.4 else 0,
                 face=-1, **SK)
            S.hearts_float(ctx, t, x, y - 300, n=6, seed=5, start=s3 + 0.4)
            badge(ctx, 'FLACON DORÉ', 330, 520, 74, GOLDC, fg=INK, scale=pop(t, s3 + wt('xs_s3', 'FLACON', 0.9)), rot=-0.05)
            kp = pop(t, s3 + wt('xs_s3', 'POINTS', 2.6))
            if kp > 0.01:
                text(ctx, '+100 POINTS', 360, 760, 100, fill=GREENC, scale=kp, rot=-0.1 + 0.03 * math.sin(t * 7))
            for i in range(5): sparkle(ctx, 560 + (i * 83) % 300, 700 + (i * 127) % 420, 28, t, ph=i)
            flash(ctx, u)
    elif t < d5:                                     # 7-8. prix, puis débat au spectateur
        if t < s4:
            u = t - d4
            footage(ctx, 'fl1', 0.6 + u * 0.3, 1.0, 1.06, 2, 540, 900)
            snow(ctx, t, n=40, alpha=0.7)
            mini(ctx, 'david', 'D', 200, 1070, t, sh, sc=0.4, hat=True, jump=40 * abs(math.sin(u * 6)), eyes='happy', brows=0.6, smile=1.0,
                 look=(1, 0), arms=('cheer', 'cheer'), **DK)
            mini(ctx, 'sarah', 'S', 800, 1070, t, sh, sc=0.4, eyes='heart', brows=0.6, smile=1.0, look=(-1, 0), arms=('hip', 'cheer'), face=-1, **SK)
            kp = pop(t, d4 + wt('xs_d4', 'MOINS', 0.6))
            if kp > 0.01: price_tag(ctx, SAFE_CX, 640, 0.8 * kp, t, 'MOINS DE 25 €', sub=None)
            flash(ctx, u)
        else:
            u = t - s4
            footage(ctx, 'nom', 1.5 + u * 0.6, 1.08, 1.12, 4, 560, 560, offset=60)
            ctx.save(); ctx.rectangle(0, 0, W / 2, H); ctx.set_source_rgba(*GREENC, 0.32); ctx.fill()
            ctx.rectangle(W / 2, 0, W / 2, H); ctx.set_source_rgba(*REDX, 0.32); ctx.fill(); ctx.restore()
            badge(ctx, 'PARFUM AU SECRET SANTA ?', SAFE_CX, 420, 62, (1, 1, 1), fg=INK, scale=pop(t, s4 + 0.05), rot=-0.02)
            kA = pop(t, s4 + wt('xs_s4', 'BONNE', 1.4)); kB = pop(t, s4 + wt('xs_s4', 'TROP', 2.0))
            choice_card(ctx, 'BONNE IDÉE', 250, 600, GREENC, kA, -0.06, t)
            choice_card(ctx, 'TROP PERSO', 710, 600, REDX, kB, 0.06, t)
            text(ctx, 'OU', SAFE_CX, 610, 90, fill=hexc('#ffd23f'), scale=pop(t, s4 + wt('xs_s4', 'OU', 1.8)), rot=0.08 * math.sin(t * 6))
            mini(ctx, 'sarah', 'S', SAFE_CX, 1070, t, sh, sc=0.42, eyes='open', brows=0.7, smile=1.0, look=(0, 0.7),
                 arms=('point_side', 'point_side') if kB > 0.5 else ('hip', 'chin'), face=-1, **SK)
            kc = pop(t, s4 + wt('xs_s4', 'DIS', 3.0))
            if kc > 0.01:
                comment_bubble(ctx, 790, 820, kc * 0.85, t)
            ban = False; cap_y = 1240
            flash(ctx, u)
    else:                                            # 9. appel à l'action
        v = t - d5
        footage(ctx, 'fl1', 1.0 + min(v, 0.9) * 0.4, 1.0, 1.0, 1)
        snow(ctx, t, n=45, alpha=0.7)
        mini(ctx, 'sarah', 'S', 800, 870, t, sh, sc=0.3, eyes='heart', brows=0.5, smile=1.0, look=(-1, 0.4), arms=('hip', 'wave'), face=-1, **SK)
        mini(ctx, 'david', 'D', 640, 870, t, sh, sc=0.32, hat=True, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
             look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1, **DK)
        price_tag(ctx, 330, 520, 0.62, t, 'MOINS DE 25 €', sub=None)
        ctx.restore(); L.banner(ctx, t, BAN, bg=GOLDC, fg=INK); L.cta(ctx, t, d5 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=GOLDC, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_ss():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.75); T = TL.T; d1, s1, d2, s2, d3, s3, d4, s4, d5 = (T[c] for c, _ in ORDER)
    slam = d3 - 0.55 + 0.18
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.08, 0.5), ('bells', 0.15, 0.35), ('pop', d1 + wt('xs_d1', 'VINGT', 1.8), 0.6),
           ('boing', d1 + wt('xs_d1', 'TU', 2.7) - 0.1, 0.5),
           ('whoosh', s1 - 0.03, 0.5), ('stamp', s1 + 0.35, 0.7), ('pop', s1 + wt('xs_s1', 'DOUZE', 2.5), 0.6),
           ('swipe', d2 - 0.03, 0.5), ('sparkle', d2 + 0.1, 0.4),
           ('whoosh', s2 - 0.03, 0.5), ('stamp', slam - 0.05, 0.9),
           ('drumroll', d3 + 0.02, 0.2), ('sparkle', d3 + wt('xs_d3', 'GOLD', 1.8), 0.35), ('pop', d3 + wt('xs_d3', 'LATTAFA', 2.2), 0.6),
           ('whoosh', s3 - 0.03, 0.5), ('heart', s3 + 0.4, 0.6), ('ding', s3 + wt('xs_s3', 'POINTS', 2.6), 0.6),
           ('swipe', d4 - 0.03, 0.6), ('coins', d4 + wt('xs_d4', 'MOINS', 0.6), 0.6),
           ('whoosh', s4 - 0.03, 0.5), ('pop', s4 + wt('xs_s4', 'BONNE', 1.4), 0.6), ('pop', s4 + wt('xs_s4', 'TROP', 2.0), 0.6),
           ('sparkle', s4 + wt('xs_s4', 'DIS', 3.0), 0.5),
           ('bells', d5 + 0.05, 0.4), ('ding', d5 + RCTA + 0.05, 0.7)]
    sh = Shot('secret_santa', TL.dur, draw_ss, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
