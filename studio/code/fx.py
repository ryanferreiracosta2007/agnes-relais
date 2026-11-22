# -*- coding: utf-8 -*-
"""Effets d'émotion dessinés autour d'une tête (coordonnées monde)."""
import math, random
from ink import *

def spring(t, t0, amp=1.0, f=13.0, d=7.0):
    if t < t0: return 0.0
    u = t - t0
    return amp * math.exp(-d * u) * math.sin(f * u)

def sweat(ctx, x, y, t, s=1.0):
    u = (t * 0.8) % 1.0
    yy = y + 60 * u
    ctx.save(); ctx.translate(x, yy); ctx.scale(s, s)
    ink_fill(ctx, lambda c: blob(c, [(0, -30), (16, 4), (0, 20), (-16, 4)], 7, 0.3), hexc('#8fd3ff'), lw=4)
    ctx.restore()

def vein(ctx, x, y, t, s=1.0):
    k = 1 + 0.15 * math.sin(t * 18)
    ctx.save(); ctx.translate(x, y); ctx.scale(s * k, s * k)
    for a in range(4):
        ctx.save(); ctx.rotate(a * math.pi / 2 + math.pi / 4)
        ctx.new_path(); ctx.move_to(6, -6); ctx.curve_to(22, -6, 22, -22, 6, -22)
        ctx.set_source_rgb(*INK); ctx.set_line_width(12); ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc('#e8263d')); ctx.set_line_width(6); ctx.stroke(); ctx.restore()
    ctx.restore()

def shock_lines(ctx, x, y, t, r=170, n=12, col=INK):
    for i in range(n):
        a = 2 * math.pi * i / n + 0.15 * math.sin(t * 30 + i)
        r0 = r + 10 * math.sin(t * 40 + i); r1 = r0 + 55
        ctx.new_path(); ctx.move_to(x + r0 * math.cos(a), y + r0 * math.sin(a)); ctx.line_to(x + r1 * math.cos(a), y + r1 * math.sin(a))
        ctx.set_source_rgb(*col); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def spit(ctx, x, y, t, t0, direction=-1):
    if t < t0 or t > t0 + 1.0: return
    u = t - t0; rnd = random.Random(11)
    for i in range(26):
        a = rnd.uniform(-0.5, 0.5); sp = rnd.uniform(500, 1300); r = rnd.uniform(5, 15)
        px = x + direction * sp * u * math.cos(a); py = y + sp * u * math.sin(a) + 700 * u * u
        ctx.new_path(); ctx.arc(px, py, r, 0, 7); ctx.set_source_rgba(0.75, 0.9, 1.0, max(0, 0.95 - u)); ctx.fill_preserve()
        ctx.set_source_rgba(*INK, max(0, 0.6 - u)); ctx.set_line_width(2.5); ctx.stroke()

def dust(ctx, x, y, t, t0):
    if t < t0 or t > t0 + 0.9: return
    u = (t - t0) / 0.9; rnd = random.Random(3)
    for i in range(9):
        a = rnd.uniform(math.pi, 2 * math.pi); d = 60 + 160 * u
        ctx.new_path(); ctx.arc(x + d * math.cos(a) * 1.4, y + d * math.sin(a) * 0.5, 50 * (1 - u) + 20, 0, 7)
        ctx.set_source_rgba(0.9, 0.86, 0.8, 1 - u); ctx.fill_preserve(); ctx.set_source_rgba(*INK, 0.8 * (1 - u)); ctx.set_line_width(4); ctx.stroke()

def sniff_marks(ctx, x, y, t):
    for i in range(3):
        k = (t * 3 + i * 0.33) % 1.0
        ctx.new_path(); ctx.arc(x - 30 - 50 * k, y - 10 * i, 10 + 6 * i, -0.8, 0.8)
        ctx.set_source_rgba(*INK, 1 - k); ctx.set_line_width(6); ctx.stroke()

def can(ctx, x, y, s, t, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ink_fill(ctx, lambda c: rrect(c, -30, -55, 60, 110, 10), hexc('#d7263d'), lw=5)
    ctx.new_path(); ctx.rectangle(-30, -12, 60, 22); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()
