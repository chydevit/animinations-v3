# Engine API (engine/)

The frame is 1920×1080 at 24 fps. Sets are painted at SW×SH = 2400×1350, so the camera can push in without blur.
Camera: `cam((cx, cy, zoom), (cx, cy, zoom))` in set coordinates; zoom 1.0 shows 1920 px of the set.

## Shot helpers (script_src.py)
| helper | use |
|---|---|
| `S(lines, vis, cam, badge, note, pre, post, min_d, xin, music, amb, sfx, fade_in, fade_out, trans)` | any shot; `vis` is a zero-argument lambda returning a scene |
| `GUIDE(key, lambda m: X.make_*(…, people=[grp(depth, guide(x, y, h, pose, yaw))], mouth_fn=m), cam)` | the guide speaks, lip-synced to her clip |
| `PH(file, lines, z, fx, fy)` | authentic photo, Ken Burns move, credit from the manifest |
| `MC(file, lines, km, en, date, inst, found)` | museum card: framed object and label |
| `ZH(lines, zh, en, source, km)` | classical Chinese excerpt in vertical columns |
| `M(lines, view_a, view_b, elements)` | animated map; a view is (lon, lat, width in degrees) |
| `CH(num, km, en, years, under, music, amb, trans)` | chapter card |

Transitions (`trans`): fade (default), cut, ripple, lotus, ink.
Badges: recon, legend, photo, artifact, inscription, text, map, map_recon, satellite, comparison, schematic, guide.
Add new ones with `cards.BADGES["key"] = (colour, km, en)` in script_src.py.

## Cards (cards.py)
`title_card(km, en, sub_km, sub_en, under)` · `chapter_card(num, km, en, years, under)` ·
`claim_board(title_km, title_en, [(class, km, en)], under)` (classes: record, inscription, archaeology, legend,
debated, hypothesis) · `timeline_card(title_km, title_en, [(label, km, en)], focus, under)` ·
`text_card([(text, size, colour, font, weight)], under)` · `lower_third(km, en, under)` · `scrolling_credits(blocks)`.
`under` is a scene shown dimmed behind the card.

## Map elements (maps.py)
- `dict(k="marker", lon, lat, km, en, at, side, pulse, color, r)`
- `dict(k="label", lon, lat, km, en, size, at)`
- `dict(k="blob", pts=[(lon, lat)…], fill, at, grow)` approximate extent, never a border
- `dict(k="line"|"glowline", pts, at, draw, color, lw, dash, ships=n, speed)` routes, with moving ships
- `dict(k="note", km, en, cls, x, y, w, at)` paper note with a claim class
- `dict(k="era", text, km, at)` large date in the corner

Terrain: `geo/dem_sea.npz` (wide view) and `geo/dem_delta.npz` (used when the view is narrower than 9°), from `scripts/fetch_geo.py`.

## Sets (sets.py)
Each builder takes `tod` (time of day: dawn, day, golden, dusk, night, lamp) and `people=[grp(depth, F(...))]`, plus `mouth_fn`.
make_delta · make_lowland(flood) · make_puppet(figures, title) · make_port · make_sea(fleet) · make_palace ·
make_temple(stele) · make_workshop · make_monastery · make_chenla.

`F(x, y, h, who, pose, yaw, seed, vx=, vy=, boat=, talk=, expr=)` places a figure. `grp(depth, *figs)` puts figures on a
parallax layer (0.6 is about mid-ground).

A new set returns `dict(layers=[(cache_key, painter(ctx), depth)…], dyn=fn(ctx, t, d, depth), dyn_depths=[…])`.
Paint with the paper helpers in paper.py: `sheet(ctx, path, colour, shadow, seed)`, `jag`, `path_poly`, `path_ellipse`,
`palm`, `stilt_house`, `brick_shrine`, `boat`, `ship`, `lotus`, `water`, `ridge`, `sky`, `clouds`.

## Cast (cast.py)
`CAST[key] = dict(km, en, era, B=<body>, skin, hair, hair_c, wrap=(style, colour, pattern), top, orn, face)`.
Bodies: ADULT_M, ADULT_F, TEEN_F, CHILD, ELDER_M, ELDER_F.
Poses include: idle, stand, walk, walk_slow, ask, talk, point, wave, offer, bow, pray, kneel, kneel_pray, sit, sit_talk,
read, write, harvest, sickle, carry_pot_head, carry_shoulder, carry_box, paddle, pole_boat, oar, craft,
hammer_small, shoot_bow, present_scroll, release, tablet, brush.
Expressions: neutral, smile, focus, surprise, worry, sad, call, calm, wonder.
`build/character_sheet.py [who]` draws a turnaround, expression and pose sheet, plus a line-up of the whole cast.

## Audio (audio.py)
Music moods (MOTIFS): opening, land, legend, port, water, fleet, envoys, india, life, kings, decline, legacy, credits.
Add a mood as `dict(root, scale, cell, lead, bpm, pad, perc/skor/gong/bells)`. Lead instruments: khloy, roneat,
kong, chapei, tro.
Ambience (`amb`): delta, port, sea, lamp, workshop, river, market, night, forest, temple, village, none.
SFX: `sfx=("hit", "bell")`. Transitions and chapter cards get their own sounds automatically. The master is -16 LUFS, and music
ducks under the voices.
