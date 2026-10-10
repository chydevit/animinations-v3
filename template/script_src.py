"""Shot list.  The timeline is built from the real lengths of the synthesised lines (estimated until they exist).

Shot helpers: S (any scene), GUIDE (guide talking, lip-synced), PH (authentic photo), MC (museum card),
ZH (Chinese text card), M (map), CH (chapter card).
Badges: recon / legend / guide / photo / artifact / inscription / text / map / map_recon / satellite / comparison /
schematic.  Every shot that is not authentic evidence must carry a badge that says so.

SAMPLE CONTENT (Sambor Prei Kuk) — replace the SHOTS section with your film; keep the helpers and the assembly.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)

import soundfile as sf  # noqa: E402

import cards  # noqa: E402
import maps  # noqa: E402
import photos  # noqa: E402
import sets as X  # noqa: E402
from core import SH, SW, EN_SERIF  # noqa: E402
from narration import N, WHO, VOICES  # noqa: E402
from sets import F, grp  # noqa: E402

PROJECT = json.load(open(os.path.join(ROOT, "project.json")))
GAP = 0.45
FPS = PROJECT.get("fps", 24)
_MAN = None


def man():
    global _MAN
    if _MAN is None:
        try:
            _MAN = {os.path.basename(e["file"]): e for e in json.load(open(os.path.join(ROOT, "archive", "manifest.json")))}
        except Exception:
            _MAN = {}
    return _MAN


def have(f):
    return os.path.exists(os.path.join(ROOT, "archive", "img", f))


def credit(f):
    return man().get(f, {}).get("attribution_line")


SHOTS = []
CHAPTERS = []
USED = set()


def S(lines=(), vis=None, cam=None, badge=None, note=None, pre=0.6, post=0.9, min_d=0.0, xin=0.8, music=None,
      amb=None, sfx=(), fade_in=0.0, fade_out=0.0, tag=None, trans=None, guide=False):
    SHOTS.append(dict(lines=list(lines), vis=vis, cam=cam or dict(a=(SW / 2, SH / 2, 1.0), b=(SW / 2, SH / 2, 1.08)),
                      badge=badge, note=note, pre=pre, post=post, min_d=min_d, xin=xin, music=music, amb=amb,
                      sfx=list(sfx), fade_in=fade_in, fade_out=fade_out, tag=tag, trans=trans, guide=guide))


def cam(a, b=None, e="io"):
    """Camera move from a=(cx, cy, zoom) to b in set coordinates (sets are SW x SH = 2400 x 1350)."""
    return dict(a=a, b=b or a, ease=e)


def PH(f, lines, z=(1.0, 1.12), fx=(0.5, 0.5), fy=(0.5, 0.5), contain=None, badge="photo", cap=None, **kw):
    """Authentic photo with a Ken Burns move.  Falls back to a text card if archive/img/<f> is missing."""
    if not have(f):
        S(lines, lambda: cards.text_card([(N[lines[0]][1], 34, "#f4ead2", EN_SERIF, "SemiBold")]), **kw)
        return
    USED.add(f)
    e = man().get(f, {})
    c = cap or e.get("object_name") or e.get("title")
    S(lines, lambda: photos.photo(f, z, fx, fy, contain), badge=badge, note="%s  ·  %s" % (c, credit(f)), **kw)


def MC(f, lines, km=None, en=None, date=None, inst=None, found=None, note=None, badge="artifact", focus=(0.5, 0.5),
       z=(1.0, 1.15), side="r", **kw):
    """Museum card: authentic object photo + label (name, date, holding institution, credit)."""
    if not have(f):
        return
    USED.add(f)
    e = man().get(f, {})
    card = dict(km=km or e.get("object_name_km") or "", en=en or e.get("object_name") or e.get("title"),
                date=date or e.get("object_date"), inst=inst or e.get("holding_institution"),
                found=found or e.get("find_place"), note=note, credit=credit(f))
    S(lines, lambda: photos.museum_card(f, card, z, focus, side), badge=badge, **kw)


def ZH(lines, zh, en, source, km=None, **kw):
    S(lines, lambda: photos.zh_excerpt(zh, en, source, km), badge="text", **kw)


def M(lines, va, vb, els, badge="map", note=None, **kw):
    """Animated map from view va=(lon, lat, width_deg) to vb.  els: markers, labels, lines, blobs, notes, era."""
    S(lines, lambda: maps.map_scene(va, vb, els), badge=badge,
      note=note or "Paper-cut terrain from SRTM-derived tiles · rivers: Natural Earth · positions approximate", **kw)


def CH(num, km, en, years, under=None, music=None, amb=None, trans="ink"):
    CHAPTERS.append(len(SHOTS))
    S([], lambda: cards.chapter_card(num, km, en, years, under() if under else None), pre=0, post=4.8, xin=1.4,
      music=music, amb=amb, tag="chapter", trans=trans)


# ---------------------------------------------------------------- guide lip-sync
_ENV = {}


def mouth_for(key, offset=0.6):
    """mouth_fn(t) for the guide: voice envelope of line `key`, starting `offset` s into the shot."""
    def fn(t):
        if key not in _ENV:
            from narrate import wav_for
            p = wav_for(key)
            if os.path.exists(p):
                import audio
                _ENV[key] = audio.envelope(p, FPS)
            else:
                _ENV[key] = None
        env = _ENV[key]
        i = int((t - offset) * FPS)
        if env is None:
            import math
            return max(0.0, math.sin(t * 9)) * 0.7 if 0 <= t - offset < line_dur(key) else 0.0
        return float(env[i]) if 0 <= i < len(env) else 0.0
    return fn


def GUIDE(key, scene_fn, camv, **kw):
    """The guide speaks line `key`: scene_fn(mouth_fn) builds the set with her talking."""
    S([key], lambda: scene_fn(mouth_for(key)), camv, badge="guide", guide=True, **kw)


def guide(x, y, h, pose="ask", yaw=30, **kw):
    return F(x, y, h, "tonle", pose, yaw, 11, talk=True, expr=kw.pop("expr", "wonder"), **kw)


def mk(lon, lat, km, en, at=0.5, side="r", **kw):
    d = dict(k="marker", lon=lon, lat=lat, km=km, en=en, at=at, side=side)
    d.update(kw)
    return d


def era(text, km=None, at=0.3):
    return dict(k="era", text=text, km=km, at=at)


GUIDE_NOTE = "Neang Tonle is a fictional guide, not a historical person"
TITLE_KM, TITLE_EN = PROJECT["title_km"], PROJECT["title_en"]

# ================================================================ SHOTS (sample: Sambor Prei Kuk)
SPK = (105.043, 12.871)
CAMBODIA = (104.9, 12.5, 7.5)

S([], lambda: X.make_chenla("dawn"), cam((1200, 700, 1.05), (1250, 690, 1.12)), badge="recon", pre=0, post=3.0,
  fade_in=2.5, xin=0, music="opening", amb="forest")
GUIDE("t0", lambda m: X.make_chenla("golden", people=[grp(0.6, guide(1500, 1150, 330, "wave", -30))], mouth_fn=m),
      cam((1450, 900, 1.5), (1450, 880, 1.6)), note=GUIDE_NOTE, trans="lotus")
S([], lambda: cards.title_card(TITLE_KM, TITLE_EN, "សតវត្សរ៍ទី ៧", "7th century",
                               under=X.make_chenla("golden")),
  cam((1200, 700, 1.05), (1200, 680, 1.12)), pre=0, post=5.0, xin=1.4, trans="lotus")

CH(1, "ទីក្រុងឦសានបុរៈ", "The City of Isanapura", "7th century CE",
   under=lambda: X.make_chenla("day"), music="kings", amb="forest")
M(["a1"], (104.9, 12.5, 9.0), CAMBODIA, [mk(*SPK, "សំបូរព្រៃគុក", "Sambor Prei Kuk", 1.0, "r", pulse=True),
                                        era("Kampong Thom", "ខេត្តកំពង់ធំ", 1.5)])
S(["a2"], lambda: cards.claim_board("អ្វីដែលយើងដឹង", "What we know", [
    ("inscription", "សិលាចារឹក នាមព្រះបាទ ឦសានវរ្ម័នទី ១", "Inscriptions name King Isanavarman I"),
    ("archaeology", "ប្រាសាទឥដ្ឋ ក្នុងព្រៃ", "Brick temples in the forest"),
    ("debated", "ទំហំពិតនៃទីក្រុង", "The city's true extent")],
    under=X.make_chenla("golden")), pre=0.4, post=1.5)
S(["a3"], lambda: X.make_chenla("golden"), cam((1250, 900, 1.3), (1250, 860, 1.6)), badge="recon")
S(["a4"], lambda: cards.text_card([("UNESCO World Heritage · 2017", 54, "#f2cf7a", EN_SERIF, "Bold"),
                                   ("បេតិកភណ្ឌពិភពលោក", 44, "#fff4dc", "Noto Sans Khmer", "Bold")],
                                  under=X.make_chenla("dusk")), pre=0.4, post=1.2)
GUIDE("t1", lambda m: X.make_chenla("dusk", people=[grp(0.6, guide(1300, 1150, 330, "point", 30, expr="smile"))],
                                    mouth_fn=m),
      cam((1300, 930, 1.5), (1300, 900, 1.35)), note=GUIDE_NOTE, post=3.0, fade_out=2.5)


# ================================================================ CREDITS
def credit_blocks():
    imgs = ["%s — %s" % ((e.get("object_name") or f)[:80], e.get("attribution_line") or e.get("licence"))
            for f, e in sorted(man().items()) if f in USED]
    return [("%s · %s" % (TITLE_KM, TITLE_EN.upper()),
             ["An educational documentary in paper-cut 2D animation, maps and authentic evidence",
              "Narration: Khmer · Subtitles: English", GUIDE_NOTE]),
            ("SOURCES", ["See docs/fact_sheet.md"]),
            ("ARCHIVAL IMAGES", imgs or ["None"]),
            ("MAP DATA", ["Terrain: SRTM-derived terrarium tiles (Mapzen / AWS) · Natural Earth (public domain)"]),
            ("NOTE", ["Paper-cut scenes are artistic reconstructions.",
                      "Khmer narration should be reviewed by a native-speaking historian before publication."])]


S([], lambda: cards.scrolling_credits(credit_blocks()), pre=0, post=24.0, xin=1.5, music="credits", tag="credits",
  amb="none")


# ================================================================ timeline assembly (keep as is)
def narr_wav(key):
    from narrate import wav_for
    return wav_for(key)


_DUR = {}


def line_dur(key):
    if key not in _DUR:
        p = narr_wav(key)
        _DUR[key] = sf.info(p).duration if os.path.exists(p) else len(N[key][0]) * 0.0747
    return _DUR[key]


# Optional chapter start times (s), one per CH(), e.g. from the brief.  Holds are stretched so each chapter starts
# on time (narration is never cut).  END_TARGET (project.json "end_target") does the same for the credits.
TARGETS = []
_EXTRA = None


def _layout(extra):
    t = 0.0
    starts = []
    for i, s in enumerate(SHOTS):
        xin = s["xin"] if i > 0 else 0.0
        start = max(0.0, t - xin) if i > 0 else 0.0
        lt = s["pre"] + sum(line_dur(k) + GAP for k in s["lines"])
        dur = max(lt - (GAP if s["lines"] else 0) + s["post"] + extra.get(i, 0.0), s["min_d"])
        starts.append(start)
        t = start + dur
    return starts


def _extras():
    global _EXTRA
    if _EXTRA is not None:
        return _EXTRA
    extra = {}
    goals = list(TARGETS[:len(CHAPTERS)])
    bounds = [0] + CHAPTERS[:len(goals)]
    if PROJECT.get("end_target"):
        goals.append(PROJECT["end_target"])
        bounds.append(len(SHOTS) - 1)
    for k, tgt in enumerate(goals):
        starts = _layout(extra)
        nxt = bounds[k + 1]
        deficit = tgt - starts[nxt]
        body = [i for i in range(bounds[k], nxt) if SHOTS[i]["lines"]]
        if deficit > 0 and body:
            for i in body:
                extra[i] = extra.get(i, 0.0) + deficit / len(body)
    _EXTRA = extra
    return extra


def build():
    extra = _extras()
    t = 0.0
    out, placements, cues = [], [], []
    for i, s in enumerate(SHOTS):
        xin = s["xin"] if i > 0 else 0.0
        start = max(0.0, t - xin) if i > 0 else 0.0
        lt = s["pre"]
        for k in s["lines"]:
            d = line_dur(k)
            placements.append(dict(key=k, t=start + lt, dur=d, wav=narr_wav(k), who=WHO.get(k, "nar")))
            cues.append(dict(start=start + lt, end=start + lt + d + 0.15, en=N[k][1], km=N[k][0], key=k,
                             who=WHO.get(k, "nar")))
            lt += d + GAP
        dur = max(lt - (GAP if s["lines"] else 0) + s["post"] + extra.get(i, 0.0), s["min_d"])
        out.append(dict(make=s["vis"], start=start, dur=dur, cam=s["cam"], badge=s["badge"], badge_note=s["note"],
                        xin=xin, fade_in=s["fade_in"], fade_out=s["fade_out"], music=s["music"], amb=s["amb"],
                        sfx=s["sfx"], tag=s["tag"], lines=s["lines"], trans=s["trans"]))
        t = start + dur
    return out, placements, _split_cues(cues)


def _split_cues(cues, limit=84):
    import re
    out = []
    for c in cues:
        en = c["en"]
        if len(en) <= limit:
            out.append(c)
            continue
        parts = re.split(r"(?<=[.;:,!?])\s+", en)
        chunks, cur = [], ""
        for p in parts:
            if cur and len(cur) + len(p) + 1 > limit:
                chunks.append(cur)
                cur = p
            else:
                cur = (cur + " " + p).strip()
        if cur:
            chunks.append(cur)
        tot = sum(len(x) for x in chunks)
        t0, span = c["start"], c["end"] - c["start"]
        for j, ch in enumerate(chunks):
            d = span * len(ch) / tot
            out.append(dict(c, start=t0, end=t0 + d - (0.04 if j < len(chunks) - 1 else 0), en=ch))
            t0 += d
    return out


def timeline(burn=True):
    import film
    shots, _, cues = build()
    return film.Timeline(shots, cues, burn=burn)


if __name__ == "__main__":
    shots, pl, cues = build()
    tot = shots[-1]["start"] + shots[-1]["dur"]
    print("shots: %d  lines: %d  runtime: %d:%02d" % (len(shots), len(pl), tot // 60, tot % 60))
    for i in CHAPTERS:
        print("  chapter at %d:%02d" % (shots[i]["start"] // 60, shots[i]["start"] % 60))
    print("not placed:", [k for k in N if k not in {p["key"] for p in pl}])
