# -*- coding: utf-8 -*-
"""Dentifrice Miswak : « POV : tu fouilles la salle de bain de ton date — red flag ou green flag ? »
   Mini Inès, lampe torche à la main, inspecte la salle de bain : tube écrasé au milieu (RED FLAG), brosse à dents
   écrabouillée (RED FLAG) ; mini Hamza (le date) débarque paniqué : « regarde plutôt ça ! » ; le vrai tube Miswak,
   aux plantes, extrait pur d'Al-Arak : GREEN FLAG. Question : « ton red flag, c'est quoi ? »"""
import math
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from mini2 import mini, leaf, ease_out
import fg_data as FG

WORDS = {c: FG.words_for(c) for c in FG.CUTS}
for w in ('DATE ?', 'RED', 'GREEN', 'FLAG.', 'FLAG !', 'FLAG,', 'PLANTES,', "D'AL-ARAK ?", 'CINQ', 'EUROS.', 'COMMENTAIRE.',
          'ÉCRASÉ', 'ÉCRABOUILLÉE...'):
    if w not in S.HL: S.HL = S.HL + (w,)
MINT = hexc('#3ddc97'); GREEN_D = hexc('#0f5132'); REDX = hexc('#e8263d'); YELC = hexc('#ffd23f')
GREENF = hexc('#22c55e'); TILE = hexc('#cfe7ee'); TILE_D = hexc('#9cc3cf'); NIGHT = hexc('#101826')
BAN_A = 'POV : LA SALLE DE BAIN DE TON DATE'; BAN_B = 'RED FLAG OU GREEN FLAG ?'
ORDER = [('fi_1', 'I'), ('fi_2', 'I'), ('fi_3', 'I'), ('fh_1', 'H'), ('fi_4', 'I'), ('fi_5', 'I'), ('fh_2', 'H'),
         ('fi_6', 'I'), ('fh_3', 'H')]
PAUSE = {'fi_5': 0.05}
HK = dict(outfit='sweat')

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def wt2(clip, prefix, n, default):
    hits = [r for w, r in WORDS.get(clip, []) if w.startswith(prefix)]
    return hits[n] if len(hits) > n else default

def head_c(x, fy, sc, jump=0.0):
    return x, fy - 770 * sc - jump + 165 * sc

def word_pop(ctx, txt, x, y, size, col, t, t0, rot=0.0, fg=INK):
    k = pop(t, t0, 0.25)
    if k > 0.01: badge(ctx, txt, x, y, size, col, fg=fg, scale=k, rot=rot)

def shake_at(t, t0, amp=26, d=0.5):
    u = t - t0
    if u < 0 or u > d: return 0.0, 0.0
    e = (1 - u / d) * amp
    return e * math.sin(u * 91), e * math.cos(u * 73)

# ------------------------------------------------------------------ accessoires
def flag(ctx, x, y, s, t, col, label, k=1.0, rot=0.0, fg=(1, 1, 1)):
    """drapeau planté (pied en x, y) qui flotte ; label écrit sur le tissu"""
    if k <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * k, s * k)
    ink_fill(ctx, lambda c: rrect(c, -9, -520, 18, 520, 8), hexc('#8a8f99'), lw=5)
    ink_fill(ctx, lambda c: c.arc(0, -528, 18, 0, 7), YELC, lw=5)
    fw, fh = 330, 190
    def cloth(c):
        n = 12
        top = [(9 + fw * i / n, -505 + 14 * math.sin(t * 9 + i * 0.7) * i / n) for i in range(n + 1)]
        bot = [(9 + fw * i / n, -505 + fh + 14 * math.sin(t * 9 + i * 0.7) * i / n) for i in range(n, -1, -1)]
        c.move_to(*top[0])
        for p in top[1:] + bot: c.line_to(*p)
        c.close_path()
    ink_fill(ctx, cloth, col, lw=7)
    ctx.save(); ctx.translate(9 + fw / 2, -505 + fh / 2 + 7 * math.sin(t * 9 + 4)); ctx.rotate(0.03 * math.sin(t * 9))
    lines = label.split('\n')
    for i, ln in enumerate(lines):
        text(ctx, ln, 0, (i - (len(lines) - 1) / 2) * 74, 78, fill=fg, stroke=INK, shadow=False)
    ctx.restore()
    ctx.restore()

def bathroom(ctx, t, tint=0.0):
    """mur carrelé + étagère dessinés"""
    ctx.set_source_rgb(*TILE); ctx.paint()
    ctx.set_source_rgb(*TILE_D); ctx.set_line_width(5)
    for i in range(0, W + 1, 135):
        ctx.move_to(i, 0); ctx.line_to(i, H); ctx.stroke()
    for j in range(0, H + 1, 135):
        ctx.move_to(0, j); ctx.line_to(W, j); ctx.stroke()
    ink_fill(ctx, lambda c: rrect(c, -40, 980, W + 80, 60, 10), hexc('#f3efe6'), lw=7)
    ctx.set_source_rgba(0, 0, 0, 0.18); ctx.rectangle(0, 1040, W, 40); ctx.fill()
    if tint: ctx.set_source_rgba(*NIGHT, tint); ctx.paint()

def squeezed_tube(ctx, x, y, s, t, rot=0.0):
    """tube générique (sans marque) écrasé en plein milieu"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    def body(c):
        c.move_to(-260, -70); c.curve_to(-120, -80, -60, -18, 0, -16); c.curve_to(60, -18, 140, -95, 230, -60)
        c.line_to(230, 60); c.curve_to(140, 95, 60, 18, 0, 16); c.curve_to(-60, 18, -120, 80, -260, 70); c.close_path()
    ink_fill(ctx, body, hexc('#eeeeee'), lw=8)
    for k in (-1, 1):
        ctx.new_path(); ctx.move_to(-40, k * 10); ctx.line_to(40, -k * 12); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    ink_fill(ctx, lambda c: rrect(c, 228, -38, 70, 76, 10), hexc('#9aa3ad'), lw=7)
    ink_fill(ctx, lambda c: rrect(c, -290, -78, 34, 156, 6), hexc('#d6d6d6'), lw=6)
    ctx.restore()

def sad_brush(ctx, x, y, s, t, rot=0.0):
    """brosse à dents usée, poils écrabouillés partout"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -330, -26, 470, 52, 26), hexc('#7fb7ff'), lw=7)
    ink_fill(ctx, lambda c: rrect(c, 120, -34, 200, 68, 24), hexc('#7fb7ff'), lw=7)
    for i in range(9):
        bx = 140 + i * 20; a = (i - 4) * 0.28 + 0.12 * math.sin(t * 3 + i)
        ctx.new_path(); ctx.move_to(bx, -30)
        ctx.line_to(bx + 95 * math.sin(a), -30 - 95 * math.cos(a) * (0.55 + 0.25 * (i % 3)))
        ctx.set_source_rgb(*INK); ctx.set_line_width(13); ctx.stroke()
        ctx.new_path(); ctx.move_to(bx, -30)
        ctx.line_to(bx + 95 * math.sin(a), -30 - 95 * math.cos(a) * (0.55 + 0.25 * (i % 3)))
        ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(7); ctx.stroke()
    ctx.restore()

def flies(ctx, x, y, t, n=3, r=90):
    for i in range(n):
        a = t * (3 + i) + i * 2.1
        px, py = x + r * math.cos(a), y + 0.5 * r * math.sin(a * 1.3)
        ctx.new_path(); ctx.arc(px, py, 9, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
        for sd in (-1, 1):
            ctx.new_path(); ctx.arc(px + sd * 9, py - 9, 8, 0, 7); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()

def torch_light(ctx, cx, cy, r=330, a=0.82):
    g = cairo.RadialGradient(cx, cy, r * 0.55, cx, cy, r)
    g.add_color_stop_rgba(0, *NIGHT, 0.0); g.add_color_stop_rgba(1, *NIGHT, a)
    ctx.set_source(g); ctx.paint()

def torch(ctx, x, y, s, rot):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -20, -90, 40, 120, 10), hexc('#3a3f4a'), lw=5)
    ink_fill(ctx, lambda c: (c.move_to(-34, -150), c.line_to(34, -150), c.line_to(20, -90), c.line_to(-20, -90), c.close_path()), YELC, lw=5)
    ctx.restore()

def magnifier(ctx, x, y, s, rot=-0.5):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -14, 60, 28, 140, 10), hexc('#6b3e1f'), lw=5)
    ctx.new_path(); ctx.arc(0, 0, 70, 0, 7); ctx.set_source_rgba(0.8, 0.95, 1, 0.35); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(16); ctx.stroke_preserve(); ctx.set_source_rgb(*YELC); ctx.set_line_width(8); ctx.stroke()
    ctx.restore()

def comment_bubble(ctx, x, y, s, t):
    if s <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(0.06 * math.sin(t * 5))
    ink_fill(ctx, lambda c: (rrect(c, -110, -80, 220, 140, 40), c.move_to(-40, 58), c.line_to(-70, 110), c.line_to(10, 58)), (1, 1, 1), lw=7)
    for i in range(3):
        ctx.new_path(); ctx.arc(-50 + 50 * i, -10, 14, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.restore()

def counter(ctx, t, n_red, n_green):
    """compteur en haut à gauche : drapeaux rouges / verts"""
    ctx.save(); ctx.translate(120, 400)
    for i in range(n_red):
        ink_fill(ctx, lambda c, i=i: (c.move_to(i * 62, 0), c.line_to(i * 62 + 48, 16), c.line_to(i * 62, 32), c.close_path()), REDX, lw=4)
        ctx.new_path(); ctx.move_to(i * 62, -6); ctx.line_to(i * 62, 70); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    for j in range(n_green):
        i = n_red + j
        ink_fill(ctx, lambda c, i=i: (c.move_to(i * 62, 0), c.line_to(i * 62 + 48, 16), c.line_to(i * 62, 32), c.close_path()), GREENF, lw=4)
        ctx.new_path(); ctx.move_to(i * 62, -6); ctx.line_to(i * 62, 70); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()

def ines(ctx, t, sh, x, fy, sc, face=-1, **kw):
    kw.setdefault('eyes', 'open'); kw.setdefault('brows', 0.3); kw.setdefault('smile', 0.4)
    kw.setdefault('look', (-1, 0.2)); kw.setdefault('arms', ('hip', 'hip'))
    mini(ctx, 'ines', 'I', x, fy, t, sh, sc=sc, face=face, **kw)

def hamza(ctx, t, sh, x, fy, sc, face=1, **kw):
    kw.setdefault('eyes', 'open'); kw.setdefault('brows', 0.3); kw.setdefault('smile', 0.6)
    mini(ctx, 'hamza', 'H', x, fy, t, sh, sc=sc, face=face, **HK, **kw)

# ------------------------------------------------------------------ montage
def draw_fg(ctx, t, sh):
    TL = sh.tl; T = TL.T; i1, i2, i3, h1, i4, i5, h2, i6, h3 = (T[c] for c, _ in ORDER)
    cap_y = 1220; ban = BAN_A if t < i4 else BAN_B
    r1 = i2 + wt('fi_2', 'RED', 1.9); r2 = i3 + wt('fi_3', 'RED', 1.6); g1 = i5 + wt('fi_5', 'GREEN', 0.0)
    ctx.save()
    dx, dy = shake_at(t, r1, 24, 0.45); ex, ey = shake_at(t, r2, 30, 0.5)
    ctx.translate(dx + ex, dy + ey)
    nred = int(t >= r1) + int(t >= r2); ngreen = int(t >= g1)
    if t < i2:                                     # 1. le vrai tube dans le noir, lampe torche d'Inès qui balaye
        u = t - i1
        footage(ctx, 'd_hero', t, 1.12, 1.2, i2, 540, 820)
        lx = 470 + 140 * math.sin(u * 2.2); ly = 760 + 80 * math.cos(u * 1.7)
        torch_light(ctx, lx, ly, 460, 0.72)
        ines(ctx, t, sh, 760, 1440, 0.44, eyes='half', brows=0.8, smile=0.7, arms=('point_side', 'lips'), look=(-1, -0.3),
             walk=t * 5, tilt=0.06 * math.sin(t * 4))
        hx, hy = head_c(760, 1440, 0.44)
        torch(ctx, hx - 170, hy + 120, 0.9, -0.9 + 0.2 * math.sin(u * 2.2))
        text(ctx, '?', lx + 120, ly - 160, 120, fill=YELC, scale=pop(t, 0.6), rot=0.15)
        badge(ctx, 'RED FLAG OU GREEN FLAG ?', SAFE_CX, 420, 62, (1, 1, 1), fg=REDX, scale=pop(t, 0.15), rot=-0.03)
        cap_y = 1050
        if t < 0.2: ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - t / 0.2)); ctx.paint()
    elif t < i3:                                   # 2. le tube écrasé au milieu : RED FLAG
        u = t - i2
        bathroom(ctx, t)
        z = 1.0 + 0.08 * min(u, 2.5) / 2.5
        ctx.save(); ctx.translate(SAFE_CX, 880); ctx.scale(z, z); ctx.translate(-SAFE_CX, -880)
        squeezed_tube(ctx, SAFE_CX - 20, 900, 1.25, t, rot=-0.05)
        flies(ctx, SAFE_CX - 20, 740, t)
        ctx.restore()
        word_pop(ctx, 'ÉCRASÉ AU MILIEU…', SAFE_CX, 560, 66, (1, 1, 1), t, i2 + wt('fi_2', 'ÉCRASÉ', 1.0), rot=-0.04)
        if t >= r1:
            ctx.set_source_rgba(*REDX, 0.22 * max(0, 1 - (t - r1) / 0.5)); ctx.paint()
            flag(ctx, 640, 985, 0.85, t, REDX, 'RED\nFLAG', k=pop(t, r1, 0.3), rot=0.08)
        ines(ctx, t, sh, 780, 1530, 0.4, face=-1, eyes='half', brows=-0.8, smile=-0.8, arms=('face', 'hip'), look=(-1, -0.4))
        cap_y = 1170
        flash(ctx, u)
    elif t < h1:                                   # 3. la brosse écrabouillée : 2e RED FLAG
        u = t - i3
        bathroom(ctx, t)
        ctx.save(); ctx.translate(SAFE_CX, 860); ctx.rotate(-0.03 * math.sin(t * 3)); ctx.translate(-SAFE_CX, -860)
        sad_brush(ctx, SAFE_CX + 20, 900, 1.25, t, rot=-0.08)
        ctx.restore()
        flies(ctx, SAFE_CX + 230, 720, t, n=4, r=110)
        word_pop(ctx, 'ÉCRABOUILLÉE…', SAFE_CX, 560, 70, (1, 1, 1), t, i3 + wt('fi_3', 'ÉCRAB', 0.8), rot=0.04)
        flag(ctx, 140, 985, 0.55, t, REDX, 'RED\nFLAG', rot=-0.1)
        if t >= r2:
            ctx.set_source_rgba(*REDX, 0.28 * max(0, 1 - (t - r2) / 0.5)); ctx.paint()
            flag(ctx, 560, 985, 0.9, t, REDX, 'RED\nFLAG !', k=pop(t, r2, 0.3), rot=0.1)
            stamp = pop(t, r2 + 0.15, 0.25)
            if stamp > 0.01: badge(ctx, 'x2', 860, 620, 110, REDX, fg=(1, 1, 1), scale=stamp, rot=0.15)
        ines(ctx, t, sh, 790, 1530, 0.4, face=-1, eyes='wide', brows=-1.0, smile=-1.0, arms=('face', 'face'), look=(-1, 0.4),
             jump=30 * max(0, math.sin((t - r2) * 9)) if t >= r2 else 0)
        cap_y = 1170
        flash(ctx, u)
    elif t < i4:                                   # 4. Hamza (le date) débarque paniqué : « regarde plutôt ça ! »
        u = t - h1
        footage(ctx, 'd_main', u * 1.0, 1.0, 1.08, i4 - h1, 540, 860)
        speed_lines(ctx, t, 540, 860, alpha=0.25)
        xin = 260 - 520 * (1 - ease_out(u / 0.25))
        hamza(ctx, t, sh, xin, 1360, 0.42, jump=34 * abs(math.sin(u * 10)) if u < 1.2 else 0, eyes='wide', brows=1.0, smile=0.3,
              look=(1, -0.2), arms=('run', 'run') if u < 1.0 else ('point_side', 'hip'), walk=t * 14 if u < 1.0 else 0)
        sweat(ctx, xin + 90, 920, t, 0.8)
        word_pop(ctx, 'ATTENDS !', 300, 470, 90, YELC, t, h1 + 0.05, rot=-0.06)
        word_pop(ctx, 'REGARDE ÇA !', 640, 600, 70, (1, 1, 1), t, h1 + wt('fh_1', 'REGARDE', 1.0), rot=0.05)
        counter(ctx, t, nred, 0)
        flash(ctx, u)
    elif t < i5:                                   # 5. vrai tube : aux plantes, extrait pur d'Al-Arak (Inès intriguée, loupe)
        u = t - i4
        footage(ctx, 'd_boite', u * 0.7, 1.0, 1.1, i5 - i4, 540, 900)
        for j in range(5): leaf(ctx, 120 + j * 190, (t * 120 + j * 260) % 1700 + 200, 1.1, t * 2 + j)
        word_pop(ctx, 'AUX PLANTES', SAFE_CX, 470, 84, MINT, t, i4 + wt('fi_4', 'PLANTES', 1.3), rot=-0.04)
        word_pop(ctx, "EXTRAIT PUR D'AL-ARAK", SAFE_CX, 600, 62, GREEN_D, t, i4 + wt('fi_4', "L'EXTRAIT", 2.2), rot=0.03, fg=YELC)
        ines(ctx, t, sh, 780, 1340, 0.4, eyes='wide', brows=0.9, smile=0.5, arms=('chin', 'hip'), look=(-1, -0.2), tilt=0.06)
        hx, hy = head_c(780, 1340, 0.4)
        magnifier(ctx, hx - 150, hy + 30, 0.9, rot=-0.4)
        counter(ctx, t, nred, 0)
        cap_y = 1180
        flash(ctx, u)
    elif t < h2:                                   # 6. GREEN FLAG : drapeau vert, Inès yeux en cœur
        u = t - i5
        footage(ctx, 'd_duo', u * 1.0, 1.0, 1.08, h2 - i5, 540, 900)
        rays(ctx, 540, 820, t, GREENF, alpha=0.22)
        ctx.set_source_rgba(*GREENF, 0.25 * max(0, 1 - (t - g1) / 0.5) if t >= g1 else 0); ctx.paint()
        flag(ctx, 560, 1150, 1.0, t, GREENF, 'GREEN\nFLAG', k=pop(t, g1, 0.3), rot=-0.06)
        ines(ctx, t, sh, 230, 1400, 0.36, face=1, eyes='heart', brows=0.6, smile=1.0, arms=('cheer', 'cheer'), look=(1, -0.3),
             jump=40 * abs(math.sin(u * 7)))
        S.hearts_float(ctx, t, 260, 900, n=6, start=g1)
        counter(ctx, t, nred, ngreen)
        cap_y = 1230
        flash(ctx, u, col=GREENF)
    elif t < i6:                                   # 7. Hamza fier : ce qui est écrit sur la boîte
        u = t - h2
        footage(ctx, 'd_face', 0.4 + u * 0.6, 1.0, 1.08, i6 - h2, 540, 960)
        ctx.set_source_rgba(0, 0, 0, 0.3); ctx.paint()
        badge(ctx, 'SUR LA BOÎTE :', SAFE_CX, 420, 66, (1, 1, 1), fg=INK, scale=pop(t, h2 + 0.1), rot=-0.03)
        for j, (lab, pre) in enumerate((('DENTS FORTES', 'DENTS'), ('GENCIVES SAINES', 'GENCIVES'), ('HALEINE FRAÎCHE', 'HALEINE'))):
            k = pop(t, h2 + wt('fh_2', pre, 1.5 + j))
            badge(ctx, lab, SAFE_CX - 40, 570 + j * 130, 70, GREENF if j != 1 else hexc('#141414'),
                  fg=INK if j != 1 else GREENF, scale=k, rot=(-0.04, 0.03, -0.02)[j])
            L.check(ctx, SAFE_CX + 330, 570 + j * 130, 0.8, k)
        hamza(ctx, t, sh, 760, 1440, 0.36, face=-1, eyes='happy' if (u % 2) < 1.4 else 'wink', brows=0.7, smile=1.0,
              look=(-1, -0.6), arms=('hip', 'point_side'), tilt=0.04 * math.sin(t * 5))
        ines(ctx, t, sh, 230, 1440, 0.3, face=1, eyes='heart', smile=0.9, arms=('lips', 'hip'), look=(1, 0))
        cap_y = 1000
        flash(ctx, u)
    elif t < h3:                                   # 8. question au spectateur : ton red flag, c'est quoi ?
        u = t - i6
        bathroom(ctx, t, tint=0.12)
        ctx.set_source_rgba(*REDX, 0.30); ctx.paint()
        badge(ctx, 'ET TOI, TON RED FLAG', SAFE_CX, 420, 76, (1, 1, 1), fg=REDX, scale=pop(t, i6 + 0.05), rot=-0.03)
        badge(ctx, 'SALLE DE BAIN ?', SAFE_CX, 530, 76, REDX, fg=(1, 1, 1), scale=pop(t, i6 + 0.35), rot=0.03)
        flag(ctx, 180, 1180, 0.55, t, REDX, 'RED\nFLAG', rot=-0.1)
        flag(ctx, 760, 1180, 0.55, t, REDX, '???', rot=0.1, k=pop(t, i6 + 0.6))
        ines(ctx, t, sh, 480, 1200, 0.42, face=1, eyes='open', brows=0.6, smile=1.0, arms=('point_side', 'hip'), look=(0.3, 0.7))
        kc = pop(t, i6 + wt('fi_6', 'COMMENTAIRE', 2.4))
        if kc > 0.01:
            comment_bubble(ctx, 740, 760, kc * 0.85, t)
            badge(ctx, 'DIS-LE EN COMMENTAIRE', SAFE_CX, 660, 56, MINT, fg=INK, scale=kc, rot=0.02)
        cap_y = 1290; ban = None
        flash(ctx, u)
    else:                                          # 9. prix + appel à l'action
        u = t - h3
        footage(ctx, 'd_sortie', 0.6 + min(u, 3.0) * 0.5, 1.0, 1.06, 3, 540, 1100)
        kp = pop(t, h3 + wt('fh_3', 'CINQ', 1.0))
        tc = h3 + wt('fh_3', 'LE', 2.0)
        flag(ctx, 840, 1100, 0.5, t, GREENF, 'GREEN\nFLAG', rot=0.08)
        if t < tc:
            hamza(ctx, t, sh, 700, 1010, 0.4, face=-1, jump=40 * abs(math.sin(u * 6)), eyes='happy', brows=0.6, smile=1.0,
                  look=(-1, 0), arms=('cheer', 'cheer'))
            if kp > 0.01: price_tag(ctx, SAFE_CX - 60, 620, 0.95 * kp, t, 'MOINS DE 5 €', sub=None)
            flash(ctx, u)
        else:
            v = t - tc
            hamza(ctx, t, sh, 640, 1010, 0.36, face=-1, eyes='open', brows=0.5, smile=1.0,
                  look=(-0.6, 0.8), arms=(('down', 'point_down', min(1, v / 0.3)), 'hip'))
            ines(ctx, t, sh, 330, 1010, 0.3, face=1, eyes='heart' if (v % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0,
                 arms=('cheer', 'hip'), look=(1, 0.5))
            price_tag(ctx, SAFE_CX - 60, 560, 0.85, t, 'MOINS DE 5 €', sub=None)
            ctx.restore(); L.banner(ctx, t, BAN_B, bg=YELC, fg=INK); L.cta(ctx, t, tc + 0.1); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban == BAN_A: L.banner(ctx, t, ban, bg=NIGHT, fg=YELC, size=60)
    elif ban: L.banner(ctx, t, ban, bg=YELC, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_fg():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.04, tail=0.45); T = TL.T; i1, i2, i3, h1, i4, i5, h2, i6, h3 = (T[c] for c, _ in ORDER)
    r1 = i2 + wt('fi_2', 'RED', 1.9); r2 = i3 + wt('fi_3', 'RED', 1.6); g1 = i5 + wt('fi_5', 'GREEN', 0.0)
    sfx = [('swipe', 0.02, 0.35), ('sparkle', 0.6, 0.2),
           ('whoosh', i2 - 0.03, 0.4), ('buzz', r1, 0.55), ('stamp', r1 + 0.02, 0.4),
           ('whoosh', i3 - 0.03, 0.4), ('buzz', r2, 0.6), ('stamp', r2 + 0.15, 0.5),
           ('scratch', h1 - 0.08, 0.45), ('boing', h1 + 0.2, 0.3),
           ('swipe', i4 - 0.03, 0.4), ('pop', i4 + wt('fi_4', 'PLANTES', 1.3), 0.4), ('sparkle', i4 + wt('fi_4', "L'EXTRAIT", 2.2), 0.4),
           ('bells', g1, 0.45), ('heart', g1 + 0.2, 0.5),
           ('whoosh', h2 - 0.03, 0.45), ('ding', h2 + wt('fh_2', 'DENTS', 1.5), 0.5), ('ding', h2 + wt('fh_2', 'GENCIVES', 2.5), 0.5),
           ('ding', h2 + wt('fh_2', 'HALEINE', 3.5), 0.55),
           ('drumroll', i6 + 0.1, 0.25), ('sparkle', i6 + wt('fi_6', 'COMMENTAIRE', 2.4), 0.5),
           ('swipe', h3 - 0.03, 0.6), ('coins', h3 + wt('fh_3', 'CINQ', 1.0), 0.6),
           ('ding', h3 + wt('fh_3', 'LE', 2.0) + 0.15, 0.7)]
    sh = Shot('red_flag', TL.dur, draw_fg, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
