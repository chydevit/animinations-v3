"""Paper-cut maps of Southeast Asia (Web Mercator). Elevation bands from SRTM-derived terrain tiles become stacked
sheets of paper; rivers and modern borders from Natural Earth; animated elements on top.

map_scene(va, vb, els, ...)   va/vb = (lon, lat, width_deg) camera at start/end of the shot
Elements (dicts with k=...): marker, label, line (animated route; ships=True moves boats along it), blob (approximate
extent, hatched), glowline (canals), note (boxed text with class tag), era (year badge), border_note.
"""
import math
import os

import cairocffi as cairo
import numpy as np

from core import (CACHE, EN_SANS, EN_SERIF, H, KM_SANS, ROOT, W, clamp, draw_text, ease, hexc, mix, np_to_surface,
                  overlay_texture, rrect, smooth, spline, src, text_surface)

GEO = os.path.join(ROOT, "geo")


def merc_y(lat):
    return math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def tile_lon(x, z):
    return x / 2 ** z * 360 - 180


def tile_lat(y, z):
    n = math.pi - 2 * math.pi * y / 2 ** z
    return math.degrees(math.atan(math.sinh(n)))


_D = {}


def _shapes(name):
    if name in _D:
        return _D[name]
    import shapefile
    p = os.path.join(GEO, name, name + ".shp")
    r = shapefile.Reader(p)
    fields = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.iterShapeRecords():
        rec = dict(zip(fields, sr.record))
        pts = sr.shape.points
        parts = list(sr.shape.parts) + [len(pts)]
        rings = []
        for i in range(len(parts) - 1):
            ring = pts[parts[i]:parts[i + 1]]
            xs = [q[0] for q in ring]
            if max(xs) < 55 or min(xs) > 140:
                continue
            rings.append([(x, merc_y(max(-85, min(85, y)))) for x, y in ring])
        if rings:
            out.append((rec, rings))
    _D[name] = out
    return out


# ------------------------------------------------------------------ paper terrain
BANDS = [(0.5, "#c9a86a"), (40, "#b8945a"), (200, "#a87a4a"), (500, "#966a40"), (1000, "#7e5636"), (2000, "#6a4a32")]
SEA = "#2f5f5a"
_DEM = {}


def dem_surface(name):
    if name in _DEM:
        return _DEM[name]
    d = np.load(os.path.join(GEO, name + ".npz"))
    dem, z, tx0, ty0 = d["dem"], int(d["z"]), int(d["x0"]), int(d["y0"])
    h, w = dem.shape
    lon0, lon1 = tile_lon(tx0, z), tile_lon(tx0 + w / 256, z)
    lat0, lat1 = tile_lat(ty0, z), tile_lat(ty0 + h / 256, z)
    bounds = (lon0, merc_y(lat0), lon1, merc_y(lat1))
    cache = os.path.join(CACHE, "paper_%s.png" % name)
    if os.path.exists(cache):
        s = cairo.ImageSurface.create_from_png(cache)
    else:
        from scipy.ndimage import gaussian_filter, shift as nshift
        e = gaussian_filter(dem, 1.2)
        # land mask from Natural Earth (so flat delta land below 1 m is not drawn as sea)
        ms = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
        mc = cairo.Context(ms)
        sx = w / (bounds[2] - bounds[0])
        sy = h / (bounds[3] - bounds[1])
        for rec, rings in _shapes("ne_10m_land"):
            for r in rings:
                mc.new_path()
                for i, (x, y) in enumerate(r):
                    (mc.move_to if i == 0 else mc.line_to)((x - bounds[0]) * sx, (y - bounds[1]) * sy)
                mc.close_path()
                mc.fill()
        ms.flush()
        land = np.ndarray((h, ms.get_stride()), np.uint8, ms.get_data())[:, :w].astype(np.float32) / 255
        e = np.where(land > 0.5, np.maximum(e, 1.0), np.minimum(e, 0.0))
        rgb = np.zeros((h, w, 3), np.float32)
        rgb[:] = hexc(SEA)
        a = np.ones((h, w), np.float32)
        sh = max(2, w // 400)
        for thr, col in BANDS:
            m = (e > thr).astype(np.float32)
            m = np.clip(gaussian_filter(m, 0.7) * 1.6 - 0.3, 0, 1)
            shadow = np.clip(nshift(m, (sh, sh), order=0) - m, 0, 1) * 0.45
            rgb = rgb * (1 - shadow[..., None])
            rgb = rgb * (1 - m[..., None]) + np.array(hexc(col), np.float32) * m[..., None]
            rim = np.clip(m - nshift(m, (-1, -1), order=0), 0, 1) * 0.18   # lit cut edge
            rgb = rgb + rim[..., None]
        # fibre / grain
        r = np.random.default_rng(3).standard_normal((h, w)).astype(np.float32)
        rgb = np.clip(rgb * (1 + 0.035 * gaussian_filter(r, 0.6)[..., None]), 0, 1)
        s = np_to_surface(np.dstack([rgb, a]))
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        s.write_to_png(cache)
    _DEM[name] = (s, bounds)
    return _DEM[name]


class View:
    def __init__(self, lon, lat, width):
        self.cx, self.cy, self.w = lon, merc_y(lat), width
        self.k = W / width

    def xy(self, lon, lat):
        return (W / 2 + (lon - self.cx) * self.k, H / 2 - (merc_y(lat) - self.cy) * self.k)

    def mxy(self, x, my):
        return (W / 2 + (x - self.cx) * self.k, H / 2 - (my - self.cy) * self.k)


def view_at(a, b, q):
    return View(a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q, a[2] * (b[2] / a[2]) ** q)


def draw_base(ctx, V, borders=True):
    ctx.set_source_rgb(*hexc(SEA))
    ctx.paint()
    overlay_texture(ctx, "weave", 0.12, 1.0, 1)
    names = ["dem_sea"] + (["dem_delta"] if V.w < 9 else [])
    for name in names:
        s, (x0, y0, x1, y1) = dem_surface(name)
        p0, p1 = V.mxy(x0, y0), V.mxy(x1, y1)
        ctx.save()
        ctx.translate(p0[0], p0[1])
        ctx.scale((p1[0] - p0[0]) / s.get_width(), (p1[1] - p0[1]) / s.get_height())
        ctx.set_source_surface(s, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
        ctx.paint_with_alpha(1.0 if name == "dem_sea" else clamp((9 - V.w) / 3))
        ctx.restore()
    overlay_texture(ctx, "fibre", 0.25, 1.0, 2)
    lw = max(1.2, min(4.5, 40 / V.w))
    riv = "ne_10m_rivers_lake_centerlines" if V.w < 14 else "ne_50m_rivers_lake_centerlines"
    for rec, rings in _shapes(riv):
        if V.w > 14 and rec.get("scalerank", 9) > 4:
            continue
        for r in rings:
            ctx.new_path()
            for i, (x, y) in enumerate(r):
                (ctx.move_to if i == 0 else ctx.line_to)(*V.mxy(x, y))
            src(ctx, "#4f8a8a", 0.95)
            ctx.set_line_width(lw)
            ctx.stroke()
    for rec, rings in _shapes("ne_50m_lakes"):
        ctx.new_path()
        for r in rings:
            for i, (x, y) in enumerate(r):
                (ctx.move_to if i == 0 else ctx.line_to)(*V.mxy(x, y))
            ctx.close_path()
        src(ctx, "#4f8a8a")
        ctx.fill()
    if borders:   # modern borders: faint, dashed, for orientation only
        for rec, rings in _shapes("ne_50m_admin_0_countries"):
            ctx.new_path()
            for r in rings:
                for i, (x, y) in enumerate(r):
                    (ctx.move_to if i == 0 else ctx.line_to)(*V.mxy(x, y))
                ctx.close_path()
            src(ctx, "#f6ecd6", 0.35)
            ctx.set_line_width(max(1.0, lw * 0.45))
            ctx.set_dash([5, 5])
            ctx.stroke()
            ctx.set_dash([])


def marker(ctx, x, y, a, color="#b5562f", r=10, pulse=0.0):
    if pulse:
        src(ctx, color, 0.5 * (1 - pulse) * a)
        ctx.new_path()
        ctx.arc(x, y, r + 30 * pulse, 0, 6.283)
        ctx.fill()
    src(ctx, "#fff4dc", a)
    ctx.new_path()
    ctx.arc(x, y, r + 3, 0, 6.283)
    ctx.fill()
    src(ctx, color, a)
    ctx.new_path()
    ctx.arc(x, y, r, 0, 6.283)
    ctx.fill()


def tag(ctx, x, y, km, en, a, side="r", size=26):
    s1 = text_surface(km, size, "#1c1410", KM_SANS, "Bold") if km else None
    s2 = text_surface(en, int(size * 0.7), "#4a3020", EN_SANS, "Medium") if en else None
    w = max(s.get_width() for s in (s1, s2) if s) + 22
    h = sum(s.get_height() for s in (s1, s2) if s) + 10
    bx = x + 20 if side == "r" else (x - 20 - w if side == "l" else x - w / 2)
    by = y - h / 2 if side in "lr" else (y - h - 20 if side == "t" else y + 20)
    src(ctx, "#000000", 0.3 * a)
    ctx.rectangle(bx + 4, by + 5, w, h)
    ctx.fill()
    ctx.rectangle(bx, by, w, h)
    src(ctx, "#efe2c6", 0.96 * a)
    ctx.fill()
    yy = by + 5
    for s in (s1, s2):
        if s:
            ctx.set_source_surface(s, bx + 11, yy)
            ctx.paint_with_alpha(a)
            yy += s.get_height()


def _path_pts(V, pts):
    return [V.xy(lon, lat) for lon, lat in pts]


def _poly_len(P):
    L = [0.0]
    for i in range(1, len(P)):
        L.append(L[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    return L


def _point_at(P, L, d):
    for i in range(1, len(P)):
        if L[i] >= d:
            f = (d - L[i - 1]) / max(1e-6, L[i] - L[i - 1])
            return (P[i - 1][0] + (P[i][0] - P[i - 1][0]) * f, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * f,
                    math.atan2(P[i][1] - P[i - 1][1], P[i][0] - P[i - 1][0]))
    return P[-1][0], P[-1][1], 0.0


def draw_elements(ctx, V, els, t, d):
    from cards import class_tag
    for e in els:
        at = e.get("at", 0.0)
        a = smooth((t - at) / e.get("fade", 0.7)) * clamp((e.get("until", 1e9) - t) / 0.5) * clamp((d - t) / 0.4)
        if a <= 0:
            continue
        k = e["k"]
        if k == "marker":
            x, y = V.xy(e["lon"], e["lat"])
            pulse = ((t - at) % 1.6) / 1.6 if e.get("pulse") else 0
            marker(ctx, x, y, a, e.get("color", "#b5562f"), e.get("r", 10), pulse)
            if e.get("km") or e.get("en"):
                tag(ctx, x, y, e.get("km"), e.get("en"), a, e.get("side", "r"), e.get("size", 26))
        elif k == "label":
            x, y = V.xy(e["lon"], e["lat"])
            draw_text(ctx, e.get("km", ""), x, y, e.get("size", 34), e.get("color", "#fff4dc"), "mc", a * 0.95,
                      shadow=0.8, font=KM_SANS, weight="Bold")
            if e.get("en"):
                draw_text(ctx, e["en"], x, y + e.get("size", 34) * 0.95, int(e.get("size", 34) * 0.62), "#f6ecd6", "mc",
                          a * 0.95, shadow=0.8, font=EN_SERIF, weight="SemiBold", italic=True)
        elif k == "blob":   # approximate extent: soft fill + hatching + dashed edge
            P = _path_pts(V, e["pts"])
            grow = ease(clamp((t - at) / e.get("grow", 2.0)))
            cx = sum(p[0] for p in P) / len(P)
            cy = sum(p[1] for p in P) / len(P)
            P = [(cx + (x - cx) * grow, cy + (y - cy) * grow) for x, y in P]
            ctx.save()
            ctx.new_path()
            spline(ctx, P, close=True)
            src(ctx, e.get("fill", "#d8aa4a"), e.get("fa", 0.3) * a)
            ctx.fill_preserve()
            ctx.clip_preserve()
            src(ctx, e.get("fill", "#d8aa4a"), 0.35 * a)
            ctx.set_line_width(2)
            for i in range(-60, 60):
                ctx.move_to(cx + i * 18 - 800, cy - 800)
                ctx.line_to(cx + i * 18 + 800, cy + 800)
            ctx.stroke()
            ctx.restore()
            ctx.new_path()
            spline(ctx, P, close=True)
            src(ctx, e.get("fill", "#d8aa4a"), 0.95 * a)
            ctx.set_line_width(3)
            ctx.set_dash([12, 8])
            ctx.stroke()
            ctx.set_dash([])
        elif k in ("line", "glowline"):
            P = _path_pts(V, e["pts"])
            L = _poly_len(P)
            prog = ease(clamp((t - at) / e.get("draw", 2.0)))
            tgt = L[-1] * prog
            ctx.new_path()
            ctx.move_to(*P[0])
            for i in range(1, len(P)):
                if L[i] <= tgt:
                    ctx.line_to(*P[i])
                else:
                    x, y, _ = _point_at(P, L, tgt)
                    ctx.line_to(x, y)
                    break
            col = e.get("color", "#f0d58a")
            if k == "glowline":
                for wdt, al in ((18, 0.12), (10, 0.25), (4, 1.0)):
                    src(ctx, col, al * a)
                    ctx.set_line_width(wdt * (0.8 + 0.2 * math.sin(t * 3)))
                    ctx.stroke_preserve()
                ctx.new_path()
            else:
                src(ctx, col, a)
                ctx.set_line_width(e.get("lw", 4))
                ctx.set_dash(e.get("dash", [14, 9]), -t * 30)
                ctx.stroke()
                ctx.set_dash([])
            if e.get("ships") and prog >= 1:
                for j in range(e["ships"]):
                    dd = ((t * e.get("speed", 60) + j * L[-1] / e["ships"]) % L[-1])
                    x, y, ang = _point_at(P, L, dd)
                    ctx.save()
                    ctx.translate(x, y)
                    ctx.rotate(ang)
                    src(ctx, "#2a1a10", a)
                    ctx.move_to(-14, -4)
                    ctx.line_to(14, -4)
                    ctx.line_to(9, 5)
                    ctx.line_to(-9, 5)
                    ctx.close_path()
                    ctx.fill()
                    src(ctx, "#efe2c6", a)
                    ctx.move_to(-2, -5)
                    ctx.line_to(-2, -20)
                    ctx.line_to(9, -7)
                    ctx.close_path()
                    ctx.fill()
                    ctx.restore()
        elif k == "note":
            x, y = e.get("x", 80), e.get("y", H - 330)
            s1 = text_surface(e.get("km", ""), 24, "#1c1410", KM_SANS, "", width=e.get("w", 720))
            s2 = text_surface(e.get("en", ""), 18, "#4a3020", EN_SANS, "", width=e.get("w", 720)) if e.get("en") else None
            hh = s1.get_height() + (s2.get_height() if s2 else 0) + 28 + (40 if e.get("cls") else 0)
            ww = max(s1.get_width(), s2.get_width() if s2 else 0) + 30
            src(ctx, "#000000", 0.3 * a)
            ctx.rectangle(x + 5, y + 6, ww, hh)
            ctx.fill()
            ctx.rectangle(x, y, ww, hh)
            src(ctx, "#efe2c6", 0.96 * a)
            ctx.fill()
            yy = y + 10
            if e.get("cls"):
                class_tag(ctx, x + 14, yy, e["cls"], a, 18)
                yy += 40
            ctx.set_source_surface(s1, x + 15, yy)
            ctx.paint_with_alpha(a)
            if s2:
                ctx.set_source_surface(s2, x + 15, yy + s1.get_height() + 4)
                ctx.paint_with_alpha(a)
        elif k == "era":
            draw_text(ctx, e["text"], W - 70, 150, 64, "#f2cf7a", "tr", a, shadow=0.9, font=EN_SERIF, weight="Bold")
            if e.get("km"):
                draw_text(ctx, e["km"], W - 70, 230, 28, "#fff4dc", "tr", a, shadow=0.9, font=KM_SANS, weight="Bold")


def map_scene(va, vb=None, els=(), borders=True, ease_frac=1.0, note=True):
    vb = vb or va

    def over(ctx, t, d):
        q = ease(clamp(t / (d * ease_frac)))
        V = view_at(va, vb, q)
        draw_base(ctx, V, borders)
        draw_elements(ctx, V, els, t, d)
        if borders and note:
            a = clamp(t / 0.8) * clamp((d - t) / 0.5)
            draw_text(ctx, "- - -  modern borders, for orientation only", W - 60, H - 60, 16, "#f6ecd6", "br", 0.75 * a,
                      shadow=0.8, font=EN_SANS)
    return dict(layers=[], over=over)
