# -*- coding: utf-8 -*-
"""Bibliothèque commune des sketchs : timeline, sous-titres mot par mot, bandeau, caméra, acteurs, découpe des voix."""
import math, json, wave, cairo
import numpy as np
from ink import *
from chars import draw_char
from scenes import clip_len

SAFE_CX, CAP_Y = 480, 1190

def cut_clip(src, segs, gaps, out):
    w = wave.open(f'voix/{src}.wav'); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    parts = []
    for i, (s, e) in enumerate(segs):
        x = a[int(s * sr):int(e * sr)].copy(); f = int(0.012 * sr); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f); parts.append(x)
        if i < len(segs) - 1: parts.append(np.zeros(int(gaps[i] * sr), np.float32))
    o = wave.open(f'clips/{out}.wav', 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes(np.clip(np.concatenate(parts), -32767, 32767).astype(np.int16).tobytes())

def map_words(words, segs, gaps):
    """mots (texte, t absolu dans la prise) -> temps relatifs au clip découpé"""
    offs = []; o = 0
    for i, (s, e) in enumerate(segs):
        offs.append(o - s); o += (e - s) + (gaps[i] if i < len(gaps) else 0)
    out = []
    for w_, t in words:
        for (s, e), off in zip(segs, offs):
            if s - 0.05 <= t < e:
                out.append((w_, max(0.0, t + off))); break
    return out

class Timeline:
    def __init__(self, order, pause_before, words, start=0.12, gap=0.07, tail=1.3):
        self.order = order; self.words = words; self.T = {}
        t = start
        for c, _ in order:
            t += pause_before.get(c, 0); self.T[c] = t; t += clip_len(c) + gap
        self.dur = t + tail

    def voices(self):
        return [(c, self.T[c], w) for c, w in self.order]

    def captions(self, ctx, t, y=CAP_Y, size=104):
        for clip, who in self.order:
            words = self.words.get(clip, [])
            if not words: continue
            a = self.T[clip]; L = clip_len(clip)
            later = [self.T[c] for c, _ in self.order if self.T[c] > a]
            end = min([a + L + 0.25] + later)
            if not (a <= t < end): continue
            cuts = [0] + page_cuts(words, size=size) + [len(words)]
            page = None
            for i in range(len(cuts) - 1):
                if t - a >= words[cuts[i]][1] - 0.05: page = (cuts[i], cuts[i + 1])
            if page is None: return
            draw_words(ctx, t, a, L, words[page[0]:page[1]], y, size)

def page_cuts(words, maxw=780, size=104, gap=22):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4); c = cairo.Context(surf)
    cuts = []; lines = 1; cur = 0
    for i, (w_, r) in enumerate(words):
        wd = text_w(c, w_, size)
        if cur and cur + gap + wd > maxw:
            lines += 1; cur = 0
            if lines > 2: cuts.append(i); lines = 1
        cur += (gap if cur else 0) + wd
        if w_.endswith(('.', '?', '!', '…')) and i + 1 < len(words) and cur > 300 and (not cuts or cuts[-1] != i + 1):
            cuts.append(i + 1); lines = 1; cur = 0
    return sorted(set(cuts))

def draw_words(ctx, t, a, L, ws, y, size=104, gap=22):
    lines = [[]]; cur = 0
    for w_, r in ws:
        wd = text_w(ctx, w_, size)
        if lines[-1] and cur + gap + wd > 780: lines.append([]); cur = 0
        lines[-1].append((w_, r, wd)); cur += (gap if cur else 0) + wd
    for li, ln in enumerate(lines):
        tot = sum(wd for _, _, wd in ln) + gap * (len(ln) - 1)
        sc = min(1.0, 860 / tot)
        x = SAFE_CX - tot * sc / 2; yy = y + (li - (len(lines) - 1) / 2) * size * 1.08
        for w_, r, wd in ln:
            ta = a + r
            if t >= ta - 0.03:
                k = ease_out_back((t - ta + 0.03) / 0.18, 2.6)
                nxt = [rr for _, rr in ws if rr > r]
                active = t < a + (min(nxt) if nxt else L + 0.25)
                col = YEL if active else (1, 1, 1)
                if 'PANIER' in w_ or 'ORANGE' in w_: col = ORANGE
                ctx.save(); ctx.translate(x + wd * sc / 2, yy - (10 if active else 0))
                ctx.rotate((-0.05 if len(w_) % 2 else 0.05) if active else 0)
                text(ctx, w_, 0, 0, size * sc, fill=col, sw=15 * sc, scale=k * (1.12 if active else 1.0))
                ctx.restore()
            x += (wd + gap) * sc

YEL = (1.0, 0.82, 0.25); ORANGE = hexc('#ff6a13')

def banner(ctx, t, txt, bg=(1, 1, 1), fg=INK, size=70):
    k = pop(t, 0.0, 0.3) if t < 0.4 else 1.0
    ctx.save(); ctx.translate(SAFE_CX, 275); ctx.scale(k, k); ctx.rotate(-0.02)
    w = min(text_w(ctx, txt, size) + 60, 900)
    ctx.new_path(); rrect(ctx, -w / 2 + 7, -48 + 9, w, 96, 22); ctx.set_source_rgba(*INK, 0.5); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -48, w, 96, 22); ctx.set_source_rgb(*bg); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    text(ctx, txt, 0, 2, size, fill=fg, stroke=None, shadow=False, max_w=w - 40)
    ctx.restore()

def view(ctx, z, wx, wy, sx=SAFE_CX + 20, sy=760, shake=0.0, t=0.0):
    dx, dy = jit(boil_seed(t, 30), 5, shake) if shake else (0, 0)
    ctx.translate(sx + dx, sy + dy); ctx.scale(z, z); ctx.translate(-wx, -wy)

def actor(ctx, who, x, y, t, sh, tag, sq=0.0, rot=0.0, sc=0.95, **kw):
    fy = y + 560 * sc
    ctx.save(); ctx.translate(x, fy); ctx.rotate(rot); ctx.scale(1 + sq, 1 - sq); ctx.translate(-x, -fy)
    if who == 'david': kw.setdefault('outfit', 'tee')
    draw_char(ctx, who, x, y, sc, t + (0.4 if tag == 'I' else 0), mouth=sh.mouth(tag, t), **kw)
    ctx.restore()

def cta(ctx, t, t0, cap_y=None):
    """badge PANIER ORANGE + flèche vers le bouton Acheter (zone sûre)"""
    from props import badge, cart_icon, arrow
    k = pop(t, t0)
    badge(ctx, 'PANIER ORANGE', SAFE_CX - 30, 1150, 84, ORANGE, scale=k, rot=-0.03)
    cart_icon(ctx, SAFE_CX + 320, 1145, 0.9 * k)
    if k > 0:
        bob = 18 * math.sin(t * 7); arrow(ctx, 300, 1230 + bob * 0.5, 210, 1360 + bob * 0.5, t, w=54)

def check(ctx, x, y, s, k):
    if k <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s * k, s * k)
    ink_fill(ctx, lambda c: c.arc(0, 0, 38, 0, 7), hexc('#2fa84f'), lw=5)
    ctx.new_path(); ctx.move_to(-18, 0); ctx.line_to(-5, 15); ctx.line_to(20, -14)
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.restore()
