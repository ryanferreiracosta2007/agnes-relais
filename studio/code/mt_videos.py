# -*- coding: utf-8 -*-
"""Tondeuse Philips OneBlade 360 : « La météo de ta barbe ».
   Parodie de bulletin météo télé : mini Léa, présentatrice, commente la VRAIE image d'un cou poilu comme une carte météo
   (nuages d'orage, pluie de poils, VIGILANCE ORANGE). Mini Hamza proteste (« c'est mon style ! »).
   Éclaircie = le OneBlade (vraies images : il taille, fait les contours, rase), « ciel dégagé » sur le cou rasé.
   Prix, panier orange, puis question météo au spectateur : soleil, nuages ou tempête ?"""
import math
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, ease_out
from tb_videos import comment_bubble
from rasoir_videos import coupon_note, LIME
import mt_data as MT

WORDS = {c: MT.words_for(c) for c in MT.CUTS}
for w in ('MÉTÉO', 'BARBE !', 'ALERTE', 'ORANGE :', 'POILS', 'TEMPÊTE,', 'STYLE !', 'ÉCLAIRCIE', 'ONEBLADE', 'TAILLE,',
          'CONTOURS', 'RASE.', 'CIEL', 'DÉGAGÉ.', '50,99 €,', '29,99 €', 'COUPONS', 'DESSOUS,', 'ORANGE.', 'SOLEIL,',
          'NUAGES', 'TEMPÊTE ?', 'COMMENTAIRE.'):
    if w not in S.HL: S.HL = S.HL + (w,)
ORG = hexc('#ff7a00'); SKY = hexc('#2f7fd8'); NAVY = hexc('#12305e'); STORM = hexc('#5b6270'); SUN = hexc('#ffd23f')
REDL = hexc('#e8263d')
BAN = "LA MÉTÉO DE TA BARBE"
ORDER = [('xm_l1', 'L'), ('xm_l2', 'L'), ('xm_h1', 'H'), ('xm_l3', 'L'), ('xm_l4', 'L'), ('xm_h2', 'H'), ('xm_l5', 'L'),
         ('xm_l6', 'L'), ('xm_l7', 'L')]
PAUSE = {'xm_l2': 0.2, 'xm_h1': 0.0, 'xm_l3': 0.05, 'xm_l4': 0.0, 'xm_h2': 0.05, 'xm_l5': 0.08, 'xm_l6': 0.05, 'xm_l7': 0.08}

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

# ---------------------------------------------------------------- pictos météo
def cloud(ctx, x, y, s, col=(1, 1, 1), t=0.0):
    if s <= 0.01: return
    dx = 6 * math.sin(t * 1.7)
    ctx.save(); ctx.translate(x + dx, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: (c.arc(-60, 10, 48, 0, 7), c.new_sub_path(), c.arc(0, -20, 64, 0, 7), c.new_sub_path(),
                             c.arc(62, 8, 50, 0, 7), c.new_sub_path(), rrect(c, -100, 0, 200, 60, 30)), col, lw=6)
    ctx.restore()

def sun(ctx, x, y, s, t):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(t * 0.8)
    for i in range(10):
        a = i * math.pi / 5
        ctx.new_path(); ctx.move_to(78 * math.cos(a), 78 * math.sin(a)); ctx.line_to(118 * math.cos(a), 118 * math.sin(a))
        ctx.set_source_rgb(*INK); ctx.set_line_width(20); ctx.set_line_cap(1); ctx.stroke()
        ctx.new_path(); ctx.move_to(78 * math.cos(a), 78 * math.sin(a)); ctx.line_to(118 * math.cos(a), 118 * math.sin(a))
        ctx.set_source_rgb(*SUN); ctx.set_line_width(10); ctx.stroke()
    ctx.rotate(-t * 0.8)
    ink_fill(ctx, lambda c: c.arc(0, 0, 66, 0, 7), SUN, lw=6)
    for sx in (-1, 1):
        ctx.new_path(); ctx.arc(sx * 22, -8, 8, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.new_path(); ctx.arc(0, 8, 28, 0.2, math.pi - 0.2); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()

def bolt(ctx, x, y, s, t):
    if (t * 4) % 1.0 > 0.55: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: (c.move_to(10, 0), c.line_to(-26, 60), c.line_to(0, 60), c.line_to(-18, 120), c.line_to(34, 44),
                             c.line_to(8, 44), c.line_to(28, 0), c.close_path()), SUN, lw=5)
    ctx.restore()

def storm(ctx, x, y, s, t, rain=True):
    """nuage d'orage qui « pleut » des poils"""
    if s <= 0.01: return
    if rain:
        for i in range(9):
            ph = (t * 1.6 + i * 0.37) % 1.0
            rx = x + (i - 4) * 26 * s; ry = y + 40 * s + ph * 200 * s
            ctx.new_path(); ctx.move_to(rx, ry); ctx.curve_to(rx + 6 * s, ry + 12 * s, rx - 6 * s, ry + 20 * s, rx + 2 * s, ry + 32 * s)
            ctx.set_source_rgba(0.08, 0.06, 0.05, 1 - ph); ctx.set_line_width(5 * s); ctx.set_line_cap(1); ctx.stroke()
    cloud(ctx, x, y, s, STORM, t)
    bolt(ctx, x + 20 * s, y + 30 * s, 0.9 * s, t)

def alert_tri(ctx, x, y, s, t):
    k = 1 + 0.08 * math.sin(t * 12)
    ctx.save(); ctx.translate(x, y); ctx.scale(s * k, s * k)
    ink_fill(ctx, lambda c: (c.move_to(0, -60), c.line_to(64, 52), c.line_to(-64, 52), c.close_path()), ORG, lw=6)
    text(ctx, '!', 0, 14, 70, fill=INK, stroke=None, shadow=False)
    ctx.restore()

def tv_bug(ctx, t, y=385):
    """logo de chaîne « RAY MÉTÉO » + petit soleil"""
    ctx.new_path(); rrect(ctx, 70, y - 34, 330, 68, 14); ctx.set_source_rgb(*NAVY); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    text(ctx, 'RAY MÉTÉO', 250, y + 2, 42, fill=(1, 1, 1), stroke=None, shadow=False)
    sun(ctx, 108, y, 0.26, t)

def alert_band(ctx, t, t0, txt='VIGILANCE ORANGE', sub='POILS SUR TOUT LE COU', y=520):
    k = ease_out((t - t0) / 0.3)
    if k <= 0: return
    x = -900 + 960 * k
    ctx.new_path(); rrect(ctx, x, y - 50, 840, 100, 14); ctx.set_source_rgb(*ORG); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, txt, x + 470, y + 2, 72, fill=INK, stroke=None, shadow=False)
    alert_tri(ctx, x + 70, y, 0.6, t)
    ctx.new_path(); rrect(ctx, x + 60, y + 50, 720, 60, 10); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    text(ctx, sub, x + 420, y + 81, 44, fill=INK, stroke=None, shadow=False)

def lower_third(ctx, t, t0, y=1040):
    k = ease_out((t - t0) / 0.3)
    if k <= 0: return
    x = -500 + 560 * k
    ctx.new_path(); rrect(ctx, x, y - 44, 600, 88, 12); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    ctx.new_path(); rrect(ctx, x, y + 34, 440, 52, 10); ctx.set_source_rgb(*SUN); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    text(ctx, 'PHILIPS ONEBLADE 360', x + 300, y + 2, 54, fill=INK, stroke=None, shadow=False)
    text(ctx, "l'éclaircie du jour", x + 220, y + 62, 36, font='Patrick Hand', fill=INK, stroke=None, shadow=False)

def lea(ctx, t, sh, x=190, fy=1385, sc=0.5, **kw):
    kw.setdefault('eyes', 'open'); kw.setdefault('brows', 0.5); kw.setdefault('smile', 0.9)
    mini(ctx, 'lea', 'L', x, fy, t, sh, sc=sc, arms=kw.pop('arms', ('hip', 'point_side')), face=1, **kw)

def hamza(ctx, t, sh, x=760, fy=1385, sc=0.5, **kw):
    kw.setdefault('eyes', 'open'); kw.setdefault('brows', 0.0); kw.setdefault('smile', 0.5)
    mini(ctx, 'hamza', 'H', x, fy, t, sh, sc=sc, arms=kw.pop('arms', ('hip', 'hip')), face=-1, **kw)

def check_line(ctx, txt, x, y, k, col=SUN):
    badge(ctx, txt, x, y, 76, col, fg=INK, scale=k, rot=-0.03)
    L.check(ctx, x + text_w(ctx, txt, 76) / 2 + 60, y, 0.75, k)

def weather_card(ctx, x, y, k, kind, lab, sub, t):
    if k <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.rotate(0.03 * math.sin(t * 3 + x))
    bg = {'sun': hexc('#bfe3ff'), 'cloud': hexc('#d9dde3'), 'storm': hexc('#8d95a3')}[kind]
    ctx.new_path(); rrect(ctx, -128 + 6, -150 + 8, 256, 300, 26); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ink_fill(ctx, lambda c: rrect(c, -128, -150, 256, 300, 26), bg, lw=6)
    if kind == 'sun': sun(ctx, 0, -50, 0.62, t)
    elif kind == 'cloud': sun(ctx, 30, -80, 0.4, t); cloud(ctx, -10, -40, 0.6, (1, 1, 1), t)
    else: storm(ctx, 0, -60, 0.6, t)
    text(ctx, lab, 0, 62, 50, fill=(1, 1, 1))
    text(ctx, sub, 0, 112, 32, font='Patrick Hand', fill=INK, stroke=None, shadow=False)
    ctx.restore()

# ---------------------------------------------------------------- scènes
def draw_mt(ctx, t, sh):
    TL = sh.tl; T = TL.T; l1, l2, h1, l3, l4, h2, l5, l6, l7 = (T[c] for c, _ in ORDER)
    cap_y = 1240; ban = True; bug = True
    ctx.save()
    if t < l2:                                     # 1. la météo de ta barbe : vraie tondeuse sur le cou poilu = carte météo
        footage(ctx, 'r_rase', 0.4 + t, 1.0, 1.08, l2, 540, 700)
        storm(ctx, 330, 560, 1.0 * pop(t, 0.1), t)
        cloud(ctx, 700, 470, 0.7 * pop(t, 0.35), STORM, t + 1)
        lea(ctx, t, sh, eyes='wide' if t < 0.6 else 'open', brows=1.0, smile=1.0, jump=abs(math.sin(t * 7)) * 14)
        if t < 0.15: ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - t / 0.15)); ctx.paint()
        cap_y = 820
    elif t < h1:                                   # 2. vigilance orange : des poils partout sur le cou
        u = t - l2
        footage(ctx, 'r_rase2', 0.0, 1.12, 1.2, 3.0, 540, 760)
        ctx.set_source_rgba(1, 0.45, 0, 0.16 + 0.06 * math.sin(t * 10)); ctx.paint()
        storm(ctx, 300, 820, 0.8, t); storm(ctx, 660, 760, 0.7, t + 0.5)
        alert_band(ctx, t, l2 + 0.05)
        lea(ctx, t, sh, eyes='wide', brows=1.0, smile=0.2, arms=('face', 'point_side'))
        flash(ctx, u, col=(1, 0.6, 0.2))
        cap_y = 1240
    elif t < l3:                                   # 3. Hamza proteste : c'est mon style !
        u = t - h1
        footage(ctx, 'r_rase2', 0.0, 1.2, 1.25, 3.0, 540, 760)
        storm(ctx, 300, 760, 0.6, t)
        jy = 240 * (1 - ease_out(u / 0.3))
        hamza(ctx, t, sh, x=700, fy=1385 + jy, eyes='open', brows=-1.0, smile=0.0, arms=('hip', 'point_side'), sc=0.56)
        vein(ctx, 760, 1385 + jy - 470, t, 1.0)
        lea(ctx, t, sh, x=170, eyes='half', brows=0.8, smile=0.4, arms=('lips', 'hip'))
        badge(ctx, "C'EST MON STYLE !", SAFE_CX, 500, 90, REDL, fg=(1, 1, 1), scale=pop(t, h1 + wt('xm_h1', 'STYLE', 1.6)), rot=0.05)
        if t < h1 + wt('xm_h1', 'STYLE', 1.6):
            shock_lines(ctx, 700, 1000, t, r=230)
        flash(ctx, u)
        cap_y = 700
    elif t < l4:                                   # 4. l'éclaircie : la main prend le OneBlade
        u = t - l3
        footage(ctx, 'r_prise', 0.8 + u * 0.9, 1.0, 1.06, 3.2, 540, 900)
        tk = wt('xm_l3', 'ÉCLAIRCIE', 0.6)
        if t > l3 + tk:
            rays(ctx, 760, 560, t, SUN, alpha=0.11 * min(1, (t - l3 - tk) / 0.4))
            sun(ctx, 760, 560 + 160 * (1 - ease_out((t - l3 - tk) / 0.5)), 0.9, t)
            cloud(ctx, 300 - 500 * ease_out((t - l3 - tk) / 0.8), 520, 0.7, STORM, t)
        else:
            cloud(ctx, 300, 520, 0.7, STORM, t); cloud(ctx, 700, 560, 0.7, STORM, t + 1)
        badge(ctx, 'ÉCLAIRCIE', 380, 720, 96, SUN, fg=INK, scale=pop(t, l3 + tk), rot=-0.05)
        lower_third(ctx, t, l3 + wt('xm_l3', 'PHILIPS', 1.5))
        flash(ctx, u)
        cap_y = 1250
    elif t < h2:                                   # 5. il taille, contours, rase (vraies images)
        u = t - l4
        if u < 1.2: footage(ctx, 'r_rase', 1.6 + u, 1.02, 1.08, 1.2, 520, 800)
        else: footage(ctx, 'r_rase2', 0.6 + (u - 1.2), 1.0, 1.06, 1.6, 540, 800)
        for j, (lab, pre, d) in enumerate((('TAILLE', 'TAILLE', 0.3), ('CONTOURS', 'CONTOURS', 1.0), ('RASE', 'RASE', 1.8))):
            check_line(ctx, lab, 330, 640 + j * 120, pop(t, l4 + wt('xm_l4', pre, d)))
        sun(ctx, 770, 520, 0.55, t)
        flash(ctx, u if u < 1.2 else u - 1.2)
        cap_y = 1250
    elif t < l5:                                   # 6. Hamza : bon… d'accord. Ciel dégagé.
        u = t - h2
        footage(ctx, 'r_lisse', 0.3 + u, 1.0, 1.06, 2.4, 540, 800)
        rays(ctx, 720, 520, t, SUN, alpha=0.09)
        sun(ctx, 720, 520, 0.8 * pop(t, h2 + 0.05), t)
        tc = h2 + wt('xm_h2', 'CIEL', 1.2)
        badge(ctx, 'CIEL DÉGAGÉ', 360, 760, 100, hexc('#bfe3ff'), fg=INK, scale=pop(t, tc), rot=-0.04)
        hz = t >= tc
        hamza(ctx, t, sh, x=740, eyes='heart' if hz else 'half', brows=0.6 if hz else -0.3, smile=1.0 if hz else 0.2,
              arms=('cheer', 'hip') if hz else ('chin', 'hip'), sc=0.52)
        if hz:
            for i in range(4): sparkle(ctx, 640 + 70 * i, 900 - 40 * (i % 2), 22, t, ph=i)
        flash(ctx, u)
        cap_y = 1240
    elif t < l6:                                   # 7. le prix
        u = t - l5
        t2 = l5 + wt('xm_l5', '29,99', 1.7)
        if t < t2:
            footage(ctx, 'r_kit2', 0.3 + u * 0.8, 1.0, 1.06, 2.0, 540, 900)
            price_tag(ctx, SAFE_CX - 80, 650, 0.85 * pop(t, l5 + 0.05), t, '50,99 €', sub=None, col=(1, 1, 1))
            flash(ctx, u)
        else:
            footage(ctx, 'r_kit', 0.5 + (t - t2) * 0.6, 1.0, 1.05, 2.5, 540, 1000)
            price_tag(ctx, 300, 560, 0.55, t, '50,99 €', sub=None, col=(1, 1, 1))
            ks = ease_out((t - t2) / 0.25)
            ctx.new_path(); ctx.move_to(170, 600); ctx.line_to(170 + 270 * ks, 510); ctx.set_source_rgb(*REDL); ctx.set_line_width(14)
            ctx.set_line_cap(1); ctx.stroke()
            price_tag(ctx, 560, 770, 0.9 * pop(t, t2), t, '29,99 €', sub='AVEC LES COUPONS')
            coupon_note(ctx, y=890)
            sun(ctx, 790, 460, 0.45, t)
            flash(ctx, t - t2)
        cap_y = 1290; ban = False
    elif t < l7:                                   # 8. appel à l'action + prix
        u = t - l6
        footage(ctx, 'r_kit', 2.0 + u * 0.5, 1.05, 1.1, 2.5, 540, 1000)
        price_tag(ctx, SAFE_CX, 560, 0.75, t, '29,99 €', sub='AVEC LES COUPONS')
        coupon_note(ctx, y=700)
        lea(ctx, t, sh, x=780, fy=1075, sc=0.34, eyes='happy', smile=1.0, arms=('wave', 'point_down'))
        ctx.restore(); L.banner(ctx, t, BAN, bg=SUN, fg=INK); tv_bug(ctx, t)
        L.cta(ctx, t, l6 + 0.3); TL.captions(ctx, t, 860); flash(ctx, u); return
    else:                                          # 9. question météo au spectateur
        u = t - l7
        footage(ctx, 'r_kit2', 1.0 + u * 0.4, 1.0, 1.04, 4.0, 540, 900)
        ctx.set_source_rgba(0.05, 0.1, 0.2, 0.35); ctx.paint()
        badge(ctx, 'ET CHEZ TOI ?', SAFE_CX, 450, 92, SUN, fg=INK, scale=pop(t, l7 + 0.05), rot=-0.04)
        for j, (kind, lab, sub, pre, d) in enumerate((('sun', 'SOLEIL', 'tout rasé', 'SOLEIL', 0.6),
                                                      ('cloud', 'NUAGES', 'barbe de 3 jours', 'NUAGES', 1.0),
                                                      ('storm', 'TEMPÊTE', 'grosse barbe', 'TEMPÊTE', 1.4))):
            weather_card(ctx, 205 + j * 275, 700, pop(t, l7 + wt('xm_l7', pre, d)), kind, lab, sub, t)
        comment_bubble(ctx, 830, 445, 0.6 * pop(t, l7 + wt('xm_l7', 'DIS-LE', 2.2)), t)
        ctx.restore(); L.banner(ctx, t, BAN, bg=SUN, fg=INK); tv_bug(ctx, t)
        L.cta(ctx, t, l6 + 0.3); TL.captions(ctx, t, 960, size=90); flash(ctx, u); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=SUN, fg=INK)
    if bug: tv_bug(ctx, t)
    TL.captions(ctx, t, cap_y)

def build_mt():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, gap=0.05, tail=0.75); T = TL.T
    l1, l2, h1, l3, l4, h2, l5, l6, l7 = (T[c] for c, _ in ORDER)
    t29 = l5 + wt('xm_l5', '29,99', 1.7)
    sfx = [('whoosh', 0.0, 0.6), ('bells', 0.05, 0.4), ('pop', 0.12, 0.4), ('pop', 0.38, 0.35),
           ('buzz', l2 + wt('xm_l2', 'DES', 0.65), 0.2),
           ('boing', h1 + 0.05, 0.5), ('stamp', h1 + wt('xm_h1', 'STYLE', 1.6), 0.6),
           ('whoosh', l3 - 0.02, 0.5), ('sparkle', l3 + wt('xm_l3', 'ÉCLAIRCIE', 0.6), 0.7), ('swipe', l3 + wt('xm_l3', 'PHILIPS', 1.5), 0.4),
           ('swipe', l4 - 0.02, 0.5), ('ding', l4 + wt('xm_l4', 'TAILLE', 0.3), 0.5), ('ding', l4 + wt('xm_l4', 'CONTOURS', 1.0), 0.5),
           ('ding', l4 + wt('xm_l4', 'RASE', 1.8), 0.5),
           ('whoosh', h2 - 0.02, 0.5), ('heart', h2 + wt('xm_h2', 'CIEL', 1.2), 0.6), ('sparkle', h2 + wt('xm_h2', 'CIEL', 1.2) + 0.1, 0.5),
           ('swipe', l5 - 0.03, 0.6), ('pop', l5 + 0.05, 0.5), ('scratch', t29, 0.4), ('coins', t29 + 0.05, 0.6),
           ('whoosh', l6 - 0.03, 0.5), ('ding', l6 + 0.35, 0.7),
           ('swipe', l7 - 0.03, 0.5), ('pop', l7 + wt('xm_l7', 'SOLEIL', 0.6), 0.45), ('pop', l7 + wt('xm_l7', 'NUAGES', 1.0), 0.45),
           ('pop', l7 + wt('xm_l7', 'TEMPÊTE', 1.4), 0.45), ('bells', l7 + wt('xm_l7', 'DIS-LE', 2.2), 0.35)]
    sh = Shot('meteo_barbe', TL.dur, draw_mt, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
