# -*- coding: utf-8 -*-
"""Plans des pubs Parfum 6 (corps commun + 3 accroches)."""
import math, os, wave, random
import numpy as np
import cairo
from ink import *
from chars import draw_char
from props import *

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIP = lambda n: os.path.join(ROOT, 'clips', n + '.wav')

# ------------------------------------------------------------------ enveloppes de voix (bouche)
_ENV = {}
def clip_len(name):
    with wave.open(CLIP(name)) as w:
        return w.getnframes() / w.getframerate()

def env(name):
    if name in _ENV: return _ENV[name]
    with wave.open(CLIP(name)) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() > 1: a = a.reshape(-1, w.getnchannels()).mean(1)
    hop = sr // 60
    n = len(a) // hop
    r = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1))
    r = r / (np.percentile(r, 95) + 1e-6)
    _ENV[name] = (r, 60)
    return _ENV[name]

class Shot:
    def __init__(self, name, dur, draw, voices=(), sfx=(), caps=(), cap_y=1330):
        self.name, self.dur, self.draw = name, dur, draw
        self.voices = list(voices)   # (clip, at, who)
        self.sfx = list(sfx)         # (sfx_name, at, gain)
        self.caps = list(caps)       # (text, t0, t1)
        self.cap_y = cap_y

    def mouth(self, who, t):
        for clip, at, w in self.voices:
            if w != who: continue
            L = clip_len(clip)
            if at <= t < at + L:
                r, fr = env(clip)
                i = int((t - at) * fr)
                v = float(r[min(i, len(r) - 1)])
                return clamp(v * 0.95 - 0.08) * (0.75 + 0.25 * math.sin(t * 31))
        return 0.0

    def talking(self, who, t):
        return any(w == who and at <= t < at + clip_len(c) for c, at, w in self.voices)

def caps_from(clip, at, chunks, end_pad=0.25):
    """chunks : [(texte, t_rel)] -> sous-titres absolus dans le plan"""
    L = clip_len(clip); out = []
    for i, (txt, r) in enumerate(chunks):
        t1 = at + (chunks[i + 1][1] if i + 1 < len(chunks) else L + end_pad)
        out.append((txt, at + r, t1))
    return out

# ------------------------------------------------------------------ calques communs
_PAPER = {}
def paper(k='base'):
    if k not in _PAPER:
        _PAPER[k] = paper_surface(seed=len(_PAPER) + 2)
    return _PAPER[k]

def overlay_legal(ctx):
    ctx.save()
    x = 34
    for s, bg in (("PUBLICITÉ", (0.08, 0.08, 0.08)), ("IMAGES VIRTUELLES", (0.08, 0.08, 0.08))):
        ctx.select_font_face('Patrick Hand'); ctx.set_font_size(44)
        w = ctx.text_extents(s).x_advance + 30
        ctx.new_path(); rrect(ctx, x, 146, w, 58, 12); ctx.set_source_rgba(*bg, 0.78); ctx.fill()
        ctx.move_to(x + 15, 190); ctx.set_source_rgb(1, 1, 1); ctx.show_text(s)
        x += w + 14
    ctx.restore()

HL = ('€', 'PANIER', 'ORANGE', 'LATTAFA', 'GOLD', 'NOËL', 'CADEAU', 'BLACK', 'FRIDAY', '25')

def draw_caption(ctx, txt, t, t0, y):
    k = ease_out_back((t - t0) / 0.16, 2.2) if t >= t0 else 0
    if k <= 0: return
    words = txt.split(' ')
    size = 96
    lines = [words]
    if text_w(ctx, txt, size) > 920 and len(words) > 1:
        best = None
        for i in range(1, len(words)):
            a, b = ' '.join(words[:i]), ' '.join(words[i:])
            m = max(text_w(ctx, a, size), text_w(ctx, b, size))
            if best is None or m < best[0]: best = (m, i)
        i = best[1]; lines = [words[:i], words[i:]]
    for li, ws in enumerate(lines):
        yy = y + (li - (len(lines) - 1) / 2) * size * 1.05
        full = ' '.join(ws); tw = min(text_w(ctx, full, size), 980); sc_fit = tw / max(text_w(ctx, full, size), 1)
        x = W / 2 - tw / 2
        for w_ in ws:
            ww = text_w(ctx, w_ + ' ', size) * sc_fit
            col = YEL if any(h in w_.upper() for h in HL) else (1, 1, 1)
            if 'PANIER' in w_ or 'ORANGE' in w_: col = ORANGE
            ctx.save(); ctx.translate(x + text_w(ctx, w_, size) * sc_fit / 2, yy); ctx.scale(k, k)
            text(ctx, w_, 0, 0, size * sc_fit, fill=col, sw=size * 0.13 * sc_fit)
            ctx.restore()
            x += ww

def flash(ctx, t, d=0.12, col=(1, 1, 1)):
    if t < d:
        ctx.set_source_rgba(*col, 0.85 * (1 - t / d)); ctx.paint()

def footage(ctx, seg, t, zoom0=1.0, zoom1=1.08, dur=4.0, cx=W / 2, cy=H / 2, offset=0):
    files = sorted(os.listdir(os.path.join(ROOT, 'seg', seg)))
    i = min(int(t * 30) + offset, len(files) - 1)
    s = load_jpg(os.path.join(ROOT, 'seg', seg, files[i]))
    z = zoom0 + (zoom1 - zoom0) * ease(t / dur)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)
    ctx.set_source_surface(s, 0, 0); ctx.paint(); ctx.restore()
    # vignette chaude + cadre encre
    g = cairo.RadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.12, 0.05, 0, 0.55)
    ctx.set_source(g); ctx.paint()
    ctx.new_path(); rrect(ctx, 16, 16, W - 32, H - 32, 30); ctx.set_source_rgb(*INK); ctx.set_line_width(14); ctx.stroke()

def cam(ctx, t, z=1.0, cx=W / 2, cy=H / 2, shake=0.0, seed=0):
    dx, dy = (jit(boil_seed(t, 24) + seed, 1, shake) if shake > 0 else (0, 0))
    ctx.translate(cx + dx, cy + dy); ctx.scale(z, z); ctx.translate(-cx, -cy)

def shake_at(t, times, amp=16, d=0.3):
    s = 0
    for t0 in times:
        if t0 <= t < t0 + d: s = max(s, amp * (1 - (t - t0) / d))
    return s

def hearts_float(ctx, t, x, y, n=6, seed=0, start=0.0):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.uniform(0, 1.6); u = ((t - start + ph) % 1.8) / 1.8
        if t < start: return
        hx = x + rnd.uniform(-120, 120) + 25 * math.sin(t * 3 + i); hy = y - u * 320
        a = 1 - u
        ctx.save(); ctx.translate(hx, hy); ctx.scale(0.6 + 0.6 * a, 0.6 + 0.6 * a)
        ink_fill(ctx, lambda c: heart(c, 0, 0, 34), hexc('#e8455e'), lw=4)
        ctx.restore()

# ------------------------------------------------------------------ décors réutilisables
def bg_boutique(ctx, t):
    sd = boil_seed(t)
    floor_wall(ctx, t, hexc('#f1ddd0'), hexc('#d9bfa8'), 1320, 11)
    # panneaux de marbre
    for i in range(4):
        ink_line(ctx, [(i * 300 - 40, 0), (i * 300 + 60, 700), (i * 300 + 10, 1320)], sd + i, 2.5, color=(0.8, 0.7, 0.65))
    # étagères dorées avec flacons génériques
    cols = [hexc('#f2a6c4'), hexc('#8ec5ff'), hexc('#c9a2f0'), hexc('#ffd0a0'), hexc('#a8e6cf')]
    for row, y in enumerate((430, 760)):
        ink_fill(ctx, lambda c, y=y: c.rectangle(40, y, W - 80, 26), GOLD, lw=5)
        for k in range(6):
            bx = 120 + k * 168; col = cols[(k + row) % 5]
            ink_fill(ctx, lambda c, bx=bx, y=y: blob(c, [(bx - 34, y), (bx - 40, y - 90), (bx - 20, y - 120),
                                                        (bx + 20, y - 120), (bx + 40, y - 90), (bx + 34, y)],
                                                     sd + k + row * 9, 0.8), col, lw=4)
            ink_fill(ctx, lambda c, bx=bx, y=y: c.rectangle(bx - 12, y - 150, 24, 30), GOLD, lw=4)
    # spot
    g = cairo.RadialGradient(300, 900, 50, 300, 900, 600)
    g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.55); g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
    ctx.set_source(g); ctx.paint()

def bg_bedroom(ctx, t):
    sd = boil_seed(t)
    floor_wall(ctx, t, hexc('#a9bfd6'), hexc('#c79c6e'), 1380, 21)
    hatch_rect(ctx, 0, 0, W, 1380, sd, False, 22, 0.12)
    window_night(ctx, 640, 220, 320, 380, t, 5)
    # poster
    ink_fill(ctx, lambda c: c.rectangle(90, 260, 260, 340), hexc('#f4c430'), lw=6)
    text(ctx, 'RAP', 220, 430, 110, fill=hexc('#d7263d'), rot=-0.1)
    # lit
    ink_fill(ctx, lambda c: blob(c, [(-40, 1250), (W + 40, 1200), (W + 40, 1700), (-40, 1700)], sd, 2),
             hexc('#e7e2f2'), lw=7, shade=lambda c: c.rectangle(0, 1450, W, 300), seed=sd)

def bg_restaurant(ctx, t):
    sd = boil_seed(t)
    ctx.set_source_rgb(*hexc('#3b2550')); ctx.paint()
    hatch_rect(ctx, 0, 0, W, H, sd, True, 26, 0.18)
    window_night(ctx, 340, 420, 400, 460, t, 9)
    string_lights(ctx, t, 300, 3)
    g = cairo.RadialGradient(W / 2, 1400, 80, W / 2, 1400, 900)
    g.add_color_stop_rgba(0, 1, 0.75, 0.35, 0.45); g.add_color_stop_rgba(1, 1, 0.6, 0.3, 0)
    ctx.set_source(g); ctx.paint()

def fg_table(ctx, t):
    sd = boil_seed(t)
    ink_fill(ctx, lambda c: blob(c, [(-40, 1390), (W + 40, 1390), (W + 40, H + 40), (-40, H + 40)], sd, 1.5),
             hexc('#7a4a2b'), lw=8, shade=lambda c: c.rectangle(0, 1470, W, 600), seed=sd)
    ink_fill(ctx, lambda c: blob(c, [(-40, 1390), (W + 40, 1390), (W + 40, 1420), (-40, 1420)], sd + 1, 1),
             hexc('#f2e6d0'), lw=6)
    # bougie
    ink_fill(ctx, lambda c: c.rectangle(515, 1290, 50, 110), hexc('#fff4dc'), lw=5)
    fl = 1 + 0.15 * math.sin(t * 17)
    ink_fill(ctx, lambda c: blob(c, [(540, 1290), (522, 1262), (540, 1210 - 10 * fl), (558, 1262)], sd + 2, 1),
             hexc('#ffb43a'), lw=4)
    g = cairo.RadialGradient(540, 1250, 10, 540, 1250, 260)
    g.add_color_stop_rgba(0, 1, 0.8, 0.4, 0.45 * fl); g.add_color_stop_rgba(1, 1, 0.8, 0.4, 0)
    ctx.set_source(g); ctx.paint()

def bg_xmas(ctx, t):
    sd = boil_seed(t)
    floor_wall(ctx, t, hexc('#e9cba0'), hexc('#9c5b3a'), 1360, 31)
    hatch_rect(ctx, 0, 0, W, 1360, sd, False, 30, 0.1)
    window_night(ctx, 620, 230, 360, 420, t, 7)
    ctx.save(); ctx.rectangle(620, 230, 360, 420); ctx.clip(); snow(ctx, t, 25, 4); ctx.restore()
    string_lights(ctx, t, 190, 8, 7)
    xmas_tree(ctx, 170, 980, 1.05, t, 2)

def bg_gold(ctx, t, col=hexc('#f6c453'), ray=hexc('#ffe9a8')):
    ctx.set_source_rgb(*col); ctx.paint()
    rays(ctx, W / 2, 800, t, ray, 18, 0.55)
    hatch_rect(ctx, 0, 0, W, H, boil_seed(t), False, 24, 0.08)

def bg_street(ctx, t):
    sd = boil_seed(t)
    ctx.set_source_rgb(*hexc('#2a2346')); ctx.paint()
    for i, (x, w, h, c) in enumerate([(0, 300, 1100, '#3f3466'), (280, 280, 1250, '#4a3c74'), (540, 300, 1000, '#3a2f60'),
                                      (820, 300, 1200, '#463a70')]):
        ink_fill(ctx, lambda cc, x=x, w=w, h=h: cc.rectangle(x, 1400 - h, w, h), hexc(c), lw=6,
                 shade=lambda cc, x=x, w=w, h=h: cc.rectangle(x, 1400 - h, w * 0.3, h), seed=sd + i)
        rnd = random.Random(i)
        for k in range(8):
            wx = x + 40 + (k % 3) * 80; wy = 1400 - h + 60 + (k // 3) * 150
            on = rnd.random() > 0.35
            ink_fill(ctx, lambda cc, wx=wx, wy=wy: cc.rectangle(wx, wy, 50, 80),
                     hexc('#ffd27a') if on else hexc('#1d1836'), lw=4)
    ctx.set_source_rgb(*hexc('#4b4458')); ctx.rectangle(0, 1400, W, H - 1400); ctx.fill()
    ink_line(ctx, [(-10, 1400), (W + 10, 1400)], sd, 7)
    string_lights(ctx, t, 260, 5)

# ------------------------------------------------------------------ PLANS
def S(t0, t1, t):  # fenêtre
    return t0 <= t < t1

# ---------- Accroche A : prix boutique
def hookA():
    v = [('p190', 0.0, 'hamza'), ('pparfum', 2.35, 'hamza')]
    def draw(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.04 * t, 540, 900, shake_at(t, [0.0, 2.35], 22))
        bg_boutique(ctx, t)
        # présentoir + carte prix
        ink_fill(ctx, lambda c: blob(c, [(90, 1150), (480, 1150), (470, 1700), (100, 1700)], boil_seed(t), 1.2),
                 hexc('#f7efe6'), lw=7, shade=lambda c: c.rectangle(80, 1150, 120, 600), seed=boil_seed(t))
        ink_fill(ctx, lambda c: blob(c, [(200, 1150), (215, 1000), (250, 960), (320, 960), (355, 1000), (370, 1150)],
                                     boil_seed(t) + 3, 1), hexc('#bfe3f5'), lw=6)
        ink_fill(ctx, lambda c: c.rectangle(258, 900, 54, 60), hexc('#c0c0c8'), lw=5)
        k = pop(t, 0.05, 0.3)
        price_tag(ctx, 300, 1120, 0.9 * k, t, '190 €', rot=-0.12, col=(1, 1, 1), fg=hexc('#b3122e'))
        m = sh.mouth('hamza', t); shocked = t >= 2.35
        draw_char(ctx, 'hamza', 760, 960 + (0 if not shocked else -20), 1.15, t, outfit='sweat', mouth=max(m, 0.25),
                  eyes='wide', brows=1.0, look=(-1, 0.3) if not shocked else (0, 0), smile=-0.4,
                  arms=('face', 'face') if shocked else ('down', 'point_side'), tilt=0.06 if shocked else -0.05,
                  body_rot=0.04 * math.sin(t * 30) if shocked else 0)
        if shocked: speed_lines(ctx, t, 760, 800, seed=4)
        for i in range(4) if t > 0.3 else ():
            sparkle(ctx, 200 + i * 60, 940 - i * 30, 22, t, i)
        ctx.restore()
        burst_txt = pop(t, 2.35, 0.25)
        if burst_txt > 0:
            ctx.save(); ctx.translate(760, 470); ctx.scale(burst_txt, burst_txt)
            burst(ctx, 0, 0, 150, YEL, boil_seed(t), 12, 0.7); text(ctx, '?!', 0, 0, 170, fill=hexc('#d7263d'))
            ctx.restore()
    caps = caps_from('p190', 0.0, [('190 € ?!', 0.0)]) + caps_from('pparfum', 2.35, [('POUR UN PARFUM ?!', 0.0)])
    return [Shot('hookA', 3.85, draw, v, [('scratch', 0.0, 0.9), ('boing', 2.35, 0.8), ('pop', 0.05, 0.6)], caps, cap_y=1460)]

# ---------- Scène rendez-vous (sert à l'accroche B et à la fin)
def date_scene(ctx, t, sh, zoom=1.0, zc=(780, 820), ham_cam=False, secret_t=None, rewind=0.0):
    ctx.save(); cam(ctx, t, zoom, *zc)
    bg_restaurant(ctx, t)
    ines_talk = sh.talking('ines', t)
    draw_char(ctx, 'ines', 290, 960, 1.0, t, mouth=sh.mouth('ines', t), eyes='open' if ines_talk else 'happy',
              look=(1, 0), blush=1.0, smile=0.7, arms=('down', 'chin'), tilt=0.12, body_rot=0.05)
    hm = sh.mouth('hamza', t)
    look = (0, 0.1) if ham_cam else (-1, 0)
    wink = secret_t is not None and t >= secret_t
    draw_char(ctx, 'hamza', 790, 960, 1.0, t, outfit='chic', mouth=hm, smile=0.8, look=look,
              eyes='wink' if wink and (t % 2.0) < 1.4 else 'open', brows=0.3,
              arms=('down', 'lips' if wink else 'hold'), tilt=-0.06 if not ham_cam else 0.0)
    fg_table(ctx, t)
    ctx.restore()

def hookB():
    L1 = clip_len('a1'); t2 = L1 + 0.2; L2 = clip_len('hook_seduction'); t3 = t2 + L2 + 0.15; dur = t3 + 0.95
    v = [('a1', 0.0, 'ines'), ('hook_seduction', t2, 'hamza')]
    def draw(ctx, t, sh):
        z = 1.0 if t < t2 else 1.0 + 0.75 * ease((t - t2) / 0.5)
        date_scene(ctx, t, sh, z, (790, 820), ham_cam=t >= t2, secret_t=t2 + 6.1)
        hearts_float(ctx, t, 330, 700, 5, 1, start=1.0) if t < t2 else None
        if t >= t2 + 4.1:
            price_tag(ctx, 540, 520, 0.85 * pop(t, t2 + 4.1), t, '25 €', sub='MOINS DE', rot=-0.1)
        if t >= t3:  # retour en arrière
            u = (t - t3) / (dur - t3)
            ctx.set_source_rgba(0.1, 0.08, 0.2, 0.55 + 0.4 * u); ctx.paint()
            for i in range(0, H, 9):
                ctx.rectangle(0, i, W, 3)
            ctx.set_source_rgba(1, 1, 1, 0.08); ctx.fill()
            speed_lines(ctx, t, 540, 960, (1, 1, 1), 30, 0.4, 7)
            for k in (0, 1):
                ctx.new_path(); x0 = 470 + k * 110
                ctx.move_to(x0 + 90, 760); ctx.line_to(x0, 830); ctx.line_to(x0 + 90, 900); ctx.close_path()
                ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
            text(ctx, 'QUELQUES HEURES', 540, 1000, 104, fill=YEL)
            text(ctx, 'PLUS TÔT…', 540, 1110, 104, fill=YEL)
    caps = caps_from('a1', 0.0, [('MMH… C\'EST QUOI, TON PARFUM ?', 0.0), ('IL SENT TROP BON !', 2.5)]) + \
        caps_from('hook_seduction', t2, [('ELLE M\'A DEMANDÉ CE QUE JE PORTAIS…', 0.0),
                                         ('ET TU SAIS COMBIEN JE L\'AI PAYÉ ?', 2.0), ('MOINS DE 25 €.', 4.1),
                                         ('JE TE RACONTE.', 6.1)], end_pad=0.1)
    sfx = [('heart', 0.4, 0.5), ('whoosh', t2 - 0.05, 0.6), ('stamp', t2 + 4.1, 0.8), ('rewind', t3, 0.9)]
    return [Shot('hookB', dur, draw, v, sfx, caps, cap_y=1440)]

def hookC():
    L = clip_len('hook_cadeau'); dur = L + 0.45
    v = [('hook_cadeau', 0.0, 'hamza')]
    def gift_prop(ctx, x, y, t):
        pass
    def draw(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.035 * t, 540, 900, shake_at(t, [4.15], 12))
        bg_xmas(ctx, t)
        open_k = ease((t - 5.4) / 0.4)
        draw_char(ctx, 'hamza', 600, 860, 1.05, t, outfit='noel', mouth=sh.mouth('hamza', t), smile=0.8,
                  eyes='open', brows=0.6 if t < 4.1 else 0.2, arms=('hold', 'hold'))
        gift(ctx, 600, 1260, 1.25, t, lid=open_k)
        if open_k > 0:
            bottle(ctx, 600, 1180 - 260 * open_k, 0.95 * open_k, t, glow=open_k)
            for i in range(6): sparkle(ctx, 600 + 160 * math.cos(i), 1000 + 130 * math.sin(i * 1.7), 26, t, i)
        ctx.restore()
        badge(ctx, 'IDÉE CADEAU', 540, 330, 86, hexc('#d7263d'), scale=pop(t, 0.15), rot=-0.05)
        if t > 2.6: price_tag(ctx, 830, 560, 0.62 * pop(t, 2.6), t, '25 €', sub='MOINS DE', rot=0.12)
    caps = caps_from('hook_cadeau', 0.0, [('LE CADEAU DE NOËL QUI FAIT SON EFFET…', 0.0), ('POUR MOINS DE 25 € ?', 2.1),
                                          ('ÇA EXISTE.', 4.15), ('REGARDE !', 5.45)])
    sfx = [('bells', 0.0, 0.5), ('pop', 0.15, 0.6), ('stamp', 2.6, 0.6), ('sparkle', 5.4, 0.8), ('whoosh', dur - 0.2, 0.6)]
    return [Shot('hookC', dur, draw, v, sfx, caps, cap_y=1440)]

# ---------- CORPS COMMUN
def body(cta_clip='hcta', cta_caps=None):
    shots = []

    # 1. chambre : rendez-vous + budget
    L = clip_len('rdv'); d = L + 0.45
    def draw1(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.03 * t, 540, 900)
        bg_bedroom(ctx, t)
        budget = t >= 3.0
        def ph(ctx2, x, y, tt):
            phone(ctx2, x, y - 20, 0.8, tt, rot=-0.15)
        def wal(ctx2, x, y, tt):
            wallet(ctx2, x, y + 10, 0.9, tt, open_k=ease((tt - 3.1) / 0.3))
        m = sh.mouth('hamza', t)
        if not budget:
            draw_char(ctx, 'hamza', 540, 880, 1.1, t, outfit='sweat', mouth=m, eyes='heart' if 1.0 < t < 2.9 else 'open',
                      blush=1.0 if t > 1.0 else 0, smile=0.9, arms=('down', 'phone'), prop=ph, prop_hand='R', tilt=0.08)
            k = pop(t, 0.35)
            if k > 0:  # bulle de message
                ctx.save(); ctx.translate(800, 470); ctx.scale(k, k)
                ink_fill(ctx, lambda c: rrect(c, -230, -80, 460, 160, 40), (1, 1, 1), lw=6)
                text(ctx, 'Inès : À ce soir !', -10, -10, 58, font='Patrick Hand', fill=INK, stroke=None, shadow=False)
                ink_fill(ctx, lambda c: heart(c, 175, -8, 30), hexc('#e8455e'), lw=4)
                ctx.restore()
        else:
            draw_char(ctx, 'hamza', 540, 880, 1.1, t, outfit='sweat', mouth=m, eyes='open', look=(0, 1), brows=-0.2,
                      smile=-0.6, arms=('hold', 'down'), prop=wal, prop_hand='L', tilt=-0.05)
            u = t - 3.3
            if u > 0: moth(ctx, 360 + 120 * u + 30 * math.sin(u * 6), 1150 - 260 * u, 1.2, t)
        ctx.restore()
        flash(ctx, t)
    caps = caps_from('rdv', 0.15, [('CE SOIR, RENDEZ-VOUS AVEC INÈS…', 0.0), ('ET MON BUDGET…', 2.9), ('C\'EST ÇA.', 3.7)])
    shots.append(Shot('chambre', d, draw1, [('rdv', 0.15, 'hamza')],
                      [('ding', 0.35, 0.7), ('wah', 3.75, 0.6)], caps, cap_y=1440))

    # 2. scroll / découverte
    L = clip_len('attends'); d = L + 0.4
    def draw2(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.25 * ease((t - 0.8) / 1.0), 540, 900)
        ctx.set_source_rgb(*hexc('#2b3550')); ctx.paint(); hatch_rect(ctx, 0, 0, W, H, boil_seed(t), True, 22, 0.25)
        g = cairo.RadialGradient(540, 1100, 50, 540, 900, 900)
        g.add_color_stop_rgba(0, 0.9, 0.95, 1, 0.55); g.add_color_stop_rgba(1, 0.9, 0.95, 1, 0)
        ctx.set_source(g); ctx.paint()
        wide = t > 0.85
        draw_char(ctx, 'hamza', 540, 820, 1.6, t, outfit='sweat', mouth=sh.mouth('hamza', t), eyes='wide' if wide else 'open',
                  brows=1.0 if wide else -0.4, look=(0, 1), smile=0.0)
        def scr(c, tt):
            bottle(c, 0, 10, 0.32, tt, glow=0.6)
        phone(ctx, 540, 1480, 2.1, t, screen=scr, rot=0.05)
        ctx.restore()
        if wide: text(ctx, '!', 820, 420, 200, fill=YEL, scale=pop(t, 0.85), rot=0.15)
        if t > d - 0.15: flash(ctx, 0.0)
    caps = caps_from('attends', 0.1, [('ATTENDS…', 0.15), ('C\'EST QUOI, ÇA ?', 0.8)])
    shots.append(Shot('scroll', d, draw2, [('attends', 0.1, 'hamza')], [('swipe', 0.0, 0.5), ('pop', 0.95, 0.6)], caps,
                      cap_y=560))

    # 3. produit : nom
    d = 5.6
    def draw3(ctx, t, sh):
        footage(ctx, 'nom', t, 1.0, 1.1, d, 600, 700)
        badge(ctx, 'LATTAFA', 540, 330, 78, hexc('#141414'), fg=GOLD, scale=pop(t, 0.1))
        flash(ctx, t)
    caps = caps_from('nom', 0.15, [('CONFIDENTIAL PRIVATE GOLD', 0.0), ('DE LATTAFA', 1.65), ('UNE MAISON DE PARFUM', 2.95),
                                   ('DES ÉMIRATS ARABES UNIS', 4.0)])
    shots.append(Shot('nom', d, draw3, [('nom', 0.15, 'hamza')], [('whoosh', 0.0, 0.6), ('sparkle', 0.2, 0.4)], caps,
                      cap_y=1340))

    # 4. produit : eau de parfum / 100 ml / homme & femme
    d = 4.45
    def draw4(ctx, t, sh):
        footage(ctx, 'edp', t, 1.05, 1.0, d)
        chips = [('EAU DE PARFUM', 0.1, hexc('#141414'), GOLD), ('100 ML', 1.1, GOLD, INK),
                 ('POUR HOMME', 2.5, hexc('#2f63b5'), (1, 1, 1)), ('ET POUR FEMME', 3.65, hexc('#ef7fae'), (1, 1, 1))]
        for i, (s, t0, bg, fg) in enumerate(chips):
            badge(ctx, s, 540, 1280 + (i % 2) * 140 if i >= 2 else 330 + i * 140, 82, bg, fg=fg, scale=pop(t, t0),
                  rot=(-0.04 if i % 2 else 0.04))
        flash(ctx, t)
    shots.append(Shot('edp', d, draw4, [('edp', 0.1, 'hamza')], [('pop', 0.1, 0.5), ('pop', 1.1, 0.5), ('pop', 2.5, 0.5),
                                                                  ('pop', 3.65, 0.5)], []))

    # 5. pyramide olfactive
    t_t, t_c, t_f = 0.2, 0.2 + clip_len('tete') + 0.25, 0
    t_f = t_c + clip_len('coeur') + 0.25
    d = t_f + clip_len('fond') + 0.35
    items = [('TÊTE', t_t, 470, [('peche', 'Pêche', 1.12), ('passion', 'Fruit de la passion', 1.85), ('poire', 'Poire', 3.0),
                                 ('framboise', 'Framboise', 3.75), ('cassis', 'Cassis', 4.6)]),
             ('CŒUR', t_c, 860, [('muguet', 'Muguet', 0.95)]),
             ('FOND', t_f, 1210, [('musc', 'Musc', 0.9), ('vanille', 'Vanille', 1.65), ('santal', 'Santal', 2.45),
                                  ('patchouli', 'Patchouli', 3.4)])]
    def draw5(ctx, t, sh):
        bg_gold(ctx, t)
        for lab, t0, y, its in items:
            k = pop(t, t0)
            if k <= 0: continue
            badge(ctx, lab, 540, y - 170, 70, INK, fg=YEL, scale=k)
            n = len(its)
            for i, (kind, name, r) in enumerate(its):
                kk = pop(t, t0 + r, 0.4)
                if kk <= 0: continue
                if n == 5:
                    x = 120 + i * 210; yy = y + (30 if i % 2 else -10)
                else:
                    x = 540 + (i - (n - 1) / 2) * 240; yy = y
                bob = 6 * math.sin(t * 3 + i)
                fruit(ctx, kind, x, yy + bob, 0.95 * kk, t)
                text(ctx, name, x, yy + 105, 48 if len(name) < 12 else 36, font='Patrick Hand', fill=(1, 1, 1),
                     sw=5, scale=kk, max_w=200)
        draw_char(ctx, 'hamza', 540, 1720, 0.55, t, outfit='sweat', mouth=sh.mouth('hamza', t), eyes='closed',
                  smile=0.8, tilt=-0.1, blush=0.6)
        smell_swirl(ctx, 540, 1600, t, 0.6)
        flash(ctx, t)
    sfx = [('whoosh', 0.0, 0.5)]
    for lab, t0, y, its in items:
        sfx.append(('stamp', t0, 0.35))
        for kind, name, r in its: sfx.append(('pop', t0 + r, 0.55))
    shots.append(Shot('notes', d, draw5, [('tete', t_t, 'hamza'), ('coeur', t_c, 'hamza'), ('fond', t_f, 'hamza')], sfx, []))

    # 6. fruité, sucré, chaud
    L = clip_len('fruite'); d = L + 0.3
    def draw6(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + 0.04 * t, 540, 900)
        bg_gold(ctx, t, hexc('#f39c5a'), hexc('#ffd59a'))
        def bot(c, x, y, tt): bottle(c, x, y - 40, 0.55, tt, glow=0.7)
        draw_char(ctx, 'hamza', 540, 900, 1.15, t, outfit='sweat', mouth=sh.mouth('hamza', t), eyes='closed', smile=1.0,
                  tilt=0.1 * math.sin(t * 1.5), blush=0.8, arms=('down', 'hold_high'), prop=bot, prop_hand='R')
        smell_swirl(ctx, 700, 760, t, 0.9)
        hearts_float(ctx, t, 300, 800, 4, 3)
        ctx.restore()
        for s, t0, x, y, col in (('FRUITÉ', 0.15, 250, 420, hexc('#ff8a3d')), ('SUCRÉ', 1.1, 800, 520, hexc('#ff7fb0')),
                                 ('CHAUD', 2.1, 300, 640, hexc('#e8453c'))):
            text(ctx, s, x, y, 120, fill=col, scale=pop(t, t0), rot=-0.1 if x < 500 else 0.1)
        flash(ctx, t)
    caps = caps_from('fruite', 0.15, [('FRANCHEMENT, ÇA DONNE ENVIE.', 2.85)])
    shots.append(Shot('fruite', d, draw6, [('fruite', 0.15, 'hamza')], [('pop', 0.15, 0.5), ('pop', 1.1, 0.5),
                                                                          ('pop', 2.1, 0.5), ('heart', 2.9, 0.5)], caps,
                      cap_y=1440))

    # 7. le flacon (vraies images) + pschht
    d1 = 58 / 30; d = d1 + 73 / 30
    def draw7(ctx, t, sh):
        if t < d1: footage(ctx, 'fl1', t, 1.0, 1.08, d1)
        else: footage(ctx, 'fl2', t - d1, 1.0, 1.06, d - d1)
        for i in range(5): sparkle(ctx, 300 + i * 120, 700 + 90 * math.sin(i * 2), 30, t, i)
        tp = d1 + 1.45
        if t >= tp:
            u = t - tp
            rnd = random.Random(5)
            for i in range(40):
                a = rnd.uniform(-2.6, -1.9); sp = rnd.uniform(200, 700); r = rnd.uniform(6, 18)
                x = 640 + math.cos(a) * sp * u; y = 330 + math.sin(a) * sp * u * 0.6 + 40 * u * u
                ctx.new_path(); ctx.arc(x, y, r * (1 + u), 0, 7); ctx.set_source_rgba(1, 1, 1, max(0, 0.7 - u * 0.6)); ctx.fill()
            text(ctx, 'PSCHHT !', 360, 560, 130, fill=(1, 1, 1), scale=pop(t, tp), rot=-0.15)
        flash(ctx, t)
    caps = caps_from('flacon', 0.1, [('ET LE FLACON !', 0.0), ('TOUT DORÉ…', 1.15), ('AVEC LA CALLIGRAPHIE ARABE.', 2.0)])
    shots.append(Shot('flacon', d, draw7, [('flacon', 0.1, 'hamza')], [('whoosh', 0.0, 0.5), ('sparkle', 1.2, 0.5),
                                                                         ('pschht', d1 + 1.45, 0.9)], caps, cap_y=1340))

    # 8. le prix
    L = clip_len('prix'); d = L + 0.5
    tp = 0.25 + 1.0
    def draw8(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0, 540, 900, shake_at(t, [tp], 26))
        bg_gold(ctx, t, hexc('#ffd23f'), (1, 1, 1))
        draw_char(ctx, 'hamza', 300, 1250, 0.95, t, outfit='sweat', mouth=sh.mouth('hamza', t),
                  eyes='wide' if t > tp else 'open', brows=1.0 if t > tp else 0.3, look=(1, -1), smile=0.6,
                  arms=('down', 'hold_high'))
        k = pop(t, tp, 0.25)
        if k > 0:
            ctx.save(); ctx.translate(560, 700); s = 1 + 2.5 * (1 - min(1, (t - tp) / 0.12))
            ctx.scale(s, s); ctx.translate(-560, -700)
            price_tag(ctx, 560, 700, 1.0, t, '25 €', sub='MOINS DE', rot=-0.08)
            ctx.restore()
            rnd = random.Random(2)
            for i in range(14):
                u = t - tp; x = rnd.uniform(100, 980); y = -60 + (rnd.uniform(300, 700)) * u + 300 * u * u
                ink_fill(ctx, lambda c, x=x, y=y: blob(c, ellipse_pts(x, y, 30, 30 * abs(math.cos(t * 6 + i)) + 4, 9), i, 0.4),
                         GOLD, lw=4)
        ctx.restore()
        text(ctx, 'LE PRIX ?', 540, 330, 120, fill=(1, 1, 1), scale=pop(t, 0.25))
    shots.append(Shot('prix', d, draw8, [('prix', 0.25, 'hamza')], [('drumroll', 0.25, 0.4), ('stamp', tp, 0.9),
                                                                      ('coins', tp + 0.05, 0.7)], []))

    # 9. Black Friday / Noël
    t_ou = 0.15 + clip_len('bf') + 0.25; d = t_ou + clip_len('ou') + 0.45
    def draw9(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.0 + (0.12 * ease((t - t_ou) / 0.5) if t > t_ou else 0), 600, 1000)
        bg_xmas(ctx, t)
        spray = 3.3 < t < t_ou
        giving = t >= t_ou
        def bot(c, x, y, tt): bottle(c, x, y - 30, 0.42, tt)
        def gif(c, x, y, tt): gift(c, x - 40, y, 0.75, tt)
        draw_char(ctx, 'hamza', 620, 880, 1.05, t, outfit='noel', mouth=sh.mouth('hamza', t), smile=0.9,
                  eyes='closed' if spray else 'open', arms=('down', 'spray') if spray else (('down', 'give') if giving else ('hip', 'down')),
                  prop=bot if spray else (gif if giving else None), prop_hand='R', blush=0.5 if spray else 0)
        if spray:
            u = t - 3.3
            for i in range(18):
                rnd = random.Random(i)
                ctx.new_path(); ctx.arc(760 - 40 * u * rnd.uniform(1, 4), 760 + rnd.uniform(-60, 60) * u, 8 + 14 * u, 0, 7)
                ctx.set_source_rgba(1, 1, 1, max(0, 0.6 - 0.4 * u)); ctx.fill()
        ctx.restore()
        badge(ctx, 'BLACK FRIDAY', 540, 340, 92, INK, fg=YEL, scale=pop(t, 0.15), rot=-0.05)
        badge(ctx, '+ NOËL', 540, 480, 80, hexc('#d7263d'), scale=pop(t, 1.35), rot=0.05)
        snow(ctx, t, 30, 9, 0.7)
    caps = caps_from('bf', 0.15, [('BLACK FRIDAY, NOËL QUI ARRIVE…', 0.0), ('C\'EST LE MOMENT DE SE FAIRE PLAISIR…', 2.35)]) + \
        caps_from('ou', t_ou, [('…OU DE FAIRE PLAISIR !', 0.0)])
    shots.append(Shot('noel', d, draw9, [('bf', 0.15, 'hamza'), ('ou', t_ou, 'hamza')],
                      [('bells', 0.1, 0.5), ('pschht', 3.35, 0.6), ('sparkle', t_ou, 0.6)], caps, cap_y=1440))

    # 10. rendez-vous : Inès valide
    ta = 0.3; ts = ta + clip_len('a1') + 0.2; d = ts + clip_len('secret') + 0.35
    def draw10(ctx, t, sh):
        date_scene(ctx, t, sh, 1.0 + 0.03 * t, (540, 900), secret_t=ts + 1.9)
        hearts_float(ctx, t, 300, 640, 6, 4, start=0.8)
        smell_swirl(ctx, 650, 700, t, 0.7)
        flash(ctx, t)
    caps = caps_from('a1', ta, [('MMH… C\'EST QUOI, TON PARFUM ?', 0.0), ('IL SENT TROP BON !', 2.5)]) + \
        caps_from('secret', ts, [('CONFIDENTIAL PRIVATE GOLD.', 0.0), ('MAIS ÇA RESTE ENTRE NOUS.', 1.9)])
    shots.append(Shot('rdv', d, draw10, [('a1', ta, 'ines'), ('secret', ts, 'hamza')],
                      [('whoosh', 0.0, 0.5), ('heart', 1.0, 0.5), ('wink', ts + 1.95, 0.6)], caps, cap_y=1440))

    # 11. dans la rue : Sarah et Léa valident
    tb = 0.2; tc = tb + clip_len('b1') + 0.05; d = tc + clip_len('c1') + 0.3
    def draw11(ctx, t, sh):
        ctx.save(); cam(ctx, t, 1.05 - 0.03 * t, 540, 900)
        bg_street(ctx, t)
        walk = math.sin(t * 7) * 6
        draw_char(ctx, 'sarah', 190, 980, 0.85, t, mouth=sh.mouth('sarah', t), eyes='heart' if t > 0.8 else 'open', look=(1, 0),
                  blush=1, smile=0.8, arms=('down', 'chin'), body_rot=0.08)
        draw_char(ctx, 'lea', 890, 980, 0.85, t, mouth=sh.mouth('lea', t), eyes='open' if t < tc else 'happy', look=(-1, 0),
                  smile=0.8, arms=('chin', 'down'), body_rot=-0.06)
        draw_char(ctx, 'hamza', 540, 1000 + walk, 1.0, t, outfit='chic', mouth=0, smile=0.9, eyes='open', brows=0.3,
                  arms=('down', 'down'))
        smell_swirl(ctx, 400, 820, t, 0.6, ph=1); smell_swirl(ctx, 690, 820, t, 0.6, ph=2)
        hearts_float(ctx, t, 190, 650, 3, 8, start=0.8); hearts_float(ctx, t, 890, 650, 3, 9, start=tc)
        ctx.restore(); flash(ctx, t)
    caps = caps_from('b1', tb, [('OH… ÇA SENT TROP BON, ICI !', 0.0)]) + caps_from('c1', tc, [('C\'EST CLAIR !', 0.0)])
    shots.append(Shot('rue', d, draw11, [('b1', tb, 'sarah'), ('c1', tc, 'lea')], [('whoosh', 0.0, 0.5), ('heart', 1.0, 0.5),
                                                                                   ('heart', tc + 0.3, 0.5)], caps, cap_y=1440))

    # 12. appel à l'action
    L = clip_len(cta_clip); d = L + 1.8
    def draw12(ctx, t, sh):
        bg_gold(ctx, t, hexc('#fbe3b0'), hexc('#ffc98a'))
        bottle(ctx, 400, 1080, 1.2 * pop(t, 0.0, 0.4), t, glow=1.0)
        for i in range(6): sparkle(ctx, 400 + 220 * math.cos(i * 1.1), 1040 + 200 * math.sin(i * 1.7), 28, t, i)
        draw_char(ctx, 'hamza', 830, 1080, 0.72, t, outfit='chic', mouth=sh.mouth('hamza', t), smile=0.9,
                  arms=('point_up', 'down'), eyes='open', look=(-1, -1))
        price_tag(ctx, 420, 1420, 0.62 * pop(t, 0.3), t, '25 €', sub='MOINS DE', rot=-0.06)
        bob = 14 * math.sin(t * 6)
        k = pop(t, 0.6)
        if k > 0:
            badge(ctx, 'PANIER ORANGE', 470, 540, 96, ORANGE, scale=k, rot=-0.03)
            cart_icon(ctx, 860, 535, 1.1 * k)
            arrow(ctx, 330, 640 + bob * 0.5, 130, 790 + bob * 0.5, t, w=60)
        flash(ctx, t)
    if cta_caps is None:
        cta_caps = [('CONFIDENTIAL PRIVATE GOLD, DE LATTAFA.', 0.0), ('MOINS DE 25 €.', 3.1), ('CLIQUE SUR LE PANIER ORANGE', 4.85),
                    ('EN BAS À GAUCHE.', 6.65)]
    caps = caps_from(cta_clip, 0.2, cta_caps, end_pad=1.4)
    shots.append(Shot('cta', d, draw12, [(cta_clip, 0.2, 'hamza')], [('whoosh', 0.0, 0.5), ('ding', 0.6, 0.7),
                                                                      ('ding', 0.2 + cta_caps[-2][1], 0.6)], caps, cap_y=310))
    return shots
