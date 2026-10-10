"""Character sheets: build/character_sheet.py [who ...]  -> film/character_sheets/
With no argument: a sheet for the guide plus the full cast line-up."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import cairocffi as cairo
import cast
from core import draw_text, KM_SANS, KM_DISPLAY, EN_SANS, EN_SERIF, src, lin, rrect, overlay_texture
W, H = 3840, 2160


def panel(c, x, y, w, h, km, en):
    rrect(c, x, y, w, h, 18); src(c, "#f3ecdc"); c.fill()
    rrect(c, x, y, w, h, 18); src(c, "#b8a88a"); c.set_line_width(2); c.stroke()
    draw_text(c, km, x + 24, y + 16, 30, "#3a2a1a", "tl", font=KM_SANS, weight="Bold")
    draw_text(c, en, x + w - 24, y + 22, 24, "#6a5a42", "tr", font=EN_SANS)


def sheet(who, out, works):
    C = cast.CAST[who]
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source(lin(0, 0, 0, H, [(0, "#e9dcc2"), (1, "#d6c4a0")])); c.paint()
    overlay_texture(c, "fibre", 0.5, 1.0, 2)
    draw_text(c, C["km"], 80, 50, 64, "#2a1a10", "tl", font=KM_DISPLAY)
    draw_text(c, C["en"] + " · character reference sheet", 80, 170, 40, "#4a3a2a", "tl", font=EN_SERIF, weight="SemiBold")
    if C.get("note"):
        draw_text(c, C["note"], W - 80, 120, 24, "#6a5a42", "tr", font=EN_SANS)
    panel(c, 60, 240, 2200, 1150, "ការបង្វិលតួអង្គ", "TURNAROUND")
    labs = [("ខាងមុខ", "Front"), ("បីភាគបួន", "3/4"), ("ចំហៀង", "Side"), ("ខាងក្រោយ", "Back")]
    for k, yaw in enumerate((0, 40, 90, 180)):
        x = 340 + k * 520
        cast.draw(c, x, 1310, 950, who, "idle", 0.0, yaw)
        draw_text(c, labs[k][0], x, 1330, 28, "#3a2a1a", "tc", font=KM_SANS, weight="Bold")
        draw_text(c, labs[k][1], x, 1372, 22, "#6a5a42", "tc", font=EN_SANS)
    panel(c, 2300, 240, 1480, 1150, "ទឹកមុខ", "EXPRESSIONS")
    ex = [("neutral", "ធម្មតា"), ("smile", "ញញឹម"), ("wonder", "ចង់ដឹង"), ("surprise", "ភ្ញាក់ផ្អើល"), ("worry", "ព្រួយ"), ("call", "និយាយ")]
    for k, (e, km) in enumerate(ex):
        cx, cy = 2560 + (k % 3) * 480, 560 + (k // 3) * 500
        dx, dy = cast.head_offset(who, 2600)
        c.save(); rrect(c, cx - 210, cy - 230, 420, 420, 20); c.clip(); src(c, "#e4d6b8"); c.paint()
        cast.draw(c, cx - dx, cy - dy, 2600, who, "idle", 0.0, 0 if k % 2 == 0 else 25, expr=e, cutout=False)
        c.restore()
        draw_text(c, km, cx, cy + 200, 26, "#3a2a1a", "tc", font=KM_SANS, weight="Bold")
        draw_text(c, e, cx, cy + 238, 20, "#6a5a42", "tc", font=EN_SANS)
    panel(c, 60, 1430, 3720, 680, "ឥរិយាបថ", "WALK CYCLE AND ACTIONS")
    for k in range(4):
        cast.draw(c, 260 + k * 330, 2030, 520, who, "walk", k * 0.263, 90)
    for k, p in enumerate(works):
        x = 1700 + k * 520
        cast.draw(c, x, 2030, 520, who, p, 0.35, 90 if k % 2 else 40)
        draw_text(c, p, x, 2050, 22, "#3a2a1a", "tc", font=EN_SANS, weight="Bold")
    s.write_to_png(out)


OUT = os.path.join(ROOT, "film", "character_sheets")
os.makedirs(OUT, exist_ok=True)
for k, who in enumerate(sys.argv[1:] or ["tonle"], 1):
    sheet(who, os.path.join(OUT, "%02d_%s.png" % (k, who)), ["ask", "point", "talk", "offer"])
# cast line-up
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
c.set_source(lin(0, 0, 0, H, [(0, "#e9dcc2"), (1, "#d6c4a0")])); c.paint()
draw_text(c, "តួអង្គក្នុងខ្សែភាពយន្ត", 80, 50, 64, "#2a1a10", "tl", font=KM_DISPLAY)
draw_text(c, "Cast line-up · all figures are 2D reconstructions", 80, 170, 40, "#4a3a2a", "tl", font=EN_SERIF, weight="SemiBold")
keys = list(cast.CAST)
for k, who in enumerate(keys):
    C = cast.CAST[who]
    x = 150 + k * 220
    h = 860 if C["B"] is cast.CHILD else (1000 if C["B"] is cast.TEEN_F else 1200)
    cast.draw(c, x, 1850, h, who, "idle", 0.0, 30)
    draw_text(c, C["km"], x, 1880, 22, "#3a2a1a", "tc", font=KM_SANS, weight="Bold", width=210, align="center")
    draw_text(c, C["en"], x, 1960, 17, "#6a5a42", "tc", font=EN_SANS, width=210, align="center")
s.write_to_png(os.path.join(OUT, "00_cast_lineup.png"))
print("ok")
