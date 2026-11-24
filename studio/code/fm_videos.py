# -*- coding: utf-8 -*-
"""Tondeuse Philips OneBlade 360 : « Movember, c'est fini dans six jours. Ta moustache, tu la rases quand ? »
   Mini Hamza refuse de raser sa moustache de novembre, Bernard (« un vieux balai » selon Inès).
   Il la taille et fait les contours avec le OneBlade (vraies images), et la garde. Prix, puis débat
   « après Movember : tu gardes la moustache ou tu rases tout ? »."""
import math, random
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, ease_out
from tb_videos import comment_bubble, zoom_about
from rasoir_videos import oneblade, coupon_note, LIME
import fm_data as FM

WORDS = {c: FM.words_for(c) for c in FM.CUTS}
for w in ('MOVEMBER,', 'SIX', 'JOURS.', 'MOUSTACHE,', 'QUAND ?', 'JAMAIS !', 'BERNARD.', 'BERNARD,', 'BALAI !', 'ONEBLADE',
          'TAILLE,', 'CONTOURS,', 'PROPRE !', '29,99 €', 'COUPONS', 'GARDES', 'TOUT ?', 'COMMENTAIRE.'):
    if w not in S.HL: S.HL = S.HL + (w,)
GREENC = hexc('#2fa84f'); REDX = hexc('#e8263d'); BROWN = hexc('#3a2316'); BROWN_L = hexc('#6b4429'); NAVY = hexc('#1d2b53')
BAN = "FIN DE MOVEMBER : J-6"
ORDER = [('xm_i1', 'I'), ('xm_h1', 'H'), ('xm_i2', 'I'), ('xm_h2', 'H'), ('xm_i3', 'I'), ('xm_h3', 'H'), ('xm_i4', 'I'), ('xm_h4', 'H')]
PAUSE = {'xm_h1': 0.02, 'xm_i2': 0.02, 'xm_h2': 0.03, 'xm_i3': 0.03, 'xm_h3': 0.03, 'xm_i4': 0.03, 'xm_h4': 0.05}
RCTA = 0.5
HK = dict(outfit='sweat'); IK = dict()

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

# ---------------------------------------------------------------- Bernard, la moustache
def stache(ctx, x, y, s, t, mess=1.0, wig=0.0):
    """moustache en guidon centrée sur (x, y) = sous le nez. mess 1 = Bernard en broussaille, 0 = taillée nette."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(wig * math.sin(t * 7))
    sd = 300 + boil_seed(t, 6)
    rnd = random.Random(11)
    span = 150 + 90 * mess; drop = 30 + 70 * mess; th = 34 + 26 * mess
    for sgn in (-1, 1):
        pts = [(0, -6), (sgn * span * 0.35, -th * 0.7), (sgn * span * 0.75, -th * 0.4), (sgn * span, drop * 0.2 - 10),
               (sgn * (span + 12), drop * 0.6 - 30 * (1 - mess)), (sgn * span * 0.85, drop * 0.5),
               (sgn * span * 0.45, th * 0.55), (0, th * 0.45)]
        ink_fill(ctx, lambda c, pts=pts: blob(c, pts, sd + sgn, 1.6 + 5 * mess), BROWN, lw=6)
        if mess > 0.05:      # mèches rebelles
            for i in range(9):
                bx = sgn * rnd.uniform(15, span * 0.95); by = rnd.uniform(-th * 0.4, th * 0.4)
                ang = rnd.uniform(-1.2, 1.2) + (0.5 if sgn > 0 else math.pi - 0.5)
                ln = rnd.uniform(30, 75) * mess
                ctx.new_path(); ctx.move_to(bx, by)
                ctx.curve_to(bx + math.cos(ang) * ln * 0.5, by + math.sin(ang) * ln * 0.5 + 10 * math.sin(t * 5 + i),
                             bx + math.cos(ang) * ln, by + math.sin(ang) * ln, bx + math.cos(ang) * ln * 1.1, by + math.sin(ang) * ln + 8)
                ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.set_line_cap(1); ctx.stroke()
        else:                # reflet brillant
            ctx.new_path(); ctx.move_to(sgn * span * 0.25, -th * 0.35); ctx.line_to(sgn * span * 0.6, -th * 0.25)
            ctx.set_source_rgba(1, 1, 1, 0.55); ctx.set_line_width(6); ctx.set_line_cap(1); ctx.stroke()
    ctx.restore()

def mini_stache(ctx, x, feet_y, sc, t, mess, jump=0.0, face=1, wig=0.0, scale=1.0):
    """pose la moustache sur la tête d'un mini personnage dessiné avec mini()"""
    hy = feet_y - 770 * sc - jump
    stache(ctx, x, hy + 62 * sc, 0.62 * sc * 2.2 * scale * (1 if face > 0 else 1), t, mess, wig)

def broom(ctx, x, y, s, t, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -12, -330, 24, 300, 10), hexc('#c28a4a'), lw=5)
    ink_fill(ctx, lambda c: rrect(c, -60, -50, 120, 34, 8), REDX, lw=5)
    ink_fill(ctx, lambda c: blob(c, [(-60, -20), (60, -20), (110, 130), (-110, 130)], 41 + boil_seed(t, 6), 2.5), hexc('#d9b24a'), lw=6)
    for i in range(9):
        ctx.new_path(); ctx.move_to(-50 + i * 12.5, -10); ctx.line_to(-100 + i * 25, 125)
        ctx.set_source_rgba(*INK, 0.6); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def calendar(ctx, x, y, s, t, k):
    if k <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s * k, s * k); ctx.rotate(0.06 + 0.03 * math.sin(t * 4))
    ink_fill(ctx, lambda c: rrect(c, -110, -120, 220, 240, 18), (1, 1, 1), lw=6)
    ink_fill(ctx, lambda c: rrect(c, -110, -120, 220, 70, 18), REDX, lw=6)
    text(ctx, 'NOVEMBRE', 0, -84, 40, fill=(1, 1, 1), stroke=None, shadow=False)
    text(ctx, '30', 0, 30, 120, fill=INK, stroke=None, shadow=False)
    ctx.restore()

def name_tag(ctx, x, y, k, t):
    if k <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.rotate(-0.08 + 0.04 * math.sin(t * 5))
    ink_fill(ctx, lambda c: rrect(c, -150, -55, 300, 110, 22), (1, 1, 1), lw=6)
    ink_fill(ctx, lambda c: rrect(c, -150, -55, 300, 36, 14), hexc('#2b6cd4'), lw=5)
    text(ctx, 'BONJOUR, JE SUIS', 0, -37, 24, fill=(1, 1, 1), stroke=None, shadow=False)
    text(ctx, 'BERNARD', 0, 18, 58, fill=INK, stroke=None, shadow=False)
    ctx.restore()

def lbl(ctx, txt, t, t0, y=470, bg=LIME, fg=INK, size=64, rot=-0.03):
    badge(ctx, txt, SAFE_CX, y, size, bg, fg=fg, scale=pop(t, t0), rot=rot)

def dark(ctx, a):
    ctx.set_source_rgba(0, 0, 0, a); ctx.paint()

# ---------------------------------------------------------------- dessin
def draw_fm(ctx, t, sh):
    TL = sh.tl; T = TL.T; i1, h1, i2, h2, i3, h3, i4, h4 = (T[c] for c, _ in ORDER)
    cap_y = 1200; ban = True
    ctx.save()
    if t < h1:                                       # 1. accroche : J-6, la moustache doit partir
        tq = i1 + wt('xm_i1', 'QUAND', 3.4)
        zq = ease_out((t - tq + 0.05) / 0.2)
        footage(ctx, 'r_kit', t * 0.7, 1.15, 1.25, h1, 560, 760)
        ctx.save(); zoom_about(ctx, 1 + 0.14 * zq, 640, 900)
        hx, hf = 640, 1110
        mini(ctx, 'hamza', 'H', hx, hf, t, sh, sc=0.44, eyes='wide' if zq > 0.5 else 'open', brows=0.9 if zq > 0.5 else 0.2,
             smile=-0.6 if zq > 0.5 else 0.6, look=(-1, 0), arms=('face', 'face') if zq > 0.5 else ('hip', 'chin'), face=-1, **HK)
        mini_stache(ctx, hx, hf, 0.44, t, 1.0, wig=0.08)
        if zq > 0.5: sweat(ctx, hx + 90, 640, t, 1.0)
        ctx.restore()
        mini(ctx, 'ines', 'I', 250, 1110, t, sh, sc=0.42, eyes='half', brows=0.5, smile=0.6, look=(1, -0.1),
             arms=('hip', 'point_side'), tilt=0.04 * math.sin(t * 3), **IK)
        calendar(ctx, 790, 560, 1.0, t, pop(t, i1 + wt('xm_i1', 'SIX', 1.4)))
        kj = pop(t, i1 + wt('xm_i1', 'SIX', 1.4) + 0.1)
        if kj > 0.01: text(ctx, 'J-6', 790, 745, 110, fill=hexc('#ffd23f'), scale=kj, rot=-0.08)
        if zq > 0.01: text(ctx, '?!', 760, 380 + 0, 120, fill=REDX, scale=zq, rot=0.1 * math.sin(t * 9))
        if t < 0.25: flash(ctx, t, 0.25)
    elif t < i2:                                     # 2. « Jamais ! Elle s'appelle Bernard. »
        u = t - h1
        footage(ctx, 'r_kit2', 0.3 + u * 0.4, 1.3, 1.4, i2 - h1, 600, 700)
        rays(ctx, 540, 760, t, hexc('#ffd23f'), alpha=0.1)
        hx, hf = 560, 1130
        mini(ctx, 'hamza', 'H', hx, hf, t, sh, sc=0.5, eyes='closed' if u > 0.7 else 'wide', brows=0.8, smile=1.0 if u > 0.7 else -0.2,
             look=(0, -0.3), arms=('face', 'face'), tilt=0.06 * math.sin(t * 4), blush=0.6, **HK)
        mini_stache(ctx, hx, hf, 0.5, t, 1.0, wig=0.05)
        S.hearts_float(ctx, t, hx, 520, n=6, seed=3, start=h1 + 0.6)
        if u < 0.6: shock_lines(ctx, hx, 720, t, 220)
        name_tag(ctx, SAFE_CX, 470, pop(t, h1 + wt('xm_h1', 'BERNARD', 1.4)), t)
        if u < 0.5: text(ctx, 'JAMAIS !', 300, 560, 110, fill=REDX, scale=pop(t, h1 + 0.02), rot=-0.12)
        flash(ctx, u)
    elif t < h2:                                     # 3. « un vieux balai »
        u = t - i2
        footage(ctx, 'r_kit', 1.6 + u * 0.3, 1.0, 1.05, h2 - i2, 540, 900)
        dark(ctx, 0.45)
        stache(ctx, 290, 720, 0.82, t, 1.0, wig=0.04)
        text(ctx, 'BERNARD', 290, 600, 60, fill=(1, 1, 1), scale=pop(t, i2 + 0.05), rot=-0.05)
        text(ctx, '=', 540, 720, 170, fill=(1, 1, 1), scale=pop(t, i2 + wt('xm_i2', 'RESSEMBLE', 0.3)))
        kb = pop(t, i2 + wt('xm_i2', 'VIEUX', 0.9) - 0.15)
        if kb > 0.01: broom(ctx, 720, 760, 0.95 * kb, t, rot=0.25 + 0.06 * math.sin(t * 6))
        mini(ctx, 'ines', 'I', 230, 1180, t, sh, sc=0.34, eyes='half', brows=-0.4, smile=0.8, look=(1, -0.4), arms=('lips', 'point_side'), **IK)
        mini(ctx, 'hamza', 'H', 760, 1180, t, sh, sc=0.32, eyes='wide', brows=-0.9, smile=-0.8, look=(-1, -0.3), arms=('hip', 'hip'), face=-1, **HK)
        mini_stache(ctx, 760, 1180, 0.32, t, 1.0)
        vein(ctx, 800, 870, t, 0.8)
        cap_y = 1000 if False else 1220
        flash(ctx, u)
    elif t < i3:                                     # 4. il prend le OneBlade : taille, contours, il garde Bernard
        u = t - h2
        tt = h2 + wt('xm_h2', 'TAILLE', 1.5) - 0.15
        tc = h2 + wt('xm_h2', 'CONTOURS', 2.4) - 0.15
        tg = h2 + wt('xm_h2', 'GARDE', 3.4) - 0.15
        if t < tt:
            footage(ctx, 'r_prise', 1.4 + u * 0.9, 1.0, 1.08, tt - h2, 540, 900)
            lbl(ctx, 'PHILIPS ONEBLADE 360', t, h2 + wt('xm_h2', 'PHILIPS', 0.3), y=440)
            mini(ctx, 'hamza', 'H', 760, 1150, t, sh, sc=0.3, eyes='open', brows=0.5, smile=0.8, look=(-1, -0.3),
                 arms=('point_side', 'hip'), face=-1, **HK)
            mini_stache(ctx, 760, 1150, 0.3, t, 1.0)
            flash(ctx, u)
        elif t < tc:
            v = t - tt
            footage(ctx, 'r_rase', 0.3 + v * 1.4, 1.1, 1.22, tc - tt, 480, 820)
            lbl(ctx, 'JE TAILLE', t, tt + 0.05, y=450)
            flash(ctx, v)
        elif t < tg:
            v = t - tc
            footage(ctx, 'r_rase2', 0.4 + v * 1.3, 1.05, 1.15, tg - tc, 480, 860)
            lbl(ctx, 'JE FAIS LES CONTOURS', t, tc + 0.05, y=450, bg=(1, 1, 1))
            flash(ctx, v)
        else:
            v = t - tg
            footage(ctx, 'r_kit2', 1.2 + v * 0.4, 1.25, 1.3, i3 - tg, 600, 700)
            rays(ctx, 540, 720, t, LIME, alpha=0.2)
            hx, hf = 560, 1120
            mini(ctx, 'hamza', 'H', hx, hf, t, sh, sc=0.48, eyes='happy', brows=0.6, smile=1.0, look=(0, 0), arms=('cheer', 'hip'),
                 jump=20 * abs(math.sin(v * 6)), **HK)
            mini_stache(ctx, hx, hf, 0.48, t, 0.0, jump=20 * abs(math.sin(v * 6)))
            for k in range(5): sparkle(ctx, 380 + k * 85, 520 + 30 * math.sin(k), 26, t, ph=k)
            lbl(ctx, 'BERNARD, VERSION PROPRE', t, tg + 0.1, y=440, bg=hexc('#ffd23f'))
            flash(ctx, v)
    elif t < h3:                                     # 5. « Ah ! Là, il est propre ! »
        u = t - i3
        footage(ctx, 'r_lisse2', 0.2 + u * 0.6, 1.0, 1.06, h3 - i3, 540, 760)
        dark(ctx, 0.2)
        mini(ctx, 'ines', 'I', 260, 1150, t, sh, sc=0.4, eyes='heart' if u > 0.4 else 'wide', brows=0.8, smile=1.0, blush=1.0,
             look=(1, -0.2), arms=('cheer', 'face') if u > 0.4 else ('face', 'face'), jump=24 * abs(math.sin(u * 5)) if u > 0.4 else 0, **IK)
        mini(ctx, 'hamza', 'H', 700, 1150, t, sh, sc=0.42, eyes='wink' if u > 0.8 else 'open', brows=0.6, smile=1.0,
             look=(-1, 0), arms=('chin', 'hip'), face=-1, **HK)
        mini_stache(ctx, 700, 1150, 0.42, t, 0.0)
        S.hearts_float(ctx, t, 260, 760, n=5, seed=7, start=i3 + 0.4)
        lbl(ctx, 'PROPRE !', t, i3 + wt('xm_i3', 'PROPRE', 1.1), y=470, bg=GREENC, fg=(1, 1, 1), size=80)
        for k in range(5): sparkle(ctx, 600 + (k * 71) % 220, 640 + (k * 97) % 200, 26, t, ph=k)
        flash(ctx, u)
    elif t < i4:                                     # 6. prix
        u = t - h3
        footage(ctx, 'r_kit2', 0.6 + u * 0.3, 1.0, 1.06, i4 - h3, 540, 900)
        dark(ctx, 0.25)
        k1 = pop(t, h3 + wt('xm_h3', '50', 0.5))
        if k1 > 0.01:
            price_tag(ctx, 300, 560, 0.6 * k1, t, '50,99 €', sub=None, col=(1, 1, 1))
            ks = ease_out((t - (h3 + wt('xm_h3', '29', 1.6))) / 0.25)
            if ks > 0:
                ctx.new_path(); ctx.move_to(200, 600); ctx.line_to(200 + 210 * ks, 520)
                ctx.set_source_rgb(*REDX); ctx.set_line_width(12); ctx.set_line_cap(1); ctx.stroke()
        k2 = pop(t, h3 + wt('xm_h3', '29', 1.6))
        if k2 > 0.01:
            price_tag(ctx, 620, 760, 0.85 * k2, t, '29,99 €', sub='AVEC LES COUPONS')
        mini(ctx, 'hamza', 'H', 200, 990, t, sh, sc=0.3, eyes='happy', brows=0.6, smile=1.0, look=(1, -0.4), arms=('point_side', 'hip'), **HK)
        mini_stache(ctx, 200, 990, 0.3, t, 0.0)
        coupon_note(ctx, y=1060)
        cap_y = 1220
        flash(ctx, u)
    elif t < h4:                                     # 7. débat au spectateur
        u = t - i4
        footage(ctx, 'r_kit', 2.0 + u * 0.5, 1.08, 1.12, h4 - i4, 560, 700)
        ctx.save(); ctx.rectangle(0, 0, W / 2, H); ctx.set_source_rgba(*GREENC, 0.32); ctx.fill()
        ctx.rectangle(W / 2, 0, W / 2, H); ctx.set_source_rgba(*REDX, 0.32); ctx.fill(); ctx.restore()
        badge(ctx, 'APRÈS MOVEMBER ?', SAFE_CX, 420, 66, (1, 1, 1), fg=INK, scale=pop(t, i4 + 0.05), rot=-0.02)
        kA = pop(t, i4 + wt('xm_i4', 'GARDES', 1.0)); kB = pop(t, i4 + wt('xm_i4', 'RASES', 1.7))
        badge(ctx, 'JE GARDE', 250, 590, 66, GREENC, fg=(1, 1, 1), scale=kA, rot=-0.06)
        badge(ctx, 'JE RASE TOUT', 700, 590, 66, REDX, fg=(1, 1, 1), scale=kB, rot=0.06)
        if kA > 0.01: stache(ctx, 250, 740, 0.7 * kA, t, 0.0)
        if kB > 0.01: oneblade(ctx, 700, 800, 0.55 * kB, t, rot=0.4, buzz=True)
        mini(ctx, 'ines', 'I', SAFE_CX, 1110, t, sh, sc=0.4, eyes='open', brows=0.7, smile=1.0, look=(0, 0.7),
             arms=('point_side', 'point_side') if kB > 0.5 else ('hip', 'chin'), **IK)
        comment_bubble(ctx, 800, 940, 0.8 * pop(t, i4 + wt('xm_i4', 'DIS', 2.9)), t)
        ban = False; cap_y = 1250
        flash(ctx, u)
    else:                                            # 8. appel à l'action
        v = t - h4
        footage(ctx, 'r_kit2', 1.0 + min(v, 0.9) * 0.4, 1.0, 1.0, 1)
        mini(ctx, 'ines', 'I', 800, 820, t, sh, sc=0.3, eyes='heart', brows=0.5, smile=1.0, look=(-1, 0.4), arms=('hip', 'wave'), face=-1, **IK)
        mini(ctx, 'hamza', 'H', 640, 820, t, sh, sc=0.32, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
             look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1, **HK)
        mini_stache(ctx, 640, 820, 0.32, t, 0.0)
        price_tag(ctx, 300, 520, 0.6, t, '29,99 €', sub='AVEC LES COUPONS')
        coupon_note(ctx, y=1065)
        ctx.restore(); L.banner(ctx, t, BAN, bg=hexc('#ffd23f'), fg=INK); L.cta(ctx, t, h4 + RCTA); TL.captions(ctx, t, 925); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=hexc('#ffd23f'), fg=INK)
    TL.captions(ctx, t, cap_y)

def build_fm():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.45); T = TL.T; i1, h1, i2, h2, i3, h3, i4, h4 = (T[c] for c, _ in ORDER)
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.08, 0.5), ('pop', i1 + wt('xm_i1', 'SIX', 1.4), 0.6), ('boing', i1 + wt('xm_i1', 'QUAND', 3.4) - 0.05, 0.6),
           ('heart', h1 + 0.6, 0.5), ('ding', h1 + wt('xm_h1', 'BERNARD', 1.4), 0.6),
           ('whoosh', i2 - 0.03, 0.5), ('wah', i2 + wt('xm_i2', 'VIEUX', 0.9), 0.4),
           ('swipe', h2 - 0.03, 0.5), ('buzz', h2 + wt('xm_h2', 'TAILLE', 1.5) - 0.1, 0.35), ('buzz', h2 + wt('xm_h2', 'CONTOURS', 2.4) - 0.1, 0.35),
           ('sparkle', h2 + wt('xm_h2', 'GARDE', 3.4) - 0.1, 0.5),
           ('whoosh', i3 - 0.03, 0.5), ('heart', i3 + 0.4, 0.6), ('ding', i3 + wt('xm_i3', 'PROPRE', 1.1), 0.6),
           ('swipe', h3 - 0.03, 0.5), ('pop', h3 + wt('xm_h3', '50', 0.5), 0.5), ('coins', h3 + wt('xm_h3', '29', 1.6), 0.6),
           ('whoosh', i4 - 0.03, 0.5), ('pop', i4 + wt('xm_i4', 'GARDES', 1.0), 0.6), ('pop', i4 + wt('xm_i4', 'RASES', 1.7), 0.6),
           ('sparkle', i4 + wt('xm_i4', 'COMMENTAIRE', 3.3) + 0.3, 0.35),
           ('swipe', h4 - 0.03, 0.4), ('ding', h4 + RCTA + 0.05, 0.7)]
    sh = Shot('fin_movember', TL.dur, draw_fm, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
