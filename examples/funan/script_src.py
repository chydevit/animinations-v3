"""Shot list for 'Funan – Kingdom of the Mountain' (សម័យហ្វូណន / នគរភ្នំ).  Builds the timeline from the real
lengths of the narration and of Neang Tonle's lines.

Shot helpers: S (any scene), PH (authentic photo), MC (museum card), ZH (Chinese text card), M (map), CH (chapter).
Badges: recon / legend / guide / photo / artifact / inscription / text / map / map_recon / satellite / comparison.
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
from core import SH, SW, KM_SANS, EN_SANS, EN_SERIF  # noqa: E402
from narration import N, WHO  # noqa: E402
from sets import F, grp  # noqa: E402

GAP = 0.45
FPS = 24
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
    e = man().get(f, {})
    return e.get("attribution_line")


SHOTS = []
CHAPTERS = []
USED = set()


def S(lines=(), vis=None, cam=None, badge=None, note=None, pre=0.6, post=0.9, min_d=0.0, xin=0.8, music=None,
      amb=None, sfx=(), fade_in=0.0, fade_out=0.0, tag=None, trans=None, guide=False):
    SHOTS.append(dict(lines=list(lines), vis=vis, cam=cam or dict(a=(SW / 2, SH / 2, 1.0), b=(SW / 2, SH / 2, 1.08)),
                      badge=badge, note=note, pre=pre, post=post, min_d=min_d, xin=xin, music=music, amb=amb,
                      sfx=list(sfx), fade_in=fade_in, fade_out=fade_out, tag=tag, trans=trans, guide=guide))


def cam(a, b=None, e="io"):
    return dict(a=a, b=b or a, ease=e)


def PH(f, lines, z=(1.0, 1.12), fx=(0.5, 0.5), fy=(0.5, 0.5), contain=None, badge="photo", cap=None, **kw):
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
    """Neang Tonle asks her question: scene_fn(mouth_fn) builds the set with her talking."""
    S([key], lambda: scene_fn(mouth_for(key)), camv, badge="guide", guide=True, **kw)


def tonle(x, y, h, pose="ask", yaw=30, **kw):
    return F(x, y, h, "tonle", pose, yaw, 11, talk=True, expr=kw.pop("expr", "wonder"), **kw)


# ---------------------------------------------------------------- geography
P_ = dict(oceo=(105.152, 10.233), bathe=(105.13, 10.26), ab=(104.975, 10.995), phnomda=(104.97, 10.95),
          gothap=(105.84, 10.59), bati=(104.85, 11.34), baphnom=(105.37, 11.23), spk=(105.043, 12.871),
          watphu=(105.822, 14.848), nenchua=(104.95, 10.17), dunsun=(99.2, 10.3), panpan=(99.2, 9.4),
          ksk=(99.17, 10.53), myson=(108.117, 15.767), jiaozhou=(106.05, 21.04), guangzhou=(113.26, 23.13),
          nanjing=(118.796, 32.058), arikamedu=(79.82, 11.9), tamralipti=(87.92, 22.3), mantai=(79.95, 8.88),
          pp=(104.921, 11.569))


def mk(key, km, en, at=0.5, side="r", **kw):
    lon, lat = P_[key]
    d = dict(k="marker", lon=lon, lat=lat, km=km, en=en, at=at, side=side)
    d.update(kw)
    return d


def era(text, km=None, at=0.3):
    return dict(k="era", text=text, km=km, at=at)


SEA = (100.0, 13.0, 40.0)
DELTA = (105.1, 10.75, 3.4)
FUNAN_CORE = [(104.6, 11.4), (105.6, 11.5), (106.3, 10.6), (105.9, 9.9), (105.0, 9.8), (104.5, 10.5)]
CHENLA_ZONE = [(104.6, 12.4), (105.6, 12.3), (106.3, 13.8), (106.1, 15.3), (105.2, 15.4), (104.6, 13.6)]
ISTHMUS = [(98.6, 12.0), (99.9, 12.2), (100.2, 9.4), (99.4, 8.4), (98.4, 9.4)]
GUIDE_NOTE = "Neang Tonle is a fictional guide, not a historical person"

# ================================================================ OPENING (0:00 – 0:45)
S(["o1"], lambda: X.make_delta("dawn"), cam((900, 700, 1.25), (1500, 640, 1.06)), badge="recon", pre=3.0, fade_in=2.5,
  xin=0, music="opening", amb="delta")
GUIDE("t0", lambda m: X.make_delta("dawn", people=[grp(0.6, tonle(1250, 1010, 330, "wave", 25, boat=True))], mouth_fn=m),
      cam((1250, 900, 1.6), (1250, 880, 1.75)), note=GUIDE_NOTE, trans="ripple", xin=1.2)
M(["o2"], (102.0, 13.0, 34.0), DELTA, [dict(k="blob", pts=FUNAN_CORE, at=2.0, fill="#d8aa4a"),
                                       dict(k="label", lon=105.2, lat=10.9, km="ហ្វូណន · នគរភ្នំ", en="扶南 Funan", at=3.0, size=38),
                                       dict(k="note", km="ហ្វូណន ជាឈ្មោះចិន។ ការភ្ជាប់ទៅពាក្យ វ្នំ (ភ្នំ) នៅជជែកវែកញែក",
                                            en="'Funan' is a Chinese name; the link to Old Khmer 'vnam' (mountain) is debated",
                                            cls="debated", at=4.0, x=80, y=780)],
  badge="map_recon", note="Funan's core shown as a soft zone: no borders are known")
S(["o3"], lambda: cards.claim_board("របៀបដែលយើងបង្ហាញព័ត៌មាន", "How this film labels information", [
    ("legend", "រឿងព្រេង និងប្រពៃណី", "Legends and traditions"),
    ("record", "អ្វីដែលឯកសារចិនកត់ត្រា", "What Chinese records say"),
    ("inscription", "សិលាចារឹក និងបុរាណវិទ្យា", "Inscriptions and archaeology"),
    ("debated", "ចំណុចដែលអ្នកប្រវត្តិវិទូ មិនឯកភាព", "Where historians disagree")]), pre=0.4, post=1.6, amb="none")
S([], lambda: cards.title_card("ហ្វូណន · នគរភ្នំ", "Funan – Kingdom of the Mountain", "សតវត្សរ៍ទី ១ – ៥៥០ គ.ស.",
                               "1st century – 550 CE", under=X.make_delta("golden", lotus_n=8)),
  cam((1200, 700, 1.05), (1200, 680, 1.12)), pre=0, post=6.0, xin=1.4, trans="lotus", music="opening")

# ================================================================ 1. THE LAND BEFORE FUNAN
CH(1, "ទឹកដីមុនសម័យហ្វូណន", "The Land Before Funan", "c. 400 BCE – 1st century CE",
   under=lambda: X.make_lowland("day"), music="land", amb="farm")
GUIDE("q1", lambda m: X.make_lowland("day", people=[grp(0.65, tonle(1250, 1180, 300, "ask", 25),
                                                        F(900, 1150, 280, "f_man", "harvest", 90, 1))], mouth_fn=m),
      cam((1200, 950, 1.35), (1220, 940, 1.45)), note=GUIDE_NOTE)
M(["a1"], (105.0, 11.0, 6.0), (105.0, 11.0, 4.0), [mk("ab", "អង្គរបុរី", "Angkor Borei", 1.0, "l", pulse=True),
                                                   era("c. 400 BCE", "ប្រហែល ៤០០ មុន គ.ស.", 1.5)])
S(["a2"], lambda: X.make_lowland("day", people=[grp(0.65, F(900, 1150, 280, "f_man", "harvest", 90, 1),
                                                    F(1300, 1170, 270, "f_woman", "carry_pot_head", -90, 2, vx=-14),
                                                    F(1600, 1190, 180, "f_child", "walk", -90, 3, vx=-14))]),
  cam((1100, 900, 1.15), (1250, 900, 1.25)), badge="recon")
S(["a3"], lambda: X.make_lowland("day", flood=1.0), cam((1200, 800, 1.0), (1200, 840, 1.1)), badge="recon", amb="river")
M(["a4"], (102.5, 10.5, 12.0), (102.5, 10.5, 10.0), [mk("ksk", "ខៅសាមកែវ", "Khao Sam Kaeo (Thai-Malay peninsula)", 0.8, "l"),
                                                     mk("ab", "អង្គរបុរី", "Angkor Borei", 0.8, "r"),
                                                     dict(k="line", pts=[P_["ab"], (104.2, 10.2), (102.0, 10.0), P_["ksk"]],
                                                          at=1.2, ships=2),
                                                     era("4th c. BCE – 1st c. CE", None, 0.5)], badge="map_recon",
  note="Illustrative exchange route across the Gulf of Thailand (archaeological links; route schematic)")

# ================================================================ 2. THE FOUNDING LEGEND
CH(2, "រឿងព្រេងនៃការកកើតនគរ", "The Founding Legend", "legend · not documented history",
   under=lambda: X.make_puppet([dict(kind="ship", x=1200, y=950, s=800)]), music="legend", amb="lamp")
GUIDE("q2", lambda m: X.make_lowland("golden", people=[grp(0.65, tonle(1150, 1180, 300, "ask", 30),
                                                           F(1450, 1180, 330, "f_grandma", "sit_talk", -70, 5))], mouth_fn=m),
      cam((1300, 960, 1.4), (1300, 950, 1.5)), note=GUIDE_NOTE, trans="lotus")
S(["g1"], lambda: X.make_puppet([dict(kind="waves", x=150, y=1060, s=1), dict(kind="ship", x=1200, y=960, s=760, vx=-10)],
                                ("រឿងព្រេង", "LEGEND")), cam((1200, 700, 1.0), (1200, 700, 1.06)), badge="legend", amb="lamp")
S(["g2"], lambda: X.make_puppet([dict(kind="waves", x=150, y=1060, s=1),
                                 dict(kind="person", who="f_woman", x=1350, y=1010, s=380, pose="point", yaw=-90),
                                 dict(kind="tree", x=1950, y=1150, s=600, seed=2)],
                                ("កំណែទី ១ · ឯកសារចិន សតវត្សរ៍ទី ៣", "Version 1 · Chinese records, 3rd century")),
  cam((1300, 760, 1.05), (1300, 740, 1.15)), badge="legend")
S(["g3"], lambda: X.make_puppet([dict(kind="waves", x=150, y=1060, s=1),
                                 dict(kind="ship", x=500, y=960, s=700, vx=60),
                                 dict(kind="person", who="f_noble", x=450, y=890, s=300, pose="idle", vx=60)],
                                ("ហ៊ុនទៀន · Hun Tian", "the stranger with the sacred bow")), cam((1100, 760, 1.05)), badge="legend")
S(["g4"], lambda: X.make_puppet([dict(kind="waves", x=150, y=1060, s=1),
                                 dict(kind="ship", x=700, y=960, s=650),
                                 dict(kind="person", who="f_noble", x=620, y=890, s=300, pose="shoot_bow"),
                                 dict(kind="arrow", x=820, y=760, x2=1500, y2=930, at=1.5, fly=1.0),
                                 dict(kind="person", who="f_woman", x=1650, y=1010, s=380, pose="bow", yaw=-90, at=3.5)],
                                ("លីវយី · Liu Ye", "the queen surrenders")), cam((1150, 780, 1.0), (1200, 780, 1.08)),
  badge="legend", sfx=("hit",))
S(["g5"], lambda: cards.claim_board("កំណែទី ២ · កៅណ្ឌិន្យ និងសោមា", "Version 2 · Kaundinya and Soma", [
    ("inscription", "សិលាចារឹកចាម នៅមីសឺន ឆ្នាំ ៦៥៨ គ.ស.", "Cham inscription at My Son, 658 CE"),
    ("inscription", "សិលាចារឹកអង្គរ សតវត្សរ៍ទី ១០ (ឧ. K.286 ឆ្នាំ ៩៤៨)", "Angkorian inscriptions, 10th c. (e.g. K.286, 948)"),
    ("legend", "ឯកសារចិន មិនដែលប្រើឈ្មោះ កៅណ្ឌិន្យ ឬ សោមា ទេ", "The Chinese records never use the names Kaundinya or Soma")],
    under=X.make_puppet([dict(kind="naga", x=1600, y=560, s=200)])), pre=0.4, post=1.5)
S(["g6"], lambda: X.make_puppet([dict(kind="waves", x=150, y=1080, s=1), dict(kind="naga", x=1500, y=640, s=230),
                                 dict(kind="person", who="f_noble", x=800, y=1010, s=380, pose="idle"),
                                 dict(kind="person", who="f_woman", x=1150, y=1010, s=370, pose="idle", yaw=-90)],
                                ("កំណែទី ៣ · ព្រះថោង និងនាងនាគ", "Version 3 · Preah Thong and Neang Neak (Khmer folk legend)")),
  cam((1150, 760, 1.0), (1150, 740, 1.08)), badge="legend")
S(["g7"], lambda: X.make_puppet([dict(kind="person", who="f_noble", x=950, y=1010, s=400, pose="offer"),
                                 dict(kind="person", who="f_woman", x=1300, y=1010, s=390, pose="idle", yaw=-90),
                                 dict(kind="tree", x=400, y=1150, s=620), dict(kind="tree", x=2000, y=1150, s=600, seed=4)],
                                ("ស្បៃ · the sash", "a wedding custom recalls the legend")), cam((1150, 800, 1.1)),
  badge="legend")
S(["g8"], lambda: cards.claim_board("រឿងបី ពីបីសម័យ", "Three stories from three eras", [
    ("legend", "ហ៊ុនទៀន និងលីវយី · ឯកសារចិន (សតវត្សរ៍ទី ៣ ក្រោយមក)", "Hun Tian & Liu Ye · Chinese records (from the 3rd c.)"),
    ("legend", "កៅណ្ឌិន្យ និងសោមា · សិលាចារឹក (ឆ្នាំ ៦៥៨ និងសតវត្សរ៍ទី ១០)", "Kaundinya & Soma · inscriptions (658; 10th c.)"),
    ("legend", "ព្រះថោង និងនាងនាគ · រឿងព្រេងខ្មែរ សម័យក្រោយ", "Preah Thong & Neang Neak · later Khmer folk legend")]),
  pre=0.4, post=1.8)

# ================================================================ 3. OC EO, PORT OF THE WORLD
CH(3, "អូរកែវ · កំពង់ផែនៃពិភពលោក", "Oc Eo, Port of the World", "c. 1st – 7th century CE",
   under=lambda: X.make_port("day"), music="port", amb="port")
GUIDE("q3", lambda m: X.make_port("day", people=[grp(0.6, tonle(1200, 1180, 300, "point", 40),
                                                     F(900, 870, 190, "in_merchant", "talk", 90, 1),
                                                     F(1060, 870, 185, "f_woman", "idle", -90, 2),
                                                     F(1330, 870, 190, "f_man", "carry_box", 90, 3, vx=12))], mouth_fn=m),
      cam((1200, 950, 1.3), (1200, 900, 1.2)), note=GUIDE_NOTE, trans="ripple")
PH("land_oc_eo_ba_the_panorama.jpg", ["p1"], z=(1.0, 1.12))
PH("map_oc_eo_sites_hcmc_museum.jpg", ["p2"], z=(1.0, 1.15), contain=True)
MC("oe_gold_flower_ornaments.jpg", ["p3"], km="គ្រឿងអលង្ការមាសរាងផ្កា", focus=(0.5, 0.5))
MC("oe_jewellery_glass_stone_hcmc.jpg", ["p4"], km="អង្កាំ និងគ្រឿងអលង្ការកែវ ថ្មត្បូង",
   note="Seals with Brahmi names are known from Oc Eo; individual pieces here are not identified.")
M(["p5"], (82.0, 14.0, 70.0), (95.0, 13.0, 55.0),
  [mk("oceo", "អូរកែវ", "Oc Eo", 0.4, "r"),
   dict(k="line", pts=[(45.0, 12.5), (60, 12), (75.0, 8.5), P_["arikamedu"], (88, 8), (98.0, 6.5), (104.2, 9.4), P_["oceo"]],
        at=0.8, draw=2.5, ships=3, color="#f0d58a"),
   dict(k="line", pts=[P_["guangzhou"], (111, 15), (108, 11), P_["oceo"]], at=1.6, draw=2.0, ships=2, color="#e3a1a8"),
   dict(k="label", lon=78.5, lat=20.0, km="ឥណ្ឌា", en="India", at=1.0, size=30),
   dict(k="label", lon=110.0, lat=26.5, km="ចិន", en="China", at=1.8, size=30),
   dict(k="label", lon=52.0, lat=17.0, km="ទៅពិភពរ៉ូម៉ាំង", en="towards the Roman world (via many hands)", at=2.6, size=24)],
  badge="map_recon", note="Schematic sea routes; goods passed through many intermediaries")
MC("oe_bronze_mirror_fragment_chinese_type.jpg", [], km="បំណែកកញ្ចក់សំរិទ្ធ បែបចិន",
   note="Chinese-type mirror fragment of the kind reported from Oc Eo (identification from photo; check museum label).",
   min_d=4.5, post=4.5)
MC("coin_cmp_antoninus_pius_aureus_ans.jpg", ["p6"], km="ប្រៀបធៀប៖ កាក់មាសរ៉ូម៉ាំង នៃព្រះចៅអង់តូនីនុស ពីយុស",
   note="COMPARISON: a real Roman coin. The Oc Eo piece imitates such a coin; no licensed photo of it exists.",
   badge="comparison")
S(["p7"], lambda: X.make_port("golden"), cam((1000, 900, 1.05), (1400, 880, 1.15)), badge="recon")
S(["p8"], lambda: X.make_workshop("day", people=[grp(0.6, F(700, 1050, 260, "f_smith", "craft", 90, 1),
                                                     F(1700, 1050, 260, "f_woman", "craft", -90, 3))]),
  cam((1200, 920, 1.1), (1150, 940, 1.2)), badge="recon", note="Spice traces on grinding stones: Wang, Hung et al. 2023, Science Advances")

# ================================================================ 4. MASTERS OF WATER
CH(4, "ម្ចាស់នៃទឹក", "Masters of Water", "canals of the delta", under=lambda: X.make_delta("day", boats=True),
   music="water", amb="delta")
GUIDE("q4", lambda m: X.make_delta("day", people=[grp(0.6, tonle(1150, 1010, 320, "paddle", 90, boat=True, vx=30))],
                                   mouth_fn=m), cam((1200, 900, 1.5), (1350, 890, 1.55)), note=GUIDE_NOTE, trans="ripple")
PH("land_mekong_delta_sentinel2.jpg", ["w1"], z=(1.0, 1.2), badge="satellite",
   cap="Mekong Delta from space today (Copernicus Sentinel-2): the ancient canals were first seen from the air in the 1930s")
M(["w2"], (105.0, 10.6, 3.6), (105.0, 10.6, 2.4),
  [mk("ab", "អង្គរបុរី", "Angkor Borei", 0.4, "l"), mk("oceo", "អូរកែវ", "Oc Eo", 0.6, "r"),
   mk("nenchua", "ណឿនជួ", "Nen Chua (old coast)", 1.0, "l", color="#8a6a3c"),
   dict(k="glowline", pts=[P_["ab"], (105.06, 10.62), P_["oceo"]], at=1.0, draw=2.5),
   dict(k="glowline", pts=[P_["oceo"], (105.05, 10.2), P_["nenchua"]], at=2.5, draw=2.0),
   dict(k="note", km="ប្រហែល ៧០ គ.ម. · ផ្លូវប្រឡាយ គូសតាមផែនទីចាស់", en="c. 70 km · course drawn schematically", at=3.5,
        x=80, y=820)], badge="map_recon")
PH("ab_town_from_canal_15.jpg", ["w3"], z=(1.0, 1.12), cap="Angkor Borei seen from canal 15 today")
PH("map_oc_eo_angkor_borei_efeo.jpg", ["w4"], z=(1.0, 1.15), contain=True, badge="map",
   cap="Scholarly map of Oc Eo, Angkor Borei and the ancient canals (EFEO, 2000)")
S(["w5"], lambda: X.make_delta("golden", people=[grp(0.6, F(700, 1010, 260, "f_boatman", "pole_boat", 90, 1, boat=True, vx=25),
                                                     F(1500, 1030, 250, "f_man", "paddle", -90, 2, boat=True, vx=-20))]),
  cam((1200, 880, 1.1), (1250, 880, 1.2)), badge="recon")

# ================================================================ 5. FAN SHIMAN'S EXPANSION
CH(5, "ការពង្រីកអំណាចរបស់ ហ្វានស៊ីម៉ាន", "Fan Shiman's Expansion", "early 3rd century CE",
   under=lambda: X.make_sea("golden", "funan", 4), music="fleet", amb="sea")
GUIDE("q5", lambda m: X.make_port("golden", people=[grp(0.6, tonle(1100, 1180, 300, "point", 60))], mouth_fn=m),
      cam((1250, 950, 1.3), (1300, 930, 1.35)), note=GUIDE_NOTE, trans="ripple")
ZH(["f1"], "自號扶南大王。乃治作大船，窮漲海，攻屈都昆、九稚、典孫等十餘國，開地五六千里。",
   "He styled himself Great King of Funan. He had great ships built, crossed the Swelling Sea, attacked Qudukun, Jiuzhi, "
   "Diansun and more than ten other states, and opened up five or six thousand li.",
   "Liang shu 梁書, ch. 54 (compiled 636 CE)")
M(["f2"], (103.0, 11.0, 14.0), (102.0, 11.0, 12.0),
  [dict(k="blob", pts=FUNAN_CORE, at=0.2, fill="#d8aa4a"),
   dict(k="blob", pts=ISTHMUS, at=1.5, fill="#e3a1a8", fa=0.18),
   dict(k="line", pts=[P_["oceo"], (103.5, 9.6), (101.5, 9.8), P_["dunsun"]], at=1.0, draw=2.0, ships=3, color="#e3a1a8"),
   dict(k="label", lon=99.4, lat=12.9, km="ទុនស៊ុន?", en="Dunsun? (location uncertain)", at=2.2, size=26),
   dict(k="note", km="ការអះអាងក្នុងឯកសារចិន · វិសាលភាពពិត មិនដឹង", en="Claimed in Chinese records · real extent unknown",
        cls="record", at=3.0, x=80, y=800), era("early 3rd c.", "ដើមសតវត្សរ៍ទី ៣", 0.5)], badge="map_recon")
ZH(["f3"], "為船八九丈，廣裁六七尺，頭尾似魚。",
   "They build boats eight or nine zhang long, only six or seven chi wide, with bow and stern shaped like a fish.",
   "Nan Qi shu 南齊書, ch. 58 (c. 537 CE)")
S(["f4"], lambda: X.make_sea("golden", "funan", 5), cam((1200, 800, 1.05), (1300, 800, 1.15)), badge="recon")
S(["f5"], lambda: cards.claim_board("តើយើងដឹងអ្វីខ្លះ?", "What do we really know?", [
    ("record", "ហ្វានស៊ីម៉ាន និងនាវារបស់គាត់ · ឯកសារចិន សរសេរ ៣០០–៤០០ ឆ្នាំក្រោយ", "Fan Shiman and his ships · Chinese records written 300–400 years later"),
    ("archaeology", "ទំនិញដូចគ្នា នៅជុំវិញឈូងសមុទ្រថៃ · បណ្ដាញពាណិជ្ជកម្ម", "Shared goods around the Gulf of Thailand · trade networks"),
    ("debated", "តើអំណាចនយោបាយ លាតសន្ធឹងដល់ណា?", "How far did political power really reach?")]), pre=0.4, post=1.5)

# ================================================================ 6. ENVOYS FROM CHINA
CH(6, "ទូតមកពីប្រទេសចិន", "Envoys from China", "mid-3rd century CE", under=lambda: X.make_palace("golden"),
   music="envoys", amb="palace")
GUIDE("q6", lambda m: X.make_palace("golden", people=[grp(0.6, tonle(2050, 1200, 290, "point", -60, expr="surprise"),
                                                          F(900, 1150, 330, "zh_envoy", "bow", 90, 1),
                                                          F(700, 1160, 320, "zh_envoy2", "idle", 90, 2))], mouth_fn=m),
      cam((1700, 950, 1.3), (1650, 940, 1.25)), note=GUIDE_NOTE, trans="lotus")
M(["c1"], (110.0, 20.0, 28.0), (108.0, 19.0, 24.0),
  [mk("nanjing", "ជៀនយៀ (ណានជីង)", "Jianye (Nanjing), capital of Wu", 0.5, "l"),
   mk("oceo", "ហ្វូណន", "Funan", 0.5, "l"),
   dict(k="line", pts=[P_["nanjing"], (121, 27), P_["guangzhou"], (110, 18), (108, 12), P_["oceo"]], at=1.0, draw=2.5,
        ships=2), era("c. 245–250?", "ពាក់កណ្ដាលសតវត្សរ៍ទី ៣ (កាលបរិច្ឆេទ នៅជជែក)", 0.6)], badge="map")
PH("txt_liang_shu_ch54_funan_p067.jpg", ["c2"], z=(1.0, 1.25), fy=(0.3, 0.5), contain=True, badge="text")
S(["c3"], lambda: X.make_palace("golden", people=[grp(0.6, F(900, 1150, 330, "zh_envoy", "bow", 90, 1),
                                                      F(700, 1160, 320, "zh_envoy2", "present_scroll", 90, 2),
                                                      F(1500, 1150, 340, "f_noble", "talk", -90, 3),
                                                      F(1750, 1160, 320, "f_man", "offer", -90, 4))]),
  cam((1200, 900, 1.1), (1200, 880, 1.2)), badge="recon")
ZH(["c4"], "貢賦以金銀珠香。亦有書記府庫，文字有類于胡。",
   "Taxes are paid in gold, silver, pearls and perfumes. They also have books, records and storehouses; their writing "
   "resembles that of the Hu [peoples to the west].", "Jin shu 晉書, ch. 97 (compiled 648 CE)")
S(["c5"], lambda: cards.text_card([("ការពិពណ៌នាដោយការរើសអើង ប្រាប់អំពីអ្នកសង្កេត", 40, "#f6ecd6", KM_SANS, "Bold"),
                                   ("Prejudiced descriptions tell us about the observers", 32, "#e0d0b0", EN_SERIF, "SemiBold")],
                                  under=X.make_palace("golden")), badge="recon")
PH("txt_funan_envoy_painting_liang.png", ["c6"], z=(1.0, 1.12), contain=True, badge="comparison",
   cap="A Funan envoy in a 10th-century Chinese painting after Liang originals: not an eyewitness portrait")

# ================================================================ 7. FAITH AND IDEAS FROM INDIA
CH(7, "ជំនឿ និងគំនិតពីឥណ្ឌា", "Faith and Ideas from India", "4th – 6th century CE", under=lambda: X.make_temple("golden"),
   music="india", amb="temple")
GUIDE("q7", lambda m: X.make_port("day", ships=True, people=[grp(0.6, tonle(1150, 1180, 300, "ask", 40),
                                                                 F(900, 870, 200, "brahmin", "walk_slow", 90, 1, vx=10),
                                                                 F(780, 870, 195, "monk", "walk_slow", 90, 2, vx=10))],
                                  mouth_fn=m), cam((1100, 950, 1.3), (1150, 930, 1.3)), note=GUIDE_NOTE, trans="lotus")
S(["i1"], lambda: X.make_temple("golden", people=[grp(0.6, F(900, 1150, 330, "brahmin", "pray", 90, 1),
                                                      F(1450, 1160, 320, "f_noble", "kneel_pray", -90, 2),
                                                      F(1800, 1150, 320, "monk", "idle", -90, 3))]),
  cam((1200, 850, 1.05), (1200, 830, 1.15)), badge="recon")
ZH(["i2"], "其後王憍陳如，本天竺婆羅門也……復改制度，用天竺法。",
   "A later king, Qiaochenru [Kaundinya], was originally a brahmin of India… He changed the institutions and adopted the laws of India.",
   "Liang shu 梁書, ch. 54 (compiled 636 CE)")
S(["i3"], lambda: cards.claim_board("កៅណ្ឌិន្យទី ២ ជានរណា?", "Who was 'Kaundinya II'?", [
    ("record", "ឯកសារចិន៖ ព្រាហ្មណ៍មកពីឥណ្ឌា", "Chinese record: a brahmin from India"),
    ("debated", "ឬ ស្ដេចក្នុងស្រុក យកឈ្មោះ និងរឿងព្រេង កៅណ្ឌិន្យ មកប្រើ", "Or local kings adopting the Kaundinya name and legend")]),
  pre=0.4, post=1.2)
S(["i4"], lambda: cards.text_card([("ជ័យវរ្ម័ន · រុទ្រវរ្ម័ន · គុណវរ្ម័ន", 52, "#f2cf7a", KM_SANS, "Bold"),
                                   ("Jayavarman · Rudravarman · Gunavarman", 36, "#f6ecd6", EN_SERIF, "SemiBold"),
                                   ("-varman: Sanskrit 'armour, protector'", 28, "#e0d0b0", EN_SERIF, "SemiBold")]),
  badge=None)
MC("ins_k5_go_thap_stele.jpg", ["i5"], km="សិលាចារឹកហ្គោថាប (K.5) នៃព្រះអង្គម្ចាស់ គុណវរ្ម័ន", badge="inscription",
   note="Sanskrit, undated; script of the 5th century. Mentions the lineage of Kaundinya and a footprint of Vishnu.")
MC("oe_vishnu_oc_eo_hcmc.jpg", ["i6"], km="ព្រះវិស្ណុ មកពីអូរកែវ", note="Late Funan or early pre-Angkorian.")

# ================================================================ 8. LIFE, ART AND SOCIETY
CH(8, "ជីវិត សិល្បៈ និងសង្គម", "Life, Art and Society", "from Chinese accounts and archaeology",
   under=lambda: X.make_workshop("day"), music="life", amb="workshop")
GUIDE("q8", lambda m: X.make_workshop("day", people=[grp(0.6, tonle(1200, 1180, 290, "ask", 30),
                                                         F(700, 1050, 260, "f_smith", "craft", 90, 1))], mouth_fn=m),
      cam((1200, 960, 1.35), (1180, 950, 1.4)), note=GUIDE_NOTE, trans="ink")
S(["l1"], lambda: X.make_lowland("golden", people=[grp(0.65, F(800, 1150, 290, "f_noble", "walk_slow", 90, 1, vx=18),
                                                       F(1100, 1160, 280, "f_man", "walk", 90, 2, vx=20),
                                                       F(1600, 1170, 280, "f_woman", "walk_slow", -90, 3, vx=-16))]),
  cam((1200, 900, 1.15), (1250, 900, 1.25)), badge="recon", note="Clothing after Liang shu & Nan Qi shu descriptions (reconstruction)")
MC("oe_earring_moulds.jpg", ["l2"], km="ពុម្ពថ្ម សម្រាប់ចាក់ក្រវិល")
MC("oe_house_piles_wood_angiang.jpg", ["l3"], km="សសរផ្ទះឈើ សម័យហ្វូណន",
   note="Excavated house piles: Chinese records describe raised houses.")
PH("pin_kongpeat_angkor_wat_relief.jpg", ["l4"], z=(1.0, 1.15), badge="comparison",
   cap="LATER COMPARISON: gong chime on an Angkor Wat relief (16th c.); Funan's instruments are unknown")
MC("pd_vishnu_eight_arm_nmc.jpg", ["l5"], km="ព្រះវិស្ណុ ប្រាំបីដៃ នៃភ្នំដា", focus=(0.5, 0.35))
MC("pd_krishna_govardhan_cleveland.jpg", ["l6"], km="ព្រះក្រឹស្ណ លើកភ្នំគោវធ៌ន", note="Funan or early Chenla? Dating debated.")

# ================================================================ 9. THE LAST GREAT KINGS
CH(9, "ស្ដេចដ៏អស្ចារ្យចុងក្រោយ", "The Last Great Kings", "484 – 539 CE", under=lambda: X.make_palace("dusk"),
   music="kings", amb="palace")
GUIDE("q9", lambda m: X.make_palace("dusk", people=[grp(0.6, tonle(1200, 1200, 290, "ask", 20))], mouth_fn=m),
      cam((1200, 950, 1.4), (1200, 940, 1.45)), note=GUIDE_NOTE, trans="lotus")
M(["k1"], (110.0, 20.0, 28.0), (110.0, 21.0, 24.0),
  [mk("oceo", "ហ្វូណន", "Funan", 0.4, "l"), mk("nanjing", "ណានជីង", "Nanjing (Jiankang)", 0.6, "l"),
   dict(k="line", pts=[P_["oceo"], (108, 12), (110, 18), P_["guangzhou"], (121, 27), P_["nanjing"]], at=1.0, draw=2.5,
        ships=2), era("484 CE", "ឆ្នាំ ៤៨៤", 0.5)])
S(["k2"], lambda: X.make_palace("dusk", people=[grp(0.6, F(1000, 1150, 330, "monk", "present_scroll", 90, 1),
                                                    F(1550, 1150, 340, "zh_envoy", "idle", -90, 2),
                                                    F(1750, 1160, 330, "zh_scribe", "read", -90, 3))]),
  cam((1250, 900, 1.15), (1250, 880, 1.25)), badge="recon", note="Gifts listed in the Nan Qi shu; scene reconstructed")
PH("txt_liang_shu_ch54_funan_p070.jpg", ["k3"], z=(1.0, 1.2), contain=True, badge="text")
S(["k4"], lambda: X.make_monastery(people=[grp(0.5, F(600, 1010, 300, "monk", "write", 90, 1),
                                               F(1200, 1010, 300, "monk", "read", 90, 2),
                                               F(1800, 1010, 300, "zh_scribe", "write", -90, 3))]),
  cam((1200, 850, 1.05), (1200, 850, 1.15)), badge="recon", amb="interior")
S(["k5"], lambda: X.make_monastery(people=[grp(0.5, F(600, 1010, 300, "monk", "write", 90, 1),
                                               F(1200, 1010, 300, "monk", "read", 90, 2),
                                               F(1800, 1010, 300, "zh_scribe", "write", -90, 3))]),
  cam((800, 950, 1.5), (1500, 950, 1.5)), badge="recon")
PH("ins_ta_prohm_tonle_bati_site.jpg", ["k6"], z=(1.0, 1.12),
   cap="Ta Prohm, Tonle Bati: find-site of inscription K.40 (the temple seen today is 12th-century)")
M(["k7"], (110.0, 20.0, 28.0), (106.0, 14.0, 18.0),
  [mk("oceo", "ហ្វូណន", "Funan", 0.4, "l"), mk("nanjing", "ណានជីង", "Nanjing", 0.4, "l"),
   dict(k="line", pts=[P_["oceo"], (108, 12), (110, 18), P_["guangzhou"], (121, 27), P_["nanjing"]], at=0.4, draw=1.5,
        ships=1), era("539 CE", "ឆ្នាំ ៥៣៩ · ស្ដេចចុងក្រោយ ដែលមានឈ្មោះ", 0.5)])

# ================================================================ 10. DECLINE AND THE RISE OF CHENLA
CH(10, "ការធ្លាក់ចុះ និងការរីកឡើងនៃចេនឡា", "Decline and the Rise of Chenla", "6th – 7th century CE",
   under=lambda: X.make_chenla("golden"), music="decline", amb="farm")
GUIDE("q10", lambda m: X.make_port("dusk", ships=False, people=[grp(0.6, tonle(1150, 1180, 300, "ask", 50, expr="worry"))],
                                   mouth_fn=m), cam((1200, 950, 1.35), (1250, 930, 1.3)), note=GUIDE_NOTE, trans="ripple")
M(["d1"], (102.0, 7.0, 30.0), (102.0, 7.0, 26.0),
  [dict(k="line", pts=[P_["oceo"], (103.5, 9.6), (101.0, 9.6), P_["dunsun"]], at=0.0, draw=0.1, color="#9a8a6a",
        dash=[6, 10]),
   dict(k="line", pts=[(88, 6), (96, 5.5), (100.5, 2.5), (103.8, 1.3), (106, 4), (110, 12), P_["guangzhou"]], at=1.2,
        draw=3.0, ships=3, color="#f0d58a"),
   dict(k="label", lon=101.0, lat=0.5, km="ច្រកម៉ាឡាកា", en="Strait of Malacca", at=2.5, size=24),
   dict(k="note", km="សម្មតិកម្ម៖ ផ្លូវសមុទ្រថ្មី រំលងឆ្នេរហ្វូណន", en="Hypothesis: new direct routes bypassed Funan's coast",
        cls="hypothesis", at=3.0, x=80, y=800)], badge="map_recon")
M(["d2"], (105.3, 12.0, 8.0), (105.3, 12.6, 7.0),
  [dict(k="blob", pts=FUNAN_CORE, at=0.0, grow=0.1, fill="#9a8a6a", fa=0.18),
   dict(k="blob", pts=CHENLA_ZONE, at=1.2, fill="#4f8a72", fa=0.3),
   mk("spk", "សំបូរព្រៃគុក", "Sambor Prei Kuk", 2.0, "r"), mk("watphu", "វត្តភូ", "Wat Phu", 2.4, "r")], badge="map_recon",
  note="Soft zones only: no borders are known for Funan or Chenla")
ZH(["d3"], "真臘國……本扶南之屬國也……至質多斯那，遂兼扶南而有之。",
   "The kingdom of Zhenla [Chenla]… was originally a vassal of Funan… by the time of Citrasena it had annexed Funan.",
   "Sui shu 隋書, ch. 82 (compiled 636 CE)")
PH("cl_sambor_prei_kuk_n16.jpg", ["d4"], z=(1.0, 1.12))
S(["d5"], lambda: cards.claim_board("ការវាយដណ្ដើម ឬការផ្លាស់ប្ដូរ?", "Conquest, or gradual change?", [
    ("record", "ស៊ុយស៊ូ៖ ចិត្រសេន វាយយកហ្វូណន", "Sui shu: Citrasena annexed Funan"),
    ("debated", "អ្នកប្រវត្តិវិទូខ្លះ៖ មជ្ឈមណ្ឌលអំណាច ផ្លាស់ប្ដូរបន្តិចម្ដងៗ", "Some historians: power shifted gradually"),
    ("inscription", "K.53 (៦៦៧ គ.ស.)៖ គ្រួសារមួយ បម្រើរុទ្រវរ្ម័ន រួចស្ដេចចេនឡា", "K.53 (667 CE): one family served Rudravarman, then Chenla kings")]),
  pre=0.4, post=1.5)

# ================================================================ CLOSING: LEGACY
CHAPTERS.append(len(SHOTS))
S([], lambda: cards.chapter_card(None, "កេរដំណែល", "Legacy", "from Funan towards Angkor",
                                 X.make_delta("sunset" if False else "golden")), pre=0, post=4.2, xin=1.4, trans="lotus",
  music="legacy", amb="delta", tag="chapter")
GUIDE("q11", lambda m: X.make_delta("golden", people=[grp(0.6, tonle(1250, 1010, 320, "ask", 30, boat=True, expr="worry"))],
                                    mouth_fn=m), cam((1250, 900, 1.6), (1250, 890, 1.7)), note=GUIDE_NOTE)
M(["z1"], (105.0, 12.5, 9.0), (105.0, 12.0, 8.0),
  [dict(k="blob", pts=FUNAN_CORE, at=0.2, fill="#d8aa4a", until=4.0), dict(k="blob", pts=CHENLA_ZONE, at=2.5, fill="#4f8a72"),
   mk("ab", "អង្គរបុរី", "Angkor Borei", 0.6, "l"), mk("spk", "សំបូរព្រៃគុក", "Sambor Prei Kuk", 3.0, "r")],
  badge="map_recon")
PH("ab_angkor_borei_museum.jpg", ["z2"], z=(1.0, 1.1), contain=True,
   cap="Angkor Borei Archaeological Museum, Takeo (the 611 CE inscription K.557/600 comes from Angkor Borei)")
S(["z3"], lambda: X.make_delta("golden"), cam((1000, 700, 1.1), (1500, 680, 1.0)), badge="recon")
GUIDE("t12", lambda m: X.make_delta("golden", people=[grp(0.6, tonle(1250, 1010, 320, "release", 70, boat=True, expr="calm"))],
                                    mouth_fn=m), cam((1250, 930, 1.55), (1300, 900, 1.3)), note=GUIDE_NOTE, post=5.0,
      fade_out=3.0)


# ================================================================ CREDITS
def credit_blocks():
    imgs = []
    for f, e in sorted(man().items()):
        if f in USED:
            imgs.append("%s — %s" % ((e.get("object_name") or f)[:80], e.get("attribution_line") or e.get("licence")))
    return [("ហ្វូណន · នគរភ្នំ · FUNAN – KINGDOM OF THE MOUNTAIN",
             ["An educational documentary in paper-cut 2D animation, maps and authentic evidence",
              "Narration: Khmer · Subtitles: English",
              "Neang Tonle is a fictional guide, not a historical person"]),
            ("PRIMARY SOURCES", [
                "Liang shu 梁書 ch. 54 (636) · Nan Qi shu 南齊書 ch. 58 (c. 537) · Jin shu 晉書 ch. 97 (648)",
                "Sanguozhi 三國志 (c. 290) · Song shu 宋書 (488) · Sui shu 隋書 ch. 82 (636) · Xin Tang shu 新唐書 (1060)",
                "Xu Gaoseng zhuan 續高僧傳 (645) · Kang Tai fragments in Taiping yulan 太平御覽 (983)",
                "Inscriptions K.5 (Go Thap), K.40 (Ta Prohm of Bati), K.875, K.53, K.557/600, K.286; Cham C.96 (My Son, 658)"]),
            ("SCHOLARSHIP", [
                "P. Pelliot, 'Le Fou-nan', BEFEO 3 (1903) · G. Coedès, The Indianized States of Southeast Asia (1968)",
                "M. Vickery, 'Funan reviewed', BEFEO 90–91 (2003–04) · C. Jacques (1979) · K.-H. Golzio (2023)",
                "L. Malleret, L'archéologie du delta du Mékong (1959–63) · P.-Y. Manguin (2009)",
                "M. Stark / LOMAP; Bishop, Sanderson & Stark 2004, J. Archaeol. Sci. · Wang, Hung et al. 2023, Science Advances",
                "O. W. Wolters · K. Hall · H. Kulke · N. Dowling (1999) · P. Lavy (2003) · B. Porte (2016) · Borell (2008, 2023)",
                "Khmer sources checked: Khmer Wikipedia (នគរភ្នំ etc.), RFA Khmer, VAYO FM, Kampuchea Thmey"]),
            ("ARCHIVAL IMAGES", imgs or ["None"]),
            ("MAP DATA", ["Terrain: SRTM-derived terrarium tiles (Mapzen / AWS) · Natural Earth (public domain)",
                          "Modern borders shown faintly for orientation only. Funan's extent is not known."]),
            ("NOTE", ["Paper-cut scenes are artistic reconstructions inspired by Sbek shadow-puppet art.",
                      "Legend, Chinese record, inscription, archaeology and debate are labelled throughout.",
                      "Khmer narration should be reviewed by a native-speaking historian before publication."])]


S([], lambda: cards.scrolling_credits(credit_blocks()), pre=0, post=40.0, xin=1.5, music="credits", tag="credits",
  amb="none")


# ---------------------------------------------------------------- timeline assembly
def narr_wav(key):
    from narrate import wav_for
    return wav_for(key)


_DUR = {}


def line_dur(key):
    if key not in _DUR:
        p = narr_wav(key)
        _DUR[key] = sf.info(p).duration if os.path.exists(p) else len(N[key][0]) * 0.0747
    return _DUR[key]


# chapter start targets (s) from the brief: 0:45, 2:00, 3:30, 5:30, 6:45, 8:00, 9:15, 10:45, 12:00, 13:15, 14:15
TARGETS = [45, 120, 210, 330, 405, 480, 555, 645, 720, 795, 855]
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
    """Spread spare time inside each chapter so chapters start on the brief's schedule (never cut narration)."""
    global _EXTRA
    if _EXTRA is not None:
        return _EXTRA
    extra = {}
    bounds = [0] + CHAPTERS + [len(SHOTS) - 1]   # last segment ends at the credits
    for k, tgt in enumerate(TARGETS + [900]):
        starts = _layout(extra)
        seg = range(bounds[k], bounds[k + 1])
        nxt = bounds[k + 1]
        deficit = tgt - starts[nxt]
        body = [i for i in seg if SHOTS[i]["lines"]]
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
