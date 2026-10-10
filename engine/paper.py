"""Layered Khmer paper-cut look: every element is a flat sheet of tinted paper with a slightly irregular cut edge,
a soft drop shadow onto the sheet behind, a fibre texture and (optionally) Sbek-style punched ornament.

Main helpers
  sheet(ctx, path_fn, color, depth_shadow=1.0, seed=0, texture=True, edge=True)
  jag(pts, amp, seed)               irregular cut edge for a polyline
  punch(ctx, path_fn, motif, seed)  Sbek perforations (dots / flowers / lozenges) through a sheet
Palettes per time of day: TOD[...] with sky0, sky1, sun, water, far, mid, near, light, shadow, haze.
"""
import math

import numpy as np

from core import (PAL, SH, SW, clamp, ellipse, glow, hexc, lin, mix, overlay_texture, poly, rad, rng, spline, src)

TOD = {
    "dawn": dict(sky0="#3f4d6a", sky1="#e9b48a", sun="#f6d8a0", water="#6f8a8c", far="#8c8aa0", mid="#5e7466",
                 near="#2e4a3e", light="#ffe0b0", shadow="#2a2438", haze="#c9a99a"),
    "day": dict(sky0="#7aa3b8", sky1="#efe2c6", sun="#fff3d6", water="#4f7f7a", far="#9fb0a0", mid="#4f8a72",
                near="#1f5b4f", light="#fff4dc", shadow="#2a3a3a", haze="#d8d0b8"),
    "golden": dict(sky0="#b5562f", sky1="#f0d58a", sun="#fff0c0", water="#8a7a52", far="#c08a6a", mid="#6a7a4a",
                   near="#2e4a3a", light="#ffd89a", shadow="#3a2430", haze="#e0b88a"),
    "dusk": dict(sky0="#2a2440", sky1="#c06a7a", sun="#f0b07a", water="#4a4a5e", far="#6a5a72", mid="#3a4a4e",
                 near="#1c2a2a", light="#f0b8a0", shadow="#141428", haze="#8a6a7a"),
    "night": dict(sky0="#0e1220", sky1="#2a2a40", sun="#f6e6c0", water="#1c2430", far="#2a3040", mid="#1c2430",
                  near="#10161e", light="#c8c0d8", shadow="#05070c", haze="#3a3a50"),
    "lamp": dict(sky0="#3a1e10", sky1="#c8782a", sun="#ffd890", water="#5a3a20", far="#7a4a2a", mid="#5a3420",
                 near="#2a1810", light="#ffcf8a", shadow="#1a0e08", haze="#a8683a"),
}


def jag(pts, amp=3.0, seed=0, step=None):
    """Irregular hand-cut edge: resample the polyline and jitter points perpendicular to it."""
    R = rng(seed)
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / (step or 14)))
        nx, ny = (-(y1 - y0) / L, (x1 - x0) / L) if L else (0, 0)
        for k in range(n):
            u = k / n
            j = R.normal() * amp
            out.append((x0 + (x1 - x0) * u + nx * j, y0 + (y1 - y0) * u + ny * j))
    out.append(pts[-1])
    return out


def path_poly(pts, smooth=False):
    def f(ctx):
        ctx.new_path()
        if smooth:
            spline(ctx, pts, close=True)
        else:
            poly(ctx, pts)
    return f


def path_ellipse(x, y, rx, ry, rot=0.0):
    def f(ctx):
        ctx.new_path()
        ellipse(ctx, x, y, rx, ry, rot)
    return f


def sheet(ctx, path_fn, color, shadow=1.0, seed=0, texture=True, edge=True, grad=None, alpha=1.0):
    """One sheet of paper: soft offset shadow, flat fill (or vertical gradient), fibre texture, lit top edge."""
    if shadow:
        for k, (dx, dy, a) in enumerate(((10, 12, 0.10), (6, 8, 0.12), (3, 4, 0.14))):
            ctx.save()
            ctx.translate(dx * shadow, dy * shadow)
            path_fn(ctx)
            src(ctx, "#0c0806", a * alpha)
            ctx.fill()
            ctx.restore()
    path_fn(ctx)
    if grad:
        ctx.set_source(lin(0, grad[0], 0, grad[1], [(0, grad[2], alpha), (1, grad[3], alpha)]))
    else:
        src(ctx, color, alpha)
    ctx.fill_preserve()
    if texture or edge:
        ctx.save()
        ctx.clip()
        if texture:
            overlay_texture(ctx, "fibre", 0.28 * alpha, 1.0, seed % 3 + 1)
            overlay_texture(ctx, "paper", 0.35 * alpha, 1.3, seed % 3 + 2)
        if edge:   # lit rim just inside the cut edge (paper thickness)
            ctx.translate(2.0, 2.5)
            path_fn(ctx)
            ctx.set_line_width(4.0)
            src(ctx, "#fff4dc", 0.16 * alpha)
            ctx.stroke()
        ctx.restore()
    ctx.new_path()


def punch(ctx, path_fn, motif="dots", seed=0, color="#fff0c8", a=0.85, size=6, spacing=34, box=None):
    """Sbek-style perforations: small cut-out shapes inside a sheet, lit from behind."""
    R = rng(seed)
    ctx.save()
    path_fn(ctx)
    ctx.clip()
    x0, y0, x1, y1 = box or ctx.clip_extents()
    y = y0 + spacing / 2
    row = 0
    while y < y1:
        x = x0 + (spacing / 2 if row % 2 else 0)
        while x < x1:
            jx, jy = R.normal() * 1.2, R.normal() * 1.2
            src(ctx, color, a)
            if motif == "dots":
                ctx.arc(x + jx, y + jy, size * 0.5, 0, 6.283)
                ctx.fill()
            elif motif == "flower":
                for k in range(4):
                    ang = k * math.pi / 2
                    ellipse(ctx, x + math.cos(ang) * size * 0.6, y + math.sin(ang) * size * 0.6, size * 0.5, size * 0.28, ang)
                    ctx.fill()
            elif motif == "lozenge":
                poly(ctx, [(x, y - size), (x + size * 0.6, y), (x, y + size), (x - size * 0.6, y)])
                ctx.fill()
            x += spacing
        y += spacing * 0.8
        row += 1
    ctx.restore()


def sky(ctx, P, hor=0.62, sun=(0.5, 0.5), sun_r=70, bands=7, seed=0):
    """Banded paper sky: horizontal paper strips stepping from sky0 to sky1, a cut-paper sun disc."""
    hy = SH * hor
    for i in range(bands):
        u0 = i / bands
        y0 = hy * u0 - 6
        y1 = hy * (u0 + 1 / bands) + 60
        col = mix(P["sky0"], P["sky1"], (i / (bands - 1)) ** 0.9)
        pts = jag([(-20, y1), (SW * 0.5, y1 + 18 * math.sin(i + seed)), (SW + 20, y1)], 4, seed + i, 40)
        sheet(ctx, path_poly([(-20, y0)] + [(SW + 20, y0)] + pts[::-1]), col, shadow=0.4, seed=i, edge=False)
    sx, sy = SW * sun[0], SH * sun[1]
    glow(ctx, sx, sy, sun_r * 5, P["sun"], 0.35)
    sheet(ctx, path_ellipse(sx, sy, sun_r, sun_r), P["sun"], shadow=0.3, seed=seed)


def clouds(ctx, P, n=5, y=(0.12, 0.4), seed=0, col=None):
    R = rng(seed)
    for i in range(n):
        cx = R.random() * SW
        cy = SH * (y[0] + (y[1] - y[0]) * R.random())
        w = 220 + R.random() * 320
        pts = []
        for k in range(9):
            a = math.pi + k / 8 * math.pi
            rr = (0.7 + 0.5 * R.random())
            pts.append((cx + math.cos(a) * w * 0.5, cy + math.sin(a) * w * 0.18 * rr))
        pts += [(cx + w * 0.5, cy + 10), (cx - w * 0.5, cy + 10)]
        sheet(ctx, path_poly(pts, True), col or mix(P["sky1"], "#ffffff", 0.35), shadow=0.5, seed=i, edge=False)


def ridge(ctx, P, base, amp, color, seed=0, peaks=None, shadow=1.0, x0=-40, x1=None):
    """A hill/mountain sheet across the set. peaks: [(x, height, width)] to add distinct mountains (e.g. Ba The)."""
    x1 = x1 or SW + 40
    xs = np.linspace(x0, x1, 90)
    R = rng(seed)
    ph = R.random(3) * 6
    ys = base - amp * (0.5 + 0.25 * np.sin(xs / 300 + ph[0]) + 0.15 * np.sin(xs / 110 + ph[1]))
    for (px, ph_, pw) in (peaks or []):
        ys = ys - ph_ * np.exp(-((xs - px) / pw) ** 2)
    pts = jag(list(zip(xs, ys)), 3, seed, 30) + [(x1, SH + 40), (x0, SH + 40)]
    sheet(ctx, path_poly(pts), color, shadow=shadow, seed=seed)
    return list(zip(xs, ys))


def water(ctx, P, y0, y1=SH + 40, seed=0, col=None, bands=5):
    c = col or P["water"]
    for i in range(bands):
        yy = y0 + (y1 - y0) * (i / bands) ** 1.6
        cc = mix(c, P["shadow"], 0.08 * i)
        pts = jag([(-30, yy), (SW * 0.5, yy + 6 * math.sin(i)), (SW + 30, yy)], 2.5, seed + i, 30)
        sheet(ctx, path_poly(pts + [(SW + 30, y1), (-30, y1)]), cc, shadow=0.25, seed=i, edge=False)


def water_fx(ctx, t, P, y0, y1, seed=1, speed=20, n=50):
    R = rng(seed)
    for i in range(n):
        y = y0 + (R.random() ** 1.5) * (y1 - y0)
        k = (y - y0) / max(1, (y1 - y0))
        x = (R.random() * SW * 1.2 + t * speed * (0.3 + k)) % (SW * 1.2) - SW * 0.1
        L = 30 + 120 * k * R.random()
        a = (0.15 + 0.2 * R.random()) * (0.5 + 0.5 * math.sin(t * 1.3 + i))
        src(ctx, P["light"], a)
        ctx.new_path()
        ctx.move_to(x, y)
        ctx.curve_to(x + L * 0.3, y - 3, x + L * 0.7, y - 3, x + L, y)
        ctx.set_line_width(2 + 3 * k)
        ctx.stroke()


def palm(ctx, P, x, y, h, kind="sugar", seed=0, col=None, sway=0.0):
    """Paper palm: sugar palm (round crown), coconut (drooping fronds) or nipa (stemless fronds)."""
    c = col or P["near"]
    R = rng(seed)
    if kind != "nipa":
        lean = (R.random() - 0.5) * (0.06 if kind == "sugar" else 0.25)
        tx, ty = x + lean * h + sway, y - h
        sheet(ctx, path_poly([(x - h * 0.02, y), (tx - h * 0.012, ty), (tx + h * 0.012, ty), (x + h * 0.02, y)]),
              mix(c, "#000000", 0.15), shadow=0.6, seed=seed, edge=False)
    else:
        tx, ty = x, y
    n = 16 if kind == "sugar" else 11
    for i in range(n):
        a = -math.pi + (i + R.random() * 0.5) / n * 2 * math.pi if kind == "sugar" else \
            -math.pi * (0.1 + 0.8 * i / (n - 1)) + R.normal() * 0.05
        L = h * (0.16 if kind == "sugar" else 0.3 if kind == "coconut" else 0.55) * (0.8 + 0.3 * R.random())
        if kind == "sugar":   # fan leaves
            pts = [(tx, ty)]
            for j in range(7):
                aa = a - 0.22 + 0.44 * j / 6
                rr = L * (1.0 if j % 2 == 0 else 0.85)
                pts.append((tx + math.cos(aa) * rr, ty + math.sin(aa) * rr * 0.9))
        else:                 # pinnate fronds arching down
            droop = 0.35 if kind == "coconut" else 0.15
            ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.6 + L * droop
            mx, my = tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.6
            pts = [(tx, ty), (mx - L * 0.05, my - L * 0.08), (ex, ey), (mx + L * 0.05, my + L * 0.06)]
            for j in range(6):   # leaflet notches
                u = (j + 1) / 7
                px_ = tx + (ex - tx) * u
                py_ = ty + (ey - ty) * u - math.sin(u * math.pi) * L * 0.1
                pts.insert(-1, (px_ + 8, py_ + 14))
        sheet(ctx, path_poly(pts, smooth=(kind != "sugar")), mix(c, P["light"], 0.08 * R.random()), shadow=0.4,
              seed=seed + i, edge=False)


def stilt_house(ctx, P, x, y, s, seed=0, col="#8a6a3c", roof="#b08a4a"):
    """Thatched house on piles (Chinese records describe raised houses; plan is a reconstruction)."""
    wood = mix(col, P["shadow"], 0.25)
    for k in range(5):
        xx = x - s * 0.8 + k * s * 0.4
        sheet(ctx, path_poly([(xx - s * 0.03, y), (xx - s * 0.03, y - s * 0.8), (xx + s * 0.03, y - s * 0.8),
                              (xx + s * 0.03, y)]), wood, shadow=0.5, seed=seed + k, edge=False, texture=False)
    floor = y - s * 0.75
    sheet(ctx, path_poly([(x - s * 0.9, floor - s * 0.48), (x + s * 0.9, floor - s * 0.48), (x + s * 0.9, floor),
                          (x - s * 0.9, floor)]), col, shadow=0.8, seed=seed)
    src(ctx, "#1c1410", 0.85)
    ctx.rectangle(x - s * 0.12, floor - s * 0.4, s * 0.24, s * 0.36)
    ctx.fill()
    pts = jag([(x - s * 1.25, floor - s * 0.4), (x - s * 0.1, floor - s * 1.3), (x + s * 0.1, floor - s * 1.3),
               (x + s * 1.25, floor - s * 0.4)], 3, seed, 18)
    sheet(ctx, path_poly(pts), roof, shadow=0.9, seed=seed + 1)
    R = rng(seed)
    src(ctx, mix(roof, "#000000", 0.35), 0.5)
    ctx.set_line_width(2)
    for k in range(26):
        u = R.random()
        xx = x - s * 1.1 + u * s * 2.2
        yy = floor - s * 0.45 - (1 - abs(u - 0.5) * 2) * s * 0.8 * R.random()
        ctx.move_to(xx, yy)
        ctx.line_to(xx + (u - 0.5) * s * 0.1, yy + s * 0.14)
        ctx.stroke()


def brick_shrine(ctx, P, x, y, s, seed=0, col="#a8583a"):
    """Small brick sanctuary in pre-Angkorian style (reconstruction)."""
    base = [(x - s * 0.55, y), (x + s * 0.55, y), (x + s * 0.55, y - s * 0.18), (x - s * 0.55, y - s * 0.18)]
    sheet(ctx, path_poly(base), mix(col, "#000000", 0.15), shadow=0.8, seed=seed)
    body = [(x - s * 0.42, y - s * 0.18), (x + s * 0.42, y - s * 0.18), (x + s * 0.42, y - s * 0.9),
            (x - s * 0.42, y - s * 0.9)]
    sheet(ctx, path_poly(body), col, shadow=0.8, seed=seed + 1)
    for k in range(4):
        w_ = s * (0.38 - k * 0.08)
        yy = y - s * (0.9 + k * 0.2)
        sheet(ctx, path_poly([(x - w_, yy), (x + w_, yy), (x + w_ * 0.85, yy - s * 0.2), (x - w_ * 0.85, yy - s * 0.2)]),
              mix(col, P["light"], 0.08 * k), shadow=0.6, seed=seed + 2 + k)
    src(ctx, "#140c08", 0.9)
    ctx.rectangle(x - s * 0.1, y - s * 0.7, s * 0.2, s * 0.52)
    ctx.fill()
    src(ctx, mix(col, "#000000", 0.4), 0.35)
    ctx.set_line_width(1.5)
    for k in range(10):
        yy = y - s * 0.2 - k * s * 0.07
        ctx.move_to(x - s * 0.42, yy)
        ctx.line_to(x + s * 0.42, yy)
        ctx.stroke()


def lotus(ctx, P, x, y, s, open_=1.0, seed=0, col="#e3a1a8"):
    """Lotus flower (paper petals) with a pad."""
    sheet(ctx, path_ellipse(x - s * 0.6, y + s * 0.15, s * 0.9, s * 0.22), mix("#2e6a4a", P["shadow"], 0.1), shadow=0.4,
          seed=seed, edge=False)
    n = 7
    for k in range(n):
        a = -math.pi / 2 + (k - (n - 1) / 2) * 0.32 * (0.4 + 0.6 * open_)
        L = s * (0.55 + 0.12 * (1 - abs(k - 3) / 3))
        tip = (x + math.cos(a) * L, y + math.sin(a) * L)
        pts = [(x, y), (x + math.cos(a - 0.35) * L * 0.55, y + math.sin(a - 0.35) * L * 0.55), tip,
               (x + math.cos(a + 0.35) * L * 0.55, y + math.sin(a + 0.35) * L * 0.55)]
        sheet(ctx, path_poly(pts, True), mix(col, "#ffffff", 0.25 * (k % 2)), shadow=0.3, seed=seed + k, edge=False)


# ---------------------------------------------------------------- boats and ships (reconstructions)
def boat(ctx, P, x, y, L, seed=0, col="#6a4a2a", load=True, f=1):
    """Small plank river boat."""
    pts = [(x - L * 0.5 * f, y - L * 0.06), (x - L * 0.38 * f, y + L * 0.05), (x + L * 0.38 * f, y + L * 0.05),
           (x + L * 0.52 * f, y - L * 0.09), (x + L * 0.42 * f, y - L * 0.02), (x - L * 0.42 * f, y - L * 0.0)]
    sheet(ctx, path_poly(pts, True), col, shadow=0.7, seed=seed)
    src(ctx, mix(col, "#fff0d0", 0.3), 0.6)
    ctx.set_line_width(2)
    ctx.move_to(x - L * 0.42 * f, y + L * 0.015)
    ctx.line_to(x + L * 0.45 * f, y - L * 0.01)
    ctx.stroke()
    if load:
        R = rng(seed)
        for k in range(3):
            cx = x - L * 0.2 + k * L * 0.15
            sheet(ctx, path_ellipse(cx, y - L * 0.05, L * 0.06, L * 0.05), ["#a8744a", "#c08a3e", "#8a6a3c"][k],
                  shadow=0.3, seed=seed + k, edge=False)


def ship(ctx, P, x, y, L, kind="funan", seed=0, t=0.0, f=1):
    """Sea-going ships. funan: long sewn-plank hull with rowers' oars (after Chinese descriptions of Funan ships);
    sail: hull with tilted matting sails (generic Southeast Asian / Indian Ocean trading ship). Reconstructions."""
    hull = "#5a3a22" if kind == "funan" else "#6a4a30"
    bob = math.sin(t * 1.2 + seed) * L * 0.01
    y = y + bob
    stem = 0.16 if kind == "funan" else 0.08
    pts = [(x - L * 0.5 * f, y - L * stem), (x - L * 0.4 * f, y + L * 0.03), (x + L * 0.4 * f, y + L * 0.03),
           (x + L * 0.52 * f, y - L * stem * 1.2), (x + L * 0.45 * f, y - L * 0.06), (x - L * 0.45 * f, y - L * 0.05)]
    sheet(ctx, path_poly(pts, True), hull, shadow=0.9, seed=seed)
    src(ctx, "#d8aa4a", 0.8)
    ctx.set_line_width(L * 0.006)
    ctx.move_to(x - L * 0.45 * f, y - L * 0.02)
    ctx.line_to(x + L * 0.45 * f, y - L * 0.02)
    ctx.stroke()
    if kind == "funan":
        for k in range(14):   # oars
            ox = x - L * 0.36 * f + k * L * 0.055 * f
            ph = math.sin(t * 2.0 + k * 0.1 + seed)
            src(ctx, "#2a1a10", 0.9)
            ctx.set_line_width(L * 0.006)
            ctx.move_to(ox, y - L * 0.04)
            ctx.line_to(ox - L * 0.03 * f + ph * L * 0.02 * f, y + L * 0.12)
            ctx.stroke()
        sheet(ctx, path_poly([(x - L * 0.08 * f, y - L * 0.06), (x + L * 0.1 * f, y - L * 0.06),
                              (x + L * 0.08 * f, y - L * 0.14), (x - L * 0.06 * f, y - L * 0.14)]), "#b5562f",
              shadow=0.5, seed=seed + 3)
    else:
        for k, (mx, mh) in enumerate(((-0.12, 0.62), (0.16, 0.5))):
            px = x + L * mx * f
            src(ctx, "#3a2a1a")
            ctx.set_line_width(L * 0.008)
            ctx.move_to(px, y - L * 0.05)
            ctx.line_to(px, y - L * mh)
            ctx.stroke()
            sail = [(px - L * 0.02 * f, y - L * (mh - 0.02)), (px + L * 0.2 * f, y - L * (mh - 0.06)),
                    (px + L * 0.17 * f, y - L * 0.12), (px - L * 0.04 * f, y - L * 0.1)]
            sheet(ctx, path_poly(sail), "#d9c39a" if k else "#c8a878", shadow=0.6, seed=seed + 5 + k)
            src(ctx, "#8a6a3c", 0.5)
            ctx.set_line_width(1.5)
            for j in range(5):
                u = (j + 1) / 6
                ctx.move_to(sail[0][0] + (sail[3][0] - sail[0][0]) * u, sail[0][1] + (sail[3][1] - sail[0][1]) * u)
                ctx.line_to(sail[1][0] + (sail[2][0] - sail[1][0]) * u, sail[1][1] + (sail[2][1] - sail[1][1]) * u)
                ctx.stroke()


def textile_border(ctx, x0, y0, x1, y1, col="#d8aa4a", seed=0):
    """Woven-textile border band (for cards and frames)."""
    src(ctx, col, 0.9)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.fill()
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    overlay_texture(ctx, "weave", 0.8, 1.0, seed)
    h = y1 - y0
    x = x0
    while x < x1:
        src(ctx, "#7e3520", 0.8)
        poly(ctx, [(x, y0 + h * 0.5), (x + h * 0.35, y0 + h * 0.15), (x + h * 0.7, y0 + h * 0.5), (x + h * 0.35, y0 + h * 0.85)])
        ctx.fill()
        x += h * 0.9
    ctx.restore()
