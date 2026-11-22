# -*- coding: utf-8 -*-
"""Tondeuse Philips OneBlade 360, saison 2 (réalité mixte sur les vraies images) :
   1) faux documentaire animalier : les poils fuient le prédateur
   2) Gérard, la barbe de Hamza, qui supplie qu'on n'achète pas le rasoir"""
import math, random
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from rasoir_videos import fiche_band, coupon_note, phone_ar
import rf_data as RF

WORDS = {c: RF.words_for(c) for c in RF.CUTS}
for w in ('ONEBLADE', '360.', 'PHILIPS', '29,99 €', '50,99 €', '50,99 €.', 'TAILLE,', 'CONTOURS,', 'RASE,', 'ÉTANCHE.', 'GÉRARD,', 'KEVIN,'):
    if w not in S.HL: S.HL = S.HL + (w,)
LIME = hexc('#c6e21b'); BLUE = hexc('#0b5ed7'); REDX = hexc('#e8263d'); HAIR = hexc('#1c1410'); BEARD = hexc('#5a3a28')

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def eo(u): return 1 - (1 - max(0.0, min(1.0, u))) ** 3

# ---------------------------------------------------------------- personnages
def poil(ctx, x, y, s, t, ph=0.0, scared=1.0, mouth=0.0, run=0.0, face=1, tag=None, snorkel=False, flag=False, eyes='wide'):
    """petit poil vivant : une mèche noire bouclée avec des yeux, des bras et des jambes"""
    sd = boil_seed(t) + int(ph * 100); s *= 1.9
    ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s)
    sw = math.sin(t * 18 + ph) * 0.6 * run
    for side, a in ((-1, sw), (1, -sw)):                       # jambes
        ctx.save(); ctx.translate(side * 14, 40); ctx.rotate(a)
        ctx.new_path(); ctx.move_to(0, 0); ctx.line_to(0, 46); ctx.line_to(14, 50)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(17); ctx.stroke_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(9); ctx.stroke(); ctx.restore()
    wob = math.sin(t * 9 + ph) * 8
    pts = []
    for i in range(24):                                          # corps : mèche en S
        u = i / 23; yy = 50 - u * 190; xx = 18 * math.sin(u * 5 + ph) + wob * u
        pts.append((xx, yy))
    ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(76); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(62); ctx.stroke_preserve()
    ctx.set_source_rgb(*HAIR); ctx.set_line_width(48); ctx.stroke()
    ctx.new_path(); ctx.move_to(pts[-1][0], pts[-1][1]); ctx.curve_to(pts[-1][0] + 40, pts[-1][1] - 40, pts[-1][0] + 70, pts[-1][1] + 10, pts[-1][0] + 50, pts[-1][1] + 30)
    ctx.set_source_rgb(*HAIR); ctx.set_line_width(22); ctx.stroke()
    # bras
    arm = -1.9 if scared > 0.5 else -0.6
    for side in (-1, 1):
        ctx.save(); ctx.translate(side * 26, -40); ctx.rotate(side * (arm + 0.3 * math.sin(t * 20 + ph) * scared))
        ctx.new_path(); ctx.move_to(0, 0); ctx.line_to(0, 46)
        ctx.set_source_rgb(*INK); ctx.set_line_width(9); ctx.stroke(); ctx.restore()
    if flag:
        ctx.new_path(); ctx.move_to(30, -70); ctx.line_to(30, -230); ctx.set_source_rgb(*hexc('#8a6a40')); ctx.set_line_width(8); ctx.stroke()
        ink_fill(ctx, lambda c: blob(c, [(32, -228), (130, -215 + 8 * math.sin(t * 6)), (130, -160), (32, -168)], sd, 0.5), (1, 1, 1), lw=4)
    # yeux
    ey = -95
    for ex in (-15, 17):
        r = 15 if eyes == 'wide' else 11
        ctx.new_path(); ctx.arc(ex, ey, r, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(3.5); ctx.stroke()
        if eyes == 'closed':
            ctx.new_path(); ctx.move_to(ex - 10, ey); ctx.line_to(ex + 10, ey); ctx.set_line_width(4); ctx.stroke()
        else:
            ctx.new_path(); ctx.arc(ex + 3, ey + 2, 5 if eyes == 'wide' else 6, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    if snorkel:
        ctx.new_path(); rrect(ctx, -34, ey - 22, 70, 44, 14); ctx.set_source_rgba(0.6, 0.9, 1, 0.45); ctx.fill_preserve()
        ctx.set_source_rgb(*hexc('#ff6a13')); ctx.set_line_width(6); ctx.stroke()
        ctx.new_path(); ctx.move_to(36, ey); ctx.line_to(48, ey); ctx.line_to(48, ey - 80)
        ctx.set_source_rgb(*hexc('#ffd23f')); ctx.set_line_width(9); ctx.stroke()
    # bouche
    mo = max(mouth, 0.25 * scared)
    ctx.new_path(); ctx.save(); ctx.translate(2, -60); ctx.scale(1, 0.3 + 1.1 * mo); ctx.arc(0, 0, 11, 0, 7); ctx.restore()
    ctx.set_source_rgb(*hexc('#7a1020')); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    if tag:
        badge(ctx, tag, x, y - 230 * s, 34, (1, 1, 1), fg=INK, rot=-0.06)

def gerard(ctx, x, y, s, t, mouth=0.0, brows=0.0, eyes='open', run=0.0, arms='down', face=1, sq=0.0, tears=False, rot=0.0):
    """Gérard, la barbe vivante de Hamza : touffe brune en forme de barbe, yeux, sourcils, petites jambes"""
    sd = boil_seed(t) + 900; s *= 1.6
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * face * (1 + sq * 0.5), s * (1 - sq * 0.5))
    # ombre
    ctx.save(); ctx.scale(1.4, 0.25); ctx.new_path(); ctx.arc(0, 1290, 110, 0, 7); ctx.set_source_rgba(0, 0, 0, 0.4); ctx.fill(); ctx.restore()
    sw = math.sin(t * 16) * 0.7 * run
    for side, a in ((-1, sw), (1, -sw)):
        ctx.save(); ctx.translate(side * 60, 150); ctx.rotate(a)
        ink_fill(ctx, lambda c: rrect(c, -20, 0, 40, 150, 16), hexc('#8a5a3a'), lw=6)
        ink_fill(ctx, lambda c: blob(c, [(-30, 140), (56, 140), (66, 176), (-30, 176)], 2, 0.5), (1, 1, 1), lw=6)
        ctx.restore()
    # corps : barbe en U avec un trou pour la bouche, bord en touffes
    pts = []
    for i in range(36):
        a = math.pi * 1.08 + i / 35 * math.pi * 0.84 * -1 + math.pi * 0.0
    outline = []
    for i in range(40):
        a = -0.15 * math.pi + i / 39 * 1.3 * math.pi           # du haut droit vers le haut gauche par le bas
        r = 210 + 18 * math.sin(i * 2.3 + t * 3)
        outline.append((r * math.cos(a) * 1.05, -10 + r * math.sin(a) * 1.0))
    top = [(-180, -120), (-120, -150), (-40, -120), (40, -120), (120, -150), (180, -120)]
    poly = outline + top
    ink_fill(ctx, lambda c: blob(c, poly, sd, 1.2), BEARD, lw=8, shade=lambda c: c.rectangle(-240, 40, 480, 200), seed=sd)
    for k in range(14):                                          # mèches
        a = 0.1 * math.pi + k / 13 * 0.8 * math.pi; r0 = 120; r1 = 190
        ctx.new_path(); ctx.move_to(r0 * math.cos(a), r0 * math.sin(a)); ctx.line_to(r1 * math.cos(a + 0.05), r1 * math.sin(a + 0.05))
        ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(4); ctx.stroke()
    # bras
    poses = {'down': (0.3, 0.3), 'up': (-2.4, -2.4), 'point': (0.3, -1.4), 'beg': (-1.2, -1.2), 'wave': (0.3, -2.6 + 0.4 * math.sin(t * 10)), 'face': (-2.7, -2.7)}
    al, ar = poses.get(arms, poses['down'])
    for side, a in ((-1, al), (1, ar)):
        ctx.save(); ctx.translate(side * 195, 20); ctx.rotate(-side * a)
        ink_fill(ctx, lambda c: rrect(c, -15, -10, 30, 135, 14), hexc('#8a5a3a'), lw=5)
        ink_fill(ctx, lambda c: c.arc(0, 130, 24, 0, 7), (1, 1, 1), lw=5)
        ctx.restore()
    # yeux (sur le haut de la barbe, côté joues)
    for ex in (-95, 95):
        ctx.new_path(); ctx.arc(ex, -40, 42, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
        if eyes == 'closed':
            ctx.new_path(); ctx.arc(ex, -40, 26, 0.2, math.pi - 0.2); ctx.set_line_width(7); ctx.stroke()
        else:
            r = 10 if eyes == 'tiny' else 17
            ctx.new_path(); ctx.arc(ex + 6, -34, r, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
        # sourcils (brows > 0 : affolé ; < 0 : furieux)
        ctx.new_path(); d = 1 if ex < 0 else -1
        ctx.move_to(ex - 40, -100 - 20 * brows * d); ctx.line_to(ex + 40, -100 + 20 * brows * d)
        ctx.set_source_rgb(*INK); ctx.set_line_width(16); ctx.stroke()
    if tears:
        for ex in (-95, 95):
            k = (t * 2.2 + (0.5 if ex > 0 else 0)) % 1.0
            ink_fill(ctx, lambda c, ex=ex, k=k: blob(c, ellipse_pts(ex + 20, 10 + k * 200, 12, 18, 8), 3, 0.3), (0.55, 0.85, 1), lw=3)
    # bouche (trou de la barbe)
    mo = 0.15 + 0.85 * mouth
    ctx.save(); ctx.translate(0, 70); ctx.scale(1, 0.25 + 0.9 * mo)
    ink_fill(ctx, lambda c: c.arc(0, 0, 58, 0, 7), hexc('#6b0f1a'), lw=7)
    ctx.restore()
    ctx.restore()

# ---------------------------------------------------------------- habillage documentaire
def binoculars(ctx, k=1.0):
    """masque de jumelles (deux cercles) : look « on observe l'animal »"""
    if k <= 0: return
    r = 330 + (1 - k) * 800
    ctx.save()
    ctx.push_group()
    ctx.set_source_rgba(0, 0, 0, 0.92 * k); ctx.paint()
    ctx.set_operator(cairo.OPERATOR_CLEAR)
    for cx in (SAFE_CX + 40 - 230, SAFE_CX + 40 + 230):
        ctx.new_path(); ctx.arc(cx, 880, r, 0, 7); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint(); ctx.restore()

def lower_third(ctx, t, t0, title, sub, y=1280):
    k = eo((t - t0) / 0.35)
    if k <= 0: return
    x0 = 70 - (1 - k) * 900
    ctx.save()
    ink_fill(ctx, lambda c: c.rectangle(x0, y - 60, 760, 82), hexc('#ffd23f'), lw=5)
    ink_fill(ctx, lambda c: c.rectangle(x0, y + 22, 640, 56), (1, 1, 1), lw=5)
    text(ctx, title, x0 + 22, y - 18, 64, fill=INK, stroke=None, shadow=False, align='left')
    text(ctx, sub, x0 + 22, y + 50, 38, font='Patrick Hand', fill=INK, stroke=None, shadow=False, align='left')
    ctx.restore()

def underwater(ctx, t):
    ctx.save(); ctx.set_source_rgba(0.1, 0.45, 0.85, 0.32); ctx.paint(); ctx.restore()
    rnd = random.Random(5)
    for i in range(22):
        x0 = rnd.uniform(40, 1040); sp = rnd.uniform(120, 260); r = rnd.uniform(8, 22); ph = rnd.uniform(0, 50)
        y = H - ((t * sp + ph * 40) % (H + 60)); x = x0 + 18 * math.sin(t * 2 + ph)
        ctx.new_path(); ctx.arc(x, y, r, 0, 7); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(3); ctx.stroke()
    for i in range(5):                                           # reflets ondulants
        ctx.new_path()
        for k in range(30):
            xx = k * 40; yy = 240 + i * 60 + 14 * math.sin(k * 0.6 + t * 3 + i)
            (ctx.move_to if k == 0 else ctx.line_to)(xx, yy)
        ctx.set_source_rgba(1, 1, 1, 0.12); ctx.set_line_width(10); ctx.stroke()

def red_circle(ctx, x, y, rx, ry, k, t):
    if k <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry); ctx.new_path(); ctx.arc(-math.pi / 2, 0, 1, 0, 0)
    ctx.restore()
    ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry)
    ctx.new_path(); ctx.arc(0, 0, 1, -math.pi / 2, -math.pi / 2 + 2 * math.pi * min(1, k)); ctx.restore()
    ctx.set_source_rgb(*REDX); ctx.set_line_width(12); ctx.stroke()

# ---------------------------------------------------------------- 1. DOCUMENTAIRE
BAN_DOC = "LES POILS SONT EN DANGER !"
ORDER_DOC = [('xq_1', 'P'), ('xn_1', 'N'), ('xn_2', 'N'), ('xn_3', 'N'), ('xn_4', 'N'), ('xq_2', 'P'), ('xn_6', 'N'), ('xq_3', 'P'),
             ('xn_9', 'N'), ('xq_4', 'P'), ('xn_10', 'N'), ('xn_11', 'N')]
PAUSE_DOC = {'xn_1': 0.1, 'xn_2': 0.15, 'xn_3': 0.05, 'xn_4': 0.1, 'xq_2': 0.0, 'xn_6': 0.1, 'xq_3': 0.0, 'xn_9': 0.1, 'xq_4': 0.0,
             'xn_10': 0.15, 'xn_11': 0.15}
RCTA = 0.9

def draw_doc(ctx, t, sh):
    TL = sh.tl; T = TL.T
    q1, n1, n2, n3, n4, q2, n6, q3, n9, q4, n10, n11 = (T[c] for c, _ in ORDER_DOC)
    cap_y = 1180; ban = True
    mq = lambda: sh.mouth('P', t)
    ctx.save()
    if t < n2:                                   # les poils fuient le rasoir sur le cou ; « Chut… »
        frozen = t >= n1
        footage(ctx, 'r_rase', min(t, n1) * 0.9 + (t - n1) * 0.15 * frozen, 1.0, 1.0, 1)
        for i, (bx, by, ph) in enumerate(((200, 1180, 0.0), (390, 1260, 1.3), (110, 1330, 2.1), (520, 1150, 3.3))):
            run = 0.0 if frozen else 1.0
            dx = 0 if frozen else -60 * ((t * 1.3 + i * 0.3) % 1.0)
            jitter = 0 if frozen else 6 * math.sin(t * 30 + i)
            poil(ctx, bx + dx + jitter, by, 0.85 if i else 1.0, t, ph=ph, scared=0.0 if frozen else 1.0, mouth=mq() if not frozen else 0.0,
                 run=run, face=-1, eyes='wide', tag='KEVIN' if i == 0 else None)
        if not frozen:
            shock_lines(ctx, 260, 1050, t, 170)
            text(ctx, 'AAAH !', 330, 560, 110, fill=REDX, scale=pop(t, 0.05), rot=0.1)
            cap_y = 760
        else:
            ctx.set_source_rgba(0, 0, 0, 0.25 * eo((t - n1) / 0.3)); ctx.paint()
            lower_third(ctx, t, n1 + 0.4, 'DOCUMENTAIRE', 'Épisode 1 : le prédateur des poils', y=470)
            cap_y = 760
    elif t < n4:                                 # la tanière, observée aux jumelles, puis présentation de l'espèce
        u = t - n2
        footage(ctx, 'r_kit', u * 0.35, 1.05, 1.15, n4 - n2, 420, 900)
        for i, (bx, by, ph) in enumerate(((820, 560, 0.5), (900, 700, 1.7))):
            peek = 18 * math.sin(t * 4 + i)
            poil(ctx, bx, by + peek, 0.55, t, ph=ph, scared=0.6, run=0, face=-1, eyes='wide')
        kb = 1.0 if t < n3 else max(0, 1 - (t - n3) / 0.4)
        binoculars(ctx, kb * eo(u / 0.5))
        if t >= n3:
            red_circle(ctx, 450, 960, 170, 470, (t - n3) / 0.5, t)
            lower_third(ctx, t, n3 + 0.05, 'PHILIPS ONEBLADE 360', 'Rasorus terribilis', y=1330)
            cap_y = 1150
        else:
            text(ctx, 'LA TANIÈRE', SAFE_CX, 470, 90, fill=(1, 1, 1), scale=pop(t, n2 + wt('xn_2', 'SALLE', 1.0)), rot=-0.03)
            cap_y = 1250
    elif t < n6:                                 # il sort de sa tanière : la main le prend ; « Cours, Kevin, cours ! »
        u = t - n4
        footage(ctx, 'r_prise', u * 0.8, 1.0, 1.0, 1)
        if t < q2:
            for i, (bx, by, ph) in enumerate(((830, 980, 0.3), (960, 1080, 1.1))):
                poil(ctx, bx, by, 0.6, t, ph=ph, scared=1.0, run=0, face=-1, eyes='wide')
            text(ctx, 'IL SORT !', 780, 560, 96, fill=(1, 1, 1), scale=pop(t, n4 + 0.6), rot=0.06)
        else:
            v = t - q2
            for i, (bx, by, ph, sp) in enumerate(((830, 980, 0.3, 520), (960, 1080, 1.1, 380), (700, 900, 2.4, 140))):
                x = bx + sp * v * (1 if i < 2 else 0.0) if i < 2 else 760 + 90 * v
                speed_lines(ctx, t, x - 120, by - 80, alpha=0.18)
                poil(ctx, x, by, 0.6, t, ph=ph, scared=1.0, mouth=mq(), run=1.0, face=1, eyes='wide', tag='KEVIN' if i == 2 else None)
        cap_y = 1300
    elif t < n9:                                 # ses trois façons de chasser ; un poil se fait éjecter
        u = t - n6
        footage(ctx, 'r_rase2', u * 0.7, 1.0, 1.05, n9 - n6, 480, 900)
        for i, (lab, pre) in enumerate((('IL TAILLE', 'TAILLE'), ('IL FAIT LES CONTOURS', 'CONTOURS'), ('IL RASE', 'RASE'))):
            k = pop(t, n6 + wt('xn_6', pre, 0.4 + i))
            badge(ctx, lab, SAFE_CX, 450 + i * 120, 66, LIME if i != 1 else hexc('#141414'), fg=INK if i != 1 else LIME, scale=k, rot=(-0.04, 0.03, -0.02)[i])
            L.check(ctx, SAFE_CX + 300, 450 + i * 120, 0.75, k)
        if t < q3:
            poil(ctx, 190, 950, 0.7, t, ph=0.7, scared=1.0, run=0.6, face=-1, eyes='wide')
        else:
            v = t - q3
            poil(ctx, 190 + 700 * v, 950 - 900 * v + 900 * v * v, 0.7, t, ph=0.7, scared=1.0, mouth=mq(), run=0, face=-1, eyes='wide')
            if v < 0.3: text(ctx, 'ZZZT !', 330, 800, 100, fill=LIME, scale=pop(t, q3), rot=-0.1)
        cap_y = 1180
    elif t < n10:                                # il chasse même sous l'eau
        u = t - n9
        footage(ctx, 'r_lisse', u * 0.6, 1.0, 1.0, 1)
        underwater(ctx, t)
        badge(ctx, 'ÉTANCHE', SAFE_CX + 120, 400, 92, BLUE, fg=(1, 1, 1), scale=pop(t, n9 + wt('xn_9', 'ÉTANCHE', 2.2)), rot=-0.04)
        for i, (bx, by, ph) in enumerate(((200, 860, 0.2), (420, 960, 1.5))):
            bob = 20 * math.sin(t * 2.5 + i)
            poil(ctx, bx, by + bob, 0.75, t, ph=ph, scared=1.0 if t >= q4 else 0.6, mouth=mq() if t >= q4 else 0.0, run=0.3, face=-1,
                 eyes='wide', snorkel=True)
        cap_y = 1180
    elif t < n11:                                # le prix sur la fiche, les poils s'évanouissent
        u = t - n10
        footage(ctx, 'r_kit2', 0.5 + u * 0.3, 1.0, 1.0, 1)
        ctx.set_source_rgba(0, 0, 0, 0.35); ctx.paint()
        r29 = wt('xn_10', '29', 3.0)
        fiche_band(ctx, t, n10 + 0.05, cy=780, circle_t=n10 + r29)
        if t >= n10 + r29:
            coupon_note(ctx, 1040)
            for i, (bx, ph) in enumerate(((330, 0.4), (760, 1.9))):
                fall = eo((t - n10 - r29) / 0.4)
                ctx.save(); ctx.translate(bx, 1400); ctx.rotate(fall * 1.45 * (1 if i else -1)); ctx.translate(-bx, -1290)
                poil(ctx, bx, 1290, 0.6, t, ph=ph, scared=0.0, run=0, face=1, eyes='closed')
                ctx.restore()
            text(ctx, 'PAF', 760, 1300, 70, fill=(1, 1, 1), scale=pop(t, n10 + r29 + 0.35), rot=0.1)
        cap_y = 1180
    else:                                        # appel à l'action : Kevin agite le drapeau blanc
        u = t - n11
        footage(ctx, 'r_kit2', 2.0 + min(u, 1.0) * 0.3, 1.0, 1.0, 1)
        poil(ctx, 900, 1230, 0.72, t, ph=1.0, scared=0.3, run=0, face=-1, eyes='wide', flag=True, tag='KEVIN')
        lower_third(ctx, t, n11 + 0.1, 'FIN DE L\'ÉPISODE', 'Les poils ont perdu.', y=640)
        ctx.restore(); L.banner(ctx, t, BAN_DOC, bg=LIME, fg=INK); L.cta(ctx, t, n11 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN_DOC, bg=LIME, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_doc():
    TL = L.Timeline(ORDER_DOC, PAUSE_DOC, WORDS, start=0.05); T = TL.T
    q1, n1, n2, n3, n4, q2, n6, q3, n9, q4, n10, n11 = (T[c] for c, _ in ORDER_DOC)
    r29 = wt('xn_10', '29', 3.0)
    sfx = [('buzz', 0.0, 0.5), ('pop', 0.05, 0.5), ('scratch', n1 - 0.05, 0.7), ('whoosh', n2 - 0.03, 0.4), ('pop', n2 + wt('xn_2', 'SALLE', 1.0), 0.4),
           ('stamp', n3 + 0.05, 0.6), ('whoosh', n4 - 0.03, 0.5), ('buzz', n4 + 0.5, 0.35), ('whoosh', q2, 0.6),
           ('whoosh', n6 - 0.03, 0.5), ('ding', n6 + wt('xn_6', 'TAILLE', 0.4), 0.5), ('ding', n6 + wt('xn_6', 'CONTOURS', 1.5), 0.5),
           ('ding', n6 + wt('xn_6', 'RASE', 2.8), 0.5), ('buzz', q3 - 0.1, 0.6), ('boing', q3 + 0.15, 0.6),
           ('whoosh', n9 - 0.03, 0.5), ('pop', n9 + wt('xn_9', 'ÉTANCHE', 2.2), 0.6),
           ('whoosh', n10 - 0.03, 0.5), ('coins', n10 + r29, 0.6), ('boing', n10 + r29 + 0.35, 0.5),
           ('whoosh', n11 - 0.03, 0.4), ('ding', n11 + RCTA + 0.05, 0.7)]
    sh = Shot('doc', TL.dur, draw_doc, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None

# ---------------------------------------------------------------- 2. GÉRARD LA BARBE
BAN_G = "SA BARBE NE VEUT PAS QUE TU L'ACHÈTES"
ORDER_G = [('xb_%d' % i, 'B') for i in range(1, 10)]
PAUSE_G = {'xb_2': 0.2, 'xb_3': 0.05, 'xb_4': 0.1, 'xb_5': 0.1, 'xb_6': 0.0, 'xb_7': 0.15, 'xb_8': 0.15, 'xb_9': 0.05}
AR_G = [(0.0, 'viking', 'VIKING'), (0.8, 'moustache', 'MOUSTACHE'), (1.6, 'goatee', 'BOUC'), (2.4, 'stubble', 'BARBE DE 3 JOURS')]

def draw_g(ctx, t, sh):
    TL = sh.tl; T = TL.T; b = [T['xb_%d' % i] for i in range(1, 10)]
    mo = sh.mouth('B', t)
    cap_y = 1180; ban = True
    ctx.save()
    if t < b[1]:                                 # Gérard saute du cou et s'enfuit en hurlant
        footage(ctx, 'r_rase', t * 0.9, 1.0, 1.0, 1)
        u = t
        jx = 520 - 300 * eo(u / 0.7); jy = 240 + 860 * eo(u / 0.7) - 380 * math.sin(min(1, u / 0.7) * math.pi)
        if u > 0.7: jx = 260 - 40 * math.sin((u - 0.7) * 9); jy = 1080
        gerard(ctx, jx, jy, 0.62, t, mouth=mo, brows=1.0, eyes='tiny', run=1.0 if u > 0.7 else 0.2, arms='up', face=-1, rot=0.3 * math.sin(u * 3) * (u < 0.7))
        shock_lines(ctx, jx, jy - 40, t, 200)
        if u > 0.6: sweat(ctx, jx + 120, jy - 140, t, 1.2)
        text(ctx, 'AU SECOURS !', SAFE_CX + 80, 470, 104, fill=REDX, scale=pop(t, 0.1), rot=-0.06)
        if u > 0.66 and u < 1.1: dust(ctx, jx, jy + 200, t, 0.7)
        cap_y = 760
    elif t < b[3]:                               # présentation digne, puis « mon pire ennemi »
        u = t - b[1]
        footage(ctx, 'r_kit', u * 0.3, 1.0, 1.06, b[3] - b[1], 420, 900)
        ene = t >= b[2]
        bow = 0.25 * math.sin(min(1, u / 0.6) * math.pi) if u < 0.6 else 0.0
        gerard(ctx, 830, 780, 0.5, t, mouth=mo, brows=-0.9 if ene else 0.0, eyes='open', arms='point' if ene else ('wave' if u < 1.5 else 'down'),
               face=-1, rot=bow)
        if not ene:
            badge(ctx, 'GÉRARD', 420, 640, 80, (1, 1, 1), fg=INK, scale=pop(t, b[1] + wt('xb_2', 'GÉRARD', 1.5)), rot=0.05)
            badge(ctx, 'LA BARBE DE HAMZA', 420, 750, 54, BEARD, fg=(1, 1, 1), scale=pop(t, b[1] + wt('xb_2', 'BARBE', 2.4)), rot=-0.04)
        else:
            red_circle(ctx, 580, 960, 160, 470, (t - b[2] - wt('xb_3', 'PIRE', 0.9)) / 0.5, t)
            k = pop(t, b[2] + wt('xb_3', 'ENNEMI', 1.3))
            badge(ctx, 'ENNEMI N°1', 400, 470, 92, REDX, fg=(1, 1, 1), scale=k, rot=-0.08)
            vein(ctx, 740, 640, t, 0.9)
            if t > b[2] + wt('xb_3', 'PHILIPS', 2.4) - 0.1:
                badge(ctx, 'PHILIPS ONEBLADE 360', SAFE_CX, 1300, 62, BLUE, fg=(1, 1, 1), scale=pop(t, b[2] + wt('xb_3', 'PHILIPS', 2.4)), rot=0.03)
                cap_y = 1150
    elif t < b[4]:                               # il taille, il fait les contours, il rase : Gérard saute à chaque mot
        u = t - b[3]
        footage(ctx, 'r_prise', u * 0.7, 1.0, 1.0, 1)
        hits = [wt('xb_4', p, d) for p, d in (('TAILLE', 0.3), ('CONTOURS', 1.5), ('RASE', 2.6))]
        jump = sum(140 * max(0, math.sin(min(1, max(0, (u - h) / 0.35)) * math.pi)) for h in hits)
        gerard(ctx, 870, 820 - jump, 0.45, t, mouth=mo, brows=1.0, eyes='tiny', arms='face', face=-1)
        sweat(ctx, 1000, 660 - jump, t, 1.1)
        for i, (lab, h) in enumerate(zip(('IL TAILLE', 'IL FAIT LES CONTOURS', 'IL RASE'), hits)):
            k = pop(t, b[3] + h)
            badge(ctx, lab, 380, 450 + i * 120, 60, LIME if i != 1 else hexc('#141414'), fg=INK if i != 1 else LIME, scale=k, rot=(-0.04, 0.03, -0.02)[i])
        cap_y = 1180
    elif t < b[6]:                               # l'application choisit son style : il s'indigne
        u = t - b[4]
        footage(ctx, 'r_kit2', u * 0.3, 1.0, 1.0, 1)
        ctx.set_source_rgba(0, 0, 0, 0.45); ctx.paint()
        phone_ar(ctx, t, b[4] + 0.1, AR_G, sh, cx=430, cy=700, who='hamza', outfit='sweat', tag='H', mood=dict(eyes='open', smile=0.8))
        angry = t >= b[5]
        gerard(ctx, 900, 1000 - (60 * abs(math.sin(u * 8)) if angry else 0), 0.4, t, mouth=mo, brows=-1.0 if angry else 0.6,
               eyes='open', arms='up' if angry else 'point', face=-1)
        if angry:
            vein(ctx, 920, 860, t, 0.8)
            text(ctx, 'ET MOI ?!', 900, 720, 84, fill=REDX, scale=pop(t, b[5] + 0.1), rot=0.08)
        cap_y = 1320
    elif t < b[7]:                               # le prix : il pleure
        u = t - b[6]
        footage(ctx, 'r_kit2', 1.5 + u * 0.25, 1.0, 1.0, 1)
        ctx.set_source_rgba(0, 0, 0, 0.35); ctx.paint()
        r29 = wt('xb_7', '29', 1.9)
        fiche_band(ctx, t, b[6] + 0.05, cy=780, circle_t=b[6] + r29)
        if t >= b[6] + r29: coupon_note(ctx, 1040)
        gerard(ctx, 900, 1180, 0.36, t, mouth=mo, brows=1.0, eyes='closed' if u > 1.2 else 'open', arms='face' if u > 1.2 else 'down', face=-1,
               tears=u > 1.2)
        cap_y = 1320
    else:                                        # appel à l'action sur le cou rasé : il supplie
        u = t - b[7]
        footage(ctx, 'r_lisse', u * 0.5, 1.0, 1.0, 1)
        beg = t >= b[8]
        gerard(ctx, 850, 1150, 0.45, t, mouth=mo, brows=1.0 if beg else 0.3, eyes='open', arms='beg' if beg else 'point', face=-1, tears=beg,
               sq=0.15 * math.sin(t * 10) if beg else 0.0)
        if beg: text(ctx, 'PITIÉ !', 820, 830, 96, fill=REDX, scale=pop(t, b[8] + 0.1), rot=0.07)
        ctx.restore(); L.banner(ctx, t, BAN_G, bg=BEARD, fg=(1, 1, 1)); L.cta(ctx, t, b[7] + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN_G, bg=BEARD, fg=(1, 1, 1))
    TL.captions(ctx, t, cap_y)

def build_g():
    TL = L.Timeline(ORDER_G, PAUSE_G, WORDS, start=0.05); T = TL.T; b = [T['xb_%d' % i] for i in range(1, 10)]
    r29 = wt('xb_7', '29', 1.9)
    hits = [wt('xb_4', p, d) for p, d in (('TAILLE', 0.3), ('CONTOURS', 1.5), ('RASE', 2.6))]
    sfx = [('buzz', 0.0, 0.5), ('boing', 0.05, 0.6), ('whoosh', 0.2, 0.5), ('stamp', 0.7, 0.6),
           ('whoosh', b[1] - 0.03, 0.4), ('pop', b[1] + wt('xb_2', 'GÉRARD', 1.5), 0.5), ('stamp', b[2] + wt('xb_3', 'ENNEMI', 1.3), 0.7),
           ('pop', b[2] + wt('xb_3', 'PHILIPS', 2.4), 0.5),
           ('whoosh', b[3] - 0.03, 0.4)] + [('boing', b[3] + h, 0.5) for h in hits] + [
           ('whoosh', b[4] - 0.03, 0.5), ('pop', b[4] + 0.1, 0.5), ('scratch', b[5], 0.6),
           ('whoosh', b[6] - 0.03, 0.5), ('coins', b[6] + r29, 0.6), ('wah', b[6] + r29 + 0.3, 0.6),
           ('whoosh', b[7] - 0.03, 0.4), ('ding', b[7] + RCTA + 0.05, 0.7)]
    sh = Shot('gerard', TL.dur, draw_g, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
