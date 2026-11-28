# -*- coding: utf-8 -*-
"""Parfum Lattafa : « Le calendrier de l'Avent » (28/11/2026, J-3 avant le 1er décembre).
   Le vrai flacon est visible dès 0 s derrière la grande case 24 entrouverte d'un calendrier dessiné.
   Mini Sarah (Aoede, bonnet de Noël) : « POV : tu ouvres ton calendrier de l'Avent. » ; case 1 : un tout petit chocolat ;
   case 2 : encore un tout petit chocolat (blasée). Mini Hamza (Fenrir) débarque : « Saute direct à la case 24 ! »
   La case 24 explose : vraies images du flacon, Confidential Private Gold de Lattafa ; « un vrai cadeau, tout doré,
   moins de 25 € » ; question « 24 petits chocolats ou un seul vrai cadeau ? » ; panier orange."""
import math
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, ease_out, GOLDC, REDX
from tb_videos import comment_bubble, zoom_about
from sl_videos import stamp, dark
import ca_data as CA

WORDS = {c: CA.words_for(c) for c in CA.CUTS}
for w in ('POV :', 'CALENDRIER', "L'AVENT.", 'UN :', 'PETIT', 'DEUX…', 'ENCORE', 'ATTENDS !', 'VINGT-QUATRE !', 'QUOI ?!',
          'CONFIDENTIAL', 'PRIVATE', 'GOLD', 'LATTAFA ?!', 'VRAI', 'DORÉ…', 'VINGT-CINQ', 'VINGT-QUATRE', 'SEUL', 'CADEAU ?',
          'COMMENTAIRE.'):
    if w not in S.HL: S.HL = S.HL + (w,)
CAL = hexc('#b3122e'); CAL_D = hexc('#7d0c20'); DOOR = hexc('#d62a45'); GREEN_N = hexc('#1f7a4a'); CHOC = hexc('#5a3015')
CHOC_L = hexc('#8a5428'); RECESS = hexc('#2a0a10'); SNOWC = (1, 1, 1)
BAN = "MON CALENDRIER DE L'AVENT"
ORDER = [('xc_s1', 'S'), ('xc_s2', 'S'), ('xc_s3', 'S'), ('xc_h1', 'H'), ('xc_s4', 'S'), ('xc_h2', 'H'), ('xc_s5', 'S'), ('xc_s6', 'S')]
PAUSE = {'xc_s2': 0.05, 'xc_s3': 0.05, 'xc_h1': 0.02, 'xc_s4': 0.05, 'xc_h2': 0.05, 'xc_s5': 0.08, 'xc_s6': 0.08}
RCTA = 0.4
SK = dict(); HK = dict(outfit='sweat')
HOLE = (330, 560, 420, 460)          # case 24 : x, y, w, h (le vrai flacon apparaît derrière)
DOORS = [  # (x, y, w, h, numéro)
    (95, 340, 185, 105, 7), (295, 340, 185, 105, 1), (495, 340, 185, 105, 15), (695, 340, 185, 105, 11),
    (95, 450, 185, 105, 19), (295, 450, 185, 105, 4), (495, 450, 185, 105, 22), (695, 450, 185, 105, 9),
    (95, 565, 220, 220, 13), (95, 795, 220, 220, 6), (765, 565, 120, 220, 2), (765, 795, 120, 220, 17),
    (95, 1030, 185, 110, 20), (295, 1030, 185, 110, 3), (495, 1030, 185, 110, 12), (695, 1030, 185, 110, 23)]
D1 = DOORS[1]; D2 = DOORS[10]

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

# ---------------------------------------------------------------- accessoires
def chocolate(c, x, y, s, t, rot=0.0):
    """tout petit chocolat (carré, papier doré froissé)"""
    if s <= 0.01: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    ink_fill(c, lambda k: blob(k, [(-46, -30), (46, -30), (50, 32), (-50, 32)], boil_seed(t) + 31, 1.0), hexc('#f2c94c'), lw=5)
    ink_fill(c, lambda k: rrect(k, -30, -20, 60, 40, 9), CHOC, lw=4)
    c.new_path(); rrect(c, -22, -14, 26, 12, 4); c.set_source_rgba(*CHOC_L, 0.9); c.fill()
    c.restore()

def door(c, x, y, w, h, num, t, open_k=0.0, inside=None, glow=0.0, shake=0.0):
    """porte numérotée ; open_k 0 -> 1 = la porte pivote sur sa charnière gauche"""
    dx = 7 * math.sin(t * 47) * shake
    c.save(); c.translate(dx, 0)
    if open_k > 0.01:
        c.new_path(); c.rectangle(x, y, w, h); c.set_source_rgb(*RECESS); c.fill()
        if inside: inside(x + w / 2, y + h / 2)
    if glow > 0:
        c.new_path(); rrect(c, x - 14, y - 14, w + 28, h + 28, 18); c.set_source_rgba(1, 0.85, 0.3, 0.35 * glow); c.fill()
    pw = w * (1 - 1.15 * ease_out(open_k))
    if pw > 0:
        ink_fill(c, lambda k: rrect(k, x, y, pw, h, 10), DOOR, lw=5)
        if pw > w * 0.4:
            c.save(); c.translate(x + pw / 2, y + h / 2); c.scale(pw / w, 1)
            text(c, str(num), 0, 6, min(h * 0.62, 90), fill=(1, 1, 1), stroke=INK, shadow=False); c.restore()
    else:                                                    # dos de la porte ouverte, à gauche de la charnière
        ink_fill(c, lambda k: rrect(k, x + pw, y, -pw, h, 10), CAL_D, lw=5)
    c.restore()

def board(c, t, hole_open=0.0, open1=0.0, open2=0.0, shake24=0.0, glow24=0.0, split=0.0):
    """le calendrier dessiné, avec la grande case 24 découpée (le vrai flacon derrière)"""
    hx, hy, hw, hh = HOLE
    parts = [(-1, -1), (1, -1), (-1, 1), (1, 1)] if split > 0 else [(0, 0)]
    for sx, sy in parts:
        c.save()
        if split > 0:                                         # le calendrier se déchire en 4 morceaux qui s'envolent
            e = ease_out(split)
            c.new_path()
            c.rectangle(0 if sx < 0 else hx + hw / 2, 0 if sy < 0 else hy + hh / 2,
                        hx + hw / 2 if sx < 0 else W, hy + hh / 2 if sy < 0 else H); c.clip()
            c.translate(sx * 900 * e, sy * 1100 * e); c.translate(540, 960); c.rotate(sx * sy * 0.5 * e); c.translate(-540, -960)
        # fond du calendrier avec le trou de la case 24 (règle pair-impair)
        c.new_path(); c.rectangle(0, 0, W, H); c.rectangle(hx + hw, hy, -hw, hh)
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source_rgb(*CAL); c.fill(); c.set_fill_rule(cairo.FILL_RULE_WINDING)
        for i in range(26):                                   # étoiles dorées et flocons
            px = (i * 263) % 1040 + 20; py = (i * 397) % 1840 + 40
            if hx - 20 < px < hx + hw + 20 and hy - 20 < py < hy + hh + 20: continue
            c.save(); c.translate(px, py); c.rotate(i + 0.2 * math.sin(t * 2 + i)); c.new_path()
            star(c, 0, 0, 16, 7); c.set_source_rgba(*GOLDC, 0.55); c.fill(); c.restore()
        # guirlande de sapin en haut
        ink_fill(c, lambda k: blob(k, [(30, 150), (1050, 150), (1050, 320), (30, 320)], boil_seed(t) + 5, 1.4), GREEN_N, lw=6)
        for i in range(9):
            c.new_path(); c.arc(70 + i * 118, 305 + 8 * math.sin(i * 2.3), 18, 0, 7)
            c.set_source_rgb(*(GOLDC if i % 2 else REDX)); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
        ink_line(c, [(hx, hy), (hx + hw, hy), (hx + hw, hy + hh), (hx, hy + hh), (hx, hy)], boil_seed(t), 9)
        for (x, y, w, h, n) in DOORS:
            if (x, y) == D1[:2]:
                door(c, x, y, w, h, n, t, open1, inside=lambda a, b: chocolate(c, a, b, 0.85, t))
            elif (x, y) == D2[:2]:
                door(c, x, y, w, h, n, t, open2, inside=lambda a, b: chocolate(c, a, b, 0.75, t, rot=0.3))
            else:
                door(c, x, y, w, h, n, t)
        # la porte de la case 24, entrouverte
        if split <= 0:
            ga = glow24 * (0.6 + 0.4 * math.sin(t * 9))
            if ga > 0:
                c.new_path(); rrect(c, hx - 24, hy - 24, hw + 48, hh + 48, 26); c.set_source_rgba(1, 0.85, 0.3, 0.35 * ga)
                c.set_line_width(30); c.stroke()
            pw = hw * (1 - hole_open)
            dx = 8 * math.sin(t * 51) * shake24
            if pw > 4:
                ink_fill(c, lambda k: rrect(k, hx + hw - pw + dx, hy, pw, hh, 14), DOOR, lw=7)
                if pw > 120:
                    text(c, '24', hx + hw - pw / 2 + dx, hy + hh / 2 + 10, 150, fill=GOLDC, stroke=INK, shadow=False)
            c.new_path(); c.rectangle(hx + hw - pw - 10 + dx, hy, 10, hh); c.set_source_rgba(1, 0.9, 0.5, 0.8); c.fill()
        c.restore()

def zoom_to(ctx, k, z, cx, cy, sx=SAFE_CX + 20, sy=760):
    """k 0 -> 1 : la case (cx, cy) vient au centre de la zone visible, zoom z"""
    zz = 1 + (z - 1) * k
    ctx.translate(cx + (sx - cx) * k, cy + (sy - cy) * k); ctx.scale(zz, zz); ctx.translate(-cx, -cy)

def chocolate_pile(c, cx, cy, t, n=24):
    for i in range(n):
        a = i * 2.4; r = 18 * math.sqrt(i)
        chocolate(c, cx + r * math.cos(a) * 1.5, cy + r * math.sin(a) * 0.9, 0.62, t, rot=0.4 * math.sin(i * 1.7))

# ---------------------------------------------------------------- dessin
def draw_ca(ctx, t, sh):
    TL = sh.tl; T = TL.T; s1, s2, s3, h1, s4, h2, s5, s6 = (T[c] for c, _ in ORDER)
    cap_y = 1210; ban = True
    ctx.save()
    if t < s2:                                       # 1. accroche : le calendrier, le vrai flacon derrière la case 24
        footage(ctx, 'fl1', 0, 1.0, 1.0, 1)
        z = 1.0 + 0.04 * min(1, t / 2.2)
        ctx.save(); zoom_about(ctx, z, 540, 790)
        board(ctx, t, hole_open=0.62 + 0.05 * math.sin(t * 3), glow24=1.0)
        ctx.restore()
        for i in range(4): sparkle(ctx, 400 + (i * 97) % 300, 620 + (i * 131) % 360, 26, t, ph=i)
        mini(ctx, 'sarah', 'S', 190, 1150, t, sh, sc=0.36, eyes='wide', brows=0.9, smile=1.0, look=(1, -0.5),
             arms=('cheer', 'point_side'), jump=18 * abs(math.sin(t * 6)), hat=True, **SK)
        kq = pop(t, 0.1)
        text(ctx, 'CASE 1 OU CASE 24 ?', SAFE_CX + 20, 470, 100, fill=(1, 1, 1), scale=kq, rot=-0.05 + 0.02 * math.sin(t * 8))
        if t < 0.2: flash(ctx, t, 0.2)
    elif t < s3:                                     # 2. case 1 : un tout petit chocolat
        u = t - s2; ko = ease_out((u - 0.25) / 0.45)
        footage(ctx, 'fl1', 0, 1.0, 1.0, 1)
        x, y, w, h, _ = D1
        ctx.save(); zoom_to(ctx, ease_out(u / 0.4), 2.6, x + w / 2, y + h / 2, sy=700)
        board(ctx, t, hole_open=0.62, open1=ko)
        ctx.restore()
        mini(ctx, 'sarah', 'S', 780, 1150, t, sh, sc=0.4, eyes='half' if u > 0.9 else 'open', brows=-0.3 if u > 0.9 else 0.6,
             smile=-0.4 if u > 0.9 else 0.6, look=(-1, -0.6), arms=('point_side', 'hip'), face=-1, hat=True, **SK)
        kb = pop(t, s2 + wt('xc_s2', 'TOUT', 0.9))
        badge(ctx, 'CASE 1', 300, 1000, 80, (1, 1, 1), fg=INK, rot=-0.06, scale=pop(t, s2 + 0.1))
        if kb > 0.01: badge(ctx, 'MINI CHOCOLAT', SAFE_CX, 1090, 70, GOLDC, fg=INK, rot=0.04, scale=kb)
        flash(ctx, u)
    elif t < h1:                                     # 3. case 2 : encore un tout petit chocolat (blasée)
        u = t - s3; ko = ease_out((u - 0.2) / 0.45)
        footage(ctx, 'fl1', 0, 1.0, 1.0, 1)
        x, y, w, h, _ = D2
        ctx.save(); zoom_to(ctx, ease_out(u / 0.4), 2.3, x + w / 2, y + h / 2, sx=560, sy=720)
        board(ctx, t, hole_open=0.62, open2=ko)
        ctx.restore()
        mini(ctx, 'sarah', 'S', 230, 1150, t, sh, sc=0.4, eyes='half', brows=-0.7, smile=-0.6, look=(1, -0.4),
             arms=('down', 'face'), hat=True, tilt=-0.05, **SK)
        badge(ctx, 'CASE 2', 640, 1000, 80, (1, 1, 1), fg=INK, rot=0.05, scale=pop(t, s3 + 0.1))
        ke = pop(t, s3 + wt('xc_s3', 'ENCORE', 0.8))
        if ke > 0.01: text(ctx, 'ENCORE ?!', SAFE_CX + 40, 470, 120, fill=GOLDC, scale=ke, rot=0.06)
        flash(ctx, u)
    elif t < s4:                                     # 4. Hamza débarque : « saute direct à la case 24 ! »
        u = t - h1
        footage(ctx, 'fl1', 0, 1.0, 1.0, 1)
        ctx.save(); zoom_about(ctx, 1.0 + 0.06 * min(1, u / 2.5), 540, 790)
        board(ctx, t, hole_open=0.62 + 0.1 * min(1, u / 2.5), shake24=min(1, u / 1.2), glow24=1.0)
        ctx.restore()
        rays(ctx, 540, 790, t, GOLDC, alpha=0.12 + 0.1 * min(1, u / 2))
        hx = 1050 - 280 * ease_out(u / 0.45)
        mini(ctx, 'hamza', 'H', hx, 1150, t, sh, sc=0.4, eyes='wide', brows=1.0, smile=1.0, look=(-1, -0.5),
             arms=('hip', 'point_side'), face=-1, walk=t * 16 if u < 0.45 else 0, jump=30 * abs(math.sin(u * 7)) if u < 0.6 else 0, **HK)
        mini(ctx, 'sarah', 'S', 190, 1150, t, sh, sc=0.36, eyes='wide', brows=0.4, smile=0.0, look=(1, -0.2),
             arms=('down', 'down'), hat=True, **SK)
        if u < 0.5: speed_lines(ctx, t, 900, 950, col=(1, 1, 1), n=24, alpha=0.3)
        k24 = pop(t, h1 + wt('xc_h1', 'VINGT', 1.6))
        text(ctx, 'ATTENDS !', SAFE_CX + 60, 470, 120, fill=(1, 1, 1), scale=pop(t, h1 + 0.03), rot=-0.07)
        if k24 > 0.01: badge(ctx, 'DIRECT À LA CASE 24 !', SAFE_CX, 1070, 66, GOLDC, fg=INK, rot=0.03, scale=k24)
        flash(ctx, u)
    elif t < h2:                                     # 5. la case 24 explose : le vrai flacon
        u = t - s4
        footage(ctx, 'nom', u * 0.8, 1.15, 1.05, 2.5, 540, 700, offset=40)
        rays(ctx, 560, 650, t, GOLDC, alpha=0.18 * ease_out(u / 0.4))
        if u < 0.7: board(ctx, t, split=u / 0.7)
        kn = pop(t, s4 + wt('xc_s4', 'CONFIDENTIAL', 0.8))
        stamp(ctx, 'CASE 24', SAFE_CX, 450, pop(t, s4 + 0.1, 0.25), rot=-0.1, col=REDX, size=110)
        badge(ctx, 'CONFIDENTIAL PRIVATE GOLD', SAFE_CX, 900, 58, GOLDC, fg=INK, scale=kn, rot=0.03)
        badge(ctx, 'LATTAFA', 620, 1010, 74, hexc('#141414'), fg=GOLDC, scale=pop(t, s4 + wt('xc_s4', 'LATTAFA', 2.3)), rot=-0.05)
        mini(ctx, 'sarah', 'S', 170, 1150, t, sh, sc=0.36, eyes='heart' if u > 0.8 else 'wide', brows=0.9, smile=1.0, blush=0.8,
             look=(1, -0.7), arms=('face', 'face'), hat=True, **SK)
        if kn > 0.5:
            for i in range(5): sparkle(ctx, 420 + (i * 67) % 300, 450 + (i * 113) % 420, 30, t, ph=i)
        flash(ctx, u, 0.2, col=(1, 0.95, 0.7))
    elif t < s5:                                     # 6. « un vrai cadeau, tout doré, moins de 25 € »
        u = t - h2; tm = h2 + wt('xc_h2', 'MOINS', 2.7)
        footage(ctx, 'fl2', u * 0.55, 1.0, 1.06, 3, offset=28)
        kd = pop(t, h2 + wt('xc_h2', 'TOUT', 1.3))
        text(ctx, 'UN VRAI CADEAU', SAFE_CX, 430, 100, fill=(1, 1, 1), scale=pop(t, h2 + 0.05), rot=-0.04)
        if t < tm:
            if kd > 0.01: badge(ctx, 'TOUT DORÉ', SAFE_CX + 40, 560, 80, GOLDC, fg=INK, scale=kd, rot=0.05)
        else:
            price_tag(ctx, SAFE_CX + 10, 600, 0.78 * pop(t, tm), t, 'MOINS DE 25 €', sub=None)
        mini(ctx, 'hamza', 'H', 190, 1150, t, sh, sc=0.38, eyes='happy', brows=0.6, smile=1.0, look=(1, -0.5),
             arms=('cheer', 'point_side'), jump=26 * abs(math.sin(u * 6)) if t > tm else 0, **HK)
        flash(ctx, u)
    elif t < s6:                                     # 7. question : 24 petits chocolats ou un seul vrai cadeau ?
        u = t - s5; kc = pop(t, s5 + wt('xc_s5', 'VINGT', 0.9)); kv = pop(t, s5 + wt('xc_s5', 'UN', 1.9))
        ctx.save(); ctx.translate(200, 60); footage(ctx, 'edp', u * 0.5, 0.9, 0.95, 3, 540, 900, offset=10); ctx.restore()
        ctx.save(); ctx.new_path(); ctx.rectangle(0, 0, 470, H); ctx.clip()
        ctx.set_source_rgb(*CAL); ctx.paint()
        for i in range(12):
            ctx.save(); ctx.translate((i * 151) % 440 + 20, (i * 331) % 1700 + 100); ctx.new_path(); star(ctx, 0, 0, 14, 6)
            ctx.set_source_rgba(*GOLDC, 0.5); ctx.fill(); ctx.restore()
        chocolate_pile(ctx, 235, 760, t, n=int(24 * min(1, kc)))
        ctx.restore()
        ink_line(ctx, [(470, 330), (470, 1150)], boil_seed(t), 10)
        badge(ctx, '24 PETITS CHOCOLATS', 245, 560, 50, (1, 1, 1), fg=INK, scale=kc, rot=-0.05)
        badge(ctx, '1 VRAI CADEAU', 700, 560, 64, GOLDC, fg=INK, scale=kv, rot=0.05)
        badge(ctx, 'OU', 470, 760, 80, (1, 1, 1), fg=REDX, scale=pop(t, s5 + wt('xc_s5', 'OU', 1.6)))
        text(ctx, 'ET TOI ?', SAFE_CX, 430, 110, fill=(1, 1, 1), scale=pop(t, s5 + 0.05), rot=-0.04)
        mini(ctx, 'sarah', 'S', 250, 1150, t, sh, sc=0.34, eyes='open', brows=0.7, smile=1.0, look=(0, 0.7),
             arms=('point_side', 'chin'), face=-1, hat=True, **SK)
        comment_bubble(ctx, 770, 1000, pop(t, s5 + wt('xc_s5', 'DIS', 3.6)) * 0.8, t)
        ban = False; cap_y = 1240
        flash(ctx, u)
    else:                                            # 8. prix + appel à l'action
        v = t - s6
        footage(ctx, 'fl1', 1.2 + min(v, 0.6) * 0.5, 1.0, 1.0, 1)
        price_tag(ctx, 330, 470, 0.6, t, 'MOINS DE 25 €', sub=None)
        mini(ctx, 'hamza', 'H', 820, 880, t, sh, sc=0.27, eyes='happy', brows=0.4, smile=1.0, look=(-1, 0.4), arms=('hip', 'wave'), face=-1, **HK)
        mini(ctx, 'sarah', 'S', 160, 880, t, sh, sc=0.3, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
             look=(0.4, 0.8), arms=('point_down', 'hip'), hat=True, **SK)
        ctx.restore(); L.banner(ctx, t, BAN, bg=CAL, fg=(1, 1, 1)); L.cta(ctx, t, s6 + RCTA); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=CAL, fg=(1, 1, 1))
    TL.captions(ctx, t, cap_y)

def build_ca():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.8); T = TL.T; s1, s2, s3, h1, s4, h2, s5, s6 = (T[c] for c, _ in ORDER)
    tm = h2 + wt('xc_h2', 'MOINS', 2.7)
    sfx = [('whoosh', 0.0, 0.6), ('bells', 0.05, 0.45), ('sparkle', 0.4, 0.4),
           ('swipe', s2 - 0.03, 0.4), ('pop', s2 + 0.35, 0.6), ('wah', s2 + wt('xc_s2', 'TOUT', 0.9), 0.35),
           ('swipe', s3 - 0.03, 0.4), ('pop', s3 + 0.3, 0.5), ('wah', s3 + wt('xc_s3', 'ENCORE', 0.8) + 0.3, 0.45),
           ('scratch', h1 - 0.03, 0.5), ('whoosh', h1 + 0.05, 0.6), ('drumroll', h1 + 0.9, 0.35),
           ('boing', s4 - 0.02, 0.5), ('stamp', s4 + 0.1, 0.8), ('bells', s4 + 0.15, 0.5),
           ('sparkle', s4 + wt('xc_s4', 'GOLD', 1.5), 0.5), ('pop', s4 + wt('xc_s4', 'LATTAFA', 2.3), 0.6),
           ('swipe', h2 - 0.03, 0.4), ('pschht', h2 + 0.4, 0.35), ('coins', tm, 0.6),
           ('whoosh', s5 - 0.03, 0.5), ('pop', s5 + wt('xc_s5', 'OU', 1.6), 0.6), ('sparkle', s5 + wt('xc_s5', 'DIS', 3.6), 0.5),
           ('bells', s6 + 0.05, 0.4), ('ding', s6 + RCTA + 0.05, 0.7)]
    sh = Shot('calendrier_avent', TL.dur, draw_ca, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
