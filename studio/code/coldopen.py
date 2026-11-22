# -*- coding: utf-8 -*-
"""Ouverture sur le gag : on montre d'abord le meilleur moment, puis on rembobine (« QUELQUES SECONDES PLUS TÔT… »)."""
import math
from ink import *
from props import YEL
from scenes import Shot, speed_lines
import sklib as L

REW = 0.9

def make(orig, a, b, label="QUELQUES SECONDES PLUS TÔT…"):
    H = b - a
    def draw(ctx, t, sh):
        if t < H:
            orig.draw(ctx, a + t, orig)
        elif t < H + REW:
            u = (t - H) / REW
            back = b - (b - a) * ease(u) * 0.9          # l'image recule vite
            orig.draw(ctx, back, orig)
            ctx.set_source_rgba(0.08, 0.06, 0.18, 0.55 + 0.25 * u); ctx.paint()
            for i in range(0, H_PIX, 10): ctx.rectangle(0, i, W, 3)
            ctx.set_source_rgba(1, 1, 1, 0.07); ctx.fill()
            speed_lines(ctx, t, 540, 960, (1, 1, 1), 30, 0.35, 7)
            for k in (0, 1):
                ctx.new_path(); x0 = 400 + k * 110
                ctx.move_to(x0 + 90, 700); ctx.line_to(x0, 770); ctx.line_to(x0 + 90, 840); ctx.close_path()
                ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
            words = label.split(' ')
            text(ctx, ' '.join(words[:2]), L.SAFE_CX, 950, 100, fill=YEL, scale=pop(t, H, 0.2))
            text(ctx, ' '.join(words[2:]), L.SAFE_CX, 1060, 100, fill=YEL, scale=pop(t, H + 0.08, 0.2))
        else:
            orig.draw(ctx, t - H - REW, orig)
    sh = Shot(orig.name + '_co', orig.dur + H + REW, draw, [], [], [])
    # audio : extrait du gag + rembobinage + vidéo complète
    import subprocess
    from scenes import clip_len
    v = []
    for c, at, w in orig.voices:
        L_ = clip_len(c)
        if at < b and at + L_ > a:
            off = max(0.0, a - at); end = min(L_, b - at)
            if off > 0.02 or end < L_ - 0.02:
                nc = f'{c}_cut{int(off * 1000)}_{int(end * 1000)}'
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{off:.3f}', '-t', f'{end - off:.3f}', '-i', f'clips/{c}.wav',
                                '-af', 'afade=t=in:d=0.03,areverse,afade=t=in:d=0.08,areverse', f'clips/{nc}.wav'], check=True)
                v.append((nc, max(0.0, at - a), w))
            else:
                v.append((c, at - a, w))
    v += [(c, at + H + REW, w) for c, at, w in orig.voices]
    fx = [(n, at - a, g) for n, at, g in orig.sfx if a <= at < b] + [('rewind', H - 0.05, 1.0)]
    fx += [(n, at + H + REW, g) for n, at, g in orig.sfx]
    sh.voices, sh.sfx = v, fx
    sh.tl = getattr(orig, 'tl', None)
    return sh

H_PIX = 1920
