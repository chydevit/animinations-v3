"""Paper-cut reconstruction sets (built for 'Funan'; add new make_* builders per film). Every make_* returns a scene dict for film.draw_scene.
All are artistic reconstructions (badged as such by the shot list)."""
import hashlib
import math

import numpy as np

import cast
import paper as PP
from core import (SH, SW, PAL, clamp, ellipse, glow, hexc, lin, mix, overlay_texture, poly, rad, rng, smooth, spline,
                  src)
from paper import TOD, sheet, path_poly, path_ellipse, jag

V = "f2"


def _key(name, **kw):
    return name + "_" + hashlib.sha1((V + repr(sorted(kw.items()))).encode()).hexdigest()[:10]


def _comb(*fns):
    def dyn(ctx, t, d, depth):
        for f in fns:
            if f:
                f(ctx, t, d, depth)
    return dyn


def F(x, y, h, who, pose="idle", yaw=90, seed=0, **kw):
    d = dict(x=x, y=y, h=h, who=who, pose=pose, yaw=yaw, seed=seed)
    d.update(kw)
    return d


def grp(depth, *items):
    return dict(depth=depth, items=list(items))


def people_dyn(groups, P, mouth_fn=None):
    """groups: [dict(depth, items=[F(...)])]. Items may carry vx, vy (px/s), boat=True (drawn standing in a boat),
    talk=True (mouth driven by mouth_fn(t) = guide's voice envelope)."""
    def dyn(ctx, t, d, depth):
        for g in groups:
            if g["depth"] != depth:
                continue
            its = [dict(it, x=it["x"] + it.get("vx", 0) * t, y=it["y"] + it.get("vy", 0) * t) for it in g["items"]]
            for it in sorted(its, key=lambda q: q["y"]):
                bob = math.sin(t * 1.3 + it.get("seed", 0)) * it["h"] * 0.008 if it.get("boat") else 0
                if it.get("boat"):
                    PP.boat(ctx, P, it["x"], it["y"] + bob + it["h"] * 0.03, it["h"] * 1.5, it.get("seed", 0),
                            load=it.get("load", True), f=1 if it.get("yaw", 90) >= 0 else -1)
                m = mouth_fn(t) if (it.get("talk") and mouth_fn) else None
                cast.draw(ctx, it["x"], it["y"] + bob, it["h"], it["who"], it.get("pose", "idle"),
                          t + it.get("seed", 0) * 0.37, it.get("yaw", 90), it.get("expr"), P, seed=it.get("seed", 0),
                          hz=it.get("hz", 0.0), mouth=m, silhouette=it.get("sil"), outline=not it.get("sil"),
                          perforate=it.get("perforate", False), cutout=not it.get("sil"))
    return dyn


# ================================================================ 1. MEKONG DELTA AT DAWN (opening, closing)
def make_delta(tod="dawn", people=None, mouth_fn=None, sun=(0.62, 0.5), lotus_n=6, mist_a=0.45, boats=True):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.6, sun, 70, 8, 3)
        PP.clouds(ctx, P, 5, (0.08, 0.32), 4)

    def far(ctx):
        PP.ridge(ctx, P, 790, 60, mix(P["far"], P["haze"], 0.35), 5, peaks=[(1650, 170, 160), (1820, 90, 120)])
        for i, x in enumerate(range(60, SW, 150)):
            PP.palm(ctx, P, x + (i % 3) * 30, 810, 120 + (i % 4) * 25, "sugar" if i % 3 else "coconut", 10 + i,
                    mix(P["far"], P["mid"], 0.4))

    def mid(ctx):
        PP.water(ctx, P, 800, SH + 40, 6)
        for i, x in enumerate((180, 520, 940, 1500, 2050, 2300)):
            PP.palm(ctx, P, x, 880 + (i % 2) * 20, 70, "nipa", 30 + i, mix(P["mid"], P["near"], 0.3))

    def near(ctx):
        R = rng(7)
        for i in range(lotus_n):
            PP.lotus(ctx, P, 120 + i * 420 + R.random() * 120, 1240 + R.random() * 60, 70 + R.random() * 30,
                     0.6 + 0.4 * R.random(), 50 + i)
        PP.palm(ctx, P, 60, SH + 40, 900, "coconut", 61, P["near"])
        PP.palm(ctx, P, SW - 80, SH + 60, 980, "coconut", 62, P["near"])

    layers = [(_key("dl_sky", tod=tod, s=sun), sky_, 0.0), (_key("dl_far", tod=tod), far, 0.3),
              (_key("dl_mid", tod=tod), mid, 0.6), (_key("dl_near", tod=tod, n=lotus_n), near, 1.0)]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            _mist(ctx, t, 800, 120, P["haze"], mist_a, 2, 8)
            _birds(ctx, t, 500, 380, 7, P["shadow"])
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 820, SH, 3, 16, 60)
            if boats:
                PP.boat(ctx, P, (300 + t * 22) % (SW + 400) - 200, 960, 220, 3)
        if depth == 1.0:
            _mist(ctx, t, 1150, 80, P["haze"], mist_a * 0.5, 5, 12)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6, 1.0])


def _mist(ctx, t, y, h, color, a, seed, speed):
    R = rng(seed)
    for i in range(8):
        cx = (R.random() * SW * 1.4 + t * speed * (0.6 + R.random())) % (SW * 1.4) - SW * 0.2
        cy = y + (R.random() - 0.5) * h
        rx, ry = SW * (0.15 + 0.2 * R.random()), h * (0.3 + 0.3 * R.random())
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(rx, ry)
        ctx.set_source(rad(0, 0, 0, 1, [(0, color, a), (1, color, 0)]))
        ctx.arc(0, 0, 1, 0, 6.283)
        ctx.fill()
        ctx.restore()


def _birds(ctx, t, x0, y0, n, color, speed=30):
    R = rng(3)
    for i in range(n):
        x = x0 + R.random() * 300 + t * speed * (0.9 + 0.2 * R.random())
        y = y0 + R.random() * 80 + math.sin(t * 0.8 + i) * 6
        fl = math.sin(t * 7 + i)
        s = 8
        src(ctx, color, 0.8)
        ctx.set_line_width(2)
        ctx.move_to(x - s, y - fl * s * 0.5)
        ctx.curve_to(x - s * 0.5, y - s * 0.3, x - s * 0.2, y, x, y)
        ctx.curve_to(x + s * 0.2, y, x + s * 0.5, y - s * 0.3, x + s, y - fl * s * 0.5)
        ctx.stroke()


# ================================================================ 2. BEFORE FUNAN: delta village, rice and flood
def make_lowland(tod="day", flood=0.0, people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.55, (0.25, 0.3), 60, 7, 8)
        PP.clouds(ctx, P, 6, (0.06, 0.3), 9)

    def far(ctx):
        PP.ridge(ctx, P, 720, 40, mix(P["far"], P["haze"], 0.3), 11)
        for i, x in enumerate(range(40, SW, 210)):
            PP.palm(ctx, P, x, 740, 140 + (i % 3) * 30, "sugar", 70 + i, mix(P["far"], P["mid"], 0.5))

    def fields(ctx):
        y0 = 760
        for r_ in range(7):   # paddies as paper strips separated by bunds
            yy = y0 + r_ * 60 * (1 + r_ * 0.25)
            colr = mix("#7a9a4a", "#c8b46a", (r_ % 3) * 0.25)
            pts = jag([(-30, yy), (SW + 30, yy + 10 * math.sin(r_))], 2, r_, 50)
            sheet(ctx, path_poly(pts + [(SW + 30, SH + 30), (-30, SH + 30)]), colr, shadow=0.5, seed=r_, edge=True)
            src(ctx, mix(colr, "#2a4a1a", 0.4), 0.6)
            R = rng(r_)
            for k in range(int(40 + r_ * 12)):
                x = R.random() * SW
                ctx.set_line_width(1.5 + r_ * 0.4)
                ctx.move_to(x, yy + 12 + r_ * 4)
                ctx.line_to(x - 3, yy - 2 - r_ * 2)
                ctx.move_to(x, yy + 12 + r_ * 4)
                ctx.line_to(x + 4, yy - r_ * 2)
                ctx.stroke()
        for k, (x, s) in enumerate(((420, 150), (700, 120), (1880, 160))):
            PP.stilt_house(ctx, P, x, 860 + k * 10, s, 80 + k)

    layers = [(_key("lw_sky", tod=tod), sky_, 0.0), (_key("lw_far", tod=tod), far, 0.3),
              (_key("lw_f", tod=tod), fields, 0.65)]

    def fx(ctx, t, d, depth):
        if depth == 0.65 and flood > 0:
            lvl = 1300 - flood * smooth(t / max(d, 1)) * 480
            ctx.rectangle(0, lvl, SW, SH - lvl)
            ctx.set_source(lin(0, lvl, 0, SH, [(0, P["water"], 0.85), (1, mix(P["water"], P["shadow"], 0.3), 0.92)]))
            ctx.fill()
            PP.water_fx(ctx, t, P, lvl, SH, 9, 14, 40)
        if depth == 0.0:
            _birds(ctx, t, 300, 300, 6, P["shadow"])
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.65])


# ================================================================ 3. SHADOW-PUPPET SCREEN (legend chapter)
def make_puppet(figures, title=None, fire=True, mouth_fn=None):
    """Sbek-style performance: a glowing cloth screen; leather puppets in silhouette with punched patterns.
    figures: list of dict(kind='person'|'ship'|'naga'|'tree'|'arrow'|'palace', x, y, s, ...)."""
    P = TOD["lamp"]

    def screen(ctx):
        ctx.set_source_rgb(*hexc("#120a06"))
        ctx.paint()
        ctx.set_source(rad(SW / 2, SH * 0.55, 100, SW * 0.6, [(0, "#f6d8a0"), (0.55, "#d89a52"), (1, "#5a3018")]))
        ctx.rectangle(110, 70, SW - 220, SH - 230)
        ctx.fill()
        ctx.save()
        ctx.rectangle(110, 70, SW - 220, SH - 230)
        ctx.clip()
        overlay_texture(ctx, "weave", 0.25, 1.0, 3)
        overlay_texture(ctx, "paper", 0.3, 1.5, 4)
        ctx.restore()
        src(ctx, "#2a1608")   # frame posts
        for x in (90, SW - 130):
            ctx.rectangle(x, 40, 40, SH)
            ctx.fill()
        ctx.rectangle(60, 50, SW - 120, 30)
        ctx.fill()
        ctx.rectangle(60, SH - 170, SW - 120, 30)
        ctx.fill()

    layers = [(_key("pp_screen"), screen, 0.5)]
    ink = "#1a0e08"

    def dyn(ctx, t, d, depth):
        if depth != 0.5:
            return
        flick = 0.92 + 0.08 * math.sin(t * 13) * math.sin(t * 7.3)
        ctx.save()
        ctx.rectangle(110, 70, SW - 220, SH - 230)
        ctx.clip()
        for f_ in figures:
            k = f_["kind"]
            at = f_.get("at", 0.0)
            a = smooth((t - at) / 0.8) * (1 - smooth((t - f_.get("until", 1e9)) / 0.8))
            if a <= 0:
                continue
            x = f_["x"] + f_.get("vx", 0) * max(0, t - at)
            y = f_["y"] + math.sin(t * 1.4 + f_.get("seed", 0)) * 6   # puppets sway on their rods
            ctx.push_group()
            if k == "person":
                cast.draw(ctx, x, y, f_["s"], f_["who"], f_.get("pose", "idle"), t, f_.get("yaw", 90),
                          silhouette=ink, outline=False, cutout=False, perforate=True, seed=f_.get("seed", 0))
            elif k == "ship":
                PP.ship(ctx, P, x, y, f_["s"], "funan", f_.get("seed", 0), t, f_.get("f", 1))
            elif k == "naga":
                _naga(ctx, x, y, f_["s"], t)
            elif k == "tree":
                PP.palm(ctx, P, x, y, f_["s"], "coconut", f_.get("seed", 0), ink)
            elif k == "arrow":
                p = clamp((t - at) / f_.get("fly", 1.2))
                ax = f_["x"] + (f_["x2"] - f_["x"]) * p
                ay = f_["y"] + (f_["y2"] - f_["y"]) * p - math.sin(p * math.pi) * 80
                ctx.set_line_width(6)
                src(ctx, ink)
                ctx.move_to(ax - 70, ay + 6)
                ctx.line_to(ax, ay)
                ctx.stroke()
                poly(ctx, [(ax + 18, ay - 1), (ax - 4, ay - 10), (ax - 4, ay + 9)])
                ctx.fill()
            elif k == "waves":
                for i in range(7):
                    wx = x + i * 160 + math.sin(t + i) * 20
                    ctx.new_path()
                    ctx.arc(wx, y, 70, math.pi, 2 * math.pi)
                    ctx.set_line_width(10)
                    src(ctx, ink)
                    ctx.stroke()
            elif k == "palace":
                PP.brick_shrine(ctx, P, x, y, f_["s"], 3)
            pat = ctx.pop_group()
            # silhouette everything in leather-dark ink (the group's alpha is the puppet's shape)
            src(ctx, ink, a)
            ctx.mask(pat)
        ctx.restore()
        # lamp flicker and the dalang's glow
        src(ctx, "#ffb040", 0.06 * (1 - flick) * 6)
        ctx.paint()
        if fire:
            glow(ctx, SW / 2, SH - 60, 380, "#ff9a40", 0.35 * flick)

    def over(ctx, t, d):
        if title:
            from core import draw_text, KM_SANS, EN_SERIF, W
            a = smooth((t - 0.5) / 0.8) * clamp((d - t) / 0.6)
            draw_text(ctx, title[0], W / 2, 70, 34, "#f6d8a0", "mc", a, shadow=0.8, font=KM_SANS, weight="Bold")
            draw_text(ctx, title[1], W / 2, 112, 24, "#e8c890", "mc", a, shadow=0.8, font=EN_SERIF, weight="SemiBold")
    return dict(layers=layers, dyn=dyn, dyn_depths=[0.5], over=over)


def _naga(ctx, x, y, s, t):
    """Seven-headed naga silhouette (for the Khmer Preah Thong - Neang Neak story)."""
    src(ctx, "#1a0e08")
    ctx.set_line_width(s * 0.12)
    ctx.set_line_cap(1)
    ctx.move_to(x - s * 2.2, y + s * 0.4)
    for k in range(24):
        u = k / 23
        ctx.line_to(x - s * 2.2 + u * s * 2.2, y + s * 0.4 + math.sin(u * 9 + t * 1.5) * s * 0.18)
    ctx.stroke()
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.28
        hx, hy = x + math.cos(a) * s * 0.9, y - s * 0.2 + math.sin(a) * s * 0.9
        ctx.set_line_width(s * 0.1)
        ctx.move_to(x, y + s * 0.2)
        ctx.line_to(hx, hy)
        ctx.stroke()
        ellipse(ctx, hx, hy, s * 0.14, s * 0.1, a + 1.57)
        ctx.fill()


# ================================================================ 4. OC EO PORT
def make_port(tod="day", people=None, mouth_fn=None, ships=True):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.5, (0.8, 0.22), 60, 7, 12)
        PP.clouds(ctx, P, 6, (0.05, 0.3), 13)

    def far(ctx):
        PP.ridge(ctx, P, 660, 30, mix(P["far"], P["haze"], 0.4), 14, peaks=[(600, 200, 170)])   # Ba The hill
        PP.water(ctx, P, 660, 900, 15, mix(P["water"], P["haze"], 0.3), 3)

    def town(ctx):
        # palisade and houses on piles along the waterfront
        for k in range(10):
            PP.stilt_house(ctx, P, 140 + k * 235, 820 + (k % 2) * 16, 105 + (k % 3) * 12, 100 + k,
                           roof=["#b08a4a", "#a8783a", "#c09a5a"][k % 3])
        PP.brick_shrine(ctx, P, 1900, 760, 160, 120)
        PP.water(ctx, P, 860, SH + 40, 16, P["water"], 4)
        # wooden jetty
        for k in range(12):
            x = 700 + k * 70
            sheet(ctx, path_poly([(x, 880), (x + 10, 880), (x + 10, 990), (x, 990)]), "#4a3220", shadow=0.4,
                  seed=k, edge=False, texture=False)
        sheet(ctx, path_poly([(680, 872), (1520, 872), (1520, 892), (680, 892)]), "#7a5a36", shadow=0.8, seed=3)
        # goods on the jetty
        for k in range(7):
            x = 760 + k * 105
            if k % 2:
                cast.pot(ctx, x, 872, 34, ["#a8744a", "#8a5a3a"][k % 2], P)
            else:
                sheet(ctx, path_poly([(x - 26, 872), (x + 26, 872), (x + 22, 836), (x - 22, 836)]), "#9a7a4a",
                      shadow=0.4, seed=k, edge=False)

    layers = [(_key("po_sky", tod=tod), sky_, 0.0), (_key("po_far", tod=tod), far, 0.3),
              (_key("po_town", tod=tod), town, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.3:
            _birds(ctx, t, 900, 300, 6, P["shadow"])
            if ships:
                PP.ship(ctx, P, 1700 - t * 10, 760, 380, "sail", 2, t, -1)
        if depth == 0.6:
            PP.water_fx(ctx, t, P, 900, SH, 5, 18, 50)
            if ships:
                PP.ship(ctx, P, 420 + t * 14, 1080, 720, "sail", 1, t)
                PP.ship(ctx, P, 1800 - t * 8, 1180, 640, "funan", 4, t, -1)
                PP.boat(ctx, P, (2200 - t * 40) % (SW + 400) - 200, 1290, 260, 6)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.3, 0.6, 1.0])


# ================================================================ 5. OPEN SEA (fleets, embassies)
def make_sea(tod="golden", fleet="funan", n=5, people=None, mouth_fn=None):
    P = TOD[tod]

    def sky_(ctx):
        PP.sky(ctx, P, 0.5, (0.7, 0.42), 80, 8, 20)
        PP.clouds(ctx, P, 7, (0.05, 0.38), 21)

    def sea(ctx):
        PP.water(ctx, P, SH * 0.5, SH + 40, 22, P["water"], 6)

    layers = [(_key("se_sky", tod=tod), sky_, 0.0), (_key("se_sea", tod=tod), sea, 0.4)]

    def fx(ctx, t, d, depth):
        if depth == 0.4:
            PP.water_fx(ctx, t, P, SH * 0.5, SH, 7, 30, 70)
            R = rng(9)
            for i in range(n):
                k = i / max(1, n - 1)
                L = 220 + k * 520
                x = (300 + i * 420 + R.random() * 200 + t * (16 + 10 * k)) % (SW + 600) - 300
                y = SH * 0.55 + k * 520
                PP.ship(ctx, P, x, y, L, fleet if fleet != "mixed" else ("funan" if i % 2 else "sail"), i, t)
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.0, 0.4])


# ================================================================ 6. PALACE / RECEPTION (Chinese envoys)
def make_palace(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.2, 0.3), 60, 7, 30)
        PP.ridge(ctx, P, 700, 40, mix(P["far"], P["haze"], 0.3), 31)
        # walled city: a wooden palisade on an earthen bank (Chinese records mention walled cities)
        sheet(ctx, path_poly(jag([(-30, 760), (SW + 30, 760)], 3, 32) + [(SW + 30, 860), (-30, 860)]), "#8a6a3c",
              shadow=0.8, seed=32)
        for k in range(70):
            x = k * 36
            sheet(ctx, path_poly([(x, 760), (x + 14, 690), (x + 28, 760)]), "#6a4a2a", shadow=0.4, seed=k,
                  edge=False, texture=False)

    def hall(ctx):
        # raised timber hall with a tiered roof
        sheet(ctx, path_poly([(500, 980), (1900, 980), (1900, 1010), (500, 1010)]), "#5a3a22", shadow=1.0, seed=40)
        for k in range(9):
            x = 560 + k * 165
            sheet(ctx, path_poly([(x, 980), (x + 26, 980), (x + 26, 560), (x, 560)]), "#7e3520", shadow=0.6, seed=41 + k)
        for k in range(3):
            w = 860 - k * 200
            y = 560 - k * 120
            sheet(ctx, path_poly(jag([(1200 - w, y), (1200 - w * 0.55, y - 140), (1200 + w * 0.55, y - 140),
                                      (1200 + w, y)], 3, 50 + k, 30)), ["#b08a4a", "#a8783a", "#c09a5a"][k], shadow=1.0,
                  seed=50 + k)
            PP.punch(ctx, path_poly([(1200 - w * 0.9, y - 10), (1200 + w * 0.9, y - 10), (1200 + w * 0.5, y - 120),
                                     (1200 - w * 0.5, y - 120)]), "lozenge", 60 + k, "#f6d8a0", 0.25, 7, 46)
        sheet(ctx, path_poly([(400, 1010), (2000, 1010), (2100, SH + 30), (300, SH + 30)]), "#c8a878", shadow=0.6,
              seed=70)
        overlay_texture(ctx, "weave", 0.0, 1.0, 1)

    layers = [(_key("pa_bg", tod=tod), bg, 0.2), (_key("pa_hall", tod=tod), hall, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.2, 0.6])


# ================================================================ 7. TEMPLE / INSCRIPTION (Indian ideas)
def make_temple(tod="golden", people=None, mouth_fn=None, stele=True):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.75, 0.35), 70, 7, 80)
        PP.ridge(ctx, P, 760, 60, mix(P["far"], P["haze"], 0.3), 81, peaks=[(500, 150, 200)])
        for i, x in enumerate((150, 380, 2100, 2300)):
            PP.palm(ctx, P, x, 860, 420 + (i % 2) * 80, "sugar", 82 + i, mix(P["mid"], P["near"], 0.5))

    def site(ctx):
        sheet(ctx, path_poly(jag([(-30, 900), (SW + 30, 900)], 3, 85) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#b8945a", shadow=0.6, seed=85)
        PP.brick_shrine(ctx, P, 1200, 900, 520, 86)
        if stele:   # inscribed stone stele before the sanctuary
            sheet(ctx, path_poly([(1560, 1000), (1700, 1000), (1700, 760), (1680, 730), (1580, 730), (1560, 760)]),
                  "#7a7468", shadow=1.0, seed=87)
            src(ctx, "#4a4438", 0.7)
            ctx.set_line_width(2)
            R = rng(88)
            for k in range(14):
                y = 760 + k * 16
                x = 1580
                while x < 1680:
                    w = 6 + R.random() * 10
                    ctx.move_to(x, y)
                    ctx.line_to(x + w, y)
                    x += w + 4
                ctx.stroke()
        for k in range(6):
            PP.lotus(ctx, P, 300 + k * 360, 1260, 60, 0.8, 90 + k)

    layers = [(_key("te_bg", tod=tod), bg, 0.2), (_key("te_site", tod=tod, st=stele), site, 0.6)]

    def fx(ctx, t, d, depth):
        if depth == 0.6:
            for k in range(6):   # incense smoke
                ph = (t * 0.15 + k / 6) % 1
                src(ctx, "#e8e0d0", 0.18 * (1 - ph))
                ellipse(ctx, 1200 + math.sin(t + k) * 20 + ph * 40, 860 - ph * 300, 14 + ph * 50, 10 + ph * 40)
                ctx.fill()
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.2, 0.6])


# ================================================================ 8. WORKSHOP / MARKET (life and crafts)
def make_workshop(tod="day", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.5, (0.3, 0.3), 60, 6, 100)
        PP.ridge(ctx, P, 760, 40, mix(P["far"], P["haze"], 0.3), 99)
        for k in range(6):
            PP.stilt_house(ctx, P, 160 + k * 420, 800, 130, 101 + k)

    def floor(ctx):
        sheet(ctx, path_poly(jag([(-30, 860), (SW + 30, 860)], 3, 110) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#b8945a", shadow=0.6, seed=110)
        # awning
        sheet(ctx, path_poly([(500, 560), (1900, 560), (2000, 660), (400, 660)]), "#b5562f", shadow=1.0, seed=111)
        PP.punch(ctx, path_poly([(520, 570), (1880, 570), (1970, 650), (430, 650)]), "flower", 112, "#f6d8a0", 0.35, 10, 60)
        for x in (450, 1950):
            sheet(ctx, path_poly([(x - 10, 660), (x + 10, 660), (x + 10, 1100), (x - 10, 1100)]), "#5a3a22", shadow=0.6,
                  seed=x)
        # low tables with beads, gold and pots
        for k, x in enumerate((700, 1200, 1700)):
            sheet(ctx, path_poly([(x - 170, 1050), (x + 170, 1050), (x + 170, 1080), (x - 170, 1080)]), "#7a5a36",
                  shadow=0.8, seed=120 + k)
            R = rng(130 + k)
            for j in range(26):
                c = ["#c4502a", "#3f6fa8", "#e0b84a", "#2a7a6a", "#efe6d2"][j % 5]
                ellipse(ctx, x - 150 + R.random() * 300, 1040 - R.random() * 14, 7, 6)
                src(ctx, c)
                ctx.fill()
        for k in range(4):
            cast.pot(ctx, 1950 + k * 70, 1180, 50, ["#a8744a", "#8a5a3a"][k % 2], P)

    layers = [(_key("ws_bg", tod=tod), bg, 0.2), (_key("ws_floor", tod=tod), floor, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.2, 0.6])


# ================================================================ 9. CHINESE MONASTERY (translation of sutras)
def make_monastery(people=None, mouth_fn=None):
    P = TOD["lamp"]

    def room(ctx):
        ctx.set_source(lin(0, 0, 0, SH, [(0, "#3a2414"), (1, "#1a100a")]))
        ctx.paint()
        for k in range(5):   # lattice windows
            x = 220 + k * 420
            sheet(ctx, path_poly([(x, 240), (x + 280, 240), (x + 280, 640), (x, 640)]), "#e8c890", shadow=0.8, seed=k)
            src(ctx, "#4a2a14")
            ctx.set_line_width(8)
            for j in range(1, 6):
                ctx.move_to(x + j * 280 / 6, 240)
                ctx.line_to(x + j * 280 / 6, 640)
                ctx.move_to(x, 240 + j * 400 / 6)
                ctx.line_to(x + 280, 240 + j * 400 / 6)
            ctx.stroke()
        sheet(ctx, path_poly([(0, 900), (SW, 900), (SW, SH), (0, SH)]), "#5a3a22", shadow=0.4, seed=9)
        for k in range(3):   # low writing tables with scrolls
            x = 600 + k * 600
            sheet(ctx, path_poly([(x - 200, 1000), (x + 200, 1000), (x + 200, 1030), (x - 200, 1030)]), "#3a2414",
                  shadow=0.8, seed=20 + k)
            sheet(ctx, path_poly([(x - 120, 990), (x + 120, 990), (x + 120, 1000), (x - 120, 1000)]), "#efe2c6", shadow=0.3,
                  seed=30 + k)

    layers = [(_key("mo_room"), room, 0.5)]

    def fx(ctx, t, d, depth):
        glow(ctx, 1200, 700, 900, "#ffb060", 0.12 + 0.02 * math.sin(t * 5))
    return dict(layers=layers, dyn=_comb(fx, people_dyn(people or [], P, mouth_fn)), dyn_depths=[0.5])


# ================================================================ 10. CHENLA: brick temples inland
def make_chenla(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]

    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.3, 0.35), 70, 7, 140)
        PP.ridge(ctx, P, 720, 90, mix(P["far"], P["haze"], 0.3), 141, peaks=[(1700, 160, 260)])
        tp = 760
        for i in range(30):
            x = i * 85
            sheet(ctx, path_ellipse(x, tp + (i % 3) * 10, 80, 60), mix(P["mid"], P["near"], (i % 4) * 0.2), shadow=0.6,
                  seed=150 + i, edge=False)

    def temples(ctx):
        sheet(ctx, path_poly(jag([(-30, 940), (SW + 30, 940)], 3, 160) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#9a8a5a", shadow=0.6, seed=160)
        for k, (x, s) in enumerate(((700, 380), (1250, 520), (1800, 400))):
            PP.brick_shrine(ctx, P, x, 950, s, 170 + k)

    layers = [(_key("ch_bg", tod=tod), bg, 0.25), (_key("ch_t", tod=tod), temples, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.25, 0.6])
