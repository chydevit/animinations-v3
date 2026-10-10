"""Screen-space graphics: evidence badges, subtitles, title / chapter cards (paper-cut), claim boards (legend vs
record vs debate), timelines, text cards, credits."""
import math

import cairocffi as cairo

from core import (EN_SANS, EN_SERIF, H, KM_DISPLAY, KM_SANS, KM_SERIF, PAL, W, clamp, draw_text, ease, ellipse, lin,
                  mix, overlay_texture, poly, rad, rrect, smooth, src, text_surface)

GOLD = "#d8aa4a"
INK = "#1c1410"
PAPER = "#efe2c6"
LOTUS = "#f0a8b4"

BADGES = {
    "recon": ("#c58a3a", "គំនូរស្ថាបនាឡើងវិញ", "2D RECONSTRUCTION · artistic interpretation"),
    "legend": ("#a85a9a", "រឿងព្រេង", "LEGEND · not documented history"),
    "photo": ("#5d8fb0", "រូបថតពិត", "AUTHENTIC PHOTOGRAPH"),
    "artifact": ("#5d8fb0", "វត្ថុបុរាណពិត", "AUTHENTIC ARTEFACT · museum photograph"),
    "inscription": ("#5d8fb0", "សិលាចារឹកពិត", "AUTHENTIC INSCRIPTION"),
    "text": ("#a0763a", "ឯកសារចិន", "CHINESE DYNASTIC RECORD · translated"),
    "map": ("#6b9a6a", "ផែនទីសាមញ្ញ", "SIMPLIFIED MAP · approximate"),
    "map_recon": ("#6b9a6a", "ផែនទីស្ថាបនាឡើងវិញ", "RECONSTRUCTION MAP · extent approximate"),
    "satellite": ("#5d8fb0", "រូបភាពផ្កាយរណប", "SATELLITE / AERIAL IMAGE"),
    "comparison": ("#8a8a52", "ឧទាហរណ៍ប្រៀបធៀប", "COMPARISON · not from this place or period"),
    "schematic": ("#8a7aa8", "គំនូសបំព្រួញ", "SCHEMATIC · not to scale"),
    "guide": ("#c06a7a", "តួអង្គប្រឌិត", "FICTIONAL GUIDE · not a historical person"),
}

CLASS = {
    "record": ("#4f8a5a", "កត់ត្រាក្នុងឯកសារ", "WRITTEN RECORD"),
    "inscription": ("#3f7fb0", "សិលាចារឹក", "INSCRIPTION"),
    "archaeology": ("#3a9a9a", "បុរាណវិទ្យា", "ARCHAEOLOGY"),
    "legend": ("#a85a9a", "រឿងព្រេង", "LEGEND"),
    "debated": ("#b09a3a", "អ្នកប្រវត្តិវិទូមិនទាន់ឯកភាព", "DEBATED"),
    "hypothesis": ("#9a6ab0", "សម្មតិកម្ម", "HYPOTHESIS"),
}


def black(ctx):
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()


def draw_badge(ctx, kind, t, d, note=None):
    if kind not in BADGES:
        return
    col, km, en = BADGES[kind]
    a = clamp(t / 0.8) * clamp((d - t) / 0.5) * 0.92
    if a <= 0:
        return
    x, y = 44, 40
    s1 = text_surface(km, 21, "#ffffff", KM_SANS, "Bold")
    s2 = text_surface(en, 17, "#e8e3da", EN_SANS, "Medium")
    w = 16 + s1.get_width() + 12 + s2.get_width() + 16
    h = 40
    ctx.save()
    rrect(ctx, x, y, w, h, 7)
    src(ctx, "#140e0a", 0.6 * a)
    ctx.fill()
    rrect(ctx, x, y, 6, h, 3)
    src(ctx, col, a)
    ctx.fill()
    ctx.set_source_surface(s1, x + 16, y + (h - s1.get_height()) / 2)
    ctx.paint_with_alpha(a)
    ctx.set_source_surface(s2, x + 28 + s1.get_width(), y + (h - s2.get_height()) / 2 + 1)
    ctx.paint_with_alpha(a)
    if note:
        draw_text(ctx, note, x + 4, y + h + 8, 16, "#f2eee6", "tl", a * 0.9, shadow=0.8, font=EN_SANS, width=1500)
    ctx.restore()


def draw_subtitle(ctx, cue, t):
    a = clamp((t - cue["start"]) / 0.12) * clamp((cue["end"] - t) / 0.12)
    guide = cue.get("who", "nar") != "nar"
    txt = cue["en"]
    s = text_surface(txt, 40, LOTUS if guide else "#ffffff", EN_SANS, "Medium", width=1500, align="center",
                     italic=guide)
    w, h = s.get_width(), s.get_height()
    x, y = (W - w) / 2, H - 70 - h + (1 - a) * 6
    ctx.save()
    rrect(ctx, x - 18, y - 6, w + 36, h + 12, 10)
    src(ctx, "#000000", 0.45 * a)
    ctx.fill()
    if guide:
        rrect(ctx, x - 18, y - 6, 6, h + 12, 3)
        src(ctx, LOTUS, a)
        ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.7 * a)
    ctx.mask_surface(s, x + 2, y + 2)
    ctx.set_source_surface(s, x, y)
    ctx.paint_with_alpha(a)
    ctx.restore()


def bg_paper(ctx, t, tone="#2a1a10"):
    ctx.set_source(rad(W / 2, H * 0.45, 100, W * 0.8, [(0, mix(tone, "#7e3520", 0.35)), (1, tone)]))
    ctx.paint()
    overlay_texture(ctx, "fibre", 0.35, 1.0, 2)
    overlay_texture(ctx, "paper", 0.5, 1.6, 7)


def lotus_ornament(ctx, x, y, s, a=1.0, open_=1.0, col=GOLD):
    """Unfolding lotus emblem (title and chapter cards)."""
    n = 8
    for ring, (rk, ck) in enumerate(((1.0, 0.0), (0.72, 0.25))):
        for k in range(n):
            ang = -math.pi / 2 + (k - (n - 1) / 2) * 0.36 * open_ * rk
            L = s * rk * (0.8 + 0.2 * (1 - abs(k - 3.5) / 3.5))
            tx, ty = x + math.cos(ang) * L, y + math.sin(ang) * L
            ctx.new_path()
            ctx.move_to(x, y)
            ctx.curve_to(x + math.cos(ang - 0.5) * L * 0.6, y + math.sin(ang - 0.5) * L * 0.6, tx, ty, tx, ty)
            ctx.curve_to(tx, ty, x + math.cos(ang + 0.5) * L * 0.6, y + math.sin(ang + 0.5) * L * 0.6, x, y)
            src(ctx, mix(col, "#fff0d0", ck), a * 0.9)
            ctx.fill()
    src(ctx, col, a)
    ctx.new_path()
    ctx.rectangle(x - s * 1.4, y + 4, s * 2.8, 3)
    ctx.fill()


def title_card(km, en, sub_km=None, sub_en=None, under=None):
    def over(ctx, t, d):
        if under is None:
            bg_paper(ctx, t)
        else:
            src(ctx, "#000000", 0.5)
            ctx.paint()
        a = smooth((t - 0.6) / 1.6) * clamp((d - t) / 1.0)
        lotus_ornament(ctx, W / 2, H * 0.27, 70, a, ease(clamp((t - 0.2) / 2.0)))
        rise = (1 - ease(clamp((t - 0.6) / 2.0))) * 20
        draw_text(ctx, km, W / 2, H * 0.42 + rise, 90, "#f2cf7a", "mc", a, shadow=0.7, font=KM_DISPLAY)
        b = smooth((t - 1.6) / 1.4) * clamp((d - t) / 1.0)
        draw_text(ctx, en, W / 2, H * 0.42 + 120, 60, "#f6ecd6", "mc", b, shadow=0.6, font=EN_SERIF, weight="SemiBold")
        if sub_km:
            c = smooth((t - 2.6) / 1.4) * clamp((d - t) / 1.0)
            draw_text(ctx, sub_km, W / 2, H * 0.42 + 210, 34, "#e7dcc4", "mc", c, font=KM_SERIF, shadow=0.6)
            draw_text(ctx, sub_en, W / 2, H * 0.42 + 262, 28, "#d8c8a8", "mc", c, font=EN_SERIF, italic=True, shadow=0.6)
    sc = dict(under or dict(layers=[]))
    base = sc.get("over")

    def over2(ctx, t, d):
        if base:
            base(ctx, t, d)
        over(ctx, t, d)
    sc["over"] = over2
    return sc


def _roman(n):
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def chapter_card(num, km, en, years=None, under=None):
    def over(ctx, t, d):
        if under is None:
            bg_paper(ctx, t)
        else:
            src(ctx, "#140c08", 0.66 * clamp(t / 0.6))
            ctx.paint()
        a = smooth((t - 0.3) / 1.0) * clamp((d - t) / 0.8)
        lotus_ornament(ctx, W / 2, H * 0.3, 44, a, ease(clamp((t - 0.1) / 1.5)))
        if num:
            draw_text(ctx, "ជំពូកទី %s · CHAPTER %s" % (num, _roman(num)), W / 2, H * 0.36, 28, GOLD, "mc", a,
                      shadow=0.7, font=KM_SANS, weight="Bold")
        b = smooth((t - 0.8) / 1.2) * clamp((d - t) / 0.8)
        draw_text(ctx, km, W / 2, H * 0.50, 66, "#fbf3e2", "mc", b, shadow=0.8, font=KM_DISPLAY)
        draw_text(ctx, en, W / 2, H * 0.50 + 96, 48, "#f0e6d0", "mc", b, shadow=0.8, font=EN_SERIF, weight="SemiBold")
        if years:
            draw_text(ctx, years, W / 2, H * 0.50 + 162, 30, GOLD, "mc", b, shadow=0.8, font=EN_SERIF, italic=True)
    sc = dict(under or dict(layers=[]))
    base = sc.get("over")

    def over2(ctx, t, d):
        if base:
            base(ctx, t, d)
        over(ctx, t, d)
    sc["over"] = over2
    return sc


def class_tag(ctx, x, y, kind, a=1.0, size=22):
    col, km, en = CLASS[kind]
    s1 = text_surface(km, size, "#ffffff", KM_SANS, "Bold")
    s2 = text_surface(en, int(size * 0.75), "#ffffff", EN_SANS, "Bold")
    w = s1.get_width() + s2.get_width() + 46
    h = max(s1.get_height(), s2.get_height()) + 8
    rrect(ctx, x, y, w, h, h / 2)
    src(ctx, col, 0.92 * a)
    ctx.fill()
    ctx.set_source_surface(s1, x + 16, y + (h - s1.get_height()) / 2)
    ctx.paint_with_alpha(a)
    ctx.set_source_surface(s2, x + 30 + s1.get_width(), y + (h - s2.get_height()) / 2)
    ctx.paint_with_alpha(a)
    return w, h


def _wrap(under, over):
    sc = dict(under or dict(layers=[]))
    base = sc.get("over")

    def over2(ctx, t, d):
        if base:
            base(ctx, t, d)
        over(ctx, t, d)
    sc["over"] = over2
    return sc


def claim_board(title_km, title_en, items, under=None):
    """items: [(class_kind, km_text, en_text)] laid out as paper cards."""
    def over(ctx, t, d):
        if under is None:
            bg_paper(ctx, t)
        else:
            src(ctx, "#000000", 0.55)
            ctx.paint()
        a = smooth(t / 0.8) * clamp((d - t) / 0.6)
        draw_text(ctx, title_km, W / 2, 110, 46, "#ffffff", "mc", a, font=KM_SANS, weight="Bold", shadow=0.6)
        draw_text(ctx, title_en, W / 2, 168, 30, "#e5dccb", "mc", a, font=EN_SERIF, weight="SemiBold", shadow=0.6)
        n = len(items)
        cw = min(560, (W - 200 - (n - 1) * 40) / n)
        x0 = (W - (n * cw + (n - 1) * 40)) / 2
        for i, (kind, km, en) in enumerate(items):
            ia = a * smooth((t - 0.8 - i * 0.9) / 0.7)
            if ia <= 0:
                continue
            x, y = x0 + i * (cw + 40), 240
            src(ctx, "#000000", 0.3 * ia)
            ctx.rectangle(x + 10, y + 12, cw, 560)
            ctx.fill()
            ctx.rectangle(x, y, cw, 560)
            src(ctx, PAPER, 0.96 * ia)
            ctx.fill_preserve()
            ctx.save()
            ctx.clip()
            overlay_texture(ctx, "palm", 0.6 * ia, 1.0, i)
            ctx.restore()
            src(ctx, CLASS[kind][0], ia)
            ctx.rectangle(x, y, cw, 10)
            ctx.fill()
            class_tag(ctx, x + 20, y + 30, kind, ia, 21)
            _, kh = draw_text(ctx, km, x + 24, y + 94, 30, INK, "tl", ia, font=KM_SANS, width=cw - 48)
            draw_text(ctx, en, x + 24, y + 112 + kh, 25, "#4a3a2a", "tl", ia, font=EN_SANS, width=cw - 48, italic=True)
    return _wrap(under, over)


def timeline_card(title_km, title_en, events, focus=None, under=None):
    """events: [(label, km, en)]; a cursor sweeps along a palm-leaf strip."""
    def over(ctx, t, d):
        if under is None:
            bg_paper(ctx, t)
        a = smooth(t / 0.8) * clamp((d - t) / 0.6)
        draw_text(ctx, title_km, W / 2, 96, 44, "#f6ecd6", "mc", a, font=KM_SANS, weight="Bold", shadow=0.6)
        draw_text(ctx, title_en, W / 2, 150, 28, "#e0d0b0", "mc", a, font=EN_SERIF, weight="SemiBold", italic=True)
        n = len(events)
        x0, x1, y = 170, W - 170, 520
        ctx.rectangle(x0 - 40, y - 24, x1 - x0 + 80, 48)
        src(ctx, "#d9c39a", a)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        overlay_texture(ctx, "palm", 0.8 * a, 1.0, 1)
        ctx.restore()
        prog = ease(clamp((t - 0.5) / max(1.0, d * 0.6)))
        src(ctx, "#7e3520", 0.9 * a)
        ctx.rectangle(x0, y - 4, (x1 - x0) * prog, 8)
        ctx.fill()
        for i, (yr, km, en) in enumerate(events):
            x = x0 + (x1 - x0) * (i / max(1, n - 1))
            ia = a * smooth((prog * (n - 1) - i + 0.6) / 0.6) if n > 1 else a
            if ia <= 0:
                continue
            hl = focus is not None and i == focus
            src(ctx, "#b5562f" if hl else "#5a3a22", ia)
            ctx.new_path()
            ctx.arc(x, y, 15 if hl else 11, 0, 6.283)
            ctx.fill()
            up = (i % 2 == 0)
            ty = y - 60 if up else y + 50
            draw_text(ctx, yr, x, ty, 40 if hl else 34, GOLD if hl else "#f2e2c0", "bc" if up else "tc", ia,
                      font=EN_SERIF, weight="Bold", shadow=0.5)
            draw_text(ctx, km, x, (ty - 58) if up else (ty + 56), 26, "#fbf3e2", "bc" if up else "tc", ia, font=KM_SANS,
                      width=310, align="center", shadow=0.5)
            draw_text(ctx, en, x, (ty - 140) if up else (ty + 140), 21, "#e0d0b0", "bc" if up else "tc", ia,
                      font=EN_SANS, width=300, align="center", italic=True, shadow=0.5)
    return _wrap(under, over)


def text_card(lines, under=None):
    """lines = [(text, size, color, font, weight)] centred over a darkened scene or paper."""
    def over(ctx, t, d):
        if under is None:
            bg_paper(ctx, t)
        else:
            src(ctx, "#000000", 0.5 * clamp(t / 0.8))
            ctx.paint()
        a = smooth((t - 0.3) / 1.0) * clamp((d - t) / 0.8)
        tot = sum(l[1] * 1.6 for l in lines)
        y = H / 2 - tot / 2
        for i, (txt, size, col, font, weight) in enumerate(lines):
            la = a * smooth((t - 0.3 - i * 0.35) / 0.8)
            draw_text(ctx, txt, W / 2, y, size, col, "tc", la, font=font, weight=weight, width=1600, align="center",
                      shadow=0.5)
            y += size * 1.6
    return _wrap(under, over)


def lower_third(km, en, under):
    def over(ctx, t, d):
        a = smooth((t - 0.6) / 0.6) * clamp((d - t) / 0.6)
        if a <= 0:
            return
        x, y = 90, H - 300
        s1 = text_surface(km, 34, "#ffffff", KM_SANS, "Bold")
        s2 = text_surface(en, 24, "#f0e0c0", EN_SERIF, "SemiBold")
        w = max(s1.get_width(), s2.get_width()) + 40
        src(ctx, "#140c08", 0.6 * a)
        ctx.rectangle(x, y, w, s1.get_height() + s2.get_height() + 24)
        ctx.fill()
        src(ctx, GOLD, a)
        ctx.rectangle(x, y, 6, s1.get_height() + s2.get_height() + 24)
        ctx.fill()
        ctx.set_source_surface(s1, x + 22, y + 8)
        ctx.paint_with_alpha(a)
        ctx.set_source_surface(s2, x + 22, y + 12 + s1.get_height())
        ctx.paint_with_alpha(a)
    return _wrap(under, over)


def scrolling_credits(blocks):
    def over(ctx, t, d):
        bg_paper(ctx, t, "#140c08")
        surfs = []
        for head, lines in blocks:
            surfs.append((text_surface(head, 30, GOLD, EN_SANS, "Bold", width=1500, align="center"), 18))
            for ln in lines:
                f = KM_SANS if any(0x1780 <= ord(c) <= 0x17FF for c in ln) else EN_SANS
                surfs.append((text_surface(ln, 22, "#e9e2d4", f, "", width=1500, align="center"), 4))
            surfs.append((None, 40))
        total = sum((s.get_height() if s else 0) + g for s, g in surfs)
        y = H - (H + total) * clamp(t / d) + 40
        for s, g in surfs:
            if s:
                if -100 < y < H + 50:
                    a = clamp(min((y + 60) / 200, (H - y) / 200))
                    ctx.set_source_surface(s, (W - s.get_width()) / 2, y)
                    ctx.paint_with_alpha(a)
                y += s.get_height()
            y += g
    return dict(layers=[], over=over)
