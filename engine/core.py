"""Core drawing helpers for the Khmer history documentary engine (paper-cut style).

Canvas is 1920x1080 output; sets are painted at SW x SH (1.25x) so the camera can push in and pan
without softening. Colours are hex strings; helpers take a cairo context.
"""
import hashlib
import math
import os
import shutil
import subprocess

import cairocffi as cairo
import numpy as np

W, H = 1920, 1080
SW, SH = 2400, 1350
FPS = 24
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "build", "cache")
PANGO = shutil.which("pango-view") or "/opt/homebrew/bin/pango-view"

KM_SERIF = "Noto Serif Khmer"
KM_SANS = "Noto Sans Khmer"
KM_DISPLAY = "Moul"
EN_SERIF = "Cormorant Garamond"
EN_SANS = "Helvetica Neue"
ZH_SERIF = "Songti TC"

# Funan palette: terracotta, river-mud ochre, lotus pink, deep jade, gold
PAL = dict(terra="#b5562f", terra_d="#7e3520", ochre="#c08a3e", mud="#8a6a3c", lotus="#e3a1a8", lotus_d="#c06a7a",
           jade="#1f5b4f", jade_d="#123a33", jade_l="#4f8a72", gold="#d8aa4a", gold_l="#f0d58a", ink="#1c1410",
           paper="#efe2c6", paper_d="#d9c39a", night="#141a24", sky="#e9c99a", water="#3f6e6a")


def hexc(c):
    if isinstance(c, tuple):
        return c
    c = PAL.get(c, c).lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, t):
    a, b = hexc(a), hexc(b)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def shade(c, k):
    c = hexc(c)
    if k >= 0:
        return tuple(x + (1 - x) * k for x in c)
    return tuple(x * (1 + k) for x in c)


def src(ctx, c, a=1.0):
    r, g, b = hexc(c)
    ctx.set_source_rgba(r, g, b, a)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def lerp(a, b, t):
    return a + (b - a) * t


def rng(seed):
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ paths
def poly(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def spline(ctx, pts, close=False, k=0.5):
    """Catmull-Rom through points."""
    n = len(pts)
    if n < 3:
        poly(ctx, pts, close)
        return
    P = list(pts)
    if close:
        P = [pts[-1]] + P + [pts[0], pts[1]]
    else:
        P = [pts[0]] + P + [pts[-1]]
    ctx.move_to(*P[1])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        ctx.curve_to(*c1, *c2, *p2)
    if close:
        ctx.close_path()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def ellipse(ctx, x, y, rx, ry, rot=0.0):
    ctx.new_sub_path()
    ctx.save()
    ctx.translate(x, y)
    if rot:
        ctx.rotate(rot)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def lin(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for s in stops:
        g.add_color_stop_rgba(s[0], *hexc(s[1]), s[2] if len(s) > 2 else 1.0)
    return g


def rad(x, y, r0, r1, stops, x1=None, y1=None):
    g = cairo.RadialGradient(x, y, r0, x if x1 is None else x1, y if y1 is None else y1, r1)
    for s in stops:
        g.add_color_stop_rgba(s[0], *hexc(s[1]), s[2] if len(s) > 2 else 1.0)
    return g


def glow(ctx, x, y, r, color, a=0.5):
    ctx.new_path()
    ctx.set_source(rad(x, y, 0, r, [(0, color, a), (0.4, color, a * 0.35), (1, color, 0)]))
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


# ------------------------------------------------------------------ surfaces / textures
def surface(w, h):
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h))


def np_to_surface(rgba):
    """rgba float [0,1] HxWx4 (straight alpha) -> cairo surface (premultiplied BGRA)."""
    h, w = rgba.shape[:2]
    a = rgba[..., 3:4]
    pm = np.concatenate([rgba[..., :3] * a, a], axis=2)
    bgra = (np.clip(pm[..., [2, 1, 0, 3]], 0, 1) * 255 + 0.5).astype(np.uint8)
    s = surface(w, h)
    stride = s.get_stride()
    buf = np.ndarray((h, stride // 4, 4), np.uint8, s.get_data())
    buf[:, :w] = bgra
    s.mark_dirty()
    return s


def surface_to_np(s):
    """-> uint8 HxWx4 premultiplied BGRA copy."""
    s.flush()
    h, w, st = s.get_height(), s.get_width(), s.get_stride()
    return np.ndarray((h, st // 4, 4), np.uint8, s.get_data())[:, :w].copy()


def value_noise(w, h, scale, seed, octaves=4):
    r = rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gs = max(2, int(scale * 2 ** o))
        gx, gy = gs + 2, max(2, int(gs * h / max(w, 1))) + 2
        g = r.random((gy, gx)).astype(np.float32)
        yy = np.linspace(0, gy - 2, h)
        xx = np.linspace(0, gx - 2, w)
        y0 = yy.astype(int)
        x0 = xx.astype(int)
        fy = (yy - y0)[:, None]
        fx = (xx - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        a = g[y0][:, x0]
        b = g[y0][:, x0 + 1]
        c = g[y0 + 1][:, x0]
        d = g[y0 + 1][:, x0 + 1]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        tot += amp
        amp *= 0.5
    return out / tot


_TEX = {}


def texture(kind, w=1024, h=1024, seed=1):
    """Repeatable overlay textures (grey with alpha) as cairo patterns: paper, fibre, palm, weave, stone, grain."""
    key = (kind, w, h, seed)
    if key in _TEX:
        return _TEX[key]
    n = value_noise(w, h, 6, seed, 5)
    n2 = value_noise(w, h, 40, seed + 9, 3)
    if kind == "paper":
        v = n * 0.5 + n2 * 0.5
        a = np.abs(v - 0.5) * 0.55
        col = np.where(v[..., None] > 0.5, 1.0, 0.15) * np.ones(3)
        rgba = np.dstack([col, a])
    elif kind == "fibre":   # mulberry-paper fibres
        r = rng(seed)
        img = np.zeros((h, w), np.float32)
        for _ in range(900):
            x, y = r.random() * w, r.random() * h
            ang = r.random() * math.pi
            L = 20 + r.random() * 90
            for k in range(int(L)):
                xx = int(x + math.cos(ang) * k) % w
                yy = int(y + math.sin(ang) * k + math.sin(k * 0.2) * 2) % h
                img[yy, xx] = 1.0
        from scipy.ndimage import gaussian_filter
        img = gaussian_filter(img, 0.6)
        a = np.clip(img * 0.6, 0, 0.35)
        rgba = np.dstack([np.ones((h, w, 3)), a])
    elif kind == "palm":   # palm-leaf manuscript: fine horizontal fibres
        from PIL import Image
        v = value_noise(w // 16, h, 30, seed, 3)
        v = np.asarray(Image.fromarray((v * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
        a = np.abs(v - 0.5) * 0.7
        col = np.where(v[..., None] > 0.5, 1.0, 0.0) * np.ones(3)
        rgba = np.dstack([col, a])
    elif kind == "weave":  # woven textile
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        warp = (np.sin(xx * 0.9) * 0.5 + 0.5)
        weft = (np.sin(yy * 0.9) * 0.5 + 0.5)
        chk = ((xx // 3 + yy // 3) % 2).astype(np.float32)
        v = warp * chk + weft * (1 - chk)
        a = 0.18 + 0.0 * v
        rgba = np.dstack([np.dstack([v, v, v]), a * (0.6 + 0.4 * v)])
    elif kind == "stone":
        v = n * 0.6 + n2 * 0.4
        a = np.abs(v - 0.5) * 0.9
        col = np.where(v[..., None] > 0.5, 1.0, 0.0) * np.ones(3)
        rgba = np.dstack([col, a])
    else:  # fine grain
        g = rng(seed).standard_normal((h, w)).astype(np.float32)
        a = np.clip(np.abs(g) * 0.10, 0, 0.35)
        col = (g > 0).astype(np.float32)
        rgba = np.dstack([col, col, col, a])
    s = np_to_surface(rgba.astype(np.float32))
    p = cairo.SurfacePattern(s)
    p.set_extend(cairo.EXTEND_REPEAT)
    _TEX[key] = (s, p)
    return s, p


def overlay_texture(ctx, kind, a=1.0, scale=1.0, seed=1, op=None):
    """Paint texture through the current clip."""
    s, p = texture(kind, seed=seed)
    ctx.save()
    if op is not None:
        ctx.set_operator(op)
    ctx.scale(scale, scale)
    ctx.set_source(p)
    ctx.paint_with_alpha(a)
    ctx.restore()


# ------------------------------------------------------------------ text (pango shaping for Khmer / Chinese)
_TXT = {}


def has_khmer(s):
    return any(0x1780 <= ord(ch) <= 0x17FF for ch in s or "")


def has_cjk(s):
    return any(0x4E00 <= ord(ch) <= 0x9FFF for ch in s or "")


def text_surface(text, size, color="#ffffff", font=None, weight="", width=None, align="left",
                 italic=False, spacing=None, markup=False, vertical=False):
    if not text:
        return None
    font = font or (KM_SANS if has_khmer(text) else ZH_SERIF if has_cjk(text) else EN_SANS)
    desc = "%s %s%s %dpx" % (font, "Italic " if italic else "", weight, int(size))
    key = hashlib.sha1("|".join(map(str, [text, desc, color, width, align, spacing, markup, vertical])).encode()).hexdigest()[:22]
    if key in _TXT:
        return _TXT[key]
    os.makedirs(os.path.join(CACHE, "text"), exist_ok=True)
    path = os.path.join(CACHE, "text", key + ".png")
    if not os.path.exists(path):
        tmp = path + ".%d.png" % os.getpid()
        cmd = [PANGO, "--no-display", "--pixels", "--font=" + desc, "--background=transparent",
               "--foreground=" + ("#" + "".join("%02x" % int(c * 255) for c in hexc(color))),
               "--margin=4", "--align=" + align, "--hinting=none", "-o", tmp]
        if width:
            cmd += ["--width=%d" % int(width), "--wrap=word-char"]
        if spacing:
            cmd += ["--line-spacing=%s" % spacing]
        if markup:
            cmd += ["--markup"]
        if vertical:
            cmd += ["--gravity=east", "--gravity-hint=strong", "--rotate=90"]
        cmd += ["--text", text]
        subprocess.run(cmd, check=True, capture_output=True)
        os.replace(tmp, path)
    s = cairo.ImageSurface.create_from_png(path)
    _TXT[key] = s
    return s


def draw_text(ctx, text, x, y, size, color="#ffffff", anchor="tl", a=1.0, shadow=0.0, **kw):
    """anchor: t/m/b + l/c/r. Returns (w, h)."""
    s = text_surface(text, size, color, **kw)
    if s is None:
        return 0, 0
    w, h = s.get_width(), s.get_height()
    ax = {"l": 0, "c": 0.5, "r": 1}[anchor[1]]
    ay = {"t": 0, "m": 0.5, "b": 1}[anchor[0]]
    px, py = x - w * ax, y - h * ay
    if shadow:
        ctx.set_source_rgba(0, 0, 0, shadow * a)
        for dx, dy in ((2, 3), (0, 2), (3, 4)):
            ctx.mask_surface(s, px + dx, py + dy)
    ctx.set_source_surface(s, px, py)
    ctx.paint_with_alpha(a)
    return w, h


# ------------------------------------------------------------------ images
_IMG = {}


def load_image(path, max_w=3000):
    if path in _IMG:
        return _IMG[path]
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    s = np_to_surface(np.asarray(im).astype(np.float32) / 255)
    _IMG[path] = s
    return s


def paint_cover(ctx, s, x, y, w, h, zoom=1.0, fx=0.5, fy=0.5, a=1.0, contain=False):
    """Paint surface s covering (or contained in) box (x,y,w,h), zoomed around focus fx,fy."""
    iw, ih = s.get_width(), s.get_height()
    k = (min if contain else max)(w / iw, h / ih) * zoom
    dw, dh = iw * k, ih * k
    if contain:
        ox, oy = x + (w - dw) / 2, y + (h - dh) / 2
    else:
        ox, oy = x + (w - dw) * fx, y + (h - dh) * fy
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    ctx.translate(ox, oy)
    ctx.scale(k, k)
    ctx.set_source_surface(s, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(a)
    ctx.restore()
    return ox, oy, k
