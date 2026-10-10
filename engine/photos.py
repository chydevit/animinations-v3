"""Authentic images on screen. Images are never altered in content: only scaled, panned and framed.
  photo(file, ...)            Ken Burns over a photograph (blurred copy fills letterbox space)
  museum_card(file, card)     framed object photo + museum label (name km/en, date, holding institution, credit)
  zh_excerpt(zh, en, src_)    classical Chinese passage in vertical columns on silk paper, with translation
"""
import os

import cairocffi as cairo

from core import (EN_SANS, EN_SERIF, H, KM_SANS, ROOT, W, ZH_SERIF, clamp, draw_text, ease, load_image, overlay_texture,
                  paint_cover, rrect, smooth, src, text_surface)

ARCH = os.path.join(ROOT, "archive", "img")
_BLUR = {}


def _blurred(path):
    if path in _BLUR:
        return _BLUR[path]
    from PIL import Image, ImageFilter
    import numpy as np
    from core import np_to_surface
    im = Image.open(path).convert("RGB")
    im.thumbnail((480, 480))
    im = im.filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(im).astype(np.float32) / 255 * 0.45
    s = np_to_surface(np.dstack([a, np.ones(a.shape[:2], np.float32)]))
    _BLUR[path] = s
    return s


def _path(f):
    return f if os.path.isabs(f) else os.path.join(ARCH, f)


def photo(file, z=(1.0, 1.12), fx=(0.5, 0.5), fy=(0.5, 0.5), contain=None):
    p = _path(file)

    def over(ctx, t, d):
        s = load_image(p)
        iw, ih = s.get_width(), s.get_height()
        cont = contain if contain is not None else (iw / ih < 1.25 or iw / ih > 2.2 or iw < 1000)
        q = ease(clamp(t / d))
        zz = z[0] + (z[1] - z[0]) * q
        if cont:
            paint_cover(ctx, _blurred(p), 0, 0, W, H, 1.1)
            k = min(W * 0.9 / iw, H * 0.82 / ih, 2.2) * zz
            cx = W / 2 + (0.5 - (fx[0] + (fx[1] - fx[0]) * q)) * iw * k * 0.5
            cy = H / 2 - 20 + (0.5 - (fy[0] + (fy[1] - fy[0]) * q)) * ih * k * 0.5
            ctx.save()
            src(ctx, "#000000", 0.5)
            ctx.rectangle(cx - iw * k / 2 + 8, cy - ih * k / 2 + 10, iw * k, ih * k)
            ctx.fill()
            ctx.translate(cx - iw * k / 2, cy - ih * k / 2)
            ctx.scale(k, k)
            ctx.set_source_surface(s, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            ctx.paint()
            ctx.restore()
        else:
            paint_cover(ctx, s, 0, 0, W, H, zz, fx[0] + (fx[1] - fx[0]) * q, fy[0] + (fy[1] - fy[0]) * q)
    return dict(layers=[], over=over)


def museum_card(file, card, z=(1.0, 1.15), focus=(0.5, 0.5), side="r"):
    """card = dict(km, en, date, inst, credit, note). The object photo sits in a gold-edged frame on a dark
    textile wall; the label card slides in beside it."""
    p = _path(file)

    def over(ctx, t, d):
        s = load_image(p)
        iw, ih = s.get_width(), s.get_height()
        ctx.set_source_rgb(0.09, 0.06, 0.05)
        ctx.paint()
        overlay_texture(ctx, "weave", 0.22, 1.0, 3)
        from core import rad
        ctx.set_source(rad(W * 0.36, H * 0.45, 50, W * 0.7, [(0, "#4a2a1a", 0.55), (1, "#000000", 0)]))
        ctx.paint()
        q = ease(clamp(t / d))
        zz = z[0] + (z[1] - z[0]) * q
        bw, bh = W * 0.56, H * 0.78
        bx, by = (90 if side == "r" else W - 90 - bw), (H - bh) / 2 - 20
        k = min(bw / iw, bh / ih)
        fw, fh = iw * k, ih * k
        fx_, fy_ = bx + (bw - fw) / 2, by + (bh - fh) / 2
        src(ctx, "#000000", 0.5)
        ctx.rectangle(fx_ + 12, fy_ + 16, fw, fh)
        ctx.fill()
        src(ctx, "#d8aa4a")
        ctx.rectangle(fx_ - 10, fy_ - 10, fw + 20, fh + 20)
        ctx.fill()
        src(ctx, "#2a1a10")
        ctx.rectangle(fx_ - 4, fy_ - 4, fw + 8, fh + 8)
        ctx.fill()
        ctx.save()
        ctx.rectangle(fx_, fy_, fw, fh)
        ctx.clip()
        kk = k * zz
        ox = fx_ + fw / 2 - focus[0] * iw * kk + (focus[0] - 0.5) * 0 + (0.5 - 0.5) * 0
        oy = fy_ + fh / 2 - focus[1] * ih * kk
        ox = min(fx_, max(fx_ + fw - iw * kk, ox))
        oy = min(fy_, max(fy_ + fh - ih * kk, oy))
        ctx.translate(ox, oy)
        ctx.scale(kk, kk)
        ctx.set_source_surface(s, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint()
        ctx.restore()
        # label card
        a = smooth((t - 0.6) / 0.8) * clamp((d - t) / 0.6)
        lx = (bx + bw + 60) if side == "r" else 90
        lw = W - lx - 90 if side == "r" else bx - 150
        ly = H * 0.2
        slide = (1 - ease(clamp((t - 0.6) / 0.8))) * 40
        lx += slide
        src(ctx, "#000000", 0.35 * a)
        ctx.rectangle(lx + 8, ly + 10, lw, 560)
        ctx.fill()
        ctx.rectangle(lx, ly, lw, 560)
        src(ctx, "#efe2c6", 0.97 * a)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        overlay_texture(ctx, "palm", 0.7 * a, 1.0, 2)
        ctx.restore()
        src(ctx, "#7e3520", a)
        ctx.rectangle(lx, ly, lw, 8)
        ctx.fill()
        yy = ly + 30
        _, hh = draw_text(ctx, card.get("km", ""), lx + 28, yy, 32, "#1c1410", "tl", a, font=KM_SANS, weight="Bold",
                          width=lw - 56)
        yy += hh + 4
        _, hh = draw_text(ctx, card.get("en", ""), lx + 28, yy, 28, "#3a2414", "tl", a, font=EN_SERIF, weight="Bold",
                          width=lw - 56)
        yy += hh + 18
        for lab, key in (("DATE", "date"), ("HELD BY", "inst"), ("FOUND", "found")):
            if card.get(key):
                draw_text(ctx, lab, lx + 28, yy, 15, "#8a6a3c", "tl", a, font=EN_SANS, weight="Bold")
                _, hh = draw_text(ctx, card[key], lx + 28, yy + 20, 22, "#2a1a10", "tl", a, font=EN_SANS, width=lw - 56)
                yy += hh + 30
        if card.get("note"):
            _, hh = draw_text(ctx, card["note"], lx + 28, yy, 19, "#5a3a22", "tl", a, font=EN_SANS, italic=True,
                              width=lw - 56)
            yy += hh + 10
        if card.get("credit"):
            draw_text(ctx, card["credit"], lx + 28, ly + 548, 14, "#6a5a42", "bl", a, font=EN_SANS, width=lw - 56)
    return dict(layers=[], over=over)


def zh_excerpt(zh, en, source, km=None, highlight=None):
    """Classical Chinese in vertical columns (right to left) on silk paper; translation beside it."""
    def over(ctx, t, d):
        ctx.set_source_rgb(0.1, 0.07, 0.05)
        ctx.paint()
        overlay_texture(ctx, "weave", 0.2, 1.0, 5)
        a = smooth((t - 0.2) / 0.8) * clamp((d - t) / 0.6)
        px, py, pw, ph = 140, 110, 760, 800
        src(ctx, "#000000", 0.4 * a)
        ctx.rectangle(px + 10, py + 14, pw, ph)
        ctx.fill()
        ctx.rectangle(px, py, pw, ph)
        src(ctx, "#ead9b4", a)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        overlay_texture(ctx, "fibre", 0.5 * a, 1.0, 2)
        overlay_texture(ctx, "paper", 0.5 * a, 1.4, 3)
        ctx.restore()
        src(ctx, "#7e3520", 0.8 * a)
        ctx.set_line_width(3)
        ctx.rectangle(px + 24, py + 24, pw - 48, ph - 48)
        ctx.stroke()
        chars = [c for c in zh if not c.isspace()]
        per_col = 13
        cs = 50
        ncol = (len(chars) + per_col - 1) // per_col
        x_right = px + pw - 80
        shown = int(len(chars) * clamp((t - 0.6) / max(1.0, d * 0.45))) + 1
        for i, ch in enumerate(chars[:shown]):
            col, row = divmod(i, per_col)
            x = x_right - col * (cs + 16)
            y = py + 60 + row * (cs + 4)
            hl = highlight and ch in highlight
            draw_text(ctx, ch, x, y, cs, "#8a2a10" if hl else "#1c1410", "tc", a, font=ZH_SERIF, weight="Bold")
        # red seal
        src(ctx, "#a8261a", 0.85 * a)
        ctx.rectangle(px + 50, py + ph - 130, 70, 70)
        ctx.fill()
        draw_text(ctx, "史", px + 85, py + ph - 95, 44, "#ead9b4", "mc", a, font=ZH_SERIF, weight="Bold")
        b = smooth((t - 1.2) / 0.8) * clamp((d - t) / 0.6)
        tx = px + pw + 90
        tw = W - tx - 110
        yy = 170
        if km:
            _, hh = draw_text(ctx, km, tx, yy, 30, "#f6ecd6", "tl", b, font=KM_SANS, width=tw, shadow=0.5)
            yy += hh + 22
        _, hh = draw_text(ctx, "“" + en + "”", tx, yy, 34, "#f0e0c0", "tl", b, font=EN_SERIF, weight="SemiBold",
                          italic=True, width=tw, shadow=0.5)
        yy += hh + 26
        draw_text(ctx, "— " + source, tx, yy, 22, "#d8aa4a", "tl", b, font=EN_SANS, weight="Medium", width=tw)
    return dict(layers=[], over=over)
