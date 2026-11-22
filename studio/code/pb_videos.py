# -*- coding: utf-8 -*-
"""Tondeuse Philips OneBlade 360, saison 3 : de vrais problèmes de rasage, des vraies images variées.
   1) « Les 3 galères du rasage » : coupures, contours ratés, peau qui chauffe (David présente)
   2) « POV : elle arrive dans 5 minutes » : Hamza se rase en urgence avant son rendez-vous avec Inès"""
import math, random
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from chars import draw_char
from rasoir_videos import fiche_band, coupon_note, beard, oneblade
import pb_data as PB

WORDS = {c: PB.words_for(c) for c in PB.CUTS}
for w in ('COUPURES.', 'RATÉS.', 'CHAUFFE.', 'ONEBLADE', '360', 'PEAU.', 'NETTES,', 'ARRONDIS,', 'LISSE', '29,99 €', '50,99 €', '50,99 €.',
          'TOILETTE', 'CINQ', 'MINUTES', 'PRÊT !', 'BEAU,'):
    if w not in S.HL: S.HL = S.HL + (w,)
LIME = hexc('#c6e21b'); REDX = hexc('#e8263d'); TILE = hexc('#cfe6ee'); TILE2 = hexc('#b4d3df'); PINK = hexc('#ef7fae')
HK = dict(outfit='sweat')

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def eo(u): return 1 - (1 - max(0.0, min(1.0, u))) ** 3

# ---------------------------------------------------------------- décors et accessoires
def bg_sdb(ctx, t, tint=None):
    """salle de bain dessinée : carrelage, miroir, lavabo"""
    ctx.set_source_rgb(*TILE); ctx.paint()
    for y in range(0, H, 120):
        for x in range(0 if (y // 120) % 2 == 0 else -60, W, 120):
            ctx.new_path(); ctx.rectangle(x + 3, y + 3, 114, 114); ctx.set_source_rgb(*(TILE if (x // 120 + y // 120) % 2 else TILE2)); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.25); ctx.paint()
    ink_fill(ctx, lambda c: rrect(c, 150, 420, 780, 900, 40), hexc('#e9f6fb'), lw=10)
    ctx.new_path(); ctx.move_to(260, 520); ctx.line_to(360, 470); ctx.move_to(250, 600); ctx.line_to(420, 520)
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(18); ctx.stroke()
    ink_fill(ctx, lambda c: rrect(c, 60, 1440, 960, 130, 30), (1, 1, 1), lw=9)
    if tint:
        ctx.set_source_rgba(*tint); ctx.paint()

def sepia(ctx, k=0.55):
    ctx.save(); ctx.set_operator(cairo.OPERATOR_HSL_COLOR); ctx.set_source_rgba(0.55, 0.4, 0.2, k); ctx.paint(); ctx.restore()
    ctx.set_source_rgba(0.45, 0.3, 0.1, 0.18); ctx.paint()

def tissues(ctx, x, y, sc, t, n=9, k=1.0, fly=0.0):
    """bouts de papier toilette collés sur les coupures (joues, menton, cou)"""
    rnd = random.Random(11)
    spots = [(-95, 30), (95, 40), (-45, 95), (50, 100), (0, 140), (-115, 80), (120, 75), (-60, -60), (70, -75)][:n]
    for i, (dx, dy) in enumerate(spots):
        px = x + sc * dx; py = y + sc * dy
        if fly > 0:
            px += sc * rnd.uniform(-600, 600) * fly; py += sc * (-700 * fly + 900 * fly * fly)
        else:
            rnd.uniform(0, 1)
        s = sc * (20 + 6 * (i % 3)) * k
        if s <= 0.5: continue
        ctx.save(); ctx.translate(px, py); ctx.rotate((i * 0.7) % 1.2 - 0.6 + fly * 6 * (i % 2 - 0.5))
        ink_fill(ctx, lambda c: blob(c, [(-s, -s * 0.8), (s, -s), (s * 0.9, s * 0.85), (-s * 0.85, s)], i, 0.15 * s), (1, 1, 1), lw=4)
        ctx.new_path(); ctx.arc(0, 0, s * 0.3, 0, 7); ctx.set_source_rgba(0.86, 0.1, 0.15, 0.9); ctx.fill()
        ctx.restore()

def classic_razor(ctx, x, y, s, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -22, 0, 44, 330, 20), hexc('#2f6fde'), lw=7)
    ink_fill(ctx, lambda c: rrect(c, -110, -60, 220, 70, 16), hexc('#9aa5b5'), lw=7)
    for k in range(3):
        ctx.new_path(); ctx.move_to(-95, -45 + k * 18); ctx.line_to(95, -45 + k * 18); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def flames(ctx, x, y, s, t):
    for i in range(5):
        fx_ = x + (i - 2) * 46 * s; h = (90 + 40 * math.sin(t * 12 + i * 1.7)) * s
        pts = [(fx_ - 26 * s, y), (fx_ - 10 * s, y - h * 0.6), (fx_, y - h), (fx_ + 12 * s, y - h * 0.55), (fx_ + 26 * s, y)]
        ink_fill(ctx, lambda c, pts=pts: blob(c, pts, i, 0.5), hexc('#ff6a13') if i % 2 else hexc('#ffd23f'), lw=4)

def steam(ctx, x, y, t, n=3):
    for i in range(n):
        ph = (t * 0.8 + i / n) % 1.0
        ctx.new_path()
        for k in range(12):
            yy = y - k * 14 - ph * 140; xx = x + i * 70 - 70 + 14 * math.sin(k * 0.8 + t * 4)
            (ctx.move_to if k == 0 else ctx.line_to)(xx, yy)
        ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - ph)); ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def stamp_pb(ctx, t, t0, num, label, y=520):
    """tampon « PROBLÈME N°x » + intitulé"""
    k = pop(t, t0, 0.22)
    if k <= 0.01: return
    ctx.save(); ctx.translate(SAFE_CX, y); ctx.rotate(-0.06); ctx.scale(k * (1 + 0.6 * max(0, 1 - (t - t0) / 0.15)), k)
    badge(ctx, 'PROBLÈME N°%d' % num, 0, 0, 104, REDX, fg=(1, 1, 1))
    ctx.restore()
    badge(ctx, label, SAFE_CX, y + 150, 76, (1, 1, 1), fg=INK, scale=pop(t, t0 + 0.6), rot=0.03)

def solution(ctx, t, t0, txt, y=450, size=60, bg=None, fg=INK, x=SAFE_CX, rot=-0.03):
    k = pop(t, t0)
    badge(ctx, txt, x, y, size, bg or LIME, fg=fg, scale=k, rot=rot)

def pip(ctx, seg, tt, x, y, w, h, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0, z1=None, dur=3.0):
    """incrustation d'une vraie séquence dans un cadre arrondi"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.new_path(); rrect(ctx, -w / 2 + 14, -h / 2 + 18, w, h, 36); ctx.set_source_rgba(0, 0, 0, 0.45); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, 36); ctx.save(); ctx.clip()
    s = max(w / W, h / H); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2)
    footage(ctx, seg, tt, zoom, z1 if z1 else zoom, dur, cx, cy)
    ctx.restore()
    ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, 36); ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(14); ctx.stroke()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()

def arrow_lbl(ctx, x0, y0, x1, y1, txt, t, t0, side=1):
    k = eo((t - t0) / 0.35)
    if k <= 0: return
    xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    ctx.new_path(); ctx.move_to(x0, y0); ctx.line_to(xe, ye)
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(16); ctx.stroke_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(7); ctx.stroke()
    a = math.atan2(ye - y0, xe - x0)
    for d in (2.6, -2.6):
        ctx.new_path(); ctx.move_to(xe, ye); ctx.line_to(xe + 40 * math.cos(a + d), ye + 40 * math.sin(a + d))
        ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    badge(ctx, txt, x0, y0 - 10, 50, (1, 1, 1), fg=INK, scale=pop(t, t0), rot=-0.04 * side)

def up_tri(ctx, x, y, s=34):
    ink_fill(ctx, lambda c: (c.move_to(x, y - s), c.line_to(x + s, y + s * 0.7), c.line_to(x - s, y + s * 0.7), c.close_path()), LIME, lw=5)

def dashed_line(ctx, pts, k, col, w=10, dash=26):
    if k <= 0: return
    ctx.save(); ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_dash([dash, dash * 0.6])
    ctx.set_source_rgb(*col); ctx.set_line_width(w); ctx.stroke(); ctx.restore()

def timer(ctx, t, secs, x=830, y=430, alarm=False):
    """chrono de compte à rebours façon réveil"""
    m, s_ = int(secs) // 60, int(secs) % 60; txt = '%02d:%02d' % (m, s_)
    blink = alarm and (t * 4) % 1 < 0.5
    ctx.save(); ctx.translate(x, y); ctx.rotate(0.05 + (0.06 * math.sin(t * 40) if alarm else 0))
    ink_fill(ctx, lambda c: rrect(c, -150, -64, 300, 128, 28), hexc('#141414'), lw=7)
    text(ctx, txt, 0, 0, 92, font='Bangers', fill=REDX if blink else LIME, stroke=None, shadow=False)
    ctx.restore()

def fast_fwd(ctx, t, x=150, y=430):
    if (t * 3) % 1 < 0.7:
        for k in range(2):
            ctx.new_path(); ctx.move_to(x + k * 46, y - 34); ctx.line_to(x + 46 + k * 46, y); ctx.line_to(x + k * 46, y + 34); ctx.close_path()
            ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
        text(ctx, 'x2', x + 150, y + 4, 60, fill=(1, 1, 1))

def phone_msg(ctx, t, t0, who_name, msg, x=SAFE_CX, y=760, sc=1.0):
    """notification de message vocal sur un téléphone"""
    k = ease_out_back(min(1, max(0, (t - t0) / 0.35)))
    if k <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(k * sc, k * sc); ctx.rotate(-0.04)
    ink_fill(ctx, lambda c: rrect(c, -300, -460, 600, 920, 60), hexc('#1b1c20'), lw=8)
    ctx.new_path(); rrect(ctx, -278, -438, 556, 876, 44); ctx.set_source_rgb(*hexc('#2a2f3a')); ctx.fill()
    text(ctx, who_name, 0, -330, 60, fill=(1, 1, 1), stroke=None, shadow=False)
    ink_fill(ctx, lambda c: rrect(c, -240, -230, 480, 220, 40), (1, 1, 1), lw=5)
    text(ctx, msg, 0, -120, 46, font='Patrick Hand', fill=INK, stroke=None, shadow=False, max_w=440)
    for i in range(18):                                       # onde du vocal
        hh = 18 + 40 * abs(math.sin(i * 1.7 + t * 9))
        ctx.new_path(); ctx.rectangle(-200 + i * 24, 80 - hh / 2, 12, hh); ctx.set_source_rgb(*LIME); ctx.fill()
    ink_fill(ctx, lambda c: c.arc(-230, 80, 30, 0, 7), LIME, lw=4)
    ctx.restore()

def heart_eyes_burst(ctx, x, y, t, t0):
    for i in range(6):
        u = (t - t0 - i * 0.12)
        if u < 0: continue
        a = -math.pi / 2 + (i - 2.5) * 0.4; r = 120 + 260 * eo(u / 0.9)
        hx, hy = x + r * math.cos(a), y + r * math.sin(a) - 80 * u
        ink_fill(ctx, lambda c, hx=hx, hy=hy: heart(c, hx, hy, 34), hexc('#ff4d6d'), lw=4)

# ---------------------------------------------------------------- 1. LES 3 GALÈRES (David)
BAN_G = "ARRÊTE DE TE COUPER EN TE RASANT"
ORDER_G = [('xg_%d' % i, 'D') for i in range(1, 12)]
PAUSE_G = {'xg_2': 0.2, 'xg_3': 0.05, 'xg_4': 0.1, 'xg_5': 0.15, 'xg_6': 0.05, 'xg_7': 0.15, 'xg_8': 0.05, 'xg_9': 0.15, 'xg_10': 0.15, 'xg_11': 0.1}
RCTA = 0.9

def draw_gal(ctx, t, sh):
    TL = sh.tl; T = TL.T; g = [T['xg_%d' % i] for i in range(1, 12)]
    md = sh.mouth('D', t)
    cap_y = 1180; ban = True
    ctx.save()
    if t < g[1]:                                  # accroche : la tête pleine de papier toilette
        bg_sdb(ctx, t)
        S.cam(ctx, t, z=1.0 + 0.05 * eo(t / 2), cx=540, cy=800)
        draw_char(ctx, 'hamza', 540, 700, 1.45, t, eyes='half', brows=-0.2, smile=-0.7, look=(0, 0.3), arms=('down', 'down'), **HK)
        beard(ctx, 540, 700, 1.45, 'stubble', t)
        tissues(ctx, 540, 700, 1.45, t, k=pop(t, 0.0, 0.2))
        ctx.restore(); ctx.save()
        draw_char(ctx, 'david', 900, 1250, 0.42, t, eyes='happy', smile=1.0, brows=0.4, look=(-1, -0.4), arms=('point_side', 'face'), mouth=md,
                  outfit='rose', tilt=0.08 * math.sin(t * 9))
        text(ctx, 'HAHA', 900, 930, 70, fill=(1, 1, 1), rot=0.1, scale=pop(t, 0.6))
        cap_y = 1330
    elif t < g[2]:                                # problème n°1 : coupures, flashback lame classique
        u = t - g[1]
        bg_sdb(ctx, t)
        draw_char(ctx, 'hamza', 540, 900, 0.95, t, eyes='tiny' if u > 0.9 else 'open', brows=1.0, smile=-0.8, look=(0.3, 0), arms=('down', 'face'), **HK)
        beard(ctx, 540, 900, 0.95, 'stubble', t)
        classic_razor(ctx, 690, 1010, 0.55, rot=-0.5)
        if u > 0.9:
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(640, 1000, 12, 18, 8), 2, 0.3), REDX, lw=3)
            text(ctx, 'AÏE !', 820, 820, 110, fill=REDX, scale=pop(t, g[1] + 0.9), rot=0.12)
            shock_lines(ctx, 560, 880, t, 230)
        sepia(ctx, 0.5)
        stamp_pb(ctx, t, g[1] + 0.05, 1, 'LES COUPURES', y=470)
        cap_y = 1300
    elif t < g[3]:                                # solution : conçu pour couper les poils, pas la peau (vraie séquence, zoom)
        u = t - g[2]
        footage(ctx, 'r_rase', 0.4 + u * 0.8, 1.0, 1.25, g[3] - g[2], 480, 900)
        flash(ctx, u)
        solution(ctx, t, g[2] + wt('xg_3', 'CONÇU', 1.8), 'CONÇU POUR COUPER LES POILS', y=470, size=56)
        solution(ctx, t, g[2] + wt('xg_3', 'PAS', 3.6), 'ET PAS LA PEAU', y=590, size=80, bg=(1, 1, 1))
        if t > g[2] + wt('xg_3', 'PAS', 3.6): L.check(ctx, SAFE_CX + 260, 590, 0.9, pop(t, g[2] + wt('xg_3', 'PAS', 3.6)))
        text(ctx, '(selon Philips)', SAFE_CX, 680, 34, font='Patrick Hand', fill=(1, 1, 1), sw=5)
    elif t < g[4]:                                # double protection : arrêt sur image du kit puis rasage à contre-sens
        u = t - g[3]; split = g[3] + wt('xg_4', 'AIDE', 3.6) - 0.1
        if t < split:
            footage(ctx, 'r_kit', 0.2, 1.7, 1.9, split - g[3], 600, 640)
            ctx.set_source_rgba(0, 0, 0, 0.2); ctx.paint()
            arrow_lbl(ctx, 300, 520, 520, 640, 'REVÊTEMENT LISSE', t, g[3] + wt('xg_4', 'REVÊTEMENT', 1.9))
            arrow_lbl(ctx, 800, 900, 680, 760, 'BORDS ARRONDIS', t, g[3] + wt('xg_4', 'BORDS', 2.7), side=-1)
            badge(ctx, 'DOUBLE PROTECTION', SAFE_CX, 1290, 64, LIME, fg=INK, scale=pop(t, g[3] + wt('xg_4', 'PROTECTION', 1.0)), rot=0.03)
            cap_y = 1130
        else:
            v = t - split
            footage(ctx, 'r_rase2', 0.3 + v * 0.45, 1.1, 1.0, 2.5, 480, 900)
            flash(ctx, v)
            for k in range(3):                     # flèches « à contre-sens »
                yy = 1100 - ((v * 500 + k * 160) % 480)
                up_tri(ctx, 230, yy)
            solution(ctx, t, split + 0.1, 'MÊME À CONTRE-SENS', y=470, size=70)
    elif t < g[5]:                                # problème n°2 : contours ratés
        u = t - g[4]
        bg_sdb(ctx, t)
        draw_char(ctx, 'hamza', 540, 900, 0.95, t, eyes='open', brows=0.8, smile=-0.5, look=(-0.4, 0.4), arms=('down', 'chin'), **HK)
        beard(ctx, 540, 900, 0.95, 'goatee', t, tilt=0.12)
        k = eo((u - 0.9) / 0.5)
        dashed_line(ctx, [(380, 960), (450, 1050), (520, 1000), (600, 1090), (700, 990)], k, REDX, w=12)
        if u > 1.3: text(ctx, 'TORDU…', 830, 1080, 80, fill=REDX, scale=pop(t, g[4] + 1.3), rot=0.1)
        sepia(ctx, 0.5)
        stamp_pb(ctx, t, g[4] + 0.05, 2, 'LES CONTOURS RATÉS', y=470)
        cap_y = 1310
    elif t < g[6]:                                # lame double sens : lignes nettes (vraie séquence + incrustation)
        u = t - g[5]
        footage(ctx, 'r_rase2', 1.2 + u * 0.6, 1.0, 1.15, g[6] - g[5], 480, 860)
        flash(ctx, u)
        dashed_line(ctx, [(180, 820), (880, 700)], eo((u - 0.6) / 0.6), LIME, w=12)
        solution(ctx, t, g[5] + wt('xg_6', 'DOUBLE', 0.4), 'LAME DOUBLE SENS', y=470, size=64)
        solution(ctx, t, g[5] + wt('xg_6', 'LIGNES', 1.8), 'LIGNES NETTES', y=590, size=70, bg=(1, 1, 1))
        if t > g[5] + 2.0:
            pip(ctx, 'r_rase', 1.5 + u * 0.5, 830, 1000, 300, 420, zoom=1.3, cx=480, cy=900, rot=0.05)
            cap_y = 1250
    elif t < g[7]:                                # problème n°3 : la peau qui chauffe
        u = t - g[6]
        bg_sdb(ctx, t)
        draw_char(ctx, 'hamza', 540, 900, 0.95, t, eyes='tiny', brows=1.0, smile=-0.9, look=(0, 0), arms=('face', 'face'), blush=1.0,
                  tilt=0.05 * math.sin(t * 20), **HK)
        flames(ctx, 540, 1140, 1.0, t); steam(ctx, 540, 640, t)
        sepia(ctx, 0.35)
        stamp_pb(ctx, t, g[6] + 0.05, 3, 'LA PEAU QUI CHAUFFE', y=470)
        cap_y = 1320
    elif t < g[8]:                                # préserve ta peau : écran partagé, deux vraies séquences
        u = t - g[7]
        footage(ctx, 'r_lisse', u * 0.6, 1.0, 1.08, g[8] - g[7], 540, 800)
        flash(ctx, u)
        pip(ctx, 'r_lisse2', u * 0.7, 300, 1000, 330, 470, zoom=1.2, cx=540, cy=700, rot=-0.05)
        solution(ctx, t, g[7] + wt('xg_8', 'RASE', 0.5), "PAS AUSSI PRÈS QU'UNE LAME CLASSIQUE", y=470, size=46, bg=(1, 1, 1))
        solution(ctx, t, g[7] + wt('xg_8', 'PRÉSERVE', 2.3), 'PRÉSERVE TA PEAU', y=590, size=74)
        for i in range(5): sparkle(ctx, 640 + (i * 83) % 300, 760 + (i * 61) % 260, 30, t, ph=i)
        cap_y = 1300
    elif t < g[9]:                                # prix : photo du kit puis bandeau de la fiche
        u = t - g[8]
        footage(ctx, 'r_kit2', 0.8 + u * 0.3, 1.0, 1.0, 1)
        ctx.set_source_rgba(0, 0, 0, 0.4); ctx.paint()
        r29 = wt('xg_9', '29', 1.9)
        fiche_band(ctx, t, g[8] + 0.05, cy=760, circle_t=g[8] + r29)
        if t >= g[8] + r29: coupon_note(ctx, 1020)
        cap_y = 1200
    elif t < g[10]:                               # rappel de l'accroche : les papiers s'envolent
        u = t - g[9]
        bg_sdb(ctx, t)
        draw_char(ctx, 'hamza', 540, 820, 1.05, t, eyes='happy', brows=0.5, smile=1.0, look=(0, 0), arms=('cheer', 'cheer'), **HK)
        beard(ctx, 540, 820, 1.05, 'stubble', t)
        tissues(ctx, 540, 820, 1.05, t, fly=eo(u / 0.9))
        for i in range(6): sparkle(ctx, 300 + i * 100, 640 + (i % 2) * 300, 34, t, ph=i)
        flash(ctx, u)
        cap_y = 1310
    else:                                         # appel à l'action sur une vraie séquence
        u = t - g[10]
        footage(ctx, 'r_prise', 1.0 + u * 0.5, 1.0, 1.05, 3, 540, 900)
        draw_char(ctx, 'david', 880, 1230, 0.42, t, eyes='open' if (u % 2.2) < 1.6 else 'wink', smile=1.0, brows=0.5, look=(-0.6, 0.8),
                  arms=(('down', 'point_down', u / 0.3), 'hip'), mouth=md, outfit='rose')
        ctx.restore(); L.banner(ctx, t, BAN_G, bg=REDX, fg=(1, 1, 1)); L.cta(ctx, t, g[10] + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN_G, bg=REDX, fg=(1, 1, 1))
    TL.captions(ctx, t, cap_y)

def build_gal():
    TL = L.Timeline(ORDER_G, PAUSE_G, WORDS, start=0.05); T = TL.T; g = [T['xg_%d' % i] for i in range(1, 12)]
    split = g[3] + wt('xg_4', 'AIDE', 3.6) - 0.1
    sfx = [('pop', 0.02, 0.5), ('boing', 0.3, 0.4), ('stamp', g[1] + 0.05, 0.9), ('scratch', g[1] + 0.85, 0.5),
           ('whoosh', g[2] - 0.03, 0.6), ('ding', g[2] + wt('xg_3', 'PAS', 3.6), 0.6),
           ('whoosh', g[3] - 0.03, 0.5), ('pop', g[3] + wt('xg_4', 'REVÊTEMENT', 1.9), 0.5), ('pop', g[3] + wt('xg_4', 'BORDS', 2.7), 0.5),
           ('swipe', split, 0.6), ('buzz', split + 0.1, 0.35),
           ('stamp', g[4] + 0.05, 0.9), ('whoosh', g[5] - 0.03, 0.6), ('pop', g[5] + wt('xg_6', 'LIGNES', 1.8), 0.5),
           ('stamp', g[6] + 0.05, 0.9), ('whoosh', g[7] - 0.03, 0.6), ('sparkle', g[7] + wt('xg_8', 'PRÉSERVE', 2.3), 0.6),
           ('whoosh', g[8] - 0.03, 0.5), ('coins', g[8] + wt('xg_9', '29', 1.9), 0.6),
           ('whoosh', g[9], 0.7), ('sparkle', g[9] + 0.3, 0.6), ('whoosh', g[10] - 0.03, 0.4), ('ding', g[10] + RCTA + 0.05, 0.7)]
    sh = Shot('galeres', TL.dur, draw_gal, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None

# ---------------------------------------------------------------- 2. POV : ELLE ARRIVE DANS 5 MINUTES
BAN_D = "POV : ELLE ARRIVE DANS 5 MINUTES"
ORDER_D = [('xi_d1', 'I'), ('xh_d1', 'H'), ('xh_d2', 'H'), ('xh_d3', 'H'), ('xh_d4', 'H'), ('xh_d5', 'H'), ('xh_d6', 'H'), ('xi_d2', 'I'),
           ('xh_d7', 'H'), ('xi_d3', 'I'), ('xh_d8', 'H'), ('xh_d9', 'H')]
PAUSE_D = {'xh_d1': 0.1, 'xh_d2': 0.15, 'xh_d3': 0.1, 'xh_d4': 0.05, 'xh_d5': 0.05, 'xh_d6': 0.05, 'xi_d2': 0.25, 'xh_d7': 0.2, 'xi_d3': 0.15,
           'xh_d8': 0.2, 'xh_d9': 0.15}

def draw_date(ctx, t, sh):
    TL = sh.tl; T = TL.T; d = {c: T[c] for c, _ in ORDER_D}
    mh = sh.mouth('H', t); mi = sh.mouth('I', t)
    cap_y = 1180; ban = True
    # chrono : 5:00 au premier vocal, il file pendant le rasage, alarme à la sonnette
    t5 = d['xh_d1']; tend = d['xh_d7'] + 0.6
    secs = 300 - (t - t5) / (d['xi_d2'] - t5) * 270 if t < d['xi_d2'] else max(12, 30 - (t - d['xi_d2']) * 8)
    if t >= tend: secs = 12
    ctx.save()
    if t < d['xh_d2']:                            # le vocal d'Inès, Hamza panique, barbe énorme
        bg_sdb(ctx, t)
        if t < t5:
            draw_char(ctx, 'hamza', 440, 900, 1.0, t, eyes='half', brows=-0.2, smile=0.3, look=(1, -0.6), arms=('down', 'phone'), **HK)
            beard(ctx, 440, 900, 1.0, 'viking', t)
            text(ctx, 'ZZZ', 300, 600, 70, fill=(1, 1, 1), rot=-0.1)
            phone_msg(ctx, t, 0.0, 'Inès', "J'arrive dans 5 min !", x=820, y=760, sc=0.45)
            cap_y = 1340
        else:
            u = t - t5
            S.cam(ctx, t, z=1.0 + 0.15 * eo(u / 0.25), cx=540, cy=800, shake=8 if u < 0.6 else 0)
            draw_char(ctx, 'hamza', 540, 900, 1.0, t, eyes='tiny', brows=1.0, smile=-0.9, look=(0, 0), arms=('face', 'face'), mouth=mh, **HK)
            beard(ctx, 540, 900, 1.0, 'viking', t)
            shock_lines(ctx, 540, 880, t, 300)
            sweat(ctx, 700, 700, t, 1.3)
            ctx.restore(); ctx.save()
            timer(ctx, t, 300)
            cap_y = 1320
    elif t < d['xh_d3']:                          # flashback : avant, il se coupait en allant vite
        u = t - d['xh_d2']
        bg_sdb(ctx, t)
        draw_char(ctx, 'hamza', 540, 900, 0.95, t, eyes='tiny', brows=1.0, smile=-0.8, look=(0, 0), arms=('down', 'face'),
                  tilt=0.06 * math.sin(t * 25), **HK)
        classic_razor(ctx, 690, 1000, 0.55, rot=-0.5 + 0.3 * math.sin(t * 20))
        tissues(ctx, 540, 900, 0.95, t, n=6, k=pop(t, d['xh_d2'] + 1.6, 0.2))
        if u > 1.6: text(ctx, 'AÏE !', 820, 800, 110, fill=REDX, scale=pop(t, d['xh_d2'] + 1.6), rot=0.12)
        sepia(ctx, 0.6)
        badge(ctx, 'AVANT…', 300, 460, 80, (1, 1, 1), fg=INK, rot=-0.06, scale=pop(t, d['xh_d2'] + 0.05))
        cap_y = 1310
    elif t < d['xh_d4']:                          # il attrape le OneBlade (vraie séquence) : conçu pour couper les poils, pas la peau
        u = t - d['xh_d3']
        footage(ctx, 'r_prise', u * 0.6, 1.0, 1.08, d['xh_d4'] - d['xh_d3'], 540, 900)
        flash(ctx, u)
        solution(ctx, t, d['xh_d3'] + wt('xh_d3', 'CONÇU', 1.9), 'CONÇU POUR COUPER LES POILS,', y=600, size=52)
        solution(ctx, t, d['xh_d3'] + wt('xh_d3', 'PAS', 3.4), 'PAS LA PEAU', y=710, size=76, bg=(1, 1, 1))
        text(ctx, '(selon Philips)', SAFE_CX, 800, 34, font='Patrick Hand', fill=(1, 1, 1), sw=5)
        timer(ctx, t, secs)
    elif t < d['xi_d2']:                          # le montage en accéléré : il taille, contours, rase à contre-sens
        if t < d['xh_d5']:
            u = t - d['xh_d4']; footage(ctx, 'r_rase', 0.2 + u * 1.6, 1.15, 1.25, 1.0, 480, 900); lab = 'JE TAILLE'
        elif t < d['xh_d6']:
            u = t - d['xh_d5']; footage(ctx, 'r_rase2', 0.5 + u * 1.5, 1.0, 1.1, 2.0, 480, 860); lab = 'CONTOURS : LAME DOUBLE SENS'
            dashed_line(ctx, [(180, 820), (880, 700)], eo((u - 0.3) / 0.5), LIME, w=12)
        else:
            u = t - d['xh_d6']; footage(ctx, 'r_rase', 2.0 + u * 1.6, 1.0, 1.0, 1, 480, 900); lab = 'JE RASE, MÊME À CONTRE-SENS'
            for k in range(3):
                yy = 1100 - ((u * 600 + k * 160) % 480); up_tri(ctx, 230, yy)
        flash(ctx, u)
        badge(ctx, lab, SAFE_CX, 600, 58 if len(lab) > 12 else 80, LIME, fg=INK, scale=pop(t, t - u), rot=-0.04)
        fast_fwd(ctx, t)
        timer(ctx, t, secs)
    elif t < d['xh_d7']:                          # la sonnette : « c'est moi, je suis en bas ! »
        u = t - d['xi_d2']
        bg_sdb(ctx, t)
        draw_char(ctx, 'hamza', 540, 900, 0.95, t, eyes='wide', brows=1.0, smile=0.2, look=(1, -0.3), arms=('down', 'down'), **HK)
        text(ctx, 'DRIIING !', 760, 640, 110, fill=REDX, scale=pop(t, d['xi_d2']), rot=0.1)
        ctx.restore(); ctx.save()
        timer(ctx, t, secs, alarm=True)
        cap_y = 1310
    elif t < d['xi_d3']:                          # et voilà, prêt ! (vraie séquence : peau nette)
        u = t - d['xh_d7']
        footage(ctx, 'r_lisse', 0.5 + u * 0.6, 1.1, 1.0, 1.5, 540, 800)
        flash(ctx, u)
        for i in range(6): sparkle(ctx, 360 + (i * 97) % 380, 700 + (i * 71) % 360, 34, t, ph=i)
        badge(ctx, 'PRÊT !', SAFE_CX, 560, 110, LIME, fg=INK, scale=pop(t, d['xh_d7'] + wt('xh_d7', 'PRÊT', 0.9)), rot=-0.06)
        timer(ctx, t, 12)
    elif t < d['xh_d8']:                          # Inès charmée
        u = t - d['xi_d3']
        bg_sdb(ctx, t, tint=(1, 0.75, 0.85, 0.15))
        draw_char(ctx, 'ines', 300, 940, 0.85, t, eyes='heart' if u > 0.8 else 'wide', smile=1.0, brows=0.5, look=(1, 0), arms=('lips', 'down'),
                  mouth=mi, blush=1.0)
        draw_char(ctx, 'hamza', 780, 940, 0.85, t, eyes='happy', smile=1.0, brows=0.4, look=(-1, 0), arms=('hip', 'chin'), **HK)
        beard(ctx, 780, 940, 0.85, 'stubble', t)
        for i in range(4): sparkle(ctx, 680 + i * 60, 900 + (i % 2) * 80, 26, t, ph=i)
        if u > 0.8: heart_eyes_burst(ctx, 300, 760, t, d['xi_d3'] + 0.8)
        cap_y = 1310
    elif t < d['xh_d9']:                          # le prix
        u = t - d['xh_d8']
        footage(ctx, 'r_kit2', 1.0 + u * 0.3, 1.0, 1.0, 1)
        ctx.set_source_rgba(0, 0, 0, 0.4); ctx.paint()
        r29 = wt('xh_d8', '29', 1.0)
        fiche_band(ctx, t, d['xh_d8'] + 0.05, cy=760, circle_t=d['xh_d8'] + r29)
        if t >= d['xh_d8'] + r29: coupon_note(ctx, 1020)
        cap_y = 1200
    else:                                         # appel à l'action : les deux, sur le pas de la porte
        u = t - d['xh_d9']
        footage(ctx, 'r_lisse2', 0.3 + u * 0.4, 1.0, 1.05, 3, 540, 800)
        draw_char(ctx, 'ines', 640, 760, 0.5, t, eyes='heart', smile=1.0, look=(1, 0), arms=('hip', 'wave'), blush=1.0)
        draw_char(ctx, 'hamza', 880, 760, 0.5, t, eyes='open' if (u % 2.2) < 1.6 else 'wink', smile=1.0, brows=0.5, look=(-0.6, 0.8),
                  arms=(('down', 'point_down', u / 0.3), 'hip'), mouth=mh, **HK)
        beard(ctx, 880, 760, 0.5, 'stubble', t)
        ctx.restore(); L.banner(ctx, t, BAN_D, bg=PINK, fg=INK); L.cta(ctx, t, d['xh_d9'] + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN_D, bg=PINK, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_date():
    TL = L.Timeline(ORDER_D, PAUSE_D, WORDS, start=0.05); T = TL.T; d = {c: T[c] for c, _ in ORDER_D}
    sfx = [('ding', 0.0, 0.6), ('pop', 0.05, 0.5), ('stamp', d['xh_d1'], 0.8), ('drumroll', d['xh_d1'] + 0.2, 0.3),
           ('scratch', d['xh_d2'] - 0.05, 0.6), ('scratch', d['xh_d2'] + 1.55, 0.5),
           ('whoosh', d['xh_d3'] - 0.03, 0.6), ('ding', d['xh_d3'] + wt('xh_d3', 'PAS', 3.4), 0.5),
           ('swipe', d['xh_d4'] - 0.02, 0.7), ('buzz', d['xh_d4'], 0.4), ('swipe', d['xh_d5'] - 0.02, 0.7), ('buzz', d['xh_d5'], 0.4),
           ('swipe', d['xh_d6'] - 0.02, 0.7), ('buzz', d['xh_d6'], 0.4),
           ('bells', d['xi_d2'] - 0.05, 0.9), ('whoosh', d['xh_d7'] - 0.03, 0.5), ('sparkle', d['xh_d7'] + 0.3, 0.7),
           ('heart', d['xi_d3'] + 0.8, 0.7), ('whoosh', d['xh_d8'] - 0.03, 0.5), ('coins', d['xh_d8'] + wt('xh_d8', '29', 1.0), 0.6),
           ('whoosh', d['xh_d9'] - 0.03, 0.4), ('ding', d['xh_d9'] + RCTA + 0.05, 0.7)]
    sh = Shot('date', TL.dur, draw_date, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
