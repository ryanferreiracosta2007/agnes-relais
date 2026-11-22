# -*- coding: utf-8 -*-
"""Moteur 2D style encre hachurée (cairo). Toutes les fonctions sont pures en fonction du temps."""
import math, random
import cairo
import numpy as np

W, H, FPS = 1080, 1920, 30
INK = (0.09, 0.06, 0.05)
PAPER = (0.96, 0.90, 0.78)

def hexc(h, a=None):
    h = h.lstrip('#')
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)

# ---------------------------------------------------------------- bruit / "boil"
def boil_seed(t, rate=10):
    return int(math.floor(t * rate))

def jit(seed, k, amp=1.6):
    r = random.Random(seed * 7919 + k * 104729)
    return (r.uniform(-amp, amp), r.uniform(-amp, amp))

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ease_out_back(x, s=1.7):
    x = max(0.0, min(1.0, x)) - 1
    return 1 + x * x * ((s + 1) * x + s)

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def pop(t, t0, d=0.35):
    """0 -> 1 avec rebond, débute à t0"""
    return ease_out_back((t - t0) / d) if t >= t0 else 0.0

# ---------------------------------------------------------------- textures
_PAT = {}

def hatch_pattern(spacing=11, angle=45, width=2.0, cross=False, alpha=0.55):
    key = (spacing, angle, width, cross, alpha)
    if key in _PAT:
        return _PAT[key]
    S = 128
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    c = cairo.Context(surf)
    c.set_source_rgba(*INK, alpha)
    c.set_line_width(width)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    rnd = random.Random(spacing * 31 + angle)
    for ang in ([angle, -angle] if cross else [angle]):
        # lignes diagonales périodiques (pattern 128 px, pas de 128/k)
        k = max(1, round(S / spacing))
        step = S / k
        for i in range(-2 * k, 3 * k):
            o = i * step
            if ang > 0:
                c.move_to(o + rnd.uniform(-0.6, 0.6), 0); c.line_to(o + S, S)
            else:
                c.move_to(o + S, 0); c.line_to(o + rnd.uniform(-0.6, 0.6), S)
        c.stroke()
    pat = cairo.SurfacePattern(surf)
    pat.set_extend(cairo.EXTEND_REPEAT)
    _PAT[key] = pat
    return pat

def paper_surface(base=PAPER, seed=1, vignette=0.35):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    # grain doux
    from numpy.fft import fft2, ifft2
    f = fft2(n); fy = np.fft.fftfreq(n.shape[0])[:, None]; fx = np.fft.fftfreq(n.shape[1])[None, :]
    f *= np.exp(-(fx ** 2 + fy ** 2) * 900)
    lo = np.real(ifft2(f)); lo = (lo - lo.mean()) / (lo.std() + 1e-6)
    lo = np.kron(lo, np.ones((4, 4), np.float32))[:H, :W]
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - vignette * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    img = np.zeros((H, W, 4), np.uint8)
    for i, ch in enumerate(base):
        val = (ch + lo * 0.025 + fine * 0.018) * v
        img[..., 2 - i] = np.clip(val * 255, 0, 255)
    img[..., 3] = 255
    return surf_from_array(img)

def surf_from_array(arr):
    arr = np.ascontiguousarray(arr)
    h, w = arr.shape[:2]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    buf = np.ndarray((h, surf.get_stride() // 4, 4), np.uint8, buffer=surf.get_data())
    buf[:, :w] = arr
    surf.mark_dirty()
    return surf

_IMG = {}

def load_jpg(path, size=None):
    if path in _IMG:
        return _IMG[path]
    from PIL import Image
    im = Image.open(path).convert('RGB')
    if size: im = im.resize(size)
    a = np.asarray(im)
    bgra = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)])
    s = surf_from_array(bgra)
    if len(_IMG) > 40: _IMG.clear()
    _IMG[path] = s
    return s

# ---------------------------------------------------------------- formes encrées
def blob(ctx, pts, seed, amp=1.4, closed=True):
    """courbe lisse (Catmull-Rom) passant par pts, avec tremblement"""
    P = [(x + jit(seed, i, amp)[0], y + jit(seed, i, amp)[1]) for i, (x, y) in enumerate(pts)]
    n = len(P)
    if n < 2: return
    ctx.move_to(*P[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if (closed or i > 0) else P[i]
        p1 = P[i]; p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        ctx.curve_to(*c1, *c2, *p2)
    if closed: ctx.close_path()

def ellipse_pts(cx, cy, rx, ry, n=14, rot=0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out

def ink_fill(ctx, path_fn, fill, lw=6, shade=None, seed=0, hatch=None):
    """path_fn(ctx) trace le chemin. shade: fonction qui trace la zone d'ombre (sera hachurée)."""
    ctx.new_path(); path_fn(ctx)
    if fill is not None:
        ctx.set_source_rgba(*fill) if len(fill) == 4 else ctx.set_source_rgb(*fill)
        ctx.fill_preserve()
    if shade is not None:
        ctx.save(); ctx.clip_preserve()
        ctx.new_path(); shade(ctx)
        ctx.set_source_rgba(0, 0, 0, 0.13); ctx.fill_preserve()
        ctx.set_source(hatch or hatch_pattern());
        m = cairo.Matrix(); m.translate(*jit(seed, 99, 3)); ctx.get_source().set_matrix(m)
        ctx.fill(); ctx.restore()
        ctx.new_path(); path_fn(ctx)
    if lw:
        ctx.set_source_rgb(*INK); ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.new_path()

def ink_line(ctx, pts, seed, lw=5, amp=1.2, color=INK):
    ctx.new_path(); blob(ctx, pts, seed, amp, closed=False)
    ctx.set_source_rgb(*color); ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()

def hatch_rect(ctx, x, y, w, h, seed=0, cross=False, spacing=12, alpha=0.5):
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.set_source(hatch_pattern(spacing=spacing, cross=cross, alpha=alpha))
    m = cairo.Matrix(); m.translate(*jit(seed, 3, 3)); ctx.get_source().set_matrix(m)
    ctx.paint(); ctx.restore()

# ---------------------------------------------------------------- texte
def text(ctx, s, x, y, size, font='Bangers', fill=(1, 1, 1), stroke=INK, sw=None, align='center',
         rot=0.0, scale=1.0, alpha=1.0, shadow=True, max_w=None):
    if scale <= 0.01 or alpha <= 0.01: return
    ctx.save()
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    k = 1.0
    if max_w and ext.x_advance > max_w:
        k = max_w / ext.x_advance
    ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale * k, scale * k)
    tx = {'center': -ext.x_advance / 2, 'left': 0, 'right': -ext.x_advance}[align]
    ty = size * 0.36
    sw = sw if sw is not None else size * 0.14
    if shadow:
        ctx.move_to(tx + size * 0.05, ty + size * 0.07); ctx.text_path(s)
        ctx.set_source_rgba(*INK, 0.55 * alpha); ctx.fill()
    ctx.move_to(tx, ty); ctx.text_path(s)
    if stroke and sw:
        ctx.set_source_rgba(*stroke, alpha); ctx.set_line_width(sw * 2)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*fill, alpha); ctx.fill()
    ctx.restore()

def text_w(ctx, s, size, font='Bangers'):
    ctx.select_font_face(font); ctx.set_font_size(size)
    return ctx.text_extents(s).x_advance

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def badge(ctx, s, x, y, size, bg, fg=(1, 1, 1), pad=18, rot=0.0, scale=1.0, font='Bangers', lw=5):
    if scale <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale)
    w = text_w(ctx, s, size, font) + pad * 2; h = size * 1.25
    ctx.new_path(); rrect(ctx, -w / 2 + 6, -h / 2 + 8, w, h, h * 0.25)
    ctx.set_source_rgba(*INK, 0.6); ctx.fill()
    ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, h * 0.25)
    ctx.set_source_rgb(*bg); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(lw); ctx.stroke()
    text(ctx, s, 0, 0, size, font, fill=fg, stroke=None, shadow=False)
    ctx.restore()

def star(ctx, cx, cy, r1, r2, n=5, rot=0):
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = rot + math.pi * i / n - math.pi / 2
        (ctx.move_to if i == 0 else ctx.line_to)(cx + r * math.cos(a), cy + r * math.sin(a))
    ctx.close_path()

def heart(ctx, cx, cy, s):
    ctx.move_to(cx, cy + s * 0.35)
    ctx.curve_to(cx - s * 1.1, cy - s * 0.35, cx - s * 0.45, cy - s * 1.05, cx, cy - s * 0.45)
    ctx.curve_to(cx + s * 0.45, cy - s * 1.05, cx + s * 1.1, cy - s * 0.35, cx, cy + s * 0.35)
    ctx.close_path()

def burst(ctx, cx, cy, r, color, seed, n=14, inner=0.72, rot=0.0):
    pts = []
    for i in range(2 * n):
        rr = r * (1 if i % 2 == 0 else inner) * (1 + jit(seed, i, 0.04)[0])
        a = rot + math.pi * i / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.set_source_rgb(*color); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
