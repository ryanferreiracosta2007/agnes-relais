# -*- coding: utf-8 -*-
"""Sketch parfum v2 : rythmé, émotions marquées, sous-titres mot par mot, zone visible TikTok.
Zone sûre (vidéo 1080x1920) : x 60–900, y 150–1380. Bouton « Acheter » TikTok vers (250, 1440)."""
import math, random, cairo
from ink import *
from chars import draw_char
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash, shake_at, speed_lines
from sketch import bg_room

SAFE_CX = 480          # centre visuel (la colonne d'icônes masque x > 900)
CAP_Y = 1190           # sous-titres : au-dessus du bouton Acheter
BANNER = "IL CROYAIT PAS AU PRIX…"
MX, SX, CY = 330, 770, 700   # positions monde : malin (M), sceptique (S), hauteur des têtes
G = 0.07

LINES = [  # (clip, qui, mots (texte, t relatif))
    ('x_s1', 'S', [("ATTENDS…", 0.0), ("C'EST", 1.16), ("QUOI", 1.64), ("CETTE", 1.72), ("ODEUR ?", 1.9)]),
    ('x_m1', 'M', [("C'EST", 0.0), ("MON", 0.52), ("NOUVEAU", 0.64), ("PARFUM.", 0.82)]),
    ('x_s2', 'S', [("MONTRE !", 0.0), ("ÇA", 0.6), ("DOIT", 0.72), ("COÛTER", 0.82), ("UNE", 1.1), ("BLINDE,", 1.22), ("ÇA.", 1.68)]),
    ('x_m2', 'M', [("MOINS", 0.0), ("DE", 0.34), ("25", 0.42), ("EUROS,", 0.9), ("MON", 1.24), ("FRÈRE.", 1.3)]),
    ('x_s3', 'S', []),
    ('x_m3', 'M', [("C'EST", 0.0), ("LE", 0.36), ("CONFIDENTIAL", 0.44), ("PRIVATE", 1.24), ("GOLD", 1.6), ("DE", 1.94), ("CHEZ", 2.24), ("LATTAFA.", 2.4)]),
    ('x_s4', 'S', [("J'EN", 0.12), ("PRENDS", 0.24), ("TROIS !", 0.34)]),
    ('x_m4', 'M', [("LE", 0.0), ("LIEN", 0.46), ("EST", 0.68), ("JUSTE", 0.88), ("EN", 1.1), ("DESSOUS,", 1.26), ("SUR", 1.86),
                   ("LE", 2.0), ("PANIER", 2.08), ("ORANGE.", 2.38), ("AVANT", 3.38), ("QU'IL", 3.66), ("PRENNE", 3.86), ("TOUT !", 4.08)]),
]
PAGES = {'x_s2': [3], 'x_m2': [3], 'x_m3': [5], 'x_m4': [6, 10]}  # coupures de pages (index de mot)

def schedule():
    t = 0.1; out = {}
    for clip, who, words in LINES:
        if clip == 'x_m1': t += 0.35            # le « pschht » avant la réplique
        if clip == 'x_s3': t += 0.05
        if clip == 'x_m3': t += 0.75            # réaction « QUOI » qui respire
        if clip == 'x_m4': t += 0.25
        out[clip] = t; t += clip_len(clip) + G
    return out, t + 1.2

T, DUR = schedule()

# ------------------------------------------------------------------ caméra
def view(ctx, z, wx, wy, sx=SAFE_CX + 20, sy=760, shake=0.0, t=0.0):
    dx, dy = jit(boil_seed(t, 30), 5, shake) if shake else (0, 0)
    ctx.translate(sx + dx, sy + dy); ctx.scale(z, z); ctx.translate(-wx, -wy)

# ------------------------------------------------------------------ sous-titres mot par mot
def captions(ctx, t, y=CAP_Y):
    for clip, who, words in LINES:
        if not words: continue
        a = T[clip]; L = clip_len(clip)
        later = [T[c] for c, _, _ in LINES if T[c] > a]
        end = min([a + L + 0.25] + later)
        if not (a <= t < end): continue
        cuts = [0] + PAGES.get(clip, []) + [len(words)]
        page = None
        for i in range(len(cuts) - 1):
            if t - a >= words[cuts[i]][1] - 0.05: page = (cuts[i], cuts[i + 1])
        if page is None: return
        ws = words[page[0]:page[1]]
        size = 104; gap = 22
        # mise en lignes (max 780 px de large)
        lines = [[]]; cur = 0
        for w_, r in ws:
            wd = text_w(ctx, w_, size)
            if lines[-1] and cur + gap + wd > 780: lines.append([]); cur = 0
            lines[-1].append((w_, r, wd)); cur += (gap if cur else 0) + wd
        for li, ln in enumerate(lines):
            tot = sum(wd for _, _, wd in ln) + gap * (len(ln) - 1)
            x = SAFE_CX - tot / 2; yy = y + (li - (len(lines) - 1) / 2) * size * 1.08
            for w_, r, wd in ln:
                ta = a + r
                if t >= ta - 0.03:
                    k = ease_out_back((t - ta + 0.03) / 0.18, 2.6)
                    nxt = [rr for _, rr in ws if rr > r]
                    active = t < a + (min(nxt) if nxt else L + 0.25)
                    col = (1, 1, 1)
                    if active: col = YEL
                    if any(h in w_ for h in ('PANIER', 'ORANGE')): col = ORANGE
                    if '€' in w_ or 'LATTAFA' in w_: col = YEL if not active else (1, 0.85, 0.2)
                    rot = (-0.06 if (hash(w_) % 2) else 0.06) * (1 if active else 0)
                    ctx.save(); ctx.translate(x + wd / 2, yy - (10 if active else 0)); ctx.rotate(rot)
                    text(ctx, w_, 0, 0, size, fill=col, sw=15, scale=k * (1.12 if active else 1.0))
                    ctx.restore()
                x += wd + gap

def banner(ctx, t):
    k = pop(t, 0.0, 0.3) if t < 0.4 else 1.0
    ctx.save(); ctx.translate(SAFE_CX, 275); ctx.scale(k, k); ctx.rotate(-0.02)
    size = 74; w = text_w(ctx, BANNER, size) + 60
    ctx.new_path(); rrect(ctx, -w / 2 + 7, -50 + 9, w, 100, 22); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -50, w, 100, 22); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, BANNER, 0, 2, size, fill=INK, stroke=None, shadow=False)
    ctx.restore()

# ------------------------------------------------------------------ dessin
BOT = lambda c, x, y, tt: bottle(c, x + 10, y - 45, 0.45, tt, glow=0.4)

def actor(ctx, who, x, y, t, sh, tag, sq=0.0, rot=0.0, sc=0.95, **kw):
    """personnage avec squash/stretch (sq>0 écrase, sq<0 étire), pivot aux pieds"""
    fy = y + 560 * sc
    ctx.save(); ctx.translate(x, fy); ctx.rotate(rot); ctx.scale(1 + sq, 1 - sq); ctx.translate(-x, -fy)
    outfit = 'tee' if tag == 'M' else 'rose'
    draw_char(ctx, 'david', x, y, sc, t + (0.7 if tag == 'S' else 0), outfit=outfit, mouth=sh.mouth(tag, t), **kw)
    ctx.restore()

def draw(ctx, t, sh):
    s1, m1, s2, m2, s3, m3, s4, m4 = (T[c] for c, _, _ in LINES)
    tp = m1 - 0.35                     # pschht
    tprice = m2 + 0.42                 # « vingt-cinq »
    trun = s4 + 0.75                   # il part en courant
    ctx.save()
    # ---------- plan 3 : vraies images (preuve)
    if m3 - 0.05 <= t < s4 - 0.02:
        u = t - (m3 - 0.05); d = s4 - m3
        footage(ctx, 'nom', u, 1.0, 1.14, d, 560, 640, offset=40)
        badge(ctx, 'LATTAFA', SAFE_CX, 470, 82, hexc('#141414'), fg=GOLD, scale=pop(t, m3 + 2.4), rot=-0.04)
        badge(ctx, '100 ML', SAFE_CX - 180, 640, 80, GOLD, fg=INK, scale=pop(t, m3 + 0.6), rot=0.05)
        price_tag(ctx, 640, 900, 0.62 * pop(t, m3 + 0.25), t, '25 €', sub='MOINS DE', rot=0.07)
        flash(ctx, u)
        ctx.restore(); banner(ctx, t); captions(ctx, t); return

    # ---------- caméra par plan (coupes franches + poussée lente)
    if t < tp:                         # 1. gros plan S qui renifle
        cam = (1.7 + 0.05 * t, SX, CY + 30, 0)
    elif t < s2:                       # 2. gros plan M qui se parfume
        cam = (1.65 + 0.05 * (t - tp), MX, CY + 30, 0)
    elif t < m2:                       # 3. plan large : S veut prendre le flacon
        cam = (1.05, 550, CY + 40, 0)
    elif t < s3:                       # 4. gros plan M, très calme
        cam = (1.6 + 0.2 * ease((t - m2) / 1.2), MX, CY + 40, shake_at(t, [tprice], 10))
    elif t < m3:                       # 5. très gros plan S : QUOI ?!
        cam = (2.0, SX, CY + 20, shake_at(t, [s3], 34, 0.5))
    elif t < m4:                       # 6. plan large : il part en courant
        cam = (1.05, 550, CY + 40, 0)
    else:                              # 7. M face caméra, appel à l'action
        cam = (1.2, MX - 50, CY + 100, 0)
    z, wx, wy, shk = cam
    view(ctx, z, wx, wy, shake=shk, t=t)
    bg_room(ctx, t)

    # fond d'explosion pour le QUOI
    if s3 <= t < m3:
        S.rays(ctx, SX, CY, t, hexc('#ffd23f'), 18, 0.9, 0.6)
        ctx.new_path(); ctx.arc(SX, CY, 2000, 0, 7); ctx.set_source_rgba(0.9, 0.15, 0.2, 0.25); ctx.fill()

    # ---------------- le MALIN (M)
    mk = dict(smile=0.8, eyes='half', brows=0.35, look=(1, 0), arms=('down', 'hold'), prop=BOT, prop_hand='R', tilt=0.0)
    if tp <= t < s2:                   # il se parfume puis frime
        u = (t - tp) / 0.35
        mk.update(arms=('down', ('hold', 'spray', u * 2) if u < 1 else 'spray'), eyes='closed' if t < m1 + 0.1 else 'half',
                  smile=1.0, look=(0.6, -0.2), tilt=0.08)
        if t > m1 + 0.75: mk.update(eyes='wink')
    elif s2 <= t < m2:                 # S tend la main : M retire le flacon
        mk.update(arms=('down', ('hold', 'hold_high', (t - s2) / 0.35)), eyes='half', smile=0.9, look=(1, 0), tilt=-0.08)
    elif m2 <= t < s3:                 # calme olympien
        mk.update(eyes='closed' if t < tprice else 'half', smile=1.0, brows=0.6, look=(0.3, 0), tilt=0.05,
                  arms=('down', 'hold_high'), blush=0.0)
    elif s4 <= t < m4:                 # regarde S partir, goutte de sueur
        mk.update(look=(1, 0), eyes='open', smile=0.3, brows=0.9, arms=('down', 'hold'))
    elif t >= m4:                      # face caméra
        mk.update(look=(-0.6, 0.8), eyes='open' if (t - m4) % 2.2 < 1.6 else 'wink', smile=1.0, brows=0.4,
                  arms=(('down', 'point_down', (t - m4) / 0.3), 'hold_high'), tilt=-0.05)
    msq = spring(t, tp, 0.06) + spring(t, tprice, -0.05)
    actor(ctx, 'david', MX, CY, t, sh, 'M', sq=msq, **mk)
    if tp <= t < m1 + 0.9:             # nuage de parfum
        u = t - tp
        for i in range(14):
            rnd = random.Random(i); a = rnd.uniform(-1.2, 0.6); dd = 60 + 260 * u * rnd.uniform(0.6, 1.2)
            ctx.new_path(); ctx.arc(MX + 120 + dd * math.cos(a), CY + 60 + dd * math.sin(a), 10 + 30 * u, 0, 7)
            ctx.set_source_rgba(1, 0.97, 0.85, max(0, 0.75 - 0.6 * u)); ctx.fill()
        for i in range(5): sparkle(ctx, MX - 120 + i * 70, CY - 160 + 40 * math.sin(i), 26, t, i)
    if s4 <= t < m4 and t > trun: sweat(ctx, MX + 95, CY - 90, t, 1.2)

    # ---------------- le SCEPTIQUE (S)
    sx = SX; sk = dict(smile=0.0, eyes='half', brows=-0.7, look=(-1, 0), arms=('down', 'down'), tilt=0.0)
    ssq = 0.0; srot = 0.0
    if t < tp:                         # renifle, méfiant
        sniff = math.sin(t * 16) > 0.3
        sk.update(tilt=-0.1 + 0.05 * math.sin(t * 16), look=(-1, -0.2), eyes='half', brows=-0.8, smile=-0.2,
                  arms=('down', 'chin'))
        ssq = 0.03 * math.sin(t * 16)
    elif s2 <= t < m2:                 # se jette sur le flacon, jaloux
        u = (t - s2) / 0.3
        sk.update(arms=(('down', 'grab', u), 'down'), eyes='open', brows=-1.0, smile=-0.5, look=(-1, -0.4), tilt=-0.12)
        sx = SX - 90 * ease(u); ssq = spring(t, s2, -0.08)
    elif s3 - 0.05 <= t < m3:          # QUOI ?! : yeux qui sortent, recrache sa boisson
        sk.update(eyes='tiny', brows=1.0, smile=-0.3, look=(0, 0), arms=('face', 'face') if t > s3 + 0.35 else ('down', 'drink'),
                  tilt=0.04 * math.sin(t * 40))
        ssq = -0.12 * math.exp(-4 * max(0, t - s3)) + spring(t, s3, 0.05, 20)
    elif s4 <= t < m4:                 # « j'en prends trois ! » puis il file
        sk.update(eyes='heart', brows=0.8, smile=1.0, look=(0, 0), arms=('cheer', 'cheer') if t < trun else ('run', 'run'),
                  blush=1.0)
        hop = abs(math.sin((t - s4) * 9)) * 50 if t < trun else 0
        ssq = spring(t, s4, -0.1)
        if t >= trun:
            u = t - trun; sx = SX + 1600 * u * u + 300 * u; srot = 0.25
        CYs = CY - hop
    if t >= m4: sx = 99999
    if t >= tp and t < s2 and z > 1.5: sx = 99999      # hors champ en gros plan M
    if m2 <= t < s3: sx = 99999
    if sx < 2000:
        yy = CY - (abs(math.sin((t - s4) * 9)) * 50 if s4 <= t < s4 + 0.75 else 0)
        actor(ctx, 'david', sx, yy, t, sh, 'S', sq=ssq, rot=srot, **sk)
        if t < tp: sniff_marks(ctx, sx - 40, yy + 35, t); S.smell_swirl(ctx, sx - 300, yy + 200, t, 0.7)
        if s2 <= t < m2: vein(ctx, sx + 70, yy - 95, t, 1.1)
        if s3 <= t < m3:
            shock_lines(ctx, sx, yy, t, 190)
            spit(ctx, sx - 10, yy + 75, t, s3 + 0.02, -1)
            if t < s3 + 0.35: can(ctx, sx - 60, yy + 110, 0.9, t, -0.6)
        if s4 <= t < trun: hearts_float_local(ctx, t, sx, yy - 120)
    if s4 <= t < m4 and t > trun:
        speed_lines(ctx, t, SX + 500, CY + 200, n=26, alpha=0.4, seed=8); dust(ctx, SX, CY + 520, t, trun)
    ctx.restore()

    # ---------- textes à l'écran (zone sûre)
    if t < tp: text(ctx, '?', 780, 560, 190, fill=YEL, scale=pop(t, 0.5), rot=0.15 + 0.05 * math.sin(t * 8))
    if m2 <= t < s3:
        k = pop(t, tprice, 0.25)
        if k > 0:
            ctx.save(); s_ = 1 + 2.3 * (1 - min(1, (t - tprice) / 0.12)); ctx.translate(SAFE_CX + 170, 470); ctx.scale(s_, s_); ctx.translate(-SAFE_CX - 170, -470)
            price_tag(ctx, SAFE_CX + 170, 470, 0.7, t, '25 €', sub='MOINS DE', rot=-0.07); ctx.restore()
    if s3 <= t < m3:
        k = pop(t, s3, 0.2)
        ctx.save(); ctx.translate(720, 470); ctx.scale(0.8 * k, 0.8 * k); ctx.rotate(-0.08 + 0.03 * math.sin(t * 30))
        burst(ctx, 0, 0, 230, hexc('#e8263d'), boil_seed(t), 14, 0.68); text(ctx, 'QUOI ?!', 0, 0, 150, fill=YEL, sw=16)
        ctx.restore()
    if s4 <= t < m4:
        text(ctx, 'X3 !', 760, 480, 150, fill=hexc('#ff7fb0'), scale=pop(t, s4 + 0.3), rot=0.12)
    if t >= m4:                        # appel à l'action : badge + flèche vers le bouton Acheter
        k = pop(t, m4 + 0.5)
        badge(ctx, 'PANIER ORANGE', SAFE_CX - 30, 1080, 88, ORANGE, scale=k, rot=-0.03)
        cart_icon(ctx, SAFE_CX + 330, 1075, 0.95 * k)
        if k > 0:
            bob = 18 * math.sin(t * 7)
            arrow(ctx, 330, 1165 + bob * 0.6, 210, 1350 + bob * 0.6, t, w=60)
        price_tag(ctx, 205, 470, 0.45 * pop(t, m4 + 0.1), t, '25 €', sub='MOINS DE', rot=-0.08)
    banner(ctx, t)
    captions(ctx, t, 900 if t >= m4 else CAP_Y)
    flash(ctx, min([t - c for c in (tp, s2, m2, s3, m4) if c <= t] or [9]), 0.08)

def hearts_float_local(ctx, t, x, y):
    for i in range(4):
        u = ((t * 1.5 + i * 0.25) % 1.0)
        ctx.save(); ctx.translate(x - 90 + i * 60, y - 200 * u); ctx.scale(1 - u * 0.5, 1 - u * 0.5)
        ink_fill(ctx, lambda c: heart(c, 0, 0, 30), hexc('#e8455e'), lw=4); ctx.restore()

def build():
    voices = [(c, T[c], who) for c, who, _ in LINES]
    s1, m1, s2, m2, s3, m3, s4, m4 = (T[c] for c, _, _ in LINES)
    sfx = [('sniff', 0.2, 0.7), ('sniff', 1.1, 0.7), ('pschht', m1 - 0.35, 0.9), ('sparkle', m1 + 0.2, 0.5), ('wink', m1 + 0.75, 0.6),
           ('whoosh', s2 - 0.03, 0.6), ('boing', s2 + 0.05, 0.5), ('stamp', m2 + 0.42, 0.9), ('coins', m2 + 0.45, 0.4),
           ('scratch', s3 - 0.08, 1.0), ('spit', s3 + 0.02, 0.9), ('boing', s3 + 0.1, 0.6), ('whoosh', m3 - 0.05, 0.6),
           ('pop', m3 + 0.6, 0.5), ('pop', m3 + 2.4, 0.5), ('heart', s4 + 0.2, 0.6), ('whoosh', s4 + 0.75, 1.0),
           ('pop', m4 + 0.5, 0.6), ('ding', m4 + 0.6, 0.7)]
    return [Shot('v2', DUR, draw, voices, sfx, [])], (s3 - 0.1, m3)
