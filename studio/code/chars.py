# -*- coding: utf-8 -*-
"""Personnages : Hamza, Inès, Sarah, Léa (plan taille, style encre hachurée)."""
import math
import cairo
from ink import *

SKIN = {'david': hexc('#f0c2a8'), 'hamza': hexc('#c68a5c'), 'ines': hexc('#e7b48f'), 'sarah': hexc('#f0c39e'), 'lea': hexc('#b9805a')}
HAIR = {'david': hexc('#f1e7c4'), 'hamza': hexc('#1b1310'), 'ines': hexc('#4a2a1a'), 'sarah': hexc('#8a5a32'), 'lea': hexc('#24160f')}
TOP = {'ines': hexc('#ef7fae'), 'sarah': hexc('#f4c430'), 'lea': hexc('#9a6ad6')}
OUTFIT = {'tee': hexc('#1d1d21'), 'rose': hexc('#f3b9cf'), 'sweat': hexc('#2f63b5'), 'chic': hexc('#1a1a1f'), 'noel': hexc('#c3302f')}
GOLD = hexc('#e2b33c')
LIPS = hexc('#c2475e')

DEFAULT = dict(mouth=0.0, smile=0.4, eyes='open', look=(0, 0), brows=0.0, tilt=0.0,
               arms=('down', 'down'), blush=0.0, outfit='sweat', breathe=0.0, prop=None, prop_hand='R',
               body_rot=0.0)

def _limb(ctx, pts, color, w, seed):
    """membre épais : contour encre puis remplissage"""
    for lw, col in ((w + 10, INK), (w, color)):
        ctx.new_path(); blob(ctx, pts, seed, 0.8, closed=False)
        ctx.set_source_rgb(*col); ctx.set_line_width(lw)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()

def _hand(ctx, x, y, skin, seed, r=30):
    ink_fill(ctx, lambda c: blob(c, ellipse_pts(x, y, r, r * 0.9, 9), seed, 1.0), skin, lw=5)

ARM = {  # (épaule) -> coude -> main, côté droit de l'écran (x>0). Le côté gauche est miroir.
    'down': [(150, 200), (178, 360), (170, 500)],
    'hip': [(150, 200), (235, 330), (140, 430)],
    'point_up': [(150, 200), (230, 140), (330, -10)],
    'point_side': [(150, 200), (280, 220), (420, 200)],
    'point_down': [(150, 200), (270, 300), (330, 450)],
    'phone': [(150, 200), (200, 360), (95, 250)],
    'hold': [(150, 200), (220, 330), (150, 300)],
    'hold_high': [(150, 200), (250, 230), (220, 80)],
    'wave': [(150, 200), (260, 150), (300, -20)],
    'lips': [(150, 200), (200, 330), (25, 95)],
    'give': [(150, 200), (220, 280), (260, 260)],
    'chin': [(150, 200), (180, 330), (60, 150)],
    'spray': [(150, 200), (250, 180), (170, 60)],
    'face': [(150, 200), (230, 250), (120, 40)],
    'cheer': [(150, 200), (250, 60), (230, -120)],
    'run': [(150, 200), (40, 300), (-60, 380)],
    'grab': [(150, 200), (300, 260), (430, 250)],
    'drink': [(150, 200), (220, 300), (70, 110)],
}

def arm_points(pose, side):
    if isinstance(pose, tuple):  # (pose_a, pose_b, u) : transition fluide
        a, b, u = pose; u = max(0.0, min(1.0, u)); u = u * u * (3 - 2 * u)
        pa, pb = ARM[a], ARM[b]
        pts = [(xa + (xb - xa) * u, ya + (yb - ya) * u) for (xa, ya), (xb, yb) in zip(pa, pb)]
        s = 1 if side == 'R' else -1
        return [(s * x, y) for x, y in pts]
    pts = ARM[pose]
    s = 1 if side == 'R' else -1
    return [(s * x, y) for x, y in pts]

def draw_char(ctx, who, x, y, sc, t, **kw):
    p = dict(DEFAULT); p.update(kw)
    sd = boil_seed(t) + hash(who) % 1000
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate(p['body_rot'])
    br = math.sin(t * 2.4) * 4 + p['breathe']
    skin = SKIN[who]
    female = who in ('ines', 'sarah', 'lea')
    if who == 'david' and p['outfit'] == 'sweat': p['outfit'] = 'tee'
    if who == 'david': p['blush'] = max(p['blush'], 0.75)
    top = OUTFIT[p['outfit']] if not female else TOP[who]

    # cheveux longs derrière (femmes)
    if who in ('ines', 'sarah'):
        hl = 430 if who == 'ines' else 380
        pts = [(-118, -60), (-140, 120), (-150, hl - 120), (-110, hl), (0, hl - 30), (110, hl), (150, hl - 120),
               (140, 120), (118, -60), (0, -150)]
        ink_fill(ctx, lambda c: blob(c, pts, sd + 1, 1.5), HAIR[who], lw=6,
                 shade=lambda c: c.rectangle(-160, 40, 320, 500), seed=sd)
    if who == 'lea':  # queue de cheval
        sw = math.sin(t * 3.0) * 10
        pts = [(80, -110), (170 + sw, -70), (200 + sw, 60), (175 + sw * 1.4, 220), (150 + sw, 90), (110, -40)]
        ink_fill(ctx, lambda c: blob(c, pts, sd + 2, 1.4), HAIR[who], lw=6,
                 shade=lambda c: c.rectangle(140, -80, 120, 320), seed=sd)

    # bras arrière (côté gauche de l'écran dessiné d'abord si pas levé)
    arms = p['arms']
    ctx.save(); ctx.translate(0, br * 0.3)

    # torse
    if female:
        torso = [(-60, 120), (-135, 185), (-150, 330), (-135, 560), (135, 560), (150, 330), (135, 185), (60, 120)]
    else:
        torso = [(-62, 118), (-160, 190), (-175, 340), (-150, 570), (150, 570), (175, 340), (160, 190), (62, 118)]
    ink_fill(ctx, lambda c: blob(c, torso, sd + 3, 1.2), top, lw=7,
             shade=lambda c: blob(c, [(-180, 180), (-60, 180), (-90, 600), (-200, 600)], sd + 4, 2), seed=sd)
    # détails tenue
    if not female:
        if p['outfit'] == 'sweat':
            ink_line(ctx, [(-60, 125), (0, 175), (60, 125)], sd + 5, 6)  # capuche col
            ink_line(ctx, [(-25, 165), (-30, 260)], sd + 6, 4, color=(0.95, 0.95, 0.95))
            ink_line(ctx, [(25, 165), (30, 260)], sd + 7, 4, color=(0.95, 0.95, 0.95))
            ink_fill(ctx, lambda c: blob(c, [(-95, 400), (95, 400), (110, 500), (-110, 500)], sd + 8, 1.2),
                     hexc('#27549c'), lw=5)  # poche kangourou
        elif p['outfit'] == 'chic':
            ink_fill(ctx, lambda c: blob(c, [(-45, 122), (0, 260), (45, 122)], sd + 9, 1), hexc('#f4efe6'), lw=5)
            ink_line(ctx, [(-62, 120), (-20, 330), (-40, 560)], sd + 10, 5, color=(0.25, 0.25, 0.28))
            ink_line(ctx, [(62, 120), (20, 330), (40, 560)], sd + 11, 5, color=(0.25, 0.25, 0.28))
            # chaîne dorée
            ctx.new_path(); ctx.arc(0, 140, 70, 0.25 * math.pi, 0.75 * math.pi)
            ctx.set_source_rgb(*INK); ctx.set_line_width(11); ctx.stroke_preserve()
            ctx.set_source_rgb(*GOLD); ctx.set_line_width(6); ctx.stroke()
        elif p['outfit'] in ('tee', 'rose'):
            ink_line(ctx, [(-58, 122), (0, 150), (58, 122)], sd + 5, 6)
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(-70, 300, 16, 20, 8), sd + 6, 0.4), hexc('#c9ccd2'), lw=3.5)
            for ex in (-76, -64):
                ctx.new_path(); ctx.arc(ex, 296, 3.5, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
        elif p['outfit'] == 'noel':
            for i, yy in enumerate((260, 330)):
                for k in range(-4, 5):
                    ink_fill(ctx, lambda c, k=k, yy=yy: star(c, k * 38, yy, 13, 6, 5), (1, 1, 1), lw=2.5)
            ink_fill(ctx, lambda c: blob(c, [(-62, 118), (0, 160), (62, 118), (0, 140)], sd, 1), (1, 1, 1), lw=4)
    else:
        ink_line(ctx, [(-55, 130), (0, 190), (55, 130)], sd + 5, 5)
        if who == 'ines':  # petit collier
            ctx.new_path(); ctx.arc(0, 140, 55, 0.25 * math.pi, 0.75 * math.pi); ctx.set_source_rgb(*GOLD)
            ctx.set_line_width(4); ctx.stroke()

    # cou
    ink_fill(ctx, lambda c: blob(c, [(-36, 60), (36, 60), (40, 135), (-40, 135)], sd + 12, 1), skin, lw=5,
             shade=lambda c: c.rectangle(-50, 60, 100, 40), seed=sd)
    ctx.restore()

    # tête
    ctx.save(); ctx.translate(0, br * 0.5); ctx.rotate(p['tilt'])
    _head(ctx, who, p, t, sd, skin)
    ctx.restore()

    # bras
    for side, pose in (('L', arms[0]), ('R', arms[1])):
        pts = arm_points(pose, side)
        sleeve = top
        if female: pts = [(px * 0.88, py) for px, py in pts]
        _limb(ctx, pts[:2] + [((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2)], sleeve, 58, sd + 20)
        _limb(ctx, [((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2), pts[2]], skin, 40, sd + 21)
        hx, hy = pts[2]
        if p['prop'] and p['prop_hand'] == side:
            p['prop'](ctx, hx, hy, t)
        _hand(ctx, hx, hy, skin, sd + 22 + (side == 'R'))
        pname = (pose[1] if pose[2] > 0.5 else pose[0]) if isinstance(pose, tuple) else pose
        if pname in ('point_up', 'point_side', 'point_down'):
            ang = math.atan2(pts[2][1] - pts[1][1], pts[2][0] - pts[1][0])
            nx, ny = -math.sin(ang), math.cos(ang)
            # index tendu (décalé sur le côté) + pouce replié : jamais un doigt au centre
            bx, by = hx + nx * 14 + 18 * math.cos(ang), hy + ny * 14 + 18 * math.sin(ang)
            fx, fy = bx + 46 * math.cos(ang), by + 46 * math.sin(ang)
            for lw, col in ((24, INK), (15, skin)):
                ctx.new_path(); ctx.move_to(bx, by); ctx.line_to(fx, fy)
                ctx.set_source_rgb(*col); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            tx, ty = hx - nx * 26 + 6 * math.cos(ang), hy - ny * 26 + 6 * math.sin(ang)
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(tx, ty, 14, 11, 7, ang), sd + 25, 0.5), skin, lw=4)
            ink_line(ctx, [(hx - nx * 8 + 14 * math.cos(ang), hy - ny * 8 + 14 * math.sin(ang)),
                           (hx - nx * 20, hy - ny * 20)], sd + 26, 3)
    ctx.restore()

def _head(ctx, who, p, t, sd, skin):
    female = who in ('ines', 'sarah', 'lea')
    # oreilles
    for s in (-1, 1):
        ink_fill(ctx, lambda c, s=s: blob(c, ellipse_pts(s * 102, 10, 18, 28, 8), sd + 30 + s, 1), skin, lw=5)
    # visage
    if female:
        face = [(-100, -40), (-98, 40), (-70, 100), (0, 128), (70, 100), (98, 40), (100, -40), (60, -112), (0, -122),
                (-60, -112)]
    elif who == 'david':
        face = [(-112, -40), (-114, 40), (-96, 100), (-45, 132), (45, 132), (96, 100), (114, 40), (112, -40),
                (66, -115), (0, -126), (-66, -115)]
    else:
        face = [(-104, -40), (-102, 45), (-80, 100), (-30, 125), (30, 125), (80, 100), (102, 45), (104, -40),
                (64, -115), (0, -126), (-64, -115)]
    ink_fill(ctx, lambda c: blob(c, face, sd + 31, 1.3), skin, lw=7,
             shade=lambda c: blob(c, [(-120, -130), (-55, -130), (-80, 0), (-40, 140), (-140, 140)], sd + 32, 2),
             seed=sd, hatch=hatch_pattern(10, 45, 1.6, False, 0.35))
    if who == 'david':  # fine moustache
        ink_fill(ctx, lambda c: blob(c, [(-34, 58), (0, 50), (34, 58), (30, 64), (0, 58), (-30, 64)], sd + 34, 0.6),
                 hexc('#5a3a28'), lw=0)
    if who == 'hamza':  # barbe légère hachurée
        ctx.save(); ctx.new_path(); blob(ctx, [(-95, 50), (-60, 110), (0, 128), (60, 110), (95, 50), (60, 80), (0, 92),
                                               (-60, 80)], sd + 33, 1)
        ctx.clip(); ctx.set_source(hatch_pattern(7, 45, 1.4, True, 0.35)); ctx.paint(); ctx.restore()
    # joues
    if p['blush'] > 0:
        for s in (-1, 1):
            ctx.new_path(); ctx.arc(s * 62, 45, 22, 0, 2 * math.pi)
            ctx.set_source_rgba(0.95, 0.35, 0.4, 0.45 * p['blush']); ctx.fill()

    _eyes(ctx, who, p, t, sd)
    _mouth(ctx, who, p, t, sd)
    # nez
    ink_line(ctx, [(-4, 0), (-12, 32), (2, 40), (12, 36)], sd + 40, 4.5)
    _hair_front(ctx, who, p, t, sd)

def _eyes(ctx, who, p, t, sd):
    female = who in ('ines', 'sarah', 'lea')
    blink = (t % 3.7) < 0.12
    e = p['eyes']
    lx, ly = p['look']
    b = p['brows']
    for s in (-1, 1):
        cx, cy = s * 42, -8
        mode = e
        if e == 'wink' and s == 1: mode = 'closed'
        elif e == 'wink': mode = 'open'
        if blink and mode in ('open', 'wide'): mode = 'closed'
        if mode == 'closed':
            ink_line(ctx, [(cx - 22, cy), (cx, cy + 9), (cx + 22, cy)], sd + 50 + s, 5)
        elif mode == 'happy':
            ink_line(ctx, [(cx - 22, cy + 6), (cx, cy - 8), (cx + 22, cy + 6)], sd + 50 + s, 5)
        elif mode == 'heart':
            ink_fill(ctx, lambda c: heart(c, cx, cy + 4, 26 + 4 * math.sin(t * 10)), hexc('#e23b52'), lw=4)
        elif mode in ('half', 'tiny'):
            rx, ry = (23, 17) if mode == 'half' else (33, 33)
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(cx, cy, rx, ry, 10), sd + 52 + s, 0.6), (1, 1, 1), lw=4.5)
            pr = 9 if mode == 'half' else 4.5
            ctx.new_path(); ctx.arc(cx + lx * 9, cy + ly * 6 + (4 if mode == 'half' else 0), pr, 0, 2 * math.pi)
            ctx.set_source_rgb(0.12, 0.08, 0.05); ctx.fill()
            if mode == 'half':  # paupière lourde : regard en coin / frimeur / méfiant
                ctx.save(); ctx.new_path(); blob(ctx, ellipse_pts(cx, cy, rx, ry, 10), sd + 52 + s, 0.6); ctx.clip()
                ctx.rectangle(cx - rx - 4, cy - ry - 4, 2 * rx + 8, ry + 2); ctx.set_source_rgb(*SKIN[who]); ctx.fill(); ctx.restore()
                ink_line(ctx, [(cx - rx - 3, cy - 1), (cx, cy - 3), (cx + rx + 3, cy - 1)], sd + 55 + s, 5.5)
        else:
            rx, ry = (27, 27) if mode == 'wide' else (23, 17)
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(cx, cy, rx, ry, 10), sd + 52 + s, 0.6), (1, 1, 1), lw=4.5)
            pr = 10 if mode != 'wide' else 8
            ctx.new_path(); ctx.arc(cx + lx * 9, cy + ly * 6 + 1, pr, 0, 2 * math.pi)
            ctx.set_source_rgb(0.18, 0.1, 0.06); ctx.fill()
            if who == 'david':
                ctx.new_path(); ctx.arc(cx + lx * 9, cy + ly * 6 + 1, pr + 1, 0, 2 * math.pi)
                ctx.set_source_rgb(*hexc('#8fa7b8')); ctx.fill()
                ctx.new_path(); ctx.arc(cx + lx * 9, cy + ly * 6 + 1, pr * 0.45, 0, 2 * math.pi)
                ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
            ctx.new_path(); ctx.arc(cx + lx * 9 + 3, cy + ly * 6 - 3, 3.5, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1); ctx.fill()
        if female and mode not in ('heart',):
            for k in range(3):
                ink_line(ctx, [(cx + s * (12 + k * 6), cy - 14), (cx + s * (20 + k * 9), cy - 26)], sd + 60 + k, 3.5)
        # sourcils
        by = cy - 36 - 8 * max(b, 0)
        inner = by + 10 * (-b if b < 0 else 0) - 4 * max(b, 0)
        outer = by + (6 if b > 0 else -2)
        bw = 4.5 if female else (8.5 if who == 'david' else 7)
        ink_line(ctx, [(s * 18, inner + 4), (s * 42, by - 4), (s * 66, outer)], sd + 70 + s, bw)

def _mouth(ctx, who, p, t, sd):
    m = clamp(p['mouth']); sm = p['smile']
    female = who in ('ines', 'sarah', 'lea')
    cx, cy = 0, 74
    w = 36 + 10 * m
    if m < 0.08:
        pts = [(cx - w, cy - 6 * sm), (cx, cy + 10 * sm), (cx + w, cy - 6 * sm)]
        ink_line(ctx, pts, sd + 80, 5, color=LIPS if female else INK)
        if sm > 0.5:
            ink_line(ctx, [(cx + w - 4, cy - 12 * sm), (cx + w + 6, cy - 4 * sm)], sd + 81, 3.5)
    else:
        h = 8 + 46 * m
        top = cy - 4 - 6 * sm
        pts = [(cx - w, top), (cx, top + 4 - 4 * sm), (cx + w, top), (cx + w * 0.7, top + h * 0.8),
               (cx, top + h), (cx - w * 0.7, top + h * 0.8)]
        ink_fill(ctx, lambda c: blob(c, pts, sd + 82, 0.8), hexc('#5a1414'), lw=5)
        ctx.save(); ctx.new_path(); blob(ctx, pts, sd + 82, 0.8); ctx.clip()
        ctx.rectangle(cx - w, top - 2, 2 * w, 9 + 3 * m); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        ctx.new_path(); ctx.arc(cx + 4, top + h + 6, w * 0.55, math.pi, 2 * math.pi)
        ctx.set_source_rgb(*hexc('#d9545f')); ctx.fill(); ctx.restore()
        if female:
            ctx.new_path(); blob(ctx, pts, sd + 82, 0.8); ctx.set_source_rgb(*LIPS); ctx.set_line_width(5); ctx.stroke()

def _hair_front(ctx, who, p, t, sd):
    hc = HAIR[who]
    if who == 'david' and p['outfit'] != 'noel':
        # côtés dégradés foncés
        for sx in (-1, 1):
            ink_fill(ctx, lambda c, sx=sx: blob(c, [(sx * 100, -95), (sx * 116, -40), (sx * 113, 20), (sx * 100, 10), (sx * 98, -60)],
                                                  sd + 98, 0.6), hexc('#5a4334'), lw=3)
        # crop platine texturé : pointes sur le dessus, frange droite et basse
        pts = []
        for i in range(19):
            a = math.radians(196 + i * (148 / 18))
            r = (146 if i % 2 == 0 else 122) + 6 * math.sin(i * 1.7)
            pts.append((r * 0.92 * math.cos(a), -42 + r * 0.9 * math.sin(a)))
        for i in range(13):  # bord de la frange (de droite à gauche), en dents
            x = 112 - i * (224 / 12)
            y = -34 if i % 2 == 0 else -54
            pts.append((x, y + 4 * math.sin(i)))
        def poly(c):
            P = [(x + jit(sd + 97, k, 1.3)[0], y + jit(sd + 97, k, 1.3)[1]) for k, (x, y) in enumerate(pts)]
            c.move_to(*P[0])
            for q in P[1:]: c.line_to(*q)
            c.close_path()
        ink_fill(ctx, poly, hc, lw=6, shade=lambda c: c.rectangle(-140, -200, 75, 170), seed=sd)
        ctx.save(); ctx.new_path(); poly(ctx); ctx.clip()
        for i in range(16):  # mèches
            x0 = -120 + i * 16
            ink_line(ctx, [(x0 - 6, -175), (x0 + 4, -120), (x0 - 4, -62)], sd + 110 + i, 2.4, color=hexc('#b9a679'))
        ctx.restore()
        return
    if who == 'hamza' or who == 'david':
        if p['outfit'] == 'chic':  # casquette noire
            cap = [(-112, -40), (-108, -110), (-60, -158), (0, -170), (60, -158), (108, -110), (112, -40)]
            ink_fill(ctx, lambda c: blob(c, cap + [(0, -55)], sd + 90, 1), hexc('#1c1c22'), lw=6,
                     shade=lambda c: c.rectangle(-120, -180, 80, 150), seed=sd)
            ink_fill(ctx, lambda c: blob(c, [(-110, -48), (60, -60), (170, -38), (165, -20), (40, -30), (-110, -28)],
                                         sd + 91, 1), hexc('#111114'), lw=6)
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(0, -128, 24, 16, 8), sd + 92, 0.5), GOLD, lw=3)
            # dégradé sur les côtés
            for s in (-1, 1):
                ink_fill(ctx, lambda c, s=s: blob(c, [(s * 104, -40), (s * 108, 10), (s * 96, 0), (s * 96, -40)],
                                                  sd + 93, 0.6), hc, lw=3)
            return
        if p['outfit'] == 'noel':  # bonnet de Noël
            ink_fill(ctx, lambda c: blob(c, [(-115, -60), (-80, -150), (20, -200), (140, -150), (190, -60), (160, -40),
                                              (110, -110), (40, -120), (100, -60)], sd + 94, 1.4), hexc('#c3302f'),
                     lw=6, shade=lambda c: c.rectangle(-120, -210, 90, 170), seed=sd)
            ink_fill(ctx, lambda c: blob(c, [(-125, -70), (0, -95), (125, -70), (125, -32), (0, -52), (-125, -30)],
                                         sd + 95, 1.2), (1, 1, 1), lw=6)
            ink_fill(ctx, lambda c: blob(c, ellipse_pts(178, -40, 26, 26, 9), sd + 96, 1.2), (1, 1, 1), lw=5)
            return
        # cheveux bouclés courts + dégradé
        bumps = []
        for i in range(13):
            a = math.pi + math.pi * i / 12
            r = 118 + (14 if i % 2 else 0)
            bumps.append((r * math.cos(a) * 0.98, -30 + r * math.sin(a) * 0.95))
        bumps += [(100, -40), (70, -78), (20, -70), (-40, -82), (-100, -40)]
        ink_fill(ctx, lambda c: blob(c, bumps, sd + 97, 2.0), hc, lw=6)
        ctx.save(); ctx.new_path(); blob(ctx, bumps, sd + 97, 2.0); ctx.clip()
        for i in range(9):  # reflets de boucles
            ctx.new_path(); ctx.arc(-80 + i * 20, -120 + (i % 3) * 18, 12, math.pi * 1.1, math.pi * 1.8)
            ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(3); ctx.stroke()
        ctx.restore()
        for s in (-1, 1):
            ink_fill(ctx, lambda c, s=s: blob(c, [(s * 104, -45), (s * 107, 12), (s * 96, 0), (s * 96, -45)],
                                              sd + 98, 0.6), hc, lw=3)
    else:
        if who == 'lea':
            pts = [(-108, -10), (-112, -90), (-60, -140), (20, -148), (95, -120), (112, -40), (80, -80), (0, -95),
                   (-70, -80)]
        elif who == 'ines':
            pts = [(-112, 60), (-118, -70), (-70, -135), (10, -150), (90, -125), (118, -50), (112, 60), (88, -40),
                   (20, -85), (-40, -60), (-90, -20)]
        else:
            pts = [(-110, 40), (-115, -80), (-50, -145), (40, -145), (110, -90), (114, 30), (90, -50), (30, -95),
                   (-30, -80), (-85, -30)]
        ink_fill(ctx, lambda c: blob(c, pts, sd + 99, 1.6), hc, lw=6,
                 shade=lambda c: c.rectangle(-130, -160, 90, 240), seed=sd)
        ctx.save(); ctx.new_path(); blob(ctx, pts, sd + 99, 1.6); ctx.clip()
        for i in range(5):
            ink_line(ctx, [(-60 + i * 30, -120), (-50 + i * 32, -60)], sd + 100 + i, 2.5, color=(0.85, 0.7, 0.55))
        ctx.restore()
