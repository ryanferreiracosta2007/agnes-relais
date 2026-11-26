# -*- coding: utf-8 -*-
"""Tondeuse Philips OneBlade 360 : « Micro-trottoir : j'interviewe une tondeuse. »
   Mini Inès, journaliste, tend son micro à la VRAIE tondeuse (vraies images du kit) à qui on a dessiné un visage.
   3 questions (tu sers à quoi ? tu coupes la peau ? tu coûtes combien ?), la tondeuse répond avec une voix rocailleuse,
   chaque réponse est prouvée par les vraies images. Puis Inès tend le micro au spectateur : « tu lui poserais quelle question ? »."""
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
from rasoir_videos import oneblade, coupon_note, fiche_kit, LIME
import it_data as IT

WORDS = {c: IT.words_for(c) for c in IT.CUTS}
for w in ('MICRO-TROTTOIR !', 'TONDEUSE.', 'QUOI ?', 'TAILLE,', 'CONTOURS', 'RASE.', 'PEAU ?', 'NON.', 'POILS,', 'PEAU.',
          'COMBIEN ?', '50,99 €', '29,99 €', 'COUPONS', 'QUESTION ?', 'COMMENTAIRE.'):
    if w not in S.HL: S.HL = S.HL + (w,)
REDL = hexc('#e8263d'); NAVY = hexc('#14213d'); GREY = hexc('#3a3d44'); FOAM = hexc('#5b5f68')
BAN = "J'INTERVIEWE UNE TONDEUSE"
ORDER = [('xi_i1', 'I'), ('xi_i2', 'I'), ('xi_o1', 'O'), ('xi_i3', 'I'), ('xi_o2', 'O'), ('xi_i4', 'I'), ('xi_o3', 'O'),
         ('xi_i5', 'I'), ('xi_i6', 'I')]
PAUSE = {'xi_i2': 0.0, 'xi_o1': 0.05, 'xi_i3': 0.05, 'xi_o2': 0.02, 'xi_i4': 0.08, 'xi_o3': 0.05, 'xi_i5': 0.1, 'xi_i6': 0.05}
RCTA = 0.5
FX, FY = 662, 1125          # centre du « visage » dessiné sur la vraie tondeuse (image r_kit)

def wt(clip, prefix, default):
    return next((r for w, r in WORDS.get(clip, []) if w.startswith(prefix)), default)

# ---------------------------------------------------------------- visage de la tondeuse et micro
def blade_face(ctx, t, sh, x=FX, y=FY, s=1.7, look=(0, 0), brows=0.0, eyes='open', angry=False, sweat_k=0.0):
    """yeux + bouche posés sur le manche de la vraie tondeuse ; la bouche suit la voix 'O'"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    blink = (t % 3.1) < 0.12 and eyes == 'open'
    for sx in (-1, 1):
        ex = sx * 34
        if eyes == 'wink' and sx == 1 or blink:
            ctx.new_path(); ctx.move_to(ex - 22, 0); ctx.curve_to(ex - 8, 12, ex + 8, 12, ex + 22, 0)
            ctx.set_source_rgb(*INK); ctx.set_line_width(7); ctx.set_line_cap(1); ctx.stroke()
        elif eyes == 'happy':
            ctx.new_path(); ctx.move_to(ex - 22, 6); ctx.curve_to(ex - 8, -14, ex + 8, -14, ex + 22, 6)
            ctx.set_source_rgb(*INK); ctx.set_line_width(8); ctx.set_line_cap(1); ctx.stroke()
        else:
            r = 30 if eyes == 'wide' else 25
            ink_fill(ctx, lambda c, ex=ex, r=r: c.arc(ex, 0, r, 0, 7), (1, 1, 1), lw=5)
            pr = 9 if eyes == 'wide' else 12
            ctx.new_path(); ctx.arc(ex + look[0] * 9, look[1] * 9, pr, 0, 7); ctx.set_source_rgb(*INK); ctx.fill()
            ctx.new_path(); ctx.arc(ex + look[0] * 9 - 4, look[1] * 9 - 4, 3.5, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        # sourcils : brows > 0 levés, < 0 froncés (vers le centre)
        by = -44 - 12 * max(0, brows); inner = 16 if angry or brows < -0.5 else 0
        ctx.new_path(); ctx.move_to(ex + sx * 22, by - 4); ctx.line_to(ex - sx * 22, by + inner)
        ctx.set_source_rgb(*hexc('#f2f2f2')); ctx.set_line_width(9); ctx.set_line_cap(1); ctx.stroke()
    m = sh.mouth('O', t)
    mw, mh = 46, 6 + 46 * m
    if m > 0.03:
        ink_fill(ctx, lambda c: (c.save(), c.translate(0, 82), c.scale(mw, mh), c.arc(0, 0, 1, 0, 7), c.restore()), hexc('#5a1220'), lw=5)
        ctx.new_path(); ctx.save(); ctx.translate(0, 82 + mh * 0.45); ctx.scale(mw * 0.5, max(2, mh * 0.35)); ctx.arc(0, 0, 1, 0, 7)
        ctx.restore(); ctx.set_source_rgb(*hexc('#e86a7a')); ctx.fill()
    else:
        ctx.new_path(); ctx.move_to(-30, 76); ctx.curve_to(-10, 96 if not angry else 70, 10, 96 if not angry else 70, 30, 76)
        ctx.set_source_rgb(*hexc('#f2f2f2')); ctx.set_line_width(7); ctx.set_line_cap(1); ctx.stroke()
    ctx.restore()
    if angry: vein(ctx, x + 70 * s, y - 80 * s, t, 0.8 * s)
    if sweat_k > 0: sweat(ctx, x - 70 * s, y - 70 * s, t, sweat_k * s)

def mic(ctx, x0, y0, x1, y1, s=1.0, flag=True):
    """micro de journaliste : manche de (x0, y0) vers la tête en (x1, y1)"""
    a = math.atan2(y1 - y0, x1 - x0); ln = math.hypot(x1 - x0, y1 - y0)
    ctx.save(); ctx.translate(x0, y0); ctx.rotate(a)
    ink_fill(ctx, lambda c: rrect(c, -10 * s, -13 * s, ln - 30 * s, 26 * s, 10 * s), GREY, lw=5)
    if flag:
        fw = 110 * s
        ink_fill(ctx, lambda c: rrect(c, ln - 30 * s - fw - 6 * s, -40 * s, fw, 80 * s, 10 * s), REDL, lw=5)
        ctx.save(); ctx.translate(ln - 30 * s - fw / 2 - 6 * s, 0)
        if abs(a) > math.pi / 2: ctx.rotate(math.pi)
        text(ctx, 'RAY TV', 0, 2, 30 * s, fill=(1, 1, 1), stroke=None, shadow=False); ctx.restore()
    ink_fill(ctx, lambda c: c.arc(ln, 0, 42 * s, 0, 7), FOAM, lw=6)
    for k in range(-2, 3):
        ctx.new_path(); ctx.move_to(ln + k * 14 * s, -36 * s); ctx.line_to(ln + k * 14 * s, 36 * s)
        ctx.set_source_rgba(1, 1, 1, 0.18); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def hand_pos(x, feet_y, sc, face=1, pose='point_side', side='R'):
    from chars import ARM
    hx, hy = ARM[pose][2]; s = 1 if side == 'R' else -1
    return x + s * face * hx * 0.88 * sc, feet_y - 770 * sc + hy * sc

def live_tag(ctx, t, y=385):
    """bandeau télé « EN DIRECT · MICRO-TROTTOIR »"""
    on = (t % 1.0) < 0.6
    ctx.new_path(); rrect(ctx, 70, y - 34, 190, 68, 14); ctx.set_source_rgb(*REDL); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    if on: ctx.new_path(); ctx.arc(104, y, 13, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    text(ctx, 'DIRECT', 185, y + 2, 40, fill=(1, 1, 1), stroke=None, shadow=False)
    ctx.new_path(); rrect(ctx, 250, y - 30, 460, 60, 10); ctx.set_source_rgb(*NAVY); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    text(ctx, 'MICRO-TROTTOIR', 480, y + 2, 40, fill=(1, 1, 1), stroke=None, shadow=False)

def lower_third(ctx, t, t0, y=1030):
    k = ease_out((t - t0) / 0.3)
    if k <= 0: return
    x = -500 + 560 * k
    ctx.new_path(); rrect(ctx, x, y - 44, 600, 88, 12); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    ctx.new_path(); rrect(ctx, x, y + 34, 470, 52, 10); ctx.set_source_rgb(*LIME); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    text(ctx, 'PHILIPS ONEBLADE 360', x + 300, y + 2, 54, fill=INK, stroke=None, shadow=False)
    text(ctx, 'tondeuse, invitée du jour', x + 235, y + 62, 34, font='Patrick Hand', fill=INK, stroke=None, shadow=False)

def pip_face(ctx, t, sh, x=760, y=600, eyes='open', angry=False, brows=0.0):
    """petite tondeuse dessinée qui parle, dans une bulle ronde (quand on montre les vraies images)"""
    ink_fill(ctx, lambda c: c.arc(x, y, 150, 0, 7), hexc('#dff3a0'), lw=8)
    ctx.save(); ctx.new_path(); ctx.arc(x, y, 144, 0, 7); ctx.clip()
    oneblade(ctx, x, y + 40, 0.95, t, rot=0.0)
    blade_face(ctx, t, sh, x, y + 10, s=0.62, eyes=eyes, angry=angry, brows=brows)
    ctx.restore()

def ines(ctx, t, sh, x=300, fy=1390, sc=0.58, mic_to=(FX - 70, FY + 140), **kw):
    kw.setdefault('eyes', 'open'); kw.setdefault('brows', 0.5); kw.setdefault('smile', 0.9)
    mini(ctx, 'ines', 'I', x, fy, t, sh, sc=sc, arms=kw.pop('arms', ('hip', 'point_side')), face=1, **kw)
    if mic_to:
        hx, hy = hand_pos(x, fy - kw.get('jump', 0), sc, face=1, pose='point_side', side='R')
        mic(ctx, hx - 40, hy + 10, mic_to[0], mic_to[1], s=0.8)

def check_line(ctx, txt, x, y, k, col=LIME):
    badge(ctx, txt, x, y, 76, col, fg=INK, scale=k, rot=-0.03)
    L.check(ctx, x + text_w(ctx, txt, 76) / 2 + 60, y, 0.75, k)

# ---------------------------------------------------------------- scènes
def draw_it(ctx, t, sh):
    TL = sh.tl; T = TL.T; i1, i2, o1, i3, o2, i4, o3, i5, i6 = (T[c] for c, _ in ORDER)
    cap_y = 1220; ban = True; live = True
    ctx.save()
    if t < o1:                                     # 1-2. Inès tend le micro à la vraie tondeuse qui a un visage
        zq = ease_out((t - i2) / 0.35) if t >= i2 else 0
        footage(ctx, 'r_kit', t * 0.8, 1.0 + 0.18 * zq, 1.06 + 0.18 * zq, o1, FX, FY)
        ctx.save(); ctx.translate(FX, FY); z = 1 + 0.18 * zq; ctx.scale(z, z); ctx.translate(-FX, -FY)
        surprise = t < 0.9
        blade_face(ctx, t, sh, eyes='wide' if surprise else 'open', brows=1.0 if surprise else 0.3,
                   look=(-1, 0.3) if t > 0.9 else (0, 0))
        ines(ctx, t, sh, x=290 - 60 * zq, eyes='open', brows=0.7, smile=1.0,
             jump=abs(math.sin(t * 6)) * 12 if t < i2 else 0, mic_to=(FX - 75 + 15 * zq, FY + 150))
        ctx.restore()
        if t < i2:
            badge(ctx, 'MICRO-TROTTOIR', SAFE_CX, 520, 96, REDL, fg=(1, 1, 1), scale=pop(t, 0.05), rot=-0.05)
            if t < 0.2: ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - t / 0.2)); ctx.paint()
        else:
            badge(ctx, 'QUESTION 1', SAFE_CX, 520, 92, (1, 1, 1), fg=INK, scale=pop(t, i2 + 0.02), rot=0.04)
            flash(ctx, t - i2)
        cap_y = 700
    elif t < i3:                                   # 3. réponse 1 en vraies images : il taille, contours, rase
        u = t - o1
        if u < 1.2: footage(ctx, 'r_prise', 1.6 + u, 1.0, 1.06, 1.2, 540, 900)
        else: footage(ctx, 'r_rase', u - 1.2, 1.02, 1.1, 2.4, 520, 800)
        for j, (lab, pre, d) in enumerate((('TAILLE', 'TAILLE', 0.5), ('CONTOURS', 'CONTOURS', 1.6), ('RASE', 'RASE', 2.7))):
            check_line(ctx, lab, 330, 700 + j * 120, pop(t, o1 + wt('xi_o1', pre, d)))
        pip_face(ctx, t, sh, eyes='open', brows=0.5)
        lower_third(ctx, t, o1 + 0.1)
        flash(ctx, u if u < 1.2 else u - 1.2)
        cap_y = 1250
    elif t < o2 + 0.55:                            # 4. la question qui fâche, puis « NON. » vexé
        u = t - i3
        footage(ctx, 'r_kit', 2.0 + u * 0.8, 1.2, 1.26, 1.5, FX, FY)
        ctx.save(); ctx.translate(FX, FY); ctx.scale(1.2, 1.2); ctx.translate(-FX, -FY)
        ang = t >= o2
        blade_face(ctx, t, sh, eyes='open', brows=-1.0 if ang else 0.0, angry=ang, look=(-1, 0.2))
        ines(ctx, t, sh, x=240, eyes='half', brows=-0.2, smile=0.3, arms=('lips', 'point_side'),
             mic_to=(FX - 60, FY + 150))
        ctx.restore()
        badge(ctx, 'LA QUESTION QUI FÂCHE', SAFE_CX, 520, 70, YEL, fg=INK, scale=pop(t, i3 + 0.02), rot=-0.03)
        if ang:
            S_ = 1 + 0.5 * max(0, 1 - (t - o2) / 0.15)
            badge(ctx, 'NON.', 760, 820, 130, REDL, fg=(1, 1, 1), scale=pop(t, o2) * S_, rot=0.1)
            shock_lines(ctx, FX, FY, t, r=200)
        flash(ctx, u if not ang else t - o2)
        cap_y = 700
    elif t < i4:                                   # 5. preuve : conçu pour couper les poils, pas la peau (vraies images)
        u = t - o2 - 0.55
        if u < 1.2: footage(ctx, 'r_rase2', 0.5 + u, 1.0, 1.08, 1.4, 540, 800)
        else: footage(ctx, 'r_lisse', u - 1.2, 1.0, 1.06, 2.0, 540, 800)
        k = pop(t, o2 + wt('xi_o2', 'CONÇU', 0.9))
        badge(ctx, 'CONÇU POUR COUPER', SAFE_CX, 880, 74, (1, 1, 1), fg=INK, scale=k, rot=-0.03)
        badge(ctx, 'LES POILS, PAS LA PEAU', SAFE_CX, 1000, 74, LIME, fg=INK, scale=pop(t, o2 + wt('xi_o2', 'POILS', 1.8)), rot=0.03)
        if k > 0.5: text(ctx, '(selon Philips)', SAFE_CX, 1090, 40, font='Patrick Hand', fill=(1, 1, 1), sw=5)
        pip_face(ctx, t, sh, eyes='open', brows=-0.3)
        flash(ctx, u if u < 1.2 else u - 1.2)
        cap_y = 1250
    elif t < o3:                                   # 6. dernière question : la tondeuse transpire
        u = t - i4
        footage(ctx, 'r_kit', 3.0 - u * 0.6, 1.1, 1.2, 1.8, FX, FY)
        ctx.save(); ctx.translate(FX, FY); ctx.scale(1.1, 1.1); ctx.translate(-FX, -FY)
        blade_face(ctx, t, sh, eyes='wide', brows=1.0, look=(-1, 0), sweat_k=1.0)
        ines(ctx, t, sh, x=260, eyes='half', brows=0.8, smile=1.0, mic_to=(FX - 65, FY + 150))
        ctx.restore()
        badge(ctx, 'DERNIÈRE QUESTION', SAFE_CX, 520, 80, (1, 1, 1), fg=INK, scale=pop(t, i4 + 0.02), rot=0.03)
        flash(ctx, u)
        cap_y = 700
    elif t < i5:                                   # 7. le prix
        u = t - o3
        t2 = o3 + wt('xi_o3', '29,99', 1.8)
        if t < t2:
            footage(ctx, 'r_kit2', 0.3 + u * 0.8, 1.0, 1.06, 2.0, 540, 900)
            price_tag(ctx, SAFE_CX - 80, 650, 0.85 * pop(t, o3 + 0.05), t, '50,99 €', sub=None, col=(1, 1, 1))
            flash(ctx, u)
        else:
            footage(ctx, 'r_prise', 2.2 + (t - t2) * 0.6, 1.0, 1.05, 2.5, 540, 1000)
            price_tag(ctx, 300, 560, 0.55, t, '50,99 €', sub=None, col=(1, 1, 1))
            ks = ease_out((t - t2) / 0.25)
            ctx.new_path(); ctx.move_to(170, 600); ctx.line_to(170 + 270 * ks, 510); ctx.set_source_rgb(*REDL); ctx.set_line_width(14)
            ctx.set_line_cap(1); ctx.stroke()
            price_tag(ctx, 560, 770, 0.9 * pop(t, t2), t, '29,99 €', sub='AVEC LES COUPONS')
            coupon_note(ctx, y=880)
            flash(ctx, t - t2)
        pip_face(ctx, t, sh, x=770, y=1040, eyes='happy' if t >= t2 else 'open', brows=0.6)
        cap_y = 1290; ban = False
    else:                                          # 8-9. le micro vers le spectateur, puis appel à l'action
        u = t - i5
        footage(ctx, 'r_kit', 1.0 + u * 0.5, 1.0, 1.05, 4.0, FX, FY)
        if t < i6: blade_face(ctx, t, sh, eyes='wink' if (u % 2.0) < 0.5 else 'open', brows=0.5, look=(-0.6, 0.6))
        if t < i6:
            km = ease_out(u / 0.4)
            ines(ctx, t, sh, x=260, eyes='open', brows=0.6, smile=1.0, mic_to=None, arms=('hip', 'point_side'))
            mic(ctx, 1080, 1700, 1080 - 330 * km, 1700 - 640 * km, s=0.8 + 1.2 * km, flag=True)   # le micro arrive vers toi
            badge(ctx, 'ET TOI ?', SAFE_CX, 540, 100, YEL, fg=INK, scale=pop(t, i5 + 0.05), rot=-0.05)
            kc = pop(t, i5 + wt('xi_i5', 'ÉCRIS', 1.9))
            if kc > 0.01:
                badge(ctx, 'POSE TA QUESTION À LA TONDEUSE', SAFE_CX, 660, 54, (1, 1, 1), fg=INK, scale=kc, rot=0.02)
                comment_bubble(ctx, 220, 850, kc * 0.9, t)
            cap_y = 1250
            flash(ctx, u)
        else:
            v = t - i6
            ines(ctx, t, sh, x=150, fy=1075, sc=0.34, eyes='happy', brows=0.5, smile=1.0, mic_to=None,
                 arms=('wave', ('down', 'point_down', v / 0.3)))
            price_tag(ctx, SAFE_CX, 560, 0.75, t, '29,99 €', sub='AVEC LES COUPONS')
            coupon_note(ctx, y=700)
            ctx.restore(); L.banner(ctx, t, BAN, bg=LIME, fg=INK); live_tag(ctx, t)
            L.cta(ctx, t, i6 + RCTA); TL.captions(ctx, t, 860); return
    ctx.restore()
    if ban: L.banner(ctx, t, BAN, bg=LIME, fg=INK)
    if live: live_tag(ctx, t)
    TL.captions(ctx, t, cap_y)

def build_it():
    TL = L.Timeline(ORDER, PAUSE, WORDS, start=0.05, tail=0.8); T = TL.T; i1, i2, o1, i3, o2, i4, o3, i5, i6 = (T[c] for c, _ in ORDER)
    t29 = o3 + wt('xi_o3', '29,99', 1.8)
    sfx = [('whoosh', 0.0, 0.6), ('stamp', 0.08, 0.6), ('pop', 0.9, 0.4),
           ('swipe', i2 - 0.02, 0.5), ('pop', i2 + 0.05, 0.5),
           ('swipe', o1 - 0.03, 0.6), ('buzz', o1 + 0.9, 0.25),
           ('ding', o1 + wt('xi_o1', 'TAILLE', 0.5), 0.5), ('ding', o1 + wt('xi_o1', 'CONTOURS', 1.6), 0.5),
           ('ding', o1 + wt('xi_o1', 'RASE', 2.7), 0.5),
           ('whoosh', i3 - 0.03, 0.5), ('wah', i3 + 0.1, 0.25), ('stamp', o2 + 0.02, 0.7), ('boing', o2 + 0.1, 0.4),
           ('swipe', o2 + 0.53, 0.5), ('pop', o2 + wt('xi_o2', 'CONÇU', 0.9), 0.5), ('sparkle', o2 + wt('xi_o2', 'POILS', 1.8), 0.5),
           ('whoosh', i4 - 0.03, 0.5), ('drumroll', i4 + 0.3, 0.3),
           ('swipe', o3 - 0.03, 0.6), ('pop', o3 + 0.05, 0.5), ('scratch', t29, 0.4), ('coins', t29 + 0.05, 0.6),
           ('whoosh', i5 - 0.03, 0.6), ('pop', i5 + 0.05, 0.5), ('sparkle', i5 + wt('xi_i5', 'ÉCRIS', 1.9), 0.6),
           ('bells', i6 + 0.05, 0.4), ('ding', i6 + RCTA + 0.05, 0.7)]
    sh = Shot('interview_tondeuse', TL.dur, draw_it, TL.voices(), sfx, []); sh.tl = TL
    return [sh], None
