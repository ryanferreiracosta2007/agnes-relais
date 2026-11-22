# -*- coding: utf-8 -*-
"""Lot de nuit parfum : classement, choc du prix (carrousel animé), discussion SMS."""
import math, random, os, cairo
from ink import *
from chars import draw_char
from props import *
import scenes as S
from scenes import Shot, caps_from, clip_len, footage, flash, cam, shake_at
from sketch import bg_room

T = {}  # repères de mots, remplis par make_nuit.py

def banner(ctx, txt, t, y=290, size=80):
    k = pop(t, 0.0, 0.3) if t < 0.4 else 1.0
    if k <= 0.01: return
    ctx.save(); ctx.translate(540, y); ctx.scale(k, k)
    ctx.select_font_face('Bangers'); ctx.set_font_size(size)
    w = min(ctx.text_extents(txt).x_advance + 60, 1000)
    ctx.new_path(); rrect(ctx, -w / 2 + 6, -size * 0.66 + 8, w, size * 1.32, 22); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -size * 0.66, w, size * 1.32, 22); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, txt, 0, 2, size, fill=INK, stroke=None, shadow=False, max_w=w - 50)
    ctx.restore()

BOT = lambda c, x, y, tt: bottle(c, x + 20, y - 50, 0.5, tt, glow=0.5)

# ------------------------------------------------------------------ éléments dessinés
def sock(ctx, x, y, s, t):
    sd = boil_seed(t) + 31
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    pts = [(-30, -90), (30, -90), (32, 20), (80, 40), (85, 85), (40, 95), (-30, 70), (-34, 20)]
    ink_fill(ctx, lambda c: blob(c, pts, sd, 1.2), hexc('#d7263d'), lw=6)
    ink_fill(ctx, lambda c: blob(c, [(-34, -90), (34, -90), (34, -60), (-34, -60)], sd + 1, 0.8), (1, 1, 1), lw=5)
    for i in range(3):
        ink_fill(ctx, lambda c, i=i: star(c, -10 + i * 22, -10 + (i % 2) * 30, 12, 5, 5), (1, 1, 1), lw=2.5)
    ctx.restore()

def candle(ctx, x, y, s, t):
    sd = boil_seed(t) + 41
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ink_fill(ctx, lambda c: blob(c, [(-60, -40), (60, -40), (64, 80), (-64, 80)], sd, 1.0), hexc('#cfe3f2'), lw=6,
             shade=lambda c: c.rectangle(-70, -45, 30, 130), seed=sd)
    ink_fill(ctx, lambda c: c.rectangle(-45, 0, 90, 40), hexc('#f4efe6'), lw=4)
    ink_line(ctx, [(0, -40), (0, -60)], sd, 4)
    fl = 1 + 0.15 * math.sin(t * 17)
    ink_fill(ctx, lambda c: blob(c, [(0, -58), (-12, -76), (0, -105 * fl), (12, -76)], sd + 2, 0.8), hexc('#ffb43a'), lw=4)
    ctx.restore()

def medal(ctx, x, y, s, rank, t):
    col = {1: GOLD, 2: hexc('#c9ccd2'), 3: hexc('#c27c3e')}[rank]
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    for k, cc in ((-1, hexc('#2f63b5')), (1, hexc('#d7263d'))):
        ink_fill(ctx, lambda c, k=k: blob(c, [(k * 8, -80), (k * 40, -80), (k * 22, -20), (k * 2, -20)], 3 + k, 0.4), cc, lw=4)
    ink_fill(ctx, lambda c: c.arc(0, 10, 42, 0, 7), col, lw=6)
    text(ctx, str(rank), 0, 10, 56, fill=(1, 1, 1), sw=6)
    ctx.restore()

def cross_out(ctx, x, y, w, k):
    if k <= 0: return
    for a, b in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
        ctx.new_path(); ctx.move_to(x + a[0] * w, y + a[1] * w)
        ctx.line_to(x + a[0] * w + (b[0] - a[0]) * w * k, y + a[1] * w + (b[1] - a[1]) * w * k)
        ctx.set_source_rgb(*INK); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc('#e8453c')); ctx.set_line_width(14); ctx.stroke()

def proof_shot(name, clip, banner_txt, m3):
    """vraies images du flacon + badges (repris du sketch)"""
    a = 0.1; L = clip_len(clip); d = a + L + 0.15; dn = min(d, 5.6)
    def draw(ctx, t, sh):
        if t < dn: footage(ctx, 'nom', t, 1.0, 1.12, dn, 600, 700)
        else: footage(ctx, 'fl1', t - dn, 1.0, 1.08, d - dn)
        for i, (s, r, bg, fg) in enumerate([('LATTAFA', m3[1], hexc('#141414'), GOLD), ('100 ML', m3[2], GOLD, INK),
                                            ('PÊCHE', m3[3], hexc('#ff8a3d'), (1, 1, 1)), ('VANILLE', m3[4], hexc('#f4c430'), INK),
                                            ('MUSC', m3[5], hexc('#8a6fb0'), (1, 1, 1))]):
            x = 540 if i < 2 else 200 + (i - 2) * 340; y = 470 + i * 130 if i < 2 else 1250
            badge(ctx, s, x, y, 80 if i < 2 else 66, bg, fg=fg, scale=pop(t, a + r), rot=-0.04 if i % 2 else 0.04)
        price_tag(ctx, 800, 1560, 0.5, t, '25 €', sub='MOINS DE', rot=0.08)
        banner(ctx, banner_txt, 1); flash(ctx, t)
    caps = caps_from(clip, a, [('REGARDE.', 0.0), ('CONFIDENTIAL PRIVATE GOLD', m3[0])], 0.0)
    caps[-1] = (caps[-1][0], caps[-1][1], a + m3[2])
    return Shot(name, d, draw, [(clip, a, 'p')], [('whoosh', 0.0, 0.6)] + [('pop', a + r, 0.5) for r in m3[1:]], caps, 1420)

def cta_shot(name, banner_txt, m4, extra_price=False):
    """présentateur + Black Friday + panier orange (voix m4 vérifiée)"""
    a = 0.15; d = a + clip_len('m4') + 1.2
    def draw(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.02 * t, 540, 900)
        bg_room(ctx, t)
        draw_char(ctx, 'david', 560, 1030, 1.05, t, outfit='tee', mouth=sh.mouth('p', t), smile=0.9, eyes='open',
                  look=(0, 0.5), brows=0.3, arms=('point_down', 'hold_high'), prop=BOT, prop_hand='R')
        ctx.restore()
        badge(ctx, 'BLACK FRIDAY', 540, 440, 76, INK, fg=YEL, scale=pop(t, a), rot=-0.04)
        k = pop(t, a + m4[0])
        badge(ctx, 'PANIER ORANGE', 470, 590, 92, ORANGE, scale=k, rot=-0.03); cart_icon(ctx, 850, 585, 1.05 * k)
        if k > 0:
            bob = 16 * math.sin(t * 6); arrow(ctx, 330, 680 + bob * 0.5, 130, 820 + bob * 0.5, t, w=56)
        banner(ctx, banner_txt, 1); flash(ctx, t)
    caps = caps_from('m4', a, [('BLACK FRIDAY, NOËL QUI ARRIVE…', 0.0), ('LE LIEN EST JUSTE EN DESSOUS,', m4[0]),
                               ('SUR LE PANIER ORANGE.', m4[1])], 1.0)
    return Shot(name, d, draw, [('m4', a, 'p')], [('bells', a, 0.4), ('ding', a + m4[0], 0.7)], caps, 1480)

# ================================================================== 1. CLASSEMENT
def classement():
    B = "UN SEUL QUE JE GARDE…"
    c = T['classement']  # dict de repères
    a = 0.15; d = a + clip_len('cl') + 0.5
    t3, t2, t1, tw = a + c['n3'], a + c['n2'], a + c['n1'], a + c['win']
    def draw(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.02 * t, 540, 900, shake_at(t, [tw], 20))
        bg_room(ctx, t)
        win = t >= tw
        if win: S.rays(ctx, 230, 1160, t, hexc('#ffe9a8'), 14, 0.35)
        draw_char(ctx, 'david', 720, 1040, 1.0, t, outfit='tee', mouth=sh.mouth('p', t),
                  smile=0.9 if win else 0.4, eyes='wide' if win else 'open', brows=0.8 if win else 0.2, look=(-1, 0),
                  arms=('point_side', 'down') if not win else ('down', 'hold_high'),
                  prop=BOT if win else None, prop_hand='R', tilt=-0.05)
        ctx.restore()
        # podium à gauche : 3 en bas, 2 au milieu, 1 en haut
        rows = [(3, t3, 1300, sock), (2, t2, 1040, candle), (1, t1, 780, None)]
        for rk, t0, y, fn in rows:
            k = pop(t, t0, 0.35)
            if k <= 0: continue
            medal(ctx, 90, y, 1.05 * k, rk, t)
            if fn: fn(ctx, 270, y + 10, 1.3 * k, t)
            elif t >= tw:
                kk = pop(t, tw, 0.4)
                bottle(ctx, 270, y + 30, 0.8 * kk, t, glow=1.0)
                for i in range(5): sparkle(ctx, 260 + 130 * math.cos(i * 1.3), y + 30 + 110 * math.sin(i * 1.9), 22, t, i)
            else:
                text(ctx, '?', 260, y + 10, 160, fill=YEL, rot=0.1 * math.sin(t * 6))
        # barrer 3 et 2 quand il passe au suivant
        cross_out(ctx, 270, 1310, 110, ease((t - (t2 - 0.3)) / 0.25))
        cross_out(ctx, 270, 1050, 110, ease((t - (t1 - 0.3)) / 0.25))
        banner(ctx, B, t)
        flash(ctx, t)
    caps = caps_from('cl', a, [('CADEAUX DE NOËL À MOINS DE 25 €.', 0.0), ('UN SEUL QUE JE GARDE.', c['seul']),
                               ('N°3 : LES CHAUSSETTES DE NOËL.', c['n3']), ('SYMPA… MAIS ON LES OUBLIE.', c['n3b']),
                               ('N°2 : LA BOUGIE PARFUMÉE.', c['n2']), ('ÇA FAIT PLAISIR… DEUX SEMAINES.', c['n2b']),
                               ('ET NUMÉRO UN…', c['n1']), ('LE PARFUM.', c['win'])], 0.4)
    sfx = [('pop', a, 0.5), ('stamp', t3, 0.6), ('scratch', t2 - 0.3, 0.4), ('stamp', t2, 0.6),
           ('scratch', t1 - 0.3, 0.4), ('drumroll', t1, 0.45), ('sparkle', tw, 0.9), ('stamp', tw, 0.7)]
    s1 = Shot('cl1', d, draw, [('cl', a, 'p')], sfx, caps, 1560)
    # prix
    a2 = 0.15; tp = a2 + 0.1; d2 = a2 + clip_len('m2') + 0.6
    def draw2(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0, 540, 900, shake_at(t, [tp], 24))
        S.bg_gold(ctx, t, hexc('#ffd23f'), (1, 1, 1))
        draw_char(ctx, 'david', 330, 1250, 0.95, t, outfit='tee', mouth=sh.mouth('p', t), eyes='wide', brows=1.0,
                  look=(1, -1), smile=0.7, arms=('down', 'hold_high'), prop=BOT, prop_hand='R')
        ctx.restore()
        k = pop(t, tp, 0.25)
        if k > 0:
            ctx.save(); ctx.translate(560, 700); s = 1 + 2.4 * (1 - min(1, (t - tp) / 0.12)); ctx.scale(s, s); ctx.translate(-560, -700)
            price_tag(ctx, 560, 700, 1.0, t, '25 €', sub='MOINS DE', rot=-0.08); ctx.restore()
        banner(ctx, B, 1)
    s2 = Shot('cl2', d2, draw2, [('m2', a2, 'p')], [('stamp', tp, 0.9), ('coins', tp, 0.6)],
              caps_from('m2', a2, [('MOINS DE 25 €.', 0.0)], 0.4), 1560)
    return [s1, proof_shot('cl3', 'm3', B, T['m3']), s2, cta_shot('cl4', B, T['m4'])]

# ================================================================== 2. CHOC DU PRIX (carrousel animé)
def stand(ctx, x, y, w, t, title, price, col, price_col, sd):
    ink_fill(ctx, lambda c: c.rectangle(x - w / 2, y - 520, w, 520), hexc('#f7efe6'), lw=7,
             shade=lambda c: c.rectangle(x - w / 2, y - 520, w * 0.25, 520), seed=sd)
    ink_fill(ctx, lambda c: blob(c, [(x - w / 2 - 20, y - 600), (x + w / 2 + 20, y - 600), (x + w / 2 + 20, y - 500),
                                     (x - w / 2 - 20, y - 500)], sd + 1, 1.2), col, lw=7)
    text(ctx, title, x, y - 552, 52, fill=(1, 1, 1), sw=6, max_w=w - 20)
    # étagère de flacons
    for k in range(4):
        bottle(ctx, x - w / 2 + 70 + k * (w - 140) / 3, y - 300, 0.36, t + k * 0.3)
    ink_fill(ctx, lambda c: c.rectangle(x - w / 2, y - 140, w, 140), col, lw=7)
    price_tag(ctx, x, y - 420, 0.62, t, price, rot=-0.06, col=(1, 1, 1), fg=price_col)

def crowd(ctx, cx, cy, n, t, seed=5, spread=330):
    rnd = random.Random(seed)
    people = []
    for i in range(n):
        row = i // 7
        x = cx + rnd.uniform(-spread, spread); y = cy + row * 70 + rnd.uniform(-10, 10)
        people.append((y, x, rnd.choice(['#1b1310', '#4a2a1a', '#8a5a32', '#f1e7c4', '#24160f', '#5a3a28']),
                       rnd.choice(['#2f63b5', '#d7263d', '#3e8a3a', '#f4c430', '#9a6ad6', '#1d1d21', '#ef7fae']), rnd.uniform(0, 6)))
    for y, x, hc, cc, ph in sorted(people):
        bob = 8 * abs(math.sin(t * 5 + ph))
        yy = y - bob
        ink_fill(ctx, lambda c: blob(c, [(x - 52, yy + 120), (x - 48, yy + 40), (x + 48, yy + 40), (x + 52, yy + 120)], int(ph * 10), 1.0), hexc(cc), lw=5)
        ink_fill(ctx, lambda c: c.arc(x, yy, 40, 0, 7), hexc(hc), lw=5)
        if math.sin(t * 3 + ph) > 0.7:  # bras levé
            ink_line(ctx, [(x + 40, yy + 60), (x + 70, yy - 20)], int(ph), 14, color=hexc(cc))

def choc():
    B = "190 € OU MOINS DE 25 € ?"
    c = T['choc']; a = 0.15; d = a + clip_len('ch') + 0.5
    tO, tF = a + c['ou'], a + c['franchement']
    def draw(ctx, t, sh):
        # caméra : gauche (luxe) -> droite (stand) -> dézoom sur les deux
        u1 = ease((t - (tO - 0.3)) / 0.6); u2 = ease((t - (tF - 0.2)) / 0.7)
        px = -380 + 760 * u1; px = px * (1 - u2)
        z = 1.25 * (1 - u2) + 0.62 * u2
        ctx.save()
        ctx.translate(540, 1000); ctx.scale(z, z); ctx.translate(-540 - px, -1000)
        sd = boil_seed(t)
        ctx.set_source_rgb(*hexc('#f1ddd0')); ctx.rectangle(-1200, -600, 3500, 3200); ctx.fill()
        hatch_rect(ctx, -1200, -600, 3500, 3200, sd, False, 26, 0.1)
        ctx.set_source_rgb(*hexc('#c9b39a')); ctx.rectangle(-1200, 1380, 3500, 1400); ctx.fill()
        ink_line(ctx, [(-1200, 1380), (2300, 1380)], sd, 6)
        stand(ctx, 160, 1380, 520, t, 'PARFUMERIE DE LUXE', '190 €', hexc('#141414'), hexc('#b3122e'), sd + 10)
        stand(ctx, 920, 1380, 520, t, 'CONFIDENTIAL PRIVATE GOLD', '- DE 25 €', GOLD, INK, sd + 20)
        # un seul client triste devant le luxe, la foule devant l'autre
        draw_char(ctx, 'david', 160, 1500, 0.55, t, outfit='rose', mouth=0, smile=-0.6, eyes='open', brows=-0.5, look=(1, 0),
                  arms=('down', 'down'))
        crowd(ctx, 920, 1470, 24, t, 5, 300)
        ctx.restore()
        if t < tO - 0.2: text(ctx, '190 € ?!', 540, 560, 170, fill=hexc('#e8453c'), scale=pop(t, 0.3), rot=-0.08)
        elif t < tF - 0.2: text(ctx, '100 ML !', 540, 560, 150, fill=YEL, scale=pop(t, tO + 0.4), rot=0.08)
        banner(ctx, B, t)
    caps = caps_from('ch', a, [('190 €, LE PARFUM DE LUXE ?', 0.0), ('OU MOINS DE 25 €…', c['ou']), ('POUR 100 ML ?', c['ml']),
                               ('FRANCHEMENT… LE CHOIX EST VITE FAIT.', c['franchement'])], 0.4)
    s1 = Shot('ch1', d, draw, [('ch', a, 'p')], [('scratch', a, 0.7), ('whoosh', tO - 0.3, 0.7), ('coins', tO + 0.5, 0.5),
                                                 ('whoosh', tF - 0.2, 0.6), ('heart', tF + 0.5, 0.5)], caps, 1700)
    return [s1, proof_shot('ch2', 'm3', B, T['m3']), cta_shot('ch3', B, T['m4'])]

# ================================================================== 3. DISCUSSION (POV)
def chat_screen(ctx, t, msgs, title='Inès'):
    ctx.set_source_rgb(*hexc('#0f0f12')); ctx.paint()
    # en-tête
    ctx.set_source_rgb(*hexc('#1c1c22')); ctx.rectangle(0, 360, W, 150); ctx.fill()
    ctx.save(); ctx.translate(140, 435); ctx.new_path(); ctx.arc(0, 0, 52, 0, 7); ctx.clip()
    ctx.set_source_rgb(*TOP_INES); ctx.paint()
    draw_char(ctx, 'ines', 0, 25, 0.32, t, smile=0.6, eyes='open', blush=1)
    ctx.restore()
    ctx.select_font_face('Patrick Hand'); ctx.set_font_size(54); ctx.set_source_rgb(1, 1, 1)
    ctx.move_to(215, 452); ctx.show_text(title)
    ink_fill(ctx, lambda c: heart(c, 215 + text_w(ctx, title, 54, 'Patrick Hand') + 40, 440, 22), hexc('#e8455e'), lw=3)
    # bulles, empilées depuis le bas
    vis = [m for m in msgs if t >= m['t']]
    typing = any(m['who'] != 'moi' and m['t'] - 0.7 <= t < m['t'] for m in msgs)
    y = 1560 - (126 if typing else 0); out = []
    for m in reversed(vis):
        h = m['h']; out.append((m, y - h)); y -= h + 26
    off = 0
    for m, top in out:
        if top < 530: continue
        k = pop(t, m['t'], 0.25)
        me = m['who'] == 'moi'
        w = m['w']; x = W - 50 - w if me else 50
        ctx.save(); ctx.translate(x + (w if me else 0), top + m['h']); ctx.scale(k, k); ctx.translate(-(x + (w if me else 0)), -(top + m['h']))
        ctx.new_path(); rrect(ctx, x, top, w, m['h'], 40)
        ctx.set_source_rgb(*(hexc('#2f7bf6') if me else hexc('#2b2b31'))); ctx.fill()
        if m.get('img'):
            s = load_jpg(m['img']); ctx.save(); ctx.new_path(); rrect(ctx, x + 12, top + 12, w - 24, m['h'] - 24, 30); ctx.clip()
            ctx.translate(x + 12, top + 12); sc = (w - 24) / 1080; ctx.scale(sc, sc); ctx.translate(0, -300)
            ctx.set_source_surface(s, 0, 0); ctx.paint(); ctx.restore()
        else:
            ctx.select_font_face('Patrick Hand'); ctx.set_font_size(58); ctx.set_source_rgb(1, 1, 1)
            for i, ln in enumerate(m['lines']):
                ctx.move_to(x + 36, top + 70 + i * 66); ctx.show_text(ln)
        ctx.restore()
    # « en train d'écrire… »
    for m in msgs:
        if m['who'] != 'moi' and m['t'] - 0.7 <= t < m['t']:
            ctx.new_path(); rrect(ctx, 50, 1560 - 100 + 0, 190, 100, 45); ctx.set_source_rgb(*hexc('#2b2b31')); ctx.fill()
            for i in range(3):
                yy = 1510 - 10 * max(0, math.sin(t * 12 - i * 0.9))
                ctx.new_path(); ctx.arc(100 + i * 45, yy, 13, 0, 7); ctx.set_source_rgb(0.75, 0.75, 0.8); ctx.fill()
    # barre de saisie
    ctx.new_path(); rrect(ctx, 50, 1640, W - 100, 100, 50); ctx.set_source_rgb(*hexc('#1c1c22')); ctx.fill()
    ctx.select_font_face('Patrick Hand'); ctx.set_font_size(46); ctx.set_source_rgb(0.5, 0.5, 0.55)
    ctx.move_to(100, 1705); ctx.show_text('Message…')

TOP_INES = hexc('#ef7fae')

def mk(who, txt, t0, img=None):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10); c = cairo.Context(surf)
    if img: return dict(who=who, t=t0, img=img, w=560, h=620, lines=[])
    words = txt.split(' '); lines = ['']
    for w_ in words:
        cand = (lines[-1] + ' ' + w_).strip()
        if text_w(c, cand, 58, 'Patrick Hand') > 700 and lines[-1]: lines.append(w_)
        else: lines[-1] = cand
    w = max(text_w(c, l, 58, 'Patrick Hand') for l in lines) + 72
    return dict(who=who, t=t0, w=w, h=40 + 66 * len(lines), lines=lines)

def chat():
    B = "POV : ELLE DEMANDE TON PARFUM"
    ci, cm = T['chat_ines'], T['chat_moi']
    # séquence : i1, i2, (moi) p1, photo, i3, (moi) p2, i4
    i_parts = [('i1', 'T\'as mis quoi comme parfum hier soir ?'), ('i2', 'Mes copines arrêtent pas de m\'en parler'),
               ('i3', 'Ça a l\'air trop cher, t\'es fou !'), ('i4', 'QUOI ?! Envoie-moi le lien !')]
    t = 0.9; seq = []; voices = []
    def add_voice(clip, who):
        nonlocal t
        voices.append((clip, t, who)); L = clip_len(clip); t += L + 0.35
    msgs = []
    for step in ['i1', 'i2', 'p1', 'photo', 'i3', 'p2', 'i4']:
        if step == 'photo':
            msgs.append(mk('moi', '', t, img=os.path.join(S.ROOT, 'seg', 'fl1', '0030.jpg'))); t += 1.3; continue
        who = 'moi' if step.startswith('p') else 'ines'
        txt = dict(i_parts).get(step) or {'p1': 'Pourquoi ?', 'p2': 'Moins de 25 €. 100 ml.'}[step]
        if who == 'ines': t += 0.7  # le temps de « écrire »
        msgs.append(mk(who, txt, t)); add_voice(step, 'i' if who == 'ines' else 'p')
    d = t + 0.3
    def draw(ctx, tt, sh):
        ctx.save(); cam(ctx, tt, 1.0 + 0.01 * tt, 540, 1000); chat_screen(ctx, tt, msgs); ctx.restore()
        banner(ctx, B, tt, y=250, size=72)
        last = msgs[-1]['t']
        if tt >= last:
            text(ctx, 'QUOI ?!', 760, 820, 150, fill=YEL, scale=pop(tt, last), rot=0.1)
    sfx = [('ding' if m['who'] != 'moi' else 'swipe', m['t'], 0.6 if m['who'] != 'moi' else 0.4) for m in msgs]
    s1 = Shot('chat1', d, draw, voices, sfx, [], 1700)
    return [s1, proof_shot('chat2', 'm3', B, T['m3']), cta_shot('chat3', B, T['m4'])]
