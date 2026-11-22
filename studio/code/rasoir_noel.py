# -*- coding: utf-8 -*-
"""OneBlade 360, thème Noël : 4) « Le cadeau » (Inès / Hamza)  5) « Le classement » (Sarah, réactions de Léa)."""
import math, random, cairo
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash, shake_at
import sklib as L
from sklib import SAFE_CX, CAP_Y, view, actor
from chars import draw_char
from sketch3 import bg_salon
from nuit import sock, medal, cross_out
from rasoir_videos import oneblade, beard, phone_ar, fiche_band, fiche_kit, coupon_note, bf_badge, LIME, WORDS
from rasoir_videos import wt as _wt

IX, HX, CY = 330, 770, 700
RCTA = 3.0
RED = hexc('#c3302f')

def wt(clip, prefix, default):
    return next((rr for ww, rr in WORDS.get(clip, []) if ww.startswith(prefix)), default)

def santa_hat(ctx, x, y, sc, t, tilt=0.0):
    sd = boil_seed(t) + 1500
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate(tilt)
    ink_fill(ctx, lambda c: blob(c, [(-118, -80), (-80, -170), (20, -215), (140, -165), (195, -70), (165, -50), (110, -120), (40, -135), (100, -80)],
                                 sd, 1.4), RED, lw=6, shade=lambda c: c.rectangle(-125, -225, 90, 170), seed=sd)
    ink_fill(ctx, lambda c: blob(c, [(-130, -92), (0, -118), (130, -92), (130, -52), (0, -72), (-130, -50)], sd + 1, 1.2), (1, 1, 1), lw=6)
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(185, -50, 28, 28, 9), sd + 2, 1.2), (1, 1, 1), lw=5)
    ctx.restore()

def ugly_sweater(ctx, x, y, s, t):
    sd = boil_seed(t) + 1600
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    pts = [(-70, -80), (-30, -90), (30, -90), (70, -80), (120, -40), (100, -10), (75, -30), (75, 90), (-75, 90), (-75, -30), (-100, -10), (-120, -40)]
    ink_fill(ctx, lambda c: blob(c, pts, sd, 1.0), hexc('#2f7a3a'), lw=6)
    ctx.save(); ctx.new_path(); blob(ctx, pts, sd, 1.0); ctx.clip()
    for yy, col in ((-40, RED), (55, RED)):
        ctx.new_path()
        for i in range(12):
            ctx.line_to(-120 + i * 22, yy + (12 if i % 2 else -12))
        ctx.set_source_rgb(*col); ctx.set_line_width(10); ctx.stroke()
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 8, 26, 22, 8), sd + 1, 0.6), hexc('#8a5a32'), lw=4)  # renne
    ink_fill(ctx, lambda c: c.arc(0, 18, 8, 0, 7), RED, lw=3)
    for sx_ in (-1, 1): ink_line(ctx, [(sx_ * 14, -10), (sx_ * 26, -32), (sx_ * 40, -30)], sd + 3, 4, color=hexc('#5a3a28'))
    ctx.restore(); ctx.restore()

def bird(ctx, x, y, t, t0):
    if t < t0: return
    k = ease_out_back(min(1, (t - t0) / 0.35)); bob = 6 * math.sin(t * 14)
    ctx.save(); ctx.translate(x, y - 40 * k + bob); ctx.scale(k, k)
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, 0, 34, 28, 10), 5, 0.6), hexc('#e8a93c'), lw=4)
    ink_fill(ctx, lambda c: blob(c, [(30, -4), (52, 4), (30, 10)], 6, 0.3), hexc('#f07a1a'), lw=3)
    ctx.new_path(); ctx.arc(12, -8, 5, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.restore()
    if t > t0 + 0.3: text(ctx, 'CUI CUI !', x + 80, y - 120, 56, fill=YEL, rot=0.1, scale=pop(t, t0 + 0.3))

# ================================================================== 4. LE CADEAU (Inès / Hamza)
ORDER4 = [('xn_i1', 'I'), ('xn_h1', 'H'), ('xn_i2', 'I'), ('xn_h2', 'H'), ('xn_i3', 'I'), ('xn_i4', 'I'), ('xn_h3', 'H'),
          ('xn_i5', 'I'), ('xn_i6', 'I')]
BAN4 = "ELLE LUI A OFFERT UN RASOIR…"
AR4 = [(0.0, 'santa', 'PÈRE NOËL'), (1.0, 'moustache', 'MOUSTACHE'), (2.0, 'stubble', 'BARBE DE 3 JOURS')]

def tl4():
    return L.Timeline(ORDER4, {'xn_h1': 1.3, 'xn_h3': 3.4, 'xn_i6': 0.1}, WORDS)

def draw4(ctx, t, sh):
    TL = sh.tl; T = TL.T
    i1, h1, i2, h2, i3, i4, h3, i5, i6 = (T[c] for c, _ in ORDER4)
    unwrap = i1 + clip_len('xn_i1') + 0.1
    ar_end = i4 + clip_len('xn_i4') + 1.25
    tbush = i2 + wt('xn_i2', 'BUISSON', 1.6)
    ctx.save()
    if i3 <= t < i4:                                   # vraies images du produit
        u = t - i3; d = i4 - i3
        if u < d * 0.5: footage(ctx, 'r_prise', u, 1.0, 1.1, d * 0.5, 540, 800); fl = u
        else: footage(ctx, 'r_rase', u - d * 0.5, 1.0, 1.1, d * 0.5, 540, 900); fl = u - d * 0.5
        for i, (lab, pre) in enumerate((('TAILLE', 'TAILLE'), ('CONTOURS', 'CONTOURS'), ('RASE', 'RASE'))):
            badge(ctx, lab, 230 + i * 240, 600 + (i % 2) * 70, 66, LIME if i != 1 else hexc('#141414'), fg=INK if i != 1 else LIME,
                  scale=pop(t, i3 + wt('xn_i3', pre, 2.0 + 0.5 * i)), rot=-0.05 + 0.05 * i)
        badge(ctx, 'PHILIPS ONEBLADE 360', SAFE_CX, 470, 64, hexc('#0b5ed7'), scale=pop(t, i3 + 0.1), rot=-0.03)
        snow(ctx, t, 25, 11, 0.6); flash(ctx, fl); ctx.restore(); L.banner(ctx, t, BAN4, bg=RED, fg=(1, 1, 1)); TL.captions(ctx, t); return
    if i4 <= t < ar_end:                               # appli : barbe de Père Noël
        u = t - i4
        ctx.save(); view(ctx, 1.3, HX, CY + 40, t=t); bg_salon(ctx, t); ctx.restore()
        ctx.set_source_rgba(0, 0, 0, 0.35); ctx.paint()
        t_ar = i4 + wt('xn_i4', 'STYLES', 1.4) - 0.3
        if t >= t_ar:
            uu = t - t_ar
            mood = dict(eyes='happy', smile=1.0, brows=0.6, look=(0, 0)) if uu < 1.0 else \
                (dict(eyes='tiny', smile=-0.6, brows=1.0, look=(0, 0)) if uu < 2.0 else dict(eyes='half', smile=1.0, brows=0.5, look=(0, 0)))
            phone_ar(ctx, t, t_ar, AR4, sh, mood=mood, who='hamza', outfit='sweat', tag='H')
            if 0.1 < uu < 1.0: text(ctx, 'HO HO HO !', 730, 470, 100, fill=(1, 1, 1), scale=pop(t, t_ar + 0.15), rot=0.1)
            if uu > 2.2: L.check(ctx, 760, 520, 2.4, pop(t, t_ar + 2.2))
        else:
            actor(ctx, 'ines', SAFE_CX + 20, CY + 60, t, sh, 'I', smile=1.0, eyes='open', look=(0, 0.2), arms=('down', 'hold_high'),
                  prop=lambda c, x, y, tt: phone(c, x, y - 40, 0.8, tt, rot=0.1), prop_hand='R', blush=0.5)
        snow(ctx, t, 25, 13, 0.5); flash(ctx, u); ctx.restore(); L.banner(ctx, t, BAN4, bg=RED, fg=(1, 1, 1)); TL.captions(ctx, t, 1230); return
    if ar_end <= t < h3:                               # il se rase (vraies images)
        u = t - ar_end
        footage(ctx, 'r_rase2', u, 1.0, 1.1, h3 - ar_end, 540, 900); flash(ctx, u)
        text(ctx, 'BZZZZ…', SAFE_CX, 520, 100, fill=LIME, rot=-0.05 + 0.05 * math.sin(t * 20), scale=pop(t, ar_end + 0.1))
        ctx.restore(); L.banner(ctx, t, BAN4, bg=RED, fg=(1, 1, 1)); return
    if i5 <= t < i6:                                   # prix : capture de la fiche
        u = t - i5
        fiche_kit(ctx, t); ctx.set_source_rgba(0.35, 0.02, 0.05, 0.45); ctx.paint()
        fiche_band(ctx, t, i5 + 0.05, cy=760, circle_t=i5 + wt('xn_i5', '29', 1.8))
        coupon_note(ctx, 1030); snow(ctx, t, 30, 17, 0.7); flash(ctx, u)
        ctx.restore(); L.banner(ctx, t, BAN4, bg=RED, fg=(1, 1, 1)); TL.captions(ctx, t, 1190); return

    # ---------- plans dessinés
    if t < unwrap: cam = (1.6 + 0.04 * t, IX, CY + 30, 0)
    elif t < h1: cam = (1.08, 550, CY + 60, shake_at(t, [unwrap + 0.4], 8))
    elif t < i2: cam = (1.7, HX, CY + 30, 0)
    elif t < h2: cam = (1.08, 550, CY + 60, shake_at(t, [tbush], 14))
    elif t < i3: cam = (1.7, HX, CY + 30, 0)
    elif t < i5: cam = (1.75 + 0.1 * ease((t - h3) / 1.4), HX, CY + 30, 0)
    else: cam = (1.08, 550, CY + 60, 0)
    z, wx, wy, shk = cam
    view(ctx, z, wx, wy, shake=shk, t=t); bg_salon(ctx, t)
    shaved = t >= h3
    # ---- INÈS
    ik = dict(smile=1.0, eyes='happy', brows=0.6, look=(1, 0), arms=('hold', 'hold'), blush=0.8)
    if unwrap <= t < h1: ik.update(eyes='open', arms=('chin', 'down'))
    elif h1 <= t < i2: ik.update(eyes='half', smile=0.4)
    elif i2 <= t < h2: ik.update(eyes='half' if t < tbush else 'happy', smile=0.6 if t < tbush else 1.0, brows=0.2,
                                 arms=('lips', 'down') if t < tbush else ('face', 'down'), tilt=0.08 * math.sin(t * 9) if t > tbush else 0)
    elif t >= i6: ik.update(eyes='open', look=(-0.4, 0.7), arms=(('down', 'point_down', (t - i6) / 0.3), 'down'), smile=1.0)
    if z < 1.3 or t < unwrap:
        actor(ctx, 'ines', IX, CY, t, sh, 'I', **ik)
        santa_hat(ctx, IX, CY - 40, 0.82, t, ik.get('tilt', 0.0))
        if t < unwrap: gift(ctx, IX, CY + 380, 0.75, t)
    # ---- HAMZA
    hk = dict(smile=0.6, eyes='open', brows=0.3, look=(-1, 0), arms=('down', 'down'), outfit='noel')
    hsq = 0.0
    if t < unwrap: hk.update(eyes='wide', smile=1.0)
    elif t < h1: hk.update(eyes='wide', smile=1.0, arms=('face', 'face') if t > unwrap + 0.5 else ('hold', 'hold'))
    elif t < i2: hk.update(eyes='open', brows=-1.0, smile=-0.7, look=(-0.5, 0), arms=('hip', 'hold_high'),
                           prop=lambda c, x, y, tt: oneblade(c, x + 5, y - 60, 0.55, tt, 0.25), prop_hand='R'); hsq = spring(t, h1, 0.05)
    elif t < h2: hk.update(eyes='tiny' if t > tbush else 'half', brows=1.0 if t > tbush else -0.6, smile=-0.5, arms=('down', 'chin'))
    elif t < i3: hk.update(eyes='half', brows=-0.6, smile=-0.6 if t < h2 + 0.8 else 0.2, look=(-1, 0.3), arms=('hip', 'hip'),
                           tilt=-0.1 if t < h2 + 0.8 else 0.05)
    elif h3 <= t < i5: hk.update(eyes='wink' if t > h3 + 1.0 else 'half', smile=1.0, brows=0.8, look=(0, 0), arms=('hip', 'chin'), tilt=-0.06)
    elif t >= i6: hk.update(eyes='happy', smile=1.0, arms=('down', 'hold_high'),
                            prop=lambda c, x, y, tt: oneblade(c, x + 5, y - 60, 0.55, tt, 0.25), prop_hand='R')
    if z < 1.3 or (h1 <= t < i2) or (h2 <= t < i3) or (h3 <= t < i5):
        actor(ctx, 'hamza', HX, CY, t, sh, 'H', sq=hsq, **hk)
        if not shaved:
            style = 'bush' if t >= tbush else 'full'
            if t >= tbush:
                k = ease_out_back(min(1, (t - tbush) / 0.4))
                ctx.save(); ctx.translate(HX, CY + 80); ctx.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k); ctx.translate(-HX, -CY - 80)
                beard(ctx, HX, CY, 0.95, 'bush', t); ctx.restore()
                bird(ctx, HX + 70, CY + 210, t, tbush + 0.35)
            else: beard(ctx, HX, CY, 0.95, 'full', t)
        else:
            beard(ctx, HX, CY, 0.95, 'stubble', t, alpha=0.8)
        if unwrap <= t < h1:                           # le cadeau s'ouvre, le rasoir sort
            u = t - unwrap
            gift(ctx, HX, CY + 400, 0.75, t, lid=ease(u / 0.3))
            if u > 0.25:
                kb = ease_out_back((u - 0.25) / 0.4)
                oneblade(ctx, HX, CY + 300 - 190 * kb, 0.7 * kb, t, 0.1)
                for i in range(6): sparkle(ctx, HX + 200 * math.cos(i), CY + 160 + 150 * math.sin(i * 1.7), 26, t, i)
        if h3 <= t < i5:
            for i in range(8): sparkle(ctx, HX + 210 * math.cos(i * 0.8 + t), CY + 40 + 190 * math.sin(i * 1.3), 26, t, i)
    snow(ctx, t, 18, 21, 0.5)
    ctx.restore()
    # ---- textes
    if h1 <= t < i2: text(ctx, 'VEXÉ', 760, 480, 120, fill=hexc('#e8263d'), scale=pop(t, h1 + 0.3), rot=0.1)
    if h3 <= t < i5: text(ctx, 'BEAU GOSSE', 700, 480, 110, fill=YEL, scale=pop(t, h3 + 0.9), rot=0.08)
    if t >= i6: bf_badge(ctx, t, i6 + 0.05, 440); L.cta(ctx, t, i6 + RCTA)
    L.banner(ctx, t, BAN4, bg=RED, fg=(1, 1, 1))
    TL.captions(ctx, t, 990 if t >= i6 else CAP_Y)
    cuts = [unwrap, h1, i2, h2, i3, h3, i5, i6]
    flash(ctx, min([t - c for c in cuts if c <= t] or [9]), 0.08)

def build4():
    TL = tl4(); T = TL.T; i1, h1, i2, h2, i3, i4, h3, i5, i6 = (T[c] for c, _ in ORDER4)
    unwrap = i1 + clip_len('xn_i1') + 0.1; ar_end = i4 + clip_len('xn_i4') + 1.25
    tbush = i2 + wt('xn_i2', 'BUISSON', 1.6); t_ar = i4 + wt('xn_i4', 'STYLES', 1.4) - 0.3
    sfx = [('bells', 0.0, 0.6), ('scratch', unwrap, 0.4), ('pop', unwrap + 0.3, 0.8), ('sparkle', unwrap + 0.35, 0.8),
           ('boing', h1 + 0.05, 0.6), ('wah', h1 + 0.4, 0.4), ('whoosh', i2 - 0.03, 0.4), ('boing', tbush, 0.9), ('heart', tbush + 0.4, 0.6),
           ('whoosh', h2 - 0.03, 0.4), ('whoosh', i3 - 0.03, 0.6), ('buzz', i3 + 0.1, 0.5), ('whoosh', i4 - 0.03, 0.5)]
    for ts, _, _ in AR4: sfx += [('swipe', t_ar + ts, 0.6), ('pop', t_ar + ts + 0.05, 0.4)]
    sfx += [('bells', t_ar + 0.1, 0.5), ('ding', t_ar + 2.2, 0.8), ('buzz', ar_end + 0.05, 0.9), ('sparkle', h3, 0.9),
            ('wink', h3 + 1.0, 0.6), ('whoosh', i5 - 0.03, 0.5), ('pop', i5 + 0.1, 0.6), ('ding', i5 + wt('xn_i5', '29', 1.8), 0.7),
            ('whoosh', i6 - 0.03, 0.5), ('bells', i6 + 0.05, 0.4), ('ding', i6 + RCTA + 0.05, 0.7)]
    sh = Shot('noel4', TL.dur, draw4, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None

# ================================================================== 5. LE CLASSEMENT (Sarah, réactions de Léa)
ORDER5 = [('xn_s1', 'S'), ('xn_s3', 'S'), ('xn_s2', 'S'), ('xn_s0', 'S'), ('xn_s4', 'S'), ('xn_s5', 'S'), ('xn_s6', 'S')]
BAN5 = "LE CADEAU DE NOËL POUR LUI"

def tl5():
    return L.Timeline(ORDER5, {'xn_s3': 0.1, 'xn_s2': 0.55, 'xn_s0': 0.55, 'xn_s4': 0.1, 'xn_s5': 0.05, 'xn_s6': 0.1}, WORDS)

def draw5(ctx, t, sh):
    TL = sh.tl; T = TL.T; s1, s3, s2, s0, s4, s5, s6 = (T[c] for c, _ in ORDER5)
    tw = s0 + wt('xn_s0', 'PHILIPS', 1.6)
    ctx.save()
    # réactions de Léa (gros plans courts entre deux numéros)
    lea = None
    if s2 - 0.55 <= t < s2: lea = ('roll', s2 - 0.55)
    elif s0 - 0.55 <= t < s0: lea = ('laugh', s0 - 0.55)
    if lea:
        kind, a = lea
        view(ctx, 1.8, 800, CY + 30, t=t); bg_salon(ctx, t)
        mk = dict(eyes='half', brows=-0.6, smile=-0.3, look=(-1, -0.6), arms=('hip', 'down')) if kind == 'roll' else \
            dict(eyes='happy', brows=0.6, smile=1.0, look=(0, 0), arms=('face', 'down'), tilt=0.08 * math.sin(t * 14))
        actor(ctx, 'lea', 800, CY, t, sh, 'L', **mk); santa_hat(ctx, 800, CY - 40, 0.82, t, mk.get('tilt', 0.0))
        ctx.restore()
        text(ctx, 'BOF…' if kind == 'roll' else 'MDR !', 480, 520, 140, fill=YEL, scale=pop(t, a + 0.05), rot=-0.1)
        L.banner(ctx, t, BAN5, bg=RED, fg=(1, 1, 1)); flash(ctx, t - a); return
    if s4 <= t < s5:                                   # le n°1 en vrai
        u = t - s4; d = s5 - s4; cuts = [('r_prise', 0.0), ('r_rase', d * 0.38), ('r_lisse', d * 0.75)]
        for i, (nm, a) in enumerate(cuts):
            b = cuts[i + 1][1] if i + 1 < len(cuts) else d
            if a <= u < b: footage(ctx, nm, u - a, 1.0, 1.1, b - a, 540, 880); flash(ctx, u - a)
        for i, (lab, pre) in enumerate((('TAILLE', 'TAILLE'), ('CONTOURS', 'CONTOURS'), ('RASE', 'RASE'), ('APPLI STYLES', 'APPLICATION'))):
            badge(ctx, lab, 230 + (i % 3) * 240, 470 + i * 70 if i < 3 else 700, 64, LIME if i != 1 else hexc('#141414'),
                  fg=INK if i != 1 else LIME, scale=pop(t, s4 + wt('xn_s4', pre, 0.6 + 0.6 * i)), rot=-0.05 + 0.04 * i)
        snow(ctx, t, 20, 9, 0.5); ctx.restore(); L.banner(ctx, t, BAN5, bg=RED, fg=(1, 1, 1)); TL.captions(ctx, t); return
    if s5 <= t < s6:                                   # prix
        u = t - s5
        fiche_kit(ctx, t); ctx.set_source_rgba(0.35, 0.02, 0.05, 0.45); ctx.paint()
        fiche_band(ctx, t, s5 + 0.05, cy=760, circle_t=s5 + wt('xn_s5', '29', 2.6))
        if t >= s5 + wt('xn_s5', '29', 2.6): coupon_note(ctx, 1030)
        snow(ctx, t, 30, 17, 0.7); flash(ctx, u)
        ctx.restore(); L.banner(ctx, t, BAN5, bg=RED, fg=(1, 1, 1)); TL.captions(ctx, t, 1190); return
    # ---------- plateau du classement
    view(ctx, 1.2 + 0.02 * math.sin(t * 0.7), 470, CY + 80, t=t, shake=shake_at(t, [tw], 18)); bg_salon(ctx, t)
    win = t >= tw
    if win: S.rays(ctx, 320, 700, t, hexc('#ffe9a8'), 14, 0.4)
    sk = dict(smile=0.8, eyes='open', brows=0.5, look=(-1, 0), arms=('point_side', 'down'), tilt=-0.04)
    if s1 <= t < s3: sk.update(eyes='half', smile=1.0, look=(0, 0), arms=('hip', 'chin'))
    if s3 <= t < s2 or s2 <= t < s0: sk.update(eyes='half', smile=0.2, brows=-0.3, look=(-1, 0), arms=(('down', 'point_side', 0.8), 'hip'))
    if win: sk.update(eyes='wide', smile=1.0, brows=0.9, arms=('cheer', 'hold_high'),
                      prop=lambda c, x, y, tt: oneblade(c, x + 5, y - 60, 0.55, tt, 0.25), prop_hand='R')
    if t >= s6: sk.update(eyes='open', look=(-0.4, 0.7), arms=(('down', 'point_down', (t - s6) / 0.3), 'hold_high'),
                          prop=lambda c, x, y, tt: oneblade(c, x + 5, y - 60, 0.55, tt, 0.25), prop_hand='R')
    actor(ctx, 'sarah', 650, CY + 20, t, sh, 'S', sq=spring(t, tw, -0.06), **sk)
    santa_hat(ctx, 650, CY - 20, 0.82, t, sk.get('tilt', 0.0))
    if t < s6:
        rows = [(3, s3, 1160, 'sock'), (2, s2, 920, 'pull'), (1, s0, 680, 'razor')]
        for rk, t0, y, kind in rows:
            k = pop(t, t0, 0.35)
            if k <= 0: continue
            medal(ctx, 150, y, 1.0 * k, rk, t)
            if kind == 'sock': sock(ctx, 320, y + 10, 1.1 * k, t)
            elif kind == 'pull': ugly_sweater(ctx, 320, y + 10, 0.95 * k, t)
            elif win:
                kk = pop(t, tw, 0.4); oneblade(ctx, 320, y + 40, 0.7 * kk, t, 0.15, buzz=True)
                for i in range(5): sparkle(ctx, 320 + 130 * math.cos(i * 1.3), y + 30 + 110 * math.sin(i * 1.9), 22, t, i)
            else: text(ctx, '?', 320, y + 10, 160, fill=YEL, rot=0.1 * math.sin(t * 6))
        cross_out(ctx, 320, 1170, 100, ease((t - (s2 - 0.35)) / 0.25))
        cross_out(ctx, 320, 930, 100, ease((t - (s0 - 0.35)) / 0.25))
    snow(ctx, t, 22, 5, 0.5)
    ctx.restore()
    if t >= s6: bf_badge(ctx, t, s6 + 0.05, 440); L.cta(ctx, t, s6 + RCTA)
    L.banner(ctx, t, BAN5, bg=RED, fg=(1, 1, 1))
    TL.captions(ctx, t, 990 if t >= s6 else 1320)
    flash(ctx, min([t - c for c in (s2, s0, s4, s5, s6) if c <= t] or [9]), 0.08)

def build5():
    TL = tl5(); T = TL.T; s1, s3, s2, s0, s4, s5, s6 = (T[c] for c, _ in ORDER5)
    tw = s0 + wt('xn_s0', 'PHILIPS', 1.6)
    sfx = [('bells', 0.0, 0.6), ('pop', s3, 0.6), ('stamp', s3 + 0.1, 0.5), ('scratch', s2 - 0.35, 0.4), ('wah', s2 - 0.5, 0.35),
           ('pop', s2, 0.6), ('scratch', s0 - 0.35, 0.4), ('boing', s0 - 0.5, 0.4), ('drumroll', s0, 0.45), ('sparkle', tw, 0.9),
           ('stamp', tw, 0.7), ('bells', tw + 0.1, 0.5), ('whoosh', s4 - 0.03, 0.6), ('buzz', s4 + 0.1, 0.5),
           ('whoosh', s5 - 0.03, 0.5), ('ding', s5 + wt('xn_s5', '29', 2.6), 0.7), ('whoosh', s6 - 0.03, 0.5), ('ding', s6 + RCTA + 0.05, 0.7)]
    sh = Shot('noel5', TL.dur, draw5, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
