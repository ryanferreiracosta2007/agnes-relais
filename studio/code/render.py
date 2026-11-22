# -*- coding: utf-8 -*-
import sys, subprocess, os, json
import numpy as np, cairo
from ink import W, H, FPS
import scenes as S
import audio as A

ROOT = os.path.dirname(os.path.abspath(__file__))

def draw_frame(ctx, shot, t):
    ctx.save(); shot.draw(ctx, t, shot); ctx.restore()
    for txt, t0, t1 in shot.caps:
        if t0 <= t < t1:
            S.draw_caption(ctx, txt, t, t0, shot.cap_y)
    S.overlay_legal(ctx)

def render_video(shots, out):
    total = sum(s.dur for s in shots); nf = int(round(total * FPS))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out],
                         stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    starts = np.cumsum([0] + [s.dur for s in shots])
    for f in range(nf):
        tg = f / FPS
        i = min(np.searchsorted(starts, tg, side='right') - 1, len(shots) - 1)
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint()
        draw_frame(ctx, shots[i], tg - starts[i]); ctx.restore()
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
        if f % 150 == 0: print(out, f, '/', nf, flush=True)
    p.stdin.close(); p.wait()
    return nf / FPS

def stills(shots, out, per=3):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    paths = []
    for s in shots:
        for k in range(per):
            t = s.dur * (k + 0.5) / per
            ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint(); draw_frame(ctx, s, t); ctx.restore()
            pth = f'{ROOT}/frames/st_{s.name}_{k}.png'; surf.write_to_png(pth); paths.append(pth)
    return paths

def audio_events(shots, offset=0.0):
    v, fx = [], []; t0 = offset
    for s in shots:
        v += [(c, t0 + at) for c, at, w in s.voices]
        fx += [(n, t0 + at, g) for n, at, g in s.sfx]
        t0 += s.dur
    return v, fx
