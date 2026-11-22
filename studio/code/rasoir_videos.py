# -*- coding: utf-8 -*-
"""Philips OneBlade 360 : 1) sketch « Quelle barbe te va ? »  2) présentation  3) choc du prix (capture de la fiche)."""
import math, random, cairo
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash, shake_at, speed_lines
import sklib as L
from sklib import SAFE_CX, CAP_Y, view, actor
from chars import draw_char
from sketch import bg_room

MX, SX, CY = 330, 770, 700
LIME = hexc('#c6e000'); DARK = hexc('#2b2e33'); BEARD = hexc('#5a3a28')
ROOT = S.ROOT

# ------------------------------------------------------------------ accessoires
def oneblade(ctx, x, y, s, t, rot=0.0, buzz=False):
    sd = boil_seed(t) + 1400
    if buzz: x += 3 * math.sin(t * 90); y += 2 * math.cos(t * 80)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -42, -150, 84, 330, 40), LIME, lw=6)
    ink_fill(ctx, lambda c: rrect(c, -28, -110, 56, 270, 26), DARK, lw=4)
    ink_fill(ctx, lambda c: c.arc(0, 40, 13, 0, 7), hexc('#444850'), lw=3)
    ink_fill(ctx, lambda c: blob(c, [(-26, -150), (26, -150), (20, -185), (-20, -185)], sd, 0.5), DARK, lw=4)
    ink_fill(ctx, lambda c: rrect(c, -80, -215, 160, 34, 8), hexc('#c9ccd2'), lw=5)
    ink_fill(ctx, lambda c: c.rectangle(-80, -190, 160, 10), LIME, lw=3)
    for i in range(9):
        ctx.new_path(); ctx.move_to(-70 + i * 17.5, -212); ctx.line_to(-70 + i * 17.5, -186)
        ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    if buzz:
        for k in range(3):
            ctx.new_path(); ctx.arc(x, y - 200 * s, 60 * s + k * 22 * s, -2.4, -0.7); ctx.set_source_rgba(*INK, 0.6); ctx.set_line_width(4); ctx.stroke()

def beard(ctx, x, y, sc, style, t, tilt=0.0, alpha=1.0, color=None):
    """barbe dessinée sur la tête (centre x, y ; échelle sc). Le trou laisse la bouche visible."""
    if style in (None, 'clean'): return
    BEARD = color or (hexc('#f4f4f4') if style == 'santa' else hexc('#5a3a28'))
    if style == 'santa': style = 'viking'
    bush = style == 'bush'
    if bush: style = 'full'
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate(tilt)
    sd = 77 + boil_seed(t, 6)
    def mouth_hole(c):
        c.new_sub_path(); c.save(); c.translate(0, 80); c.scale(52, 34); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
    col = BEARD + (alpha,)
    if style in ('full', 'viking', 'stubble', 'patchy'):
        ext = 330 if style == 'viking' else (250 if bush else 150)
        wx_ = 1.35 if bush else 1.0
        pts = [(-104 * wx_, -10), (-100 * wx_, 60), (-70 * wx_, 110), (-30, ext - 10), (0, ext), (30, ext - 10), (70 * wx_, 110), (100 * wx_, 60), (104 * wx_, -10),
               (78, 30), (40, 52), (0, 46), (-40, 52), (-78, 30)]
        ctx.new_path(); blob(ctx, pts, sd, 1.6); mouth_hole(ctx); ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        if style == 'stubble':
            ctx.save(); ctx.clip()
            rnd = random.Random(5)
            for i in range(260):
                px, py = rnd.uniform(-105, 105), rnd.uniform(-10, 160)
                ctx.new_path(); ctx.arc(px, py, 2.2, 0, 7); ctx.set_source_rgba(*BEARD, 0.85 * alpha); ctx.fill()
            ctx.restore()
        elif style == 'patchy':
            ctx.save(); ctx.clip()
            rnd = random.Random(9)
            for i in range(9):
                px, py = rnd.uniform(-90, 90), rnd.uniform(0, 140)
                ctx.new_path(); blob(ctx, ellipse_pts(px, py, rnd.uniform(14, 34), rnd.uniform(10, 26), 8), sd + i, 2)
                ctx.set_source_rgba(*col); ctx.fill_preserve(); ctx.set_source_rgba(*INK, 0.7 * alpha); ctx.set_line_width(3); ctx.stroke()
            ctx.set_source(hatch_pattern(6, 45, 1.5, True, 0.4)); ctx.paint()
            ctx.restore()
        else:
            ctx.set_source_rgba(*col); ctx.fill_preserve(); ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
            ctx.save(); ctx.clip_preserve(); ctx.set_source(hatch_pattern(7, 45, 1.6, True, 0.5)); ctx.paint(); ctx.restore()
            ctx.set_source_rgba(*INK, alpha); ctx.set_line_width(5); ctx.stroke()
            if bush:  # feuilles dans le buisson
                rnd = random.Random(4)
                for i in range(14):
                    px, py = rnd.uniform(-120, 120), rnd.uniform(100, 230)
                    ink_fill(ctx, lambda c, px=px, py=py: blob(c, ellipse_pts(px, py, 14, 8, 7, rnd.uniform(0, 3)), sd + i, 0.4), hexc('#3e8a3a'), lw=2.5)
            if style == 'viking':  # tresses
                for bx in (-26, 26):
                    for k in range(4):
                        ink_fill(ctx, lambda c, bx=bx, k=k: blob(c, ellipse_pts(bx, 200 + k * 34, 16, 20, 8), sd + k, 0.6), BEARD, lw=3)
                    ink_fill(ctx, lambda c, bx=bx: c.rectangle(bx - 14, 340, 28, 12), GOLD, lw=3)
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    if style in ('moustache', 'full', 'viking', 'goatee'):
        curl = style == 'moustache'
        for sgn in (-1, 1):
            pts = [(0, 48), (sgn * 30, 42), (sgn * 62, 52), (sgn * (88 if curl else 56), 40 if curl else 62),
                   (sgn * (98 if curl else 50), 18 if curl else 66), (sgn * 70, 62), (sgn * 30, 60), (0, 58)]
            ink_fill(ctx, lambda c, pts=pts: blob(c, pts, sd + 30 + sgn, 0.8), BEARD, lw=4)
    if style == 'goatee':
        ink_fill(ctx, lambda c: blob(c, [(-34, 112), (34, 112), (24, 175), (0, 190), (-24, 175)], sd + 40, 1.2), BEARD, lw=4)
    ctx.restore()

def phone_ar(ctx, t, t0, styles, sh, cx=SAFE_CX, cy=760, mood=None, who='david', outfit='rose', tag='S'):
    """téléphone plein écran : appli OneBlade, essai de barbes en réalité augmentée"""
    u = t - t0; k = ease_out_back(min(1, u / 0.35))
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k); ctx.rotate(-0.03)
    w, h = 600, 1000
    ctx.new_path(); rrect(ctx, -w / 2 + 12, -h / 2 + 16, w, h, 60); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ink_fill(ctx, lambda c: rrect(c, -w / 2, -h / 2, w, h, 60), hexc('#1b1c20'), lw=7)
    ctx.save(); ctx.new_path(); rrect(ctx, -w / 2 + 22, -h / 2 + 22, w - 44, h - 44, 44); ctx.clip()
    ctx.set_source_rgb(*hexc('#2a2f3a')); ctx.paint()
    # style courant
    cur = styles[0][1]
    for ts, name, lab in styles:
        if u >= ts: cur = (name, lab)
    name, lab = cur if isinstance(cur, tuple) else (styles[0][1], styles[0][2])
    face_y = -40
    m = mood or {}
    draw_char(ctx, who, 0, face_y, 1.45, t + 0.7, outfit=outfit, mouth=sh.mouth(tag, t), **m)
    beard(ctx, 0, face_y, 1.45, name, t, tilt=m.get('tilt', 0.0))
    # repères de suivi du visage
    for (px, py) in [(-150, face_y - 30), (150, face_y - 30), (0, face_y + 40), (-110, face_y + 150), (110, face_y + 150), (0, face_y + 230)]:
        ctx.new_path(); ctx.arc(px, py, 7, 0, 7); ctx.set_source_rgba(0.4, 1, 0.9, 0.9); ctx.fill()
    ctx.new_path(); rrect(ctx, -180, -h / 2 + 50, 360, 70, 35); ctx.set_source_rgba(0, 0, 0, 0.55); ctx.fill()
    text(ctx, 'ESSAI DE BARBE', 0, -h / 2 + 85, 44, fill=(1, 1, 1), stroke=None, shadow=False)
    # carrousel de styles en bas
    for i, (ts, nm, lb) in enumerate(styles):
        bx = -200 + i * 133; by = h / 2 - 130; act = nm == name
        ctx.new_path(); ctx.arc(bx, by, 52 if act else 42, 0, 7); ctx.set_source_rgb(*(LIME if act else (0.85, 0.85, 0.88))); ctx.fill()
        ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
        beard(ctx, bx, by - 50, 0.33, nm, t)
    ctx.restore(); ctx.restore()
    ksel = pop(t, t0 + styles[[s[1] for s in styles].index(name)][0], 0.25)
    badge(ctx, lab, cx, cy + 300, 76, LIME if name == 'stubble' else (hexc('#c3302f') if name == 'santa' else hexc('#141414')), fg=INK if name == 'stubble' else (1, 1, 1),
          scale=ksel, rot=-0.04)

def fiche_band(ctx, t, t0, cx=SAFE_CX, cy=700, sc=0.86, circle_t=None, strike_t=None):
    """capture réelle de la fiche (bandeau prix) qui arrive, puis entourage de 29,99 €"""
    u = t - t0; k = ease_out_back(min(1, u / 0.35))
    img = load_png(f'{ROOT}/seg/fiche_prix_band.png')
    w, h = img.get_width(), img.get_height()
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc * k, sc * k); ctx.rotate(-0.02)
    ctx.new_path(); rrect(ctx, -w / 2 + 14, -h / 2 + 18, w, h, 30); ctx.set_source_rgba(*INK, 0.55); ctx.fill()
    ctx.save(); ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, 30); ctx.clip()
    ctx.set_source_surface(img, -w / 2, -h / 2); ctx.paint(); ctx.restore()
    ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, 30); ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.stroke()
    # coordonnées dans la capture (1080 x 520) : 50,99 € vers (165, 115) ; 29,99 € vers (700, 370)
    if strike_t is not None and t >= strike_t:
        kk = ease((t - strike_t) / 0.25)
        ctx.new_path(); ctx.move_to(-w / 2 + 40, -h / 2 + 130); ctx.line_to(-w / 2 + 40 + 260 * kk, -h / 2 + 100)
        ctx.set_source_rgb(*hexc('#e8263d')); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    if circle_t is not None and t >= circle_t:
        kk = ease((t - circle_t) / 0.35)
        ctx.save(); ctx.translate(-w / 2 + 700, -h / 2 + 368); ctx.scale(200, 70)
        ctx.new_path(); ctx.arc(0, 0, 1, -math.pi / 2, -math.pi / 2 + 2 * math.pi * kk); ctx.restore()
        ctx.set_source_rgb(*hexc('#e8263d')); ctx.set_line_width(12); ctx.stroke()
    ctx.restore()

_PNG = {}
def load_png(p):
    if p not in _PNG:
        from PIL import Image
        import numpy as np
        im = Image.open(p).convert('RGB'); a = np.asarray(im)
        bgra = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)])
        _PNG[p] = surf_from_array(bgra)
    return _PNG[p]

def fiche_kit(ctx, t, alpha=1.0):
    """photo du kit (fiche) en entier, centrée, avec léger zoom"""
    img = load_png(f'{ROOT}/seg/fiche_kit.png')
    ctx.set_source_rgb(*hexc('#a9c8ef')); ctx.paint()
    ctx.save(); sc = 1080 / img.get_width() * (1.0 + 0.015 * math.sin(t * 0.8)); ctx.translate(540, 1000); ctx.scale(sc, sc)
    ctx.translate(-img.get_width() / 2, -img.get_height() / 2); ctx.set_source_surface(img, 0, 0); ctx.paint_with_alpha(alpha); ctx.restore()

def coupon_note(ctx, y=1010):
    text(ctx, 'Prix avec les coupons affichés sur la fiche, selon disponibilité', SAFE_CX, y, 30, font='Patrick Hand',
         fill=(1, 1, 1), sw=5, max_w=820)

def bf_badge(ctx, t, t0, y=440):
    badge(ctx, "BLACK FRIDAY : JUSQU'AU 30 NOV.", SAFE_CX, y, 58, hexc('#6a1b4d'), fg=(1, 1, 1), scale=pop(t, t0), rot=-0.03)

# ------------------------------------------------------------------ mots (remplis par make_rasoir.py)
WORDS = {}

# ================================================================== 1. SKETCH « QUELLE BARBE TE VA ? »
ORDER1 = [('xr_s1', 'S'), ('xr_m1', 'M'), ('xr_s2', 'S'), ('xr_m2', 'M'), ('xr_s3', 'S'), ('xr_m3', 'M'), ('xr_s4', 'S'),
          ('xr_m4', 'M'), ('xr_m5', 'M')]
BAN1 = "QUELLE BARBE TE VA ?"
AR_STYLES = [(0.0, 'viking', 'VIKING'), (0.75, 'moustache', 'MOUSTACHE'), (2.35, 'goatee', 'BOUC'), (3.05, 'stubble', 'BARBE DE 3 JOURS')]

def tl1():
    return L.Timeline(ORDER1, {'xr_s3': 0.85, 'xr_m3': 1.9, 'xr_m5': 0.1}, WORDS)

def draw1(ctx, t, sh):
    TL = sh.tl; T = TL.T
    s1, m1, s2, m2, s3, m3, s4, m4, m5 = (T[c] for c, _ in ORDER1)
    ar0 = m2 + clip_len('xr_m2') + 0.07
    ctx.save()
    # ---- appli en réalité augmentée
    if ar0 <= t < m3:
        u = t - ar0
        ctx.save(); view(ctx, 1.3, SX, CY + 40, t=t); bg_room(ctx, t); ctx.restore()
        ctx.set_source_rgba(0, 0, 0, 0.35); ctx.paint()
        horrified = s3 <= t < s3 + clip_len('xr_s3') + 0.2
        mood = dict(eyes='tiny', brows=1.0, smile=-0.8, look=(0, 0)) if horrified else \
            dict(eyes='open' if u < 3.1 else 'happy', brows=0.4, smile=0.6 if u < 3.1 else 1.0, look=(0, 0))
        phone_ar(ctx, t, ar0, AR_STYLES, sh, mood=mood)
        if horrified: text(ctx, 'NON !', 760, 470, 140, fill=hexc('#e8263d'), scale=pop(t, s3), rot=0.12)
        if u > 3.3: check_big(ctx, 760, 520, pop(t, ar0 + 3.3))
        ctx.restore(); L.banner(ctx, t, BAN1); TL.captions(ctx, t, 1330 - 100); flash(ctx, u); return
    # ---- vraies images : il rase
    if m3 <= t < s4:
        u = t - m3; d = s4 - m3
        if u < d * 0.62: footage(ctx, 'r_rase', u, 1.0, 1.1, d * 0.62, 540, 900)
        else: footage(ctx, 'r_lisse', u - d * 0.62, 1.0, 1.08, d * 0.4, 540, 900)
        for i, (lab, key) in enumerate((('TAILLE', 'TAILLE,'), ('CONTOURS', 'CONTOURS'), ('RASE', 'RASE,'))):
            r = next((rr for ww, rr in WORDS['xr_m3'] if ww.startswith(key[:5])), 0.6 + i * 0.6)
            badge(ctx, lab, 250 + i * 230, 470 + (i % 2) * 70, 66, LIME if i != 1 else hexc('#141414'),
                  fg=INK if i != 1 else LIME, scale=pop(t, m3 + r), rot=-0.05 + 0.05 * i)
        flash(ctx, u if u < d * 0.62 else u - d * 0.62)
        ctx.restore(); L.banner(ctx, t, BAN1); TL.captions(ctx, t); return
    # ---- prix : capture de la fiche
    if m4 <= t < m5:
        u = t - m4
        fiche_kit(ctx, t); ctx.set_source_rgba(0, 0, 0, 0.45); ctx.paint()
        r50 = next((rr for ww, rr in WORDS['xr_m4'] if ww.startswith('50')), 2.3)
        r29 = next((rr for ww, rr in WORDS['xr_m4'] if ww.startswith('29')), 4.3)
        fiche_band(ctx, t, m4 + 1.4, cy=760, circle_t=m4 + r29, strike_t=None)
        badge(ctx, 'PHILIPS ONEBLADE 360', SAFE_CX, 470, 66, hexc('#0b5ed7'), scale=pop(t, m4 + 0.1), rot=-0.03)
        if t >= m4 + r29: coupon_note(ctx, 1030)
        ctx.restore(); L.banner(ctx, t, BAN1); TL.captions(ctx, t, 1190); flash(ctx, u); return

    # ---- caméra pour les plans dessinés
    if t < m1: cam = (1.65 + 0.04 * t, SX, CY + 30, 0)
    elif t < s2: cam = (1.6, MX, CY + 30, 0)
    elif t < m2: cam = (1.7, SX, CY + 30, shake_at(t, [s2], 8))
    elif t < ar0: cam = (1.05, 550, CY + 40, 0)
    elif t < m4: cam = (1.75 + 0.1 * ease((t - s4) / 1.2), SX, CY + 30, 0)
    else: cam = (1.08, 550, CY + 60, 0)
    z, wx, wy, shk = cam
    view(ctx, z, wx, wy, shake=shk, t=t); bg_room(ctx, t)
    clean = t >= s4
    # ---- M (le malin)
    mk = dict(smile=0.8, eyes='half', brows=0.4, look=(1, 0), arms=('down', 'hold'),
              prop=lambda c, x, y, tt: oneblade(c, x + 5, y - 60, 0.55, tt, 0.25), prop_hand='R')
    if m1 <= t < s2: mk.update(arms=('down', ('hold', 'give', (t - m1) / 0.35)), smile=1.0, look=(1, 0))
    elif m2 <= t < ar0: mk.update(arms=('down', 'hold_high'), eyes='open', smile=1.0,
                                  prop=lambda c, x, y, tt: phone(c, x, y - 40, 0.75, tt, rot=0.1), prop_hand='R')
    elif t >= m5: mk.update(arms=(('down', 'point_down', (t - m5) / 0.3), 'hold_high'), eyes='open', look=(-0.4, 0.7))
    if z < 1.3 or (m1 <= t < s2):
        actor(ctx, 'david', MX, CY, t, sh, 'M', **mk)
    # ---- S (avec la barbe mal taillée, puis rasé)
    sk = dict(smile=-0.3, eyes='open', brows=1.0, look=(-1, 0), arms=('down', 'chin'), tilt=0.0)
    ssq = 0.0
    if t < m1: sk.update(eyes='open', brows=1.0, smile=-0.6, look=(0, 0.5), arms=('down', 'chin'), tilt=0.06 * math.sin(t * 5))
    elif s2 <= t < m2: sk.update(eyes='half', brows=-0.6, smile=0.3, look=(-1, 0), arms=('hip', 'down'), tilt=-0.08)
    elif m2 <= t < ar0: sk.update(eyes='wide', brows=0.8, smile=0.2, look=(-1, 0.3))
    elif s4 <= t < m4:
        sk.update(eyes='heart', brows=1.0, smile=1.0, look=(0, 0), arms=('cheer', 'face'), blush=1.0)
        ssq = spring(t, s4, -0.08)
    elif t >= m5: sk.update(eyes='happy', smile=1.0, arms=('cheer', 'down'))
    if z < 1.3 or t < m1 or (s2 <= t < m2) or (s4 <= t < m4):
        actor(ctx, 'david', SX, CY, t, sh, 'S', sq=ssq, outfit='rose', **sk)
        if not clean: beard(ctx, SX, CY, 0.95, 'patchy', t, tilt=sk.get('tilt', 0.0))
        else: beard(ctx, SX, CY, 0.95, 'stubble', t, tilt=sk.get('tilt', 0.0), alpha=0.8)
        if s4 <= t < m4:
            for i in range(8): sparkle(ctx, SX + 200 * math.cos(i * 0.8 + t), CY + 40 + 180 * math.sin(i * 1.3), 26, t, i)
        if t < m1: sweat(ctx, SX + 95, CY - 90, t, 1.1)
    ctx.restore()
    if t < m1: text(ctx, '?!', 760, 520, 170, fill=YEL, scale=pop(t, 0.5), rot=0.12)
    if s4 <= t < m4: text(ctx, '- 10 ANS !', 720, 500, 130, fill=LIME, scale=pop(t, s4 + 0.4), rot=0.1)
    if t >= m5:
        bf_badge(ctx, t, m5 + 0.05, 440); L.cta(ctx, t, m5 + RCTA)
    L.banner(ctx, t, BAN1)
    TL.captions(ctx, t, 990 if t >= m5 else CAP_Y)
    cuts = [m1, s2, m2, ar0, m3, s4, m4, m5]
    flash(ctx, min([t - c for c in cuts if c <= t] or [9]), 0.08)

def check_big(ctx, x, y, k):
    L.check(ctx, x, y, 2.4, k)

RCTA = 3.0

def build1():
    TL = tl1(); T = TL.T
    s1, m1, s2, m2, s3, m3, s4, m4, m5 = (T[c] for c, _ in ORDER1)
    ar0 = m2 + clip_len('xr_m2') + 0.07
    sfx = [('scratch', 0.1, 0.3), ('boing', 0.5, 0.5), ('whoosh', m1 - 0.03, 0.4), ('pop', m1 + 0.3, 0.5), ('whoosh', s2 - 0.03, 0.4),
           ('ding', m2 + 0.3, 0.5), ('whoosh', ar0, 0.6), ('pop', ar0 + 0.1, 0.6)]
    for ts, _, _ in AR_STYLES: sfx += [('swipe', ar0 + ts, 0.6), ('pop', ar0 + ts + 0.05, 0.4)]
    sfx += [('scratch', s3 - 0.05, 0.8), ('ding', ar0 + 3.3, 0.8), ('whoosh', m3 - 0.03, 0.6), ('buzz', m3 + 0.05, 0.9),
            ('sparkle', s4, 0.9), ('heart', s4 + 0.3, 0.6), ('whoosh', m4 - 0.03, 0.5), ('pop', m4 + 1.4, 0.7),
            ('whoosh', m5 - 0.03, 0.5), ('bells', m5 + 0.05, 0.4), ('ding', m5 + RCTA + 0.05, 0.7)]
    sh = Shot('rasoir1', TL.dur, draw1, TL.voices(), sfx, []); sh.tl = TL
    return [sh], (s3 - 0.1, s3 + clip_len('xr_s3') + 0.1)

# ================================================================== 2. PRÉSENTATION
ORDER2 = [('xr_p1', 'M'), ('xr_p2', 'M'), ('xr_p3', 'M'), ('xr_p4', 'M'), ('xr_m5', 'M')]
BAN2 = "LE RASOIR QUI FAIT TOUT"

def tl2():
    return L.Timeline(ORDER2, {'xr_p2': 0.05, 'xr_p3': 0.05, 'xr_p4': 0.05, 'xr_m5': 0.1}, WORDS)

def wt(clip, prefix, default):
    return next((rr for ww, rr in WORDS[clip] if ww.startswith(prefix)), default)

def draw2(ctx, t, sh):
    TL = sh.tl; T = TL.T; p1, p2, p3, p4, m5 = (T[c] for c, _ in ORDER2)
    ctx.save()
    if t < p2:                                     # présentateur + 3 actions
        view(ctx, 1.35 + 0.04 * t, MX + 140, CY + 70, t=t)
        bg_room(ctx, t); S.rays(ctx, MX + 140, CY, t, (1, 1, 1), 16, 0.22, 0.3)
        actor(ctx, 'david', MX + 140, CY, t, sh, 'M', smile=1.0, eyes='open', brows=0.6, look=(0, 0.2), arms=('hip', 'hold_high'),
              prop=lambda c, x, y, tt: oneblade(c, x + 5, y - 60, 0.6, tt, 0.25, buzz=True), prop_hand='R', tilt=-0.03 * math.sin(t * 4))
        ctx.restore()
        for i, (lab, pre) in enumerate((('TAILLE', 'TAILLE'), ('CONTOURS', 'CONTOURS'), ('RASE', 'RASE'))):
            badge(ctx, lab, 230 + i * 240, 470 + (i % 2) * 70, 66, LIME if i != 1 else hexc('#141414'), fg=INK if i != 1 else LIME,
                  scale=pop(t, p1 + wt('xr_p1', pre, 0.8 + 0.6 * i)), rot=-0.05 + 0.05 * i)
    elif t < p3:                                   # lame 360, visage + corps
        u = t - p2; d = p3 - p2
        if u < d * 0.55: footage(ctx, 'r_prise', u, 1.0, 1.12, d * 0.55, 540, 800); fl = u
        else: footage(ctx, 'r_rase2', u - d * 0.55, 1.0, 1.1, d * 0.45, 540, 900); fl = u - d * 0.55
        badge(ctx, 'LAME 360', SAFE_CX - 150, 470, 76, LIME, fg=INK, scale=pop(t, p2 + wt('xr_p2', '360', 0.6)), rot=-0.05)
        badge(ctx, 'VISAGE + CORPS', SAFE_CX + 60, 600, 70, hexc('#141414'), fg=LIME, scale=pop(t, p2 + wt('xr_p2', 'CORPS', 3.2) - 0.6), rot=0.04)
        flash(ctx, fl); ctx.restore()
    elif t < p4:                                   # étanche, sec / mousse, appli
        u = t - p3; d = p4 - p3
        if u < d * 0.5: footage(ctx, 'r_kit', u, 1.0, 1.1, d * 0.5, 540, 900); fl = u
        else: footage(ctx, 'r_lisse2', u - d * 0.5, 1.0, 1.08, d * 0.5, 540, 900); fl = u - d * 0.5
        for i, (lab, pre, col) in enumerate((('ÉTANCHE', 'ÉTANCHE', hexc('#4aa8d8')), ('À SEC OU AVEC MOUSSE', 'SEC', (1, 1, 1)),
                                             ('APPLI GRATUITE', 'APPLICATION', LIME))):
            L.check(ctx, 140, 470 + i * 120, 1.1, pop(t, p3 + wt('xr_p3', pre, 0.5 + i)))
            badge(ctx, lab, 140 + 60 + 20 + text_w(ctx, lab, 62) / 2 + 20, 470 + i * 120, 62, col, fg=INK,
                  scale=pop(t, p3 + wt('xr_p3', pre, 0.5 + i)), rot=0)
        flash(ctx, fl); ctx.restore()
    elif t < m5:                                   # prix (capture de la fiche)
        u = t - p4
        fiche_kit(ctx, t); ctx.set_source_rgba(0, 0, 0, 0.45); ctx.paint()
        fiche_band(ctx, t, p4 + 0.1, cy=760, circle_t=p4 + wt('xr_p4', '29', 3.0))
        if t >= p4 + wt('xr_p4', '29', 3.0): coupon_note(ctx, 1030)
        flash(ctx, u); ctx.restore()
    else:                                          # appel à l'action
        footage(ctx, 'r_kit', min(t - m5, 2.9), 1.0, 1.1, 3.0, 540, 900); flash(ctx, t - m5)
        bf_badge(ctx, t, m5 + 0.05, 600); L.cta(ctx, t, m5 + RCTA)
        ctx.restore()
        L.banner(ctx, t, BAN2, bg=LIME, fg=INK); TL.captions(ctx, t, 990); return
    L.banner(ctx, t, BAN2, bg=LIME, fg=INK)
    TL.captions(ctx, t, CAP_Y)

def build2():
    TL = tl2(); T = TL.T; p1, p2, p3, p4, m5 = (T[c] for c, _ in ORDER2)
    sfx = [('buzz', 0.05, 0.7)]
    for pre in ('TAILLE', 'CONTOURS', 'RASE'): sfx.append(('pop', p1 + wt('xr_p1', pre, 1.0), 0.5))
    sfx += [('whoosh', p2 - 0.03, 0.5), ('pop', p2 + wt('xr_p2', '360', 0.6), 0.5), ('whoosh', p3 - 0.03, 0.5)]
    for pre in ('ÉTANCHE', 'SEC', 'APPLICATION'): sfx.append(('ding', p3 + wt('xr_p3', pre, 1.0), 0.5))
    sfx += [('whoosh', p4 - 0.03, 0.5), ('pop', p4 + 0.15, 0.6), ('stamp', p4 + wt('xr_p4', '29', 3.0), 0.7),
            ('whoosh', m5 - 0.03, 0.5), ('ding', m5 + RCTA + 0.05, 0.7)]
    sh = Shot('rasoir2', TL.dur, draw2, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None

# ================================================================== 3. CHOC DU PRIX
ORDER3 = [('xr_c1', 'M'), ('xr_c2', 'M'), ('xr_p1', 'M'), ('xr_m5', 'M')]
BAN3 = "PHILIPS À MOINS DE 30 € ?!"

def tl3():
    return L.Timeline(ORDER3, {'xr_c2': 0.05, 'xr_p1': 0.08, 'xr_m5': 0.1}, WORDS)

def draw3(ctx, t, sh):
    TL = sh.tl; T = TL.T; c1, c2, p1, m5 = (T[c] for c, _ in ORDER3)
    ctx.save()
    if t < c2:                                     # choqué, il sort son téléphone
        attends = c1 + wt('xr_c1', 'ATTENDS', 1.6)
        view(ctx, 1.75 + 0.06 * t, MX, CY + 30, t=t, shake=shake_at(t, [0.05], 18))
        bg_room(ctx, t)
        actor(ctx, 'david', MX, CY, t, sh, 'M', eyes='tiny' if t < attends else 'half', brows=1.0 if t < attends else 0.5,
              smile=-0.2 if t < attends else 0.9, look=(0, 0), arms=('face', 'face') if t < attends else ('down', 'hold_high'),
              prop=None if t < attends else (lambda c, x, y, tt: phone(c, x, y - 40, 0.75, tt, rot=0.1)), prop_hand='R',
              sq=spring(t, 0.05, -0.1))
        if t < attends: shock_lines(ctx, MX, CY, t, 190)
        ctx.restore()
        text(ctx, '29,99 € ?!', 640, 480, 140, fill=YEL, scale=pop(t, 0.25), rot=0.1)
    elif t < p1:                                   # la fiche : barré, entouré
        u = t - c2
        fiche_kit(ctx, t); ctx.set_source_rgba(0, 0, 0, 0.5); ctx.paint()
        z = 1.0 + 0.12 * ease(u / (p1 - c2))
        r29 = wt('xr_c2', '29', 1.6); r50 = wt('xr_c2', '50', 3.0)
        fiche_band(ctx, t, c2 + 0.05, cy=760, sc=0.86 * z, circle_t=c2 + r29, strike_t=c2 + r50)
        badge(ctx, 'AVEC LES COUPONS', SAFE_CX, 470, 72, hexc('#e8263d'), scale=pop(t, c2 + 0.3), rot=-0.04)
        coupon_note(ctx, 1040)
        flash(ctx, u); ctx.restore()
    elif t < m5:                                   # vraies images rapides
        u = t - p1; d = m5 - p1; cuts = [('r_prise', 0.0), ('r_rase', d * 0.33), ('r_lisse', d * 0.7)]
        for i, (nm, a) in enumerate(cuts):
            b = cuts[i + 1][1] if i + 1 < len(cuts) else d
            if a <= u < b: footage(ctx, nm, u - a, 1.0, 1.1, b - a, 540, 880); flash(ctx, u - a)
        for i, (lab, pre) in enumerate((('TAILLE', 'TAILLE'), ('CONTOURS', 'CONTOURS'), ('RASE', 'RASE'))):
            badge(ctx, lab, 230 + i * 240, 470 + (i % 2) * 70, 66, LIME if i != 1 else hexc('#141414'), fg=INK if i != 1 else LIME,
                  scale=pop(t, p1 + wt('xr_p1', pre, 0.8 + 0.6 * i)), rot=-0.05 + 0.05 * i)
        ctx.restore()
    else:
        fiche_kit(ctx, t); ctx.set_source_rgba(0, 0, 0, 0.25); ctx.paint(); flash(ctx, t - m5)
        bf_badge(ctx, t, m5 + 0.05, 600); L.cta(ctx, t, m5 + RCTA)
        ctx.restore()
        L.banner(ctx, t, BAN3, bg=hexc('#e8263d'), fg=(1, 1, 1)); TL.captions(ctx, t, 990); return
    L.banner(ctx, t, BAN3, bg=hexc('#e8263d'), fg=(1, 1, 1))
    TL.captions(ctx, t, CAP_Y)

def build3():
    TL = tl3(); T = TL.T; c1, c2, p1, m5 = (T[c] for c, _ in ORDER3)
    sfx = [('scratch', 0.0, 0.8), ('boing', 0.05, 0.6), ('swipe', c1 + wt('xr_c1', 'ATTENDS', 1.6), 0.5), ('whoosh', c2 - 0.03, 0.6),
           ('pop', c2 + 0.1, 0.6), ('ding', c2 + wt('xr_c2', '29', 1.6), 0.7), ('scratch', c2 + wt('xr_c2', '50', 3.0), 0.5),
           ('whoosh', p1 - 0.03, 0.5), ('buzz', p1 + 0.1, 0.6), ('whoosh', m5 - 0.03, 0.5), ('ding', m5 + RCTA + 0.05, 0.7)]
    sh = Shot('rasoir3', TL.dur, draw3, TL.voices(), sfx, []); sh.tl = TL
    return [sh], (0.02, 0.6)
