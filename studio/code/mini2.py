# -*- coding: utf-8 -*-
"""Mini vendeurs en réalité mixte, saison 2 :
   - mini Hamza contre le dentifrice Miswak (il se fait écraser, puis surfe sur le tube)
   - mini Léa de Noël sur le parfum Lattafa (elle se fait parfumer « pschht »)"""
import math, random
from ink import *
from props import *
from fx import *
import scenes as S
from scenes import Shot, clip_len, footage, flash
import sklib as L
from sklib import SAFE_CX
from chars import draw_char
from rasoir_noel import santa_hat
import dm_data as DM

WORDS = {c: DM.words_for(c) for c in DM.CUTS}
for w in ('MISWAK', 'DABUR.', 'CINQ', 'EUROS !', 'VINGT-CINQ', 'FRAÎCHE.', 'FRAÎCHEUR !', 'CONFIDENTIAL', 'PRIVATE'):
    if w not in S.HL: S.HL = S.HL + (w,)
MINT = hexc('#3ddc97'); GREEN_D = hexc('#0f5132'); GOLDC = hexc('#e9c46a'); REDX = hexc('#e8263d')

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

def kf(keys, f):
    """interpolation linéaire de positions suivies image par image : keys = [(frame, x, y, s), ...]"""
    if f <= keys[0][0]: return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if f <= b[0]:
            u = (f - a[0]) / (b[0] - a[0]); return tuple(p + (q - p) * u for p, q in zip(a[1:], b[1:]))
    return keys[-1][1:]

def mini(ctx, who, spk, x, feet_y, t, sh, sc=0.4, walk=0.0, jump=0.0, face=1, sq=0.0, sit=False, hat=False,
         legcol='#2a2d35', shoe=(1, 1, 1), rot=0.0, **kw):
    """petit personnage en pied posé sur une surface réelle ; sq > 0 = écrasé (crêpe), sit = assis"""
    y = feet_y - (230 if sit else 770) * sc - jump
    if not sit:
        k = max(0.35, 1 - jump / 300)
        ctx.save(); ctx.translate(x, feet_y + 4); ctx.scale(70 * sc * 2.2 * k * (1 + sq), 16 * sc * 2.2 * k)
        ctx.new_path(); ctx.arc(0, 0, 1, 0, 7); ctx.set_source_rgba(0, 0, 0, 0.45); ctx.fill(); ctx.restore()
    ctx.save()
    ctx.translate(x, feet_y); ctx.rotate(rot); ctx.scale(1 + sq * 1.4, max(0.08, 1 - sq)); ctx.translate(-x, -feet_y)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc * face, sc)
    sw = math.sin(walk) * 0.45
    for side, a in ((-1, sw), (1, -sw)):
        ctx.save(); ctx.translate(side * 55, 540); ctx.rotate(-1.35 + 0.15 * side * math.sin(t * 9) if sit else a)
        ink_fill(ctx, lambda c: rrect(c, -34, 0, 68, 200, 20), hexc(legcol), lw=7)
        ink_fill(ctx, lambda c: blob(c, [(-44, 190), (60, 190), (78, 236), (-44, 236)], 3, 0.6), shoe, lw=7)
        ctx.restore()
    ctx.restore()
    ctx.save(); ctx.translate(x, 0); ctx.scale(face, 1); ctx.translate(-x, 0)
    draw_char(ctx, who, x, y, sc, t, mouth=sh.mouth(spk, t), **kw)
    if hat: santa_hat(ctx, x, y - 40 * sc / 0.95, 0.82 * sc / 0.95, t, kw.get('tilt', 0.0) + 0.1)
    ctx.restore()
    ctx.restore()

def stars_dizzy(ctx, x, y, t, r=70):
    for i in range(4):
        a = t * 5 + i * math.pi / 2
        px, py = x + r * math.cos(a), y + 0.35 * r * math.sin(a)
        ink_fill(ctx, lambda c, px=px, py=py: star(c, px, py, 24, 10, rot=t * 3), hexc('#ffd23f'), lw=4)

def mist(ctx, x, y, t, t0, dirx=1, dur=1.6, col=(1, 0.97, 0.9)):
    """nuage de parfum qui sort du vaporisateur"""
    if not (t0 <= t < t0 + dur): return
    u = (t - t0) / dur; rnd = random.Random(7)
    for i in range(26):
        d = rnd.uniform(0.2, 1.0) * (80 + 520 * ease_out(min(1, u * 1.6)))
        a = rnd.uniform(-0.45, 0.45); r = rnd.uniform(26, 60) * (0.6 + u)
        px = x + dirx * d * math.cos(a); py = y + d * math.sin(a) - 60 * u
        ctx.new_path(); ctx.arc(px, py, r, 0, 7); ctx.set_source_rgba(*col, 0.55 * (1 - u) ** 1.2); ctx.fill()

def ease_out(u): return 1 - (1 - max(0, min(1, u))) ** 3

def leaf(ctx, x, y, s, rot):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: blob(c, [(0, -40), (22, -10), (14, 30), (0, 42), (-14, 30), (-22, -10)], 5, 0.5), MINT, lw=5)
    ctx.new_path(); ctx.move_to(0, -34); ctx.line_to(0, 38); ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def miswak_stick(ctx, x, y, s, t, rot=0.3):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -16, -150, 32, 300, 14), hexc('#c9a26b'), lw=6)
    for k in range(5):
        ctx.new_path(); ctx.move_to(-12 + k * 6, -150); ctx.line_to(-16 + k * 8, -190)
        ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

# ---------------------------------------------------------------- DENTIFRICE : mini Hamza
BAN_D = "MINI HAMZA CONTRE LE DENTIFRICE"
ORDER_D = [('xh_1', 'H'), ('xh_2', 'H'), ('xh_3', 'H'), ('xh_4', 'H'), ('xh_5', 'H'), ('xh_6', 'H'), ('xh_7', 'H'), ('xh_8', 'H')]
PAUSE_D = {'xh_2': 0.55, 'xh_3': 0.05, 'xh_4': 0.1, 'xh_5': 0.1, 'xh_6': 0.15, 'xh_7': 0.1, 'xh_8': 0.25}
RCTA_D = 0.9
HK = dict(outfit='sweat')
# base du tube qui tombe (d_debout, images 40 -> 109)
DEB = [(40, 180, 820, 0), (55, 160, 890, 0), (65, 200, 900, 0), (75, 240, 920, 0), (90, 320, 930, 0), (109, 360, 940, 0)]
# centre du tube qui glisse (d_glisse) ; il part à gauche puis revient
GLI = [(0, 640, 640, 0), (6, 490, 630, 0), (12, 160, 640, 0), (18, -160, 640, 0), (24, 320, 650, 0), (36, 470, 610, 0), (48, 460, 520, 0)]

def draw_dent(ctx, t, sh):
    TL = sh.tl; T = TL.T; h1, h2, h3, h4, h5, h6, h7, h8 = (T[c] for c, _ in ORDER_D)
    land = h1 + clip_len('xh_1') + 0.05           # le tube touche la table
    cap_y = 1180; ban = True
    ctx.save()
    if t < h3:                                    # 1-2. le tube lui tombe dessus, il ressort aplati
        rate = 69 / (land * 30)
        f = min(109, 40 + int(t * rate * 30))
        footage(ctx, 'd_debout', t * rate, 1.0, 1.0, 1, offset=40)
        bx, by, _ = kf(DEB, f)
        if t < land:
            x = 430 + 20 * math.sin(t * 22) * (t > 0.3)
            mini(ctx, 'hamza', 'H', x, 955, t, sh, sc=0.42, eyes='tiny', brows=1.0, smile=-0.9, look=(-1, -1),
                 arms=('face', 'face'), tilt=0.08 * math.sin(t * 40), **HK)
            shock_lines(ctx, x, 955 - 330, t, 130)
            if t > 0.6: sweat(ctx, x + 60, 955 - 360, t, 1.0)
            text(ctx, '!!!', x + 150, 560, 110, fill=REDX, scale=pop(t, 0.05), rot=0.15)
            ctx.save(); ctx.set_source_rgba(1, 0.1, 0.1, 0.18 * (0.5 + 0.5 * math.sin(t * 14))); ctx.paint(); ctx.restore()
        else:
            u = t - land
            sq = 0.92 if u < 0.55 else max(0.0, 0.92 * (1 - spring(u, 0.55, 1.0, 9, 6)))
            x = 410 if u < 0.55 else 410 + 200 * ease_out((u - 0.55) / 0.5)
            mini(ctx, 'hamza', 'H', x, 955, t, sh, sc=0.42, sq=sq, eyes='closed' if u < 1.0 else 'half', brows=-0.4,
                 smile=0.3, look=(0, 0), arms=('down', 'down') if u < 1.1 else ('hip', 'wave'), **HK)
            if u < 0.5: dust(ctx, 400, 950, t, land)
            if u < 0.35: text(ctx, 'BOUM !', 560, 760, 150, fill=REDX, scale=pop(t, land), rot=-0.1)
            if 0.6 < u: stars_dizzy(ctx, x, 955 - 450 * (1 - sq), t)
            flash(ctx, u)
    elif t < h4:                                  # 3. il présente le tube debout
        u = t - h3
        footage(ctx, 'd_debout', 3.63, 1.0, 1.05, 1, offset=0)
        mini(ctx, 'hamza', 'H', 640, 960, t, sh, sc=0.42, eyes='open', brows=0.5, smile=1.0, look=(-1, -0.4),
             arms=('point_side', 'hip'), face=-1, **HK)
        badge(ctx, 'DABUR MISWAK', SAFE_CX + 40, 470, 84, GREEN_D, fg=hexc('#ffd23f'), scale=pop(t, h3 + wt('xh_3', 'MISWAK', 2.6)), rot=-0.04)
        badge(ctx, 'DENTIFRICE', SAFE_CX + 80, 590, 62, (1, 1, 1), fg=INK, scale=pop(t, h3 + wt('xh_3', 'DENTIFRICE', 2.0)), rot=0.04)
    elif t < h5:                                  # 4. aux plantes, extrait d'Al-Arak : il brandit un bâton de miswak
        u = t - h4
        footage(ctx, 'd_boite', u * 0.6, 1.0, 1.08, h5 - h4, 540, 900)
        bounce = abs(math.sin(u * 6)) * 18
        mini(ctx, 'hamza', 'H', 840, 1060, t, sh, sc=0.38, jump=bounce, eyes='happy' if u > 2.6 else 'open', brows=0.6, smile=1.0,
             look=(-1, -0.2), arms=('hold_high', 'point_side'), face=-1, **HK,
             prop=lambda c, x, y, tt: miswak_stick(c, x, y - 60, 0.9, tt, rot=0.25), prop_hand='R')
        badge(ctx, 'AUX PLANTES', 330, 470, 74, MINT, fg=INK, scale=pop(t, h4 + wt('xh_4', 'PLANTES', 1.0)), rot=-0.05)
        badge(ctx, "EXTRAIT PUR D'AL-ARAK", SAFE_CX, 1290, 64, GREEN_D, fg=hexc('#ffd23f'), scale=pop(t, h4 + wt('xh_4', "D'AL", 3.0)), rot=0.03)
        for i in range(5):
            leaf(ctx, 120 + i * 190, (t * 120 + i * 260) % 1700 + 200, 1.1, t * 2 + i)
        cap_y = 1120
    elif t < h6:                                  # 5. ce qui est écrit sur la boîte
        u = t - h5
        footage(ctx, 'd_face', u * 0.6, 1.0, 1.06, h6 - h5, 540, 960)
        ctx.set_source_rgba(0, 0, 0, 0.25); ctx.paint()
        mini(ctx, 'hamza', 'H', 800, 1420, t, sh, sc=0.36, eyes='open', brows=0.5, smile=1.0, look=(-1, -1), arms=('point_side', 'hip'),
             face=-1, **HK)
        badge(ctx, 'SUR LA BOÎTE :', SAFE_CX, 440, 66, (1, 1, 1), fg=INK, scale=pop(t, h5 + 0.1), rot=-0.03)
        for i, (lab, pre) in enumerate((('DENTS FORTES', 'DENTS'), ('GENCIVES SAINES', 'GENCIVES'), ('HALEINE FRAÎCHE', 'HALEINE'))):
            k = pop(t, h5 + wt('xh_5', pre, 1.5 + i))
            badge(ctx, lab, SAFE_CX - 40, 580 + i * 130, 70, MINT if i != 1 else hexc('#141414'), fg=INK if i != 1 else MINT, scale=k,
                  rot=(-0.04, 0.03, -0.02)[i])
            L.check(ctx, SAFE_CX + 330, 580 + i * 130, 0.8, k)
        cap_y = 1180
    elif t < h7:                                  # 6. il renifle la pâte : fraîcheur
        u = t - h6
        footage(ctx, 'd_pate', 0.6 + u * 0.5, 1.0, 1.05, h7 - h6, 500, 500, offset=0)
        mini(ctx, 'hamza', 'H', 700, 650, t, sh, sc=0.3, eyes='closed' if u < 0.9 else 'happy', brows=0.6, smile=0.8 if u > 0.9 else 0.2,
             look=(-1, -0.4), arms=('hip', 'hip') if u < 0.9 else ('cheer', 'cheer'), face=-1, jump=30 * abs(math.sin(u * 5)) * (u > 0.9), **HK)
        if u < 0.9: sniff_marks(ctx, 600, 470, t)
        for i in range(3): smell_swirl(ctx, 470 + i * 50, 420, t, 0.7, col=MINT, ph=i)
        for i in range(6): leaf(ctx, 300 + i * 120 + 30 * math.sin(t * 2 + i), 640 - ((u * 220 + i * 70) % 400), 0.9, t * 3 + i)
        ctx.set_source_rgba(0.7, 1, 0.9, 0.12); ctx.paint()
        cap_y = 1180
    else:                                         # 7-8. il surfe sur le tube qui glisse, puis appel à l'action
        u = t - h7
        f = min(48, int(u * 30 * 0.9))
        footage(ctx, 'd_glisse', u * 0.9, 1.0, 1.0, 1)
        cx, cy, _ = kf(GLI, f)
        if f < 48 and cx > -100:
            speed_lines(ctx, t, cx, cy, alpha=0.25)
        mx, my = cx + 30, cy - 55
        tj = h7 + 34 / 27                          # il saute du tube et atterrit sur la table, à droite
        if t >= tj:
            v = ease_out((t - tj) / 0.45); mx = mx + (880 - mx) * v; my = my + (760 - my) * v - 160 * math.sin(min(1, (t - tj) / 0.45) * math.pi)
        if cx > -100 and not (11 <= f < 34 and t < h8):
            mini(ctx, 'hamza', 'H', mx, my, t, sh, sc=0.3, eyes='happy' if t < h8 else ('open' if (t % 2.2) < 1.6 else 'wink'),
                 brows=0.6, smile=1.0, look=(0, 0.4), arms=('cheer', 'cheer') if t < h8 else (('down', 'point_down', (t - h8) / 0.3), 'hip'),
                 rot=0.12 * math.sin(t * 6) if t < tj else 0.0, **HK)
        if f < 48 and 10 < f < 26: text(ctx, 'WOUHOU !', 560, 470, 100, fill=(1, 1, 1), scale=pop(t, h7 + 0.3), rot=-0.08)
        kp = pop(t, h7 + wt('xh_7', 'CINQ', 0.8))
        if kp > 0.01: price_tag(ctx, SAFE_CX - (80 if t >= h8 else 0), 900 if t < h8 else 600, (1.15 if t < h8 else 0.95) * kp, t, 'MOINS DE 5 €', sub=None)
        if t >= h8:
            ctx.restore(); L.banner(ctx, t, BAN_D, bg=MINT, fg=INK); L.cta(ctx, t, h8 + RCTA_D); TL.captions(ctx, t, 990); return
        cap_y = 1180
    ctx.restore()
    if ban: L.banner(ctx, t, BAN_D, bg=MINT, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_dent():
    TL = L.Timeline(ORDER_D, PAUSE_D, WORDS, start=0.05); T = TL.T; h1, h2, h3, h4, h5, h6, h7, h8 = (T[c] for c, _ in ORDER_D)
    land = h1 + clip_len('xh_1') + 0.05
    sfx = [('whoosh', 0.0, 0.6), ('drumroll', 0.4, 0.35), ('stamp', land, 1.0), ('boing', land + 0.6, 0.8), ('sparkle', land + 0.7, 0.4),
           ('whoosh', h3 - 0.03, 0.5), ('pop', h3 + wt('xh_3', 'MISWAK', 2.6), 0.6),
           ('whoosh', h4 - 0.03, 0.5), ('pop', h4 + wt('xh_4', 'PLANTES', 1.0), 0.5), ('pop', h4 + wt('xh_4', "D'AL", 3.0), 0.5),
           ('whoosh', h5 - 0.03, 0.5), ('ding', h5 + wt('xh_5', 'DENTS', 1.5), 0.5), ('ding', h5 + wt('xh_5', 'GENCIVES', 2.5), 0.5),
           ('ding', h5 + wt('xh_5', 'HALEINE', 3.5), 0.5),
           ('whoosh', h6 - 0.03, 0.5), ('sniff', h6 + 0.05, 0.8), ('sparkle', h6 + 0.9, 0.6),
           ('swipe', h7 - 0.03, 0.8), ('whoosh', h7 + 0.3, 0.7), ('coins', h7 + wt('xh_7', 'CINQ', 0.8), 0.6),
           ('bells', h8 + 0.05, 0.4), ('ding', h8 + RCTA_D + 0.05, 0.7)]
    sh = Shot('mini_dent', TL.dur, draw_dent, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None

# ---------------------------------------------------------------- PARFUM : mini Léa de Noël
BAN_P = "MINI LÉA A TESTÉ LE PARFUM"
ORDER_P = [('xl_1', 'L'), ('xl_2', 'L'), ('xl_3', 'L'), ('xl_4', 'L'), ('xl_5', 'L'), ('xl_6', 'L'), ('xl_7', 'L')]
PAUSE_P = {'xl_2': 0.75, 'xl_3': 0.1, 'xl_4': 0.15, 'xl_5': 0.15, 'xl_6': 0.1, 'xl_7': 0.2}
RCTA_P = 0.9
LK = dict(outfit='noel')
# épaule droite du flacon (x pieds, y pieds, échelle)
FL2 = [(30, 830, 815, 0.27), (40, 860, 655, 0.29), (50, 880, 645, 0.30), (60, 840, 680, 0.29), (72, 760, 790, 0.27)]
FL1 = [(0, 700, 610, 0.27), (15, 800, 790, 0.32), (30, 900, 790, 0.36), (45, 850, 670, 0.35), (57, 730, 670, 0.28)]
NOM = [(40, 590, 385, 0.25), (60, 600, 395, 0.25), (80, 615, 400, 0.25), (95, 600, 385, 0.25)]   # haut du bouchon (zoom 1.25)
EDP = [(0, 820, 680, 0.31), (30, 660, 640, 0.31), (60, 660, 730, 0.31)]
NOZ = (575, 620)

def draw_parf(ctx, t, sh):
    TL = sh.tl; T = TL.T; p1, p2, p3, p4, p5, p6, p7 = (T[c] for c, _ in ORDER_P)
    tpsch = p1 + clip_len('xl_1') + 0.1
    cap_y = 1180; ban = True
    ctx.save()
    if t < p3:                                    # 1-2. « n'appuie pas ! » pschht… puis sous le charme
        rate = 0.35 if t < tpsch else 0.3
        f = min(72, 38 + int(t * rate * 30)) if t < tpsch else min(72, 38 + int(tpsch * 0.35 * 30) + int((t - tpsch) * rate * 30))
        footage(ctx, 'fl2', (f - 38) / 30, 1.0, 1.0, 1, offset=38)
        x, y, s = kf(FL2, f)
        if t < tpsch:
            mini(ctx, 'lea', 'L', x, y, t, sh, sc=s, hat=True, eyes='wide', brows=1.0, smile=-0.7, look=(-1, -0.6),
                 arms=('grab', 'face') if t > 0.3 else ('face', 'face'), tilt=0.06 * math.sin(t * 30), face=-1, **LK)
            shock_lines(ctx, x, y - 260 * s / 0.33, t, 110)
            text(ctx, 'NON !', 330, 560, 120, fill=REDX, scale=pop(t, 0.05), rot=0.1)
        else:
            u = t - tpsch
            blow = 90 * ease_out(u / 0.25) * (1 - ease(max(0, u - 0.6) / 0.8))
            love = u > 0.9
            mini(ctx, 'lea', 'L', x + blow, y - (40 * abs(math.sin(u * 3)) if love else 0), t, sh, sc=s, hat=True,
                 eyes='heart' if love else 'closed', brows=0.2, smile=1.0 if love else -0.3, look=(0, -0.5), blush=1.0 if love else 0.3,
                 arms=('cheer', 'cheer') if love else ('face', 'face'), tilt=0.1 * math.sin(u * 2) if love else 0.2, face=-1, **LK)
            mist(ctx, NOZ[0], NOZ[1], t, tpsch, dirx=1)
            if u < 0.5: text(ctx, 'PSCHHT !', 420, 520, 120, fill=(1, 1, 1), scale=pop(t, tpsch), rot=-0.08)
            if love:
                S.hearts_float(ctx, t, x, y - 300 * s / 0.33, n=7, seed=4, start=tpsch + 0.9)
                for i in range(2): smell_swirl(ctx, x - 140 + i * 280, y - 120, t, 0.6, col=GOLDC, ph=i)
            flash(ctx, u)
    elif t < p4:                                  # 3. le nom du parfum
        u = t - p3
        f = min(57, int(u * 0.45 * 30))
        footage(ctx, 'fl1', u * 0.45, 1.0, 1.0, 1)
        snow(ctx, t, n=45, alpha=0.7)
        x, y, s = kf(FL1, f)
        mini(ctx, 'lea', 'L', x, y, t, sh, sc=s, hat=True, eyes='open', brows=0.6, smile=1.0, look=(-1, 0.2), arms=('point_side', 'hip'),
             face=-1, **LK)
        badge(ctx, 'LATTAFA', SAFE_CX, 1290, 80, hexc('#141414'), fg=GOLDC, scale=pop(t, p3 + wt('xl_3', 'LATTAFA', 2.2)), rot=0.03)
        badge(ctx, 'CONFIDENTIAL PRIVATE GOLD', 400, 470, 58, GOLDC, fg=INK, scale=pop(t, p3 + wt('xl_3', 'CONFIDENTIAL', 0.5)), rot=-0.03)
        cap_y = 1130
        flash(ctx, u)
    elif t < p5:                                  # 4. la main secoue le flacon : « Hé ! Doucement ! »
        u = t - p4
        f = min(95, 40 + int(u * 0.95 * 30))
        footage(ctx, 'nom', u * 0.95, 1.25, 1.25, 1, 680, 0, offset=40)
        x, y, s = kf(NOM, f)
        wob = 0.25 * math.sin(u * 13)
        mini(ctx, 'lea', 'L', x, y, t, sh, sc=s, sit=True, hat=True, eyes='half' if u > 0.5 else 'tiny', brows=-1.0, smile=-0.6,
             look=(0, 0.6), arms=('hip', 'hip') if u > 0.5 else ('face', 'face'), rot=wob, face=-1, **LK)
        if u > 0.5: vein(ctx, x + 40, y - 150, t, 0.6)
        text(ctx, 'HÉ !', x - 230, y + 60, 110, fill=REDX, scale=pop(t, p4 + 0.05), rot=-0.12)
        ban = False; cap_y = 1180
        flash(ctx, u)
    elif t < p7:                                  # 5-6. Noël : l'idée cadeau, le flacon doré qui brille, le prix
        u = t - p5
        f = min(60, int(u * 0.33 * 30))
        footage(ctx, 'edp', u * 0.33, 1.0, 1.0, 1)
        string_lights(ctx, t, y=370, seed=2)
        snow(ctx, t, n=50, alpha=0.75)
        x, y, s = kf(EDP, f)
        happy = t >= p6
        mini(ctx, 'lea', 'L', x, y, t, sh, sc=s, hat=True, jump=60 * abs(math.sin(u * 6)) if happy else 0,
             eyes='happy' if happy else 'open', brows=0.6, smile=1.0, look=(-1, 0), arms=('cheer', 'cheer') if happy else ('hold_high', 'point_side'),
             face=-1, **LK, prop=None if happy else (lambda c, xx, yy, tt: gift(c, xx, yy - 50, 0.45, tt)), prop_hand='R')
        kc = pop(t, p5 + wt('xl_5', 'CADEAU', 1.2))
        badge(ctx, 'IDÉE CADEAU DE NOËL', SAFE_CX, 520, 66, REDX, fg=(1, 1, 1), scale=kc, rot=-0.04)
        if t > p5 + wt('xl_5', 'BRILLE', 3.8) - 0.2:
            for i in range(7): sparkle(ctx, 340 + (i * 97) % 520, 760 + (i * 131) % 520, 34, t, ph=i)
        if happy:
            kp = pop(t, p6 + wt('xl_6', 'VINGT', 0.8))
            if kp > 0.01: price_tag(ctx, SAFE_CX, 1000, 1.0 * kp, t, 'MOINS DE 25 €', sub=None)
            cap_y = 1290
        else:
            cap_y = 1180
        if u < 0.4: flash(ctx, u)
    else:                                         # 7. appel à l'action
        u = t - p7
        footage(ctx, 'fl1', 1.0 + min(u, 0.9) * 0.4, 1.0, 1.0, 1)
        snow(ctx, t, n=45, alpha=0.7)
        x, y, s = kf(FL1, 30 + min(12, int(u * 0.4 * 30)))
        mini(ctx, 'lea', 'L', x, y, t, sh, sc=s, hat=True, eyes='open' if (u % 2.2) < 1.6 else 'wink', brows=0.5, smile=1.0, look=(-0.6, 0.8),
             arms=(('down', 'point_down', u / 0.3), 'hip'), face=-1, **LK)
        ctx.restore(); L.banner(ctx, t, BAN_P, bg=GOLDC, fg=INK); L.cta(ctx, t, p7 + RCTA_P); TL.captions(ctx, t, 990); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN_P, bg=GOLDC, fg=INK)
    TL.captions(ctx, t, cap_y)

def build_parf():
    TL = L.Timeline(ORDER_P, PAUSE_P, WORDS, start=0.05); T = TL.T; p1, p2, p3, p4, p5, p6, p7 = (T[c] for c, _ in ORDER_P)
    tpsch = p1 + clip_len('xl_1') + 0.1
    sfx = [('whoosh', 0.0, 0.6), ('pop', 0.08, 0.5), ('pschht', tpsch, 1.0), ('heart', tpsch + 0.9, 0.6), ('sparkle', tpsch + 1.0, 0.5),
           ('whoosh', p3 - 0.03, 0.5), ('pop', p3 + wt('xl_3', 'CONFIDENTIAL', 0.5), 0.5), ('pop', p3 + wt('xl_3', 'LATTAFA', 2.2), 0.6),
           ('scratch', p4 - 0.05, 0.6), ('boing', p4 + 0.1, 0.6), ('boing', p4 + 0.6, 0.4),
           ('whoosh', p5 - 0.03, 0.5), ('bells', p5 + 0.1, 0.5), ('pop', p5 + wt('xl_5', 'CADEAU', 1.2), 0.6),
           ('sparkle', p5 + wt('xl_5', 'BRILLE', 3.8), 0.7), ('coins', p6 + wt('xl_6', 'VINGT', 0.8), 0.6),
           ('whoosh', p7 - 0.03, 0.5), ('ding', p7 + RCTA_P + 0.05, 0.7)]
    sh = Shot('mini_parf', TL.dur, draw_parf, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
