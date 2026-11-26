# -*- coding: utf-8 -*-
"""Dentifrice Miswak : « ASMR dentifrice raté »
   Mini Léa fait un ASMR chuchoté sur les vraies images du tube (bouchon, pâte), mini Hamza débarque en criant
   « C'EST LE MISWAK ?! », essaie de chuchoter, s'emballe de nouveau. Question au spectateur : l'ASMR, ça te détend ou ça t'énerve ?"""
import math
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, leaf, ease_out, stars_dizzy
import ar_data as AR

WORDS = {c: AR.words_for(c) for c in AR.CUTS}
for w in ('ASMR.', 'MISWAK ?!', 'CINQ', 'EUROS !', 'PLANTES,', "D'AL-ARAK.", 'COMMENTAIRE.', 'CHUCHOTE.', 'FRAÎCHE !',
          'BOUCHON...', 'PÂTE.', 'DÉTEND', "T'ÉNERVE ?"):
    if w not in S.HL: S.HL = S.HL + (w,)
MINT = hexc('#3ddc97'); GREEN_D = hexc('#0f5132'); REDX = hexc('#e8263d'); YELC = hexc('#ffd23f')
LILAC = hexc('#c9b6ff'); NIGHT = hexc('#1d1640'); FOAM = hexc('#9a9aa6'); FOAM_D = hexc('#6d6d7a')
BAN_A = 'ASMR DENTIFRICE… CHUT'; BAN_B = 'ASMR RATÉ'
ORDER = [('arl_1', 'L'), ('arl_2', 'L'), ('arl_3', 'L'), ('arh_1', 'H'), ('arl_4', 'L'),
         ('arh_2', 'H'), ('arh_3', 'H'), ('arl_5', 'L'), ('arh_4', 'H')]
PAUSE = {}
RCTA = 0.45

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def head_c(x, fy, sc, jump=0.0):
    return x, fy - 770 * sc - jump + 165 * sc

def headphones(ctx, x, y, sc, col=LILAC):
    """casque ASMR posé sur la tête (x, y = centre de la tête)"""
    r = 205 * sc
    ctx.save(); ctx.new_path(); ctx.arc(x, y - 10 * sc, r, math.pi * 1.08, math.pi * 1.92)
    ctx.set_source_rgb(*INK); ctx.set_line_width(34 * sc + 6); ctx.stroke_preserve()
    ctx.set_source_rgb(*col); ctx.set_line_width(34 * sc); ctx.stroke()
    for s in (-1, 1):
        ink_fill(ctx, lambda c, s=s: rrect(c, x + s * r - 45 * sc, y - 30 * sc, 90 * sc, 150 * sc, 40 * sc), col, lw=6)
    ctx.restore()

def foam_mic(ctx, x, y, s, t, shake=0.0):
    """gros micro ASMR en mousse sur pied"""
    ctx.save(); ctx.translate(x + shake * math.sin(t * 60) * 8, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -10, 60, 20, 260, 8), hexc('#2a2a33'), lw=5)
    ink_fill(ctx, lambda c: rrect(c, -80, 310, 160, 26, 12), hexc('#2a2a33'), lw=5)
    pts = [(95 * math.cos(a) * (1 + 0.07 * math.sin(a * 9 + t * 2)), 95 * math.sin(a) * (1 + 0.07 * math.sin(a * 9 + t * 2)))
           for a in [i * 2 * math.pi / 28 for i in range(28)]]
    ink_fill(ctx, lambda c: blob(c, pts, 3, 0.5), FOAM, lw=7)
    for i in range(14):
        a = i * 2.3; rr = 20 + (i * 37) % 60
        ctx.new_path(); ctx.arc(rr * math.cos(a), rr * math.sin(a), 6, 0, 7); ctx.set_source_rgb(*FOAM_D); ctx.fill()
    ctx.restore()

def sound_waves(ctx, x, y, t, s=1.0, col=(1, 1, 1), n=3, side=1, alpha=0.9):
    for i in range(n):
        ph = (t * 1.4 + i / n) % 1.0
        r = (40 + 120 * ph) * s
        ctx.new_path(); ctx.arc(x, y, r, -0.7 if side > 0 else math.pi - 0.7, 0.7 if side > 0 else math.pi + 0.7)
        ctx.set_source_rgba(*col, alpha * (1 - ph)); ctx.set_line_width(10 * s); ctx.stroke()

def word_pop(ctx, txt, x, y, size, col, t, t0, rot=0.0, fg=INK):
    k = pop(t, t0, 0.25)
    if k > 0.01: badge(ctx, txt, x, y, size, col, fg=fg, scale=k, rot=rot)

def shake_at(t, t0, amp=26, d=0.5):
    u = t - t0
    if u < 0 or u > d: return 0.0, 0.0
    e = (1 - u / d) * amp
    return e * math.sin(u * 91), e * math.cos(u * 73)

def dim(ctx, a, col=NIGHT):
    ctx.set_source_rgba(*col, a); ctx.paint()

def stamp_txt(ctx, txt, x, y, size, col, t, t0, rot=-0.12):
    k = pop(t, t0, 0.25)
    if k <= 0.01: return
    s = 1 + 1.4 * max(0, 1 - (t - t0) / 0.18)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * k, s * k)
    w = text_w(ctx, txt, size) + 50
    ctx.new_path(); rrect(ctx, -w / 2, -size * 0.62, w, size * 1.24, 16); ctx.set_source_rgba(1, 1, 1, 0.88); ctx.fill_preserve()
    ctx.set_source_rgb(*col); ctx.set_line_width(10); ctx.stroke()
    text(ctx, txt, 0, 4, size, fill=col, stroke=None, shadow=False)
    ctx.restore()

def comment_bubble(ctx, x, y, s, t):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(0.06 * math.sin(t * 5))
    ink_fill(ctx, lambda c: (rrect(c, -110, -80, 220, 140, 40), c.move_to(-40, 58), c.line_to(-70, 110), c.line_to(10, 58)), (1, 1, 1), lw=7)
    for i in range(3):
        ctx.new_path(); ctx.arc(-50 + 50 * i, -10, 14, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.restore()

def lea_asmr(ctx, t, sh, x, fy, sc, face=-1, **kw):
    kw.setdefault('eyes', 'half'); kw.setdefault('brows', 0.3); kw.setdefault('smile', 0.6)
    kw.setdefault('look', (-1, 0.2)); kw.setdefault('arms', ('lips', 'hip'))
    mini(ctx, 'lea', 'L', x, fy, t, sh, sc=sc, face=face, **kw)
    hx, hy = head_c(x, fy, sc, kw.get('jump', 0.0))
    headphones(ctx, hx, hy, sc)

def draw_ar(ctx, t, sh):
    TL = sh.tl; T = TL.T; l1, l2, l3, h1, l4, h2, h3, l5, h4 = (T[c] for c, _ in ORDER)
    cap_y = 1220; ban = BAN_A if t < h1 else BAN_B
    ctx.save()
    tb = h1 + wt('arh_1', 'OH', 0.0)
    th = h3 + wt('arh_3', 'HALEINE', 3.7)
    dx, dy = shake_at(t, tb, 34, 0.7)
    ex, ey = shake_at(t, th, 26, 0.6)
    ctx.translate(dx + ex, dy + ey)
    if t < l2:                                     # 1. ASMR : ambiance tamisée, vrai tube, Léa chuchote au micro mousse
        u = t - l1
        footage(ctx, 'd_hero', t, 1.0, 1.08, l2, 540, 800)
        dim(ctx, 0.30)
        foam_mic(ctx, 320, 900, 1.1, t)
        sound_waves(ctx, 330, 900, t, 1.2, col=LILAC, side=-1)
        lea_asmr(ctx, t, sh, 740, 1200, 0.56, eyes='half', arms=('lips', 'hip'), tilt=0.04 * math.sin(t * 1.5))
        word_pop(ctx, 'MONTE LE SON', 330, 560, 64, (1, 1, 1), t, 0.1, rot=-0.05)
        text(ctx, 'CHUT…', 760, 470, 90, fill=LILAC, scale=pop(t, 0.05), rot=0.06)
        if t < 0.2: ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - t / 0.2)); ctx.paint()
    elif t < l3:                                   # 2. le petit bouchon (gros plan réel), Léa tend l'oreille
        u = t - l2
        footage(ctx, 'd_bouchon', 0.3 + u * 1.1, 1.05, 1.18, l3 - l2, 540, 1000)
        dim(ctx, 0.22)
        sound_waves(ctx, 560, 1080, t, 1.4, col=(1, 1, 1))
        word_pop(ctx, 'tic…', 380, 860, 70, LILAC, t, l2 + 0.55, rot=-0.1)
        word_pop(ctx, 'tic…', 720, 800, 60, LILAC, t, l2 + 0.95, rot=0.08)
        lea_asmr(ctx, t, sh, 810, 1340, 0.36, eyes='closed', smile=1.0, arms=('face', 'hip'), look=(-1, 0.4), tilt=-0.12)
        flash(ctx, u, col=LILAC)
    elif t < h1:                                   # 3. la pâte, ralenti hypnotique
        u = t - l3
        footage(ctx, 'd_pate', 1.2 + u * 0.8, 1.1, 1.25, h1 - l3, 560, 900)
        dim(ctx, 0.25)
        for j in range(5):
            sparkle(ctx, 380 + 70 * j, 760 + 40 * math.sin(j * 2 + t), 22, t, ph=j)
        lea_asmr(ctx, t, sh, 800, 1330, 0.36, eyes='closed', smile=1.0, arms=('lips', 'hip'), look=(-1, 0.3), tilt=0.1 * math.sin(t * 2))
        text(ctx, 'mmmh…', 330, 560, 80, fill=LILAC, scale=pop(t, l3 + 0.4), rot=-0.06)
        flash(ctx, u, col=LILAC)
    elif t < l4:                                   # 4. Hamza débarque en criant : le micro tremble, ASMR RATÉ
        u = t - h1
        footage(ctx, 'd_glisse', u * 1.4, 1.0, 1.1, l4 - h1, 540, 900)
        speed_lines(ctx, t, 540, 900, alpha=0.3)
        shock_lines(ctx, 330, 700, t, r=230)
        foam_mic(ctx, 780, 960, 0.8, t, shake=1.0 if u < 1.0 else 0.2)
        xin = 330 - 600 * (1 - ease_out(u / 0.22))
        mini(ctx, 'hamza', 'H', xin, 1250, t, sh, sc=0.5, jump=40 * abs(math.sin(u * 9)), eyes='wide', brows=1.0, smile=1.0,
             look=(1, -0.2), arms=('cheer', 'cheer'), face=1)
        lea_asmr(ctx, t, sh, 860, 1330, 0.34, eyes='wide', brows=0.9, smile=-0.6, arms=('face', 'face'), look=(-1, -0.3),
                 tilt=-0.2, rot=-0.08)
        stamp_txt(ctx, 'ASMR RATÉ', SAFE_CX, 520, 120, REDX, t, h1 + clip_len('arh_1') - 0.05)
        word_pop(ctx, 'MISWAK ?!', 330, 400 + 0 * u, 70, YELC, t, h1 + wt('arh_1', 'MISWAK', 0.7), rot=0.05)
        if u < 0.12: flash(ctx, u, col=(1, 1, 1))
    elif t < h2:                                   # 5. Léa, veine sur le front : « Hamza… on chuchote. »
        u = t - l4
        footage(ctx, 'd_debout', 30 + u * 20, 1.0, 1.06, h2 - l4, 540, 900)
        dim(ctx, 0.35)
        lea_asmr(ctx, t, sh, 560, 1230, 0.55, eyes='half', brows=-1.0, smile=-0.5, arms=('lips', 'hip'), look=(-0.6, 0.0), face=-1)
        hx, hy = head_c(560, 1230, 0.55)
        vein(ctx, hx + 70, hy - 90, t, 1.2)
        mini(ctx, 'hamza', 'H', 200, 1330, t, sh, sc=0.28, eyes='tiny', brows=-0.4, smile=-0.2, look=(1, -0.6), arms=('down', 'chin'))
        sweat(ctx, 150, 1080, t, 0.7)
        cap_y = 1290
        flash(ctx, u)
    elif t < h3:                                   # 6. Hamza chuchote (trop fort) : aux plantes, extrait pur d'Al-Arak
        u = t - h2
        footage(ctx, 'd_boite', u * 0.6, 1.0, 1.1, h3 - h2, 540, 900)
        dim(ctx, 0.18)
        for j in range(5): leaf(ctx, 120 + j * 190, (t * 110 + j * 260) % 1700 + 200, 1.1, t * 2 + j)
        word_pop(ctx, '(il chuchote)', 300, 380, 50, (1, 1, 1), t, h2 + 0.1, rot=-0.04)
        word_pop(ctx, 'AUX PLANTES', SAFE_CX, 520, 78, MINT, t, h2 + wt('arh_2', 'PLANTES', 1.0), rot=-0.04)
        word_pop(ctx, "EXTRAIT PUR D'AL-ARAK", SAFE_CX, 650, 60, GREEN_D, t, h2 + wt('arh_2', "L'EXTRAIT", 1.8), rot=0.03, fg=YELC)
        mini(ctx, 'hamza', 'H', 770, 1170, t, sh, sc=0.44, eyes='half', brows=0.5, smile=0.4, look=(-1, -0.2),
             arms=('lips', 'hip'), face=-1, tilt=0.05 * math.sin(t * 6))
        flash(ctx, u)
    elif t < l5:                                   # 7. sur la boîte… et il recrie « HALEINE FRAÎCHE ! »
        u = t - h3
        footage(ctx, 'd_face', 0.4 + u * 0.6, 1.0, 1.08, l5 - h3, 540, 960)
        dim(ctx, 0.3, col=(0, 0, 0))
        badge(ctx, 'SUR LA BOÎTE :', SAFE_CX, 420, 66, (1, 1, 1), fg=INK, scale=pop(t, h3 + 0.1), rot=-0.03)
        for j, (lab, pre) in enumerate((('DENTS FORTES', 'DENTS'), ('GENCIVES SAINES', 'GENCIVES'), ('HALEINE FRAÎCHE', 'HALEINE'))):
            k = pop(t, h3 + wt('arh_3', pre, 1.5 + j))
            badge(ctx, lab, SAFE_CX - 40, 570 + j * 130, 70 if j < 2 else 70 * (1 + 0.25 * (t > th)), MINT if j != 1 else hexc('#141414'),
                  fg=INK if j != 1 else MINT, scale=k, rot=(-0.04, 0.03, -0.02)[j])
            L.check(ctx, SAFE_CX + 330, 570 + j * 130, 0.8, k)
        loud = t > th
        mini(ctx, 'hamza', 'H', 800, 1370, t, sh, sc=0.34, eyes='wide' if loud else 'half', brows=0.9 if loud else 0.4,
             smile=1.0, look=(-1, -0.8), arms=('cheer', 'cheer') if loud else ('lips', 'point_side'), face=-1,
             jump=40 * abs(math.sin(u * 9)) if loud else 0)
        if loud:
            shock_lines(ctx, 800, 1150, t, r=150)
            lea_asmr(ctx, t, sh, 240, 1370, 0.3, eyes='closed', brows=-1.0, smile=-0.7, arms=('face', 'face'), look=(1, 0), face=1)
        cap_y = 1080
        flash(ctx, u)
    elif t < h4:                                   # 8. question : l'ASMR, ça te détend ou ça t'énerve ?
        u = t - l5
        footage(ctx, 'd_duo', u * 0.8, 1.05, 1.12, h4 - l5, 540, 900)
        ctx.save(); ctx.rectangle(0, 0, W / 2, H); ctx.set_source_rgba(*LILAC, 0.42); ctx.fill()
        ctx.rectangle(W / 2, 0, W / 2, H); ctx.set_source_rgba(*REDX, 0.34); ctx.fill(); ctx.restore()
        badge(ctx, "L'ASMR, ÇA TE…", SAFE_CX, 400, 76, (1, 1, 1), fg=INK, scale=pop(t, l5 + 0.05), rot=-0.03)
        kL = pop(t, l5 + wt('arl_5', 'DÉTEND', 1.6)); kR = pop(t, l5 + wt('arl_5', "T'ÉNERVE", 2.2))
        badge(ctx, 'DÉTEND', 250, 560, 84, NIGHT, fg=LILAC, scale=kL, rot=-0.06)
        badge(ctx, 'ÉNERVE', 710, 560, 84, REDX, fg=(1, 1, 1), scale=kR, rot=0.06)
        text(ctx, 'OU', SAFE_CX, 560, 80, fill=YELC, scale=pop(t, l5 + 1.9), rot=0.08 * math.sin(t * 6))
        lea_asmr(ctx, t, sh, 270, 1120, 0.4, eyes='half', brows=0.3, smile=1.0, arms=('lips', 'hip'), look=(0.5, 0.6), face=1)
        mini(ctx, 'hamza', 'H', 730, 1120, t, sh, sc=0.42, eyes='open', brows=0.6, smile=1.0, look=(-0.4, 0.7),
             arms=('cheer', 'cheer'), jump=30 * abs(math.sin(u * 6)), face=-1)
        kc = pop(t, l5 + wt('arl_5', 'COMMENTAIRE', 3.0))
        if kc > 0.01:
            comment_bubble(ctx, 520, 800, kc * 0.85, t)
            badge(ctx, 'DIS-LE EN COMMENTAIRE', SAFE_CX, 232, 52, MINT, fg=INK, scale=kc, rot=0.02)
        cap_y = 1270; ban = None
        flash(ctx, u)
    else:                                          # 9. prix + appel à l'action (Hamza, enfin à voix normale)
        u = t - h4
        footage(ctx, 'd_sortie', 0.6 + min(u, 2.6) * 0.55, 1.0, 1.06, 3, 540, 1100)
        kp = pop(t, h4 + wt('arh_4', 'CINQ', 0.6))
        tc = h4 + wt('arh_4', 'LE', 1.2)
        if t < tc:
            mini(ctx, 'hamza', 'H', 770, 1010, t, sh, sc=0.42, jump=50 * abs(math.sin(u * 6)), eyes='happy', brows=0.6, smile=1.0,
                 look=(-1, 0), arms=('cheer', 'cheer'), face=-1)
            if kp > 0.01: price_tag(ctx, SAFE_CX, 650, 0.95 * kp, t, 'MOINS DE 5 €', sub=None)
            flash(ctx, u)
        else:
            v = t - tc
            mini(ctx, 'hamza', 'H', 650, 1010, t, sh, sc=0.38, eyes='open', brows=0.5, smile=1.0,
                 look=(-0.6, 0.8), arms=(('down', 'point_down', v / 0.3), 'hip'), face=-1)
            lea_asmr(ctx, t, sh, 850, 1010, 0.32, eyes='open' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
                     arms=('lips', 'hip'), look=(-1, 0.5))
            price_tag(ctx, SAFE_CX, 560, 0.85, t, 'MOINS DE 5 €', sub=None)
            ctx.restore(); L.banner(ctx, t, BAN_B, bg=YELC, fg=INK); L.cta(ctx, t, tc + 0.1); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban == BAN_A: L.banner(ctx, t, ban, bg=NIGHT, fg=LILAC)
    elif ban: L.banner(ctx, t, ban, bg=YELC, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_ar():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.55); T = TL.T; l1, l2, l3, h1, l4, h2, h3, l5, h4 = (T[c] for c, _ in ORDER)
    tb = h1 + wt('arh_1', 'OH', 0.0); th = h3 + wt('arh_3', 'HALEINE', 3.7)
    sfx = [('sparkle', 0.05, 0.25),
           ('pop', l2 + 0.55, 0.18), ('pop', l2 + 0.95, 0.15), ('pop', l2 + 1.25, 0.12),
           ('pschht', l3 + 0.5, 0.12), ('sparkle', l3 + 0.9, 0.15),
           ('scratch', tb - 0.12, 0.45), ('stamp', h1 + clip_len('arh_1') - 0.05, 0.6),
           ('swipe', l4 - 0.03, 0.4), ('buzz', l4 + 0.3, 0.25),
           ('whoosh', h2 - 0.03, 0.4), ('pop', h2 + wt('arh_2', 'PLANTES', 1.0), 0.4), ('sparkle', h2 + wt('arh_2', "L'EXTRAIT", 1.8), 0.4),
           ('whoosh', h3 - 0.03, 0.5), ('ding', h3 + wt('arh_3', 'DENTS', 1.5), 0.5), ('ding', h3 + wt('arh_3', 'GENCIVES', 2.5), 0.5),
           ('ding', th, 0.6), ('boing', th + 0.05, 0.4),
           ('drumroll', l5 + 0.1, 0.25), ('pop', l5 + wt('arl_5', 'DÉTEND', 1.6), 0.5), ('pop', l5 + wt('arl_5', "T'ÉNERVE", 2.2), 0.5),
           ('sparkle', l5 + wt('arl_5', 'COMMENTAIRE', 3.0), 0.5),
           ('swipe', h4 - 0.03, 0.6), ('coins', h4 + wt('arh_4', 'CINQ', 0.6), 0.6),
           ('ding', h4 + wt('arh_4', 'LE', 1.2) + 0.15, 0.7)]
    sh = Shot('asmr_rate', TL.dur, draw_ar, TL.voices(), sfx, []); sh.tl = TL

    return [sh], (0.0, tb)
