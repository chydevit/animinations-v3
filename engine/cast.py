"""2.5D cel-shaded figure rig (paper cut-out finish) for the Funan cast.

Every figure is a small 3D skeleton (units = head heights, y up, z = the way the character faces) projected
orthographically at a view yaw, so a character reads identically in front, 3/4, side and back views.

  draw(ctx, x, y, h, who, pose="idle", t=0.0, yaw=90, expr=None, P=None, mouth=None, cutout=True)
    x, y  ground point between the feet (px); h  standing height (px)
    yaw   0 = facing the viewer, 90 = facing screen-right, -90 = screen-left, 180 = back to the viewer
    P     palette dict with light / shadow / haze (or None for neutral light)
    mouth 0..1 overrides the mouth opening (lip-sync from the voice envelope)
    cutout draws a soft offset shadow first, so figures sit on the set like layered paper

Costumes follow what Chinese records and archaeology allow (see docs/fact_sheet.md): wrapped lower cloths,
the poncho-like cloth noted for women in the Liang shu, gold earrings and glass beads of Oc Eo type; Chinese
envoys in Han-Wu period robes; an Indian merchant and a Brahmin; Buddhist monks.  All are reconstructions.
"""
import math

from core import ellipse, hexc, mix, src

SKIN = dict(a="#8a5a3a", b="#9b6744", c="#a87452", d="#b5805c", e="#7a4e33", f="#c99a74")
OUT = "#2a1a12"
GOLD = "#e0b84a"
BRONZE = "#b5853a"
SHELL = "#efe6d2"
CARNELIAN = "#c4502a"
GLASS = "#3f6fa8"

ADULT_M = dict(thigh=1.78, shin=1.62, torso=2.5, neck=0.28, ua=1.32, fa=1.18, hand=0.42, foot=0.62,
               sh=0.84, hip=0.31, hipw=0.6, head_rx=0.4, head_ry=0.53, chest=0.8, waist=0.6, depth=0.5)
ADULT_F = dict(ADULT_M, thigh=1.72, shin=1.56, torso=2.42, ua=1.26, fa=1.12, sh=0.7, hip=0.3, hipw=0.64,
               head_rx=0.38, head_ry=0.51, chest=0.68, waist=0.53, depth=0.46)
ELDER_M = dict(ADULT_M, torso=2.38, sh=0.8, chest=0.76, waist=0.62)
ELDER_F = dict(ADULT_F, torso=2.32, chest=0.66, waist=0.56)
TEEN_F = dict(thigh=1.42, shin=1.3, torso=2.0, neck=0.24, ua=1.08, fa=0.96, hand=0.36, foot=0.52, sh=0.6,
              hip=0.26, hipw=0.5, head_rx=0.39, head_ry=0.51, chest=0.56, waist=0.46, depth=0.38)
CHILD = dict(thigh=1.02, shin=0.92, torso=1.72, neck=0.2, ua=0.88, fa=0.78, hand=0.3, foot=0.42, sh=0.56,
             hip=0.22, hipw=0.44, head_rx=0.38, head_ry=0.5, chest=0.5, waist=0.44, depth=0.34)
FEMALE_B = ("ADULT_F", "TEEN_F")


def body_height(B):
    return B["thigh"] + B["shin"] + 0.1 + B["torso"] + B["neck"] + B["head_ry"] * 1.9


CAST = {
    # --- the guide (fictional) ---------------------------------------------------------------------------------
    "tonle": dict(km="នាងទន្លេ", en="Neang Tonle (fictional guide)", era="funan", B=TEEN_F, skin="c", hair="bun_side",
                  hair_c="#15100c", wrap=("skirt_knee", "#b5562f", "stripes"), top=("poncho", "#e3a1a8"),
                  orn=["glass_neck", "gold_ear", "bronze_bangle"], face=dict(brow=0.7, jaw=0.86, nose=0.82, lips=1.1,
                                                                           child=True)),
    # --- people of Funan ------------------------------------------------------------------------------------------
    "f_man": dict(km="បុរសហ្វូណន", en="Funan man", era="funan", B=ADULT_M, skin="b", hair="bun", hair_c="#16110d",
                  wrap=("skirt_knee", "#7e3520", "stripes"), orn=["gold_ear"], face=dict(brow=1.1, jaw=1.05, nose=1.05)),
    "f_woman": dict(km="ស្ត្រីហ្វូណន", en="Funan woman", era="funan", B=ADULT_F, skin="c", hair="bun",
                    hair_c="#15100c", wrap=("skirt_long", "#1f5b4f", "stripes"), top=("poncho", "#c08a3e"),
                    orn=["glass_neck", "gold_ear"], face=dict(brow=0.8, jaw=0.92, nose=0.95, lips=1.1)),
    "f_elder": dict(km="ចាស់ទុំ", en="Elder", era="funan", B=ELDER_M, skin="a", hair="bun_grey", hair_c="#8a847c",
                    wrap=("skirt_long", "#8a6a3c", "stripes"), orn=["gold_ear"],
                    face=dict(brow=1.2, jaw=1.0, nose=1.1, age=1.0, beard=True)),
    "f_grandma": dict(km="លោកយាយ", en="Grandmother", era="funan", B=ELDER_F, skin="d", hair="bun_grey", hair_c="#8a847c",
                      wrap=("skirt_long", "#5a3a2a", "stripes"), top=("poncho", "#8a6a3c"), orn=["gold_ear"],
                      face=dict(brow=0.9, jaw=0.95, nose=1.0, age=1.0)),
    "f_boatman": dict(km="អ្នកអុំទូក", en="Boatman", era="funan", B=ADULT_M, skin="e", hair="tied_back", hair_c="#16110d",
                      wrap=("loin", "#8a6a3c"), orn=[], face=dict(brow=1.2, jaw=1.1, nose=1.1)),
    "f_smith": dict(km="ជាងមាស", en="Goldsmith", era="funan", B=ADULT_M, skin="d", hair="topknot", hair_c="#16110d",
                    wrap=("skirt_knee", "#5a3a2a", "stripes"), orn=["gold_ear", "bronze_bangle"],
                    face=dict(brow=1.1, jaw=1.0, nose=1.0)),
    "f_child": dict(km="ក្មេង", en="Child", era="funan", B=CHILD, skin="b", hair="short", hair_c="#16110d",
                    wrap=("loin", "#c08a3e"), orn=[], face=dict(brow=0.7, jaw=0.85, nose=0.8, child=True)),
    "f_noble": dict(km="អភិជន", en="Noble (reconstruction)", era="funan", B=ADULT_M, skin="c", hair="topknot",
                    hair_c="#16110d", wrap=("skirt_long", "#b5562f", "stripes"), top=("sash", "#d8aa4a"),
                    orn=["gold_ear", "gold_neck"], face=dict(brow=1.1, jaw=1.0, nose=1.0)),
    # --- visitors ---------------------------------------------------------------------------------------------------
    "zh_envoy": dict(km="ទូតចិន", en="Chinese envoy (Wu, 3rd c.)", era="china", B=ADULT_M, skin="f", hair="guan",
                     hair_c="#16110d", wrap=("robe", "#2e4a6a"), top=("robe_top", "#2e4a6a"), orn=[],
                     face=dict(brow=1.0, jaw=0.95, nose=0.9, beard=True)),
    "zh_envoy2": dict(km="ទូតចិន", en="Chinese envoy (Wu, 3rd c.)", era="china", B=ADULT_M, skin="f", hair="guan",
                      hair_c="#16110d", wrap=("robe", "#6a2e2a"), top=("robe_top", "#6a2e2a"), orn=[],
                      face=dict(brow=0.9, jaw=0.95, nose=0.9)),
    "zh_scribe": dict(km="អាចារ្យចិន", en="Chinese scribe", era="china", B=ADULT_M, skin="f", hair="bun",
                      hair_c="#16110d", wrap=("robe", "#5a5a4a"), top=("robe_top", "#5a5a4a"), orn=[],
                      face=dict(brow=0.9, jaw=0.95, nose=0.9)),
    "in_merchant": dict(km="ពាណិជ្ជករឥណ្ឌា", en="Indian merchant", era="india", B=ADULT_M, skin="e", hair="turban",
                        hair_c="#e8e0cc", wrap=("skirt_knee", "#efe6d2"), top=("uttariya", "#c08a3e"),
                        orn=["gold_ear"], face=dict(brow=1.2, jaw=1.05, nose=1.15, beard=True)),
    "brahmin": dict(km="ព្រាហ្មណ៍", en="Brahmin", era="india", B=ADULT_M, skin="d", hair="jata", hair_c="#2a2420",
                    wrap=("skirt_long", "#f1ead8"), top=("thread", "#f6f0e0"), orn=[],
                    face=dict(brow=1.1, jaw=1.0, nose=1.1, beard=True)),
    "monk": dict(km="ព្រះសង្ឃ", en="Buddhist monk", era="india", B=ADULT_M, skin="c", hair="shaved", hair_c="#3a2a22",
                 wrap=("robe", "#c9782a"), top=("robe_monk", "#d0862e"), orn=[], face=dict(brow=0.9, jaw=1.0, nose=1.0)),
    "sailor": dict(km="នាវិក", en="Sailor", era="funan", B=ADULT_M, skin="b", hair="cloth_head", hair_c="#c9b48a",
                   wrap=("loin", "#5a4a3a"), orn=[], face=dict(brow=1.2, jaw=1.1, nose=1.05)),
}

EXPR = {  # brow raise, brow tilt (inner up +), mouth curve (+ smile), mouth open, eye open
    "neutral": (0.0, 0.0, 0.0, 0.0, 1.0),
    "smile": (0.02, 0.0, 1.0, 0.15, 0.85),
    "focus": (-0.03, -0.5, -0.1, 0.0, 0.75),
    "surprise": (0.08, 0.2, 0.0, 0.7, 1.25),
    "worry": (0.02, 0.8, -0.6, 0.05, 0.95),
    "sad": (-0.01, 0.9, -0.9, 0.0, 0.7),
    "call": (0.04, 0.0, 0.2, 0.9, 1.05),
    "calm": (0.0, 0.1, 0.3, 0.0, 0.6),
    "wonder": (0.06, 0.4, 0.4, 0.25, 1.15),
}


# ------------------------------------------------------------------ poses
def _walk(t, seed, k=1.0, amp=0.42, arm=0.32, lean=0.06):
    ph = 2 * math.pi * t * 0.95 * k + seed
    s, c = math.sin(ph), math.cos(ph)
    sw = lambda x: 0.08 + 0.85 * max(0.0, x) ** 1.4
    return dict(lean=lean, neck=-0.02, l_hf=amp * s, l_k=sw(c), r_hf=-amp * s, r_k=sw(-c),
                l_sf=-arm * s, l_e=0.25, r_sf=arm * s, r_e=0.25, l_sa=0.08, r_sa=0.08)


def _strike(t, f=1.3, seed=0):
    x = (t * f + seed * 0.13) % 1.0
    return (x / 0.25) ** 2 if x < 0.25 else 1 - (x - 0.25) / 0.75


def pose_at(name, t=0.0, seed=0):
    s = math.sin
    br = s(t * 1.7 + seed) * 0.012
    P = dict(lean=0.02 + br, neck=0.0, hyaw=0.0, l_hf=0.0, l_ha=0.05, l_k=0.05, r_hf=0.0, r_ha=0.05, r_k=0.05,
             l_sf=0.05, l_sa=0.1, l_e=0.12, r_sf=0.02, r_sa=0.1, r_e=0.12, root=None, props={}, mouth=0.0)
    if name in ("idle", "stand"):
        P.update(l_sf=0.04 + 0.02 * s(t * 0.8 + seed), r_sf=0.0 + 0.02 * s(t * 0.7 + seed + 1), neck=0.02 * s(t * 0.4))
    elif name == "walk":
        P.update(_walk(t, seed))
    elif name == "walk_slow":
        P.update(_walk(t, seed, 0.7, 0.32, 0.22))
    elif name == "carry_pot_head":
        P.update(_walk(t, seed, 0.75, 0.3, 0.0))
        P.update(l_sf=0.25, l_sa=1.2, l_e=2.1, r_sf=0.25, r_sa=1.2, r_e=2.1, neck=-0.02, props=dict(head="pot"))
    elif name == "carry_shoulder":   # pole over the shoulder with two baskets
        P.update(_walk(t, seed, 0.8, 0.34, 0.15))
        P.update(r_sf=1.0, r_e=1.9, r_sa=0.2, props=dict(pole=True))
    elif name == "carry_box":
        P.update(_walk(t, seed, 0.75, 0.3, 0.0))
        P.update(l_sf=0.9, l_e=0.9, r_sf=0.9, r_e=0.9, l_sa=0.25, r_sa=0.25, props=dict(both="box"))
    elif name == "paddle":   # standing paddle stroke in a boat
        k = s(t * 1.6 + seed)
        P.update(lean=0.25 + 0.1 * k, neck=0.1, l_hf=0.2, l_k=0.3, r_hf=-0.1, r_k=0.2,
                 r_sf=0.7 + 0.5 * k, r_e=0.4, l_sf=1.4 + 0.4 * k, l_e=0.3, props=dict(r=("oar", (0, -0.95, -0.25 + 0.4 * k))))
    elif name == "pole_boat":
        k = s(t * 0.9 + seed)
        P.update(lean=0.3 + 0.1 * k, l_hf=0.35, l_k=0.4, r_hf=-0.25, r_k=0.2, r_sf=1.2 + 0.3 * k, r_e=0.6,
                 l_sf=1.5 + 0.3 * k, l_e=0.4, props=dict(r=("pole", (0, -0.98, -0.2))))
    elif name == "offer":
        P.update(ua=0, l_sf=1.0, l_e=0.6, r_sf=1.0, r_e=0.6, l_sa=0.2, r_sa=0.2, lean=0.06, props=dict(both="tray"))
    elif name == "present_scroll":
        P.update(l_sf=1.1, l_e=0.4, r_sf=1.1, r_e=0.4, l_sa=0.25, r_sa=0.25, lean=0.12, neck=0.1,
                 props=dict(both="scroll"))
    elif name == "bow":
        P.update(lean=0.55, neck=0.3, l_sf=0.6, l_e=1.3, r_sf=0.6, r_e=1.3, l_sa=-0.05, r_sa=-0.05)
    elif name == "pray":
        P.update(l_sf=0.55, l_e=2.3, r_sf=0.55, r_e=2.3, l_sa=-0.05, r_sa=-0.05, neck=0.12)
    elif name == "kneel_pray":
        P.update(lean=0.1, root=dict(y=0.95), l_hf=1.55, l_k=2.75, r_hf=1.55, r_k=2.75,
                 l_sf=0.55, l_e=2.3, r_sf=0.55, r_e=2.3, neck=0.15)
    elif name == "write":
        k = s(t * 6.0 + seed)
        P.update(lean=0.3, root=dict(y=0.62), l_hf=1.5, l_k=2.5, r_hf=1.45, r_k=2.4, l_ha=0.75, r_ha=0.75,
                 neck=0.45, l_sf=0.85, l_e=1.0, r_sf=0.9, r_e=0.9 + 0.05 * k, props=dict(l=("tablet", None), r=("brush", None)))
    elif name == "read":
        P.update(neck=0.35, l_sf=0.9, l_e=1.2, r_sf=0.9, r_e=1.2, l_sa=0.15, r_sa=0.15, props=dict(both="scroll"))
    elif name == "sit":
        P.update(lean=0.12, root=dict(y=0.62), l_hf=1.5, l_k=2.5, r_hf=1.45, r_k=2.4, l_ha=0.75, r_ha=0.75,
                 l_sf=0.55, l_e=0.7, r_sf=0.6, r_e=0.6, neck=0.05 * s(t * 0.4 + seed))
    elif name == "sit_talk":
        k = s(t * 2.1 + seed)
        P.update(lean=0.12, root=dict(y=0.62), l_hf=1.5, l_k=2.5, r_hf=1.45, r_k=2.4, l_ha=0.75, r_ha=0.75,
                 l_sf=0.55, l_e=0.7, r_sf=0.95 + 0.15 * k, r_e=1.2, r_sa=0.2, mouth=max(0, s(t * 9 + seed)) * 0.8)
    elif name == "kneel":
        P.update(lean=0.15, root=dict(y=0.95), l_hf=1.55, l_k=2.75, r_hf=1.55, r_k=2.75, l_ha=0.2, r_ha=0.2,
                 l_sf=0.35, l_e=0.9, r_sf=0.35, r_e=0.9, neck=0.2)
    elif name == "craft":   # seated craftsman working at a low anvil (beads / gold)
        k = _strike(t, 1.6, seed)
        P.update(lean=0.42, neck=0.4, root=dict(y=0.62), l_hf=1.5, l_k=2.5, r_hf=1.45, r_k=2.4, l_ha=0.75, r_ha=0.75,
                 l_sf=1.0, l_e=0.6, r_sf=1.5 - 0.5 * k, r_e=1.0 - 0.4 * k, props=dict(r=("hammer_small", None)))
    elif name == "harvest":
        k = s(t * 1.2 + seed)
        P.update(lean=0.75, neck=0.25, l_hf=0.6, l_k=0.6, r_hf=0.1, r_k=0.4, r_sf=1.1 + 0.2 * k, r_e=0.3, l_sf=0.9,
                 l_e=0.9, props=dict(r=("sickle", None)))
    elif name == "point":
        P.update(r_sf=1.55, r_e=0.05, r_sa=0.1, neck=-0.05)
    elif name == "talk":
        k = s(t * 1.8 + seed)
        P.update(r_sf=0.75 + 0.15 * k, r_e=1.1 + 0.2 * k, r_sa=0.25, l_sf=0.1, mouth=max(0, s(t * 9 + seed)) * 0.8)
    elif name == "ask":   # guide: one hand raised in a question
        k = s(t * 1.2 + seed)
        P.update(r_sf=1.2 + 0.08 * k, r_e=1.3, r_sa=0.35, l_sf=0.1, l_e=0.5, neck=-0.05 + 0.03 * k, hyaw=-20)
    elif name == "wave":
        k = s(t * 5 + seed)
        P.update(r_sf=2.5, r_e=0.5 + 0.3 * k, r_sa=0.4, l_sf=0.05)
    elif name == "release":   # kneeling, setting a lotus lamp on the water
        k = s(t * 0.5 + seed)
        P.update(lean=0.55 + 0.05 * k, root=dict(y=0.95), l_hf=1.55, l_k=2.75, r_hf=1.55, r_k=2.75,
                 l_sf=1.15, l_e=0.25, r_sf=1.1, r_e=0.3, neck=0.45, props=dict(both="lotus"))
    elif name == "shoot_bow":  # legend: Kaundinya's arrow (shadow-puppet scenes only)
        P.update(l_sf=1.57, l_e=0.0, l_sa=0.0, r_sf=1.57, r_e=2.2, r_sa=0.0, lean=-0.05, l_hf=0.35, r_hf=-0.3,
                 props=dict(l=("bow", None)))
    return P


# ------------------------------------------------------------------ geometry
def _dir_down(flex, abd, side):
    ca = math.cos(abd)
    return (side * math.sin(abd), -ca * math.cos(flex), ca * math.sin(flex))


def _lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


class _Proj:
    def __init__(self, x, y, U, yaw):
        self.x, self.y, self.U = x, y, U
        th = math.radians(yaw)
        self.c, self.s = math.cos(th), math.sin(th)

    def __call__(self, p):
        return (self.x + (p[0] * self.c + p[2] * self.s) * self.U, self.y - p[1] * self.U)

    def depth(self, p):
        return -p[0] * self.s + p[2] * self.c

    def vec(self, v):
        return (v[0] * self.c + v[2] * self.s, -v[1])


def skeleton(B, P):
    lean = P["lean"]
    up = (0.0, math.cos(lean), math.sin(lean))
    J = {}
    for side, sg in (("l", 1), ("r", -1)):
        hj = (sg * B["hip"], 0.0, 0.0)
        kn = _add(hj, _dir_down(P[side + "_hf"], P.get(side + "_ha", 0.05), sg), B["thigh"])
        an = _add(kn, _dir_down(P[side + "_hf"] - P[side + "_k"], P.get(side + "_ha", 0.05) * 0.6, sg), B["shin"])
        shin_ang = P[side + "_hf"] - P[side + "_k"]
        fdir = (0.0, -0.15, -1.0) if shin_ang < -1.1 else (0.0, 0.0, 1.0)
        J[side + "_hip"], J[side + "_knee"], J[side + "_ankle"], J[side + "_toe"] = hj, kn, an, _add(an, fdir, B["foot"])
    if P.get("root") and "y" in P["root"]:
        base = -P["root"]["y"]
    else:
        base = min(J["l_ankle"][1], J["r_ankle"][1], J["l_knee"][1] - 0.12, J["r_knee"][1] - 0.12) - 0.1
    for k in list(J):
        J[k] = (J[k][0], J[k][1] - base, J[k][2])
    pel = (0.0, -base, 0.0)
    J["pelvis"] = pel
    nk = _add(pel, up, B["torso"])
    J["neck"] = nk
    for side, sg in (("l", 1), ("r", -1)):
        sh = (sg * B["sh"], nk[1] - 0.28, nk[2] - 0.04)
        el = _add(sh, _dir_down(P[side + "_sf"], P[side + "_sa"], sg), B["ua"])
        wr = _add(el, _dir_down(P[side + "_sf"] + P[side + "_e"], P[side + "_sa"] * 0.7, sg), B["fa"])
        hd = _add(wr, _dir_down(P[side + "_sf"] + P[side + "_e"] * 1.1, P[side + "_sa"] * 0.6, sg), B["hand"] * 0.55)
        J[side + "_sh"], J[side + "_el"], J[side + "_wr"], J[side + "_hand"] = sh, el, wr, hd
    hl = lean + P.get("neck", 0.0)
    J["head"] = _add(nk, (0.0, math.cos(hl), math.sin(hl)), B["neck"] + B["head_ry"] * 0.82)
    return J


# ------------------------------------------------------------------ painting primitives
class _Paint:
    def __init__(self, ctx, U, light, shadow, haze, hz, outline=True, silhouette=None):
        self.ctx, self.U = ctx, U
        self.light, self.shadow, self.haze, self.hz = light, shadow, haze, hz
        self.lw = min(5.0, max(1.0, U * 0.045)) if outline else 0
        self.sil = silhouette
        self.L = (-0.62, -0.78)

    def col(self, c, k=0.0):
        if self.sil:
            return hexc(self.sil)
        c = hexc(c)
        if k > 0:
            c = mix(c, self.light, k)
        elif k < 0:
            c = mix(c, mix(self.shadow, c, 0.35), -k)
        if self.haze and self.hz:
            c = mix(c, self.haze, self.hz)
        return c

    def chain(self, segs, sk=0.42):
        ctx = self.ctx
        if self.lw:
            for path, color in segs:
                path(ctx)
                ctx.set_source_rgb(*self.col(OUT))
                ctx.set_line_width(self.lw * 2)
                ctx.set_line_join(1)
                ctx.stroke()
        lw, self.lw = self.lw, 0
        for path, color in segs:
            self.shape(path, color, sk=sk)
        self.lw = lw

    def shape(self, path, color, shift=None, sk=0.42, hi=0.0):
        ctx = self.ctx
        if self.lw:
            path(ctx)
            ctx.set_source_rgb(*self.col(OUT))
            ctx.set_line_width(self.lw * 2)
            ctx.set_line_join(1)
            ctx.stroke()
        path(ctx)
        if self.sil:
            ctx.set_source_rgb(*self.col(color))
            ctx.fill()
            return
        ctx.save()
        ctx.clip()
        ctx.set_source_rgb(*self.col(color, -sk))
        ctx.paint()
        dx, dy = shift if shift else (self.L[0] * self.U * 0.12, self.L[1] * self.U * 0.12)
        ctx.translate(dx, dy)
        path(ctx)
        ctx.set_source_rgb(*self.col(color))
        ctx.fill()
        if hi:
            ctx.translate(dx * 1.6, dy * 1.6)
            path(ctx)
            ctx.set_source_rgba(*self.col(color, 0.35), hi)
            ctx.fill()
        ctx.restore()


def _capsule_path(p0, p1, r0, r1):
    def path(ctx):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1e-6
        a0 = math.atan2(dx / L, -dy / L)
        ctx.new_path()
        ctx.arc(p0[0], p0[1], r0, a0, a0 + math.pi)
        ctx.arc(p1[0], p1[1], r1, a0 + math.pi, a0 + 2 * math.pi)
        ctx.close_path()
    return path


def _poly_path(pts, smooth_=False):
    def path(ctx):
        ctx.new_path()
        if smooth_ and len(pts) > 3:
            from core import spline
            spline(ctx, pts, close=True)
        else:
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.close_path()
    return path


def _ell_path(x, y, rx, ry, rot=0.0):
    def path(ctx):
        ctx.new_path()
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        ctx.scale(max(rx, 0.01), max(ry, 0.01))
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
    return path


# ------------------------------------------------------------------ the figure
def draw(ctx, x, y, h, who, pose="idle", t=0.0, yaw=90.0, expr=None, P=None, alpha=1.0, seed=0, hz=0.0,
         outline=True, silhouette=None, scale=1.0, mouth=None, cutout=True, perforate=False):
    if cutout and not silhouette:
        ctx.save()
        ctx.push_group()
        _draw(ctx, x + h * 0.022, y + h * 0.012, h, who, pose, t, yaw, expr, P, seed, hz, False, "#000000", scale, mouth)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(0.28 * alpha)
        ctx.restore()
    if alpha < 1 or perforate:
        ctx.push_group()
    _draw(ctx, x, y, h, who, pose, t, yaw, expr, P, seed, hz, outline, silhouette, scale, mouth)
    if perforate:   # Sbek-style punched holes: light shows through the leather
        from core import rng
        R = rng(seed + 3)
        ctx.save()
        ctx.set_operator(1)  # CLEAR
        for i in range(int(h * 0.9)):
            px = x + (R.random() - 0.5) * h * 0.36
            py = y - R.random() * h * 0.95
            ctx.arc(px, py, max(1.0, h * 0.0045), 0, 6.283)
            ctx.fill()
        ctx.restore()
    if alpha < 1 or perforate:
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(alpha)


def _draw(ctx, x, y, h, who, pose, t, yaw, expr, P, seed, hz, outline, silhouette, scale, mouth):
    C = CAST[who] if isinstance(who, str) else who
    B = C["B"]
    PO = pose_at(pose, t, seed) if isinstance(pose, str) else pose
    if mouth is not None:
        PO = dict(PO, mouth=mouth)
    U = h / body_height(B) * scale
    pr = _Proj(x, y, U, yaw)
    J = skeleton(B, PO)
    light = P["light"] if P else "#fff2dc"
    shadow = P["shadow"] if P else "#3a3040"
    haze = P["haze"] if P else None
    pa = _Paint(ctx, U, light, shadow, haze, hz, outline, silhouette)
    skin = SKIN.get(C["skin"], C["skin"])
    parts = []
    D = pr.depth
    female = B in (ADULT_F, TEEN_F, ELDER_F)
    wrap = C["wrap"]
    top = C.get("top")
    robe = wrap[0] == "robe"

    # ---- legs
    for side in ("l", "r"):
        hp, kn, an, toe = (J[side + k] for k in ("_hip", "_knee", "_ankle", "_toe"))
        dep = (D(kn) + D(an)) / 2 - 0.25

        def leg(hp=hp, kn=kn, an=an, toe=toe):
            calf = _lerp3(kn, an, 0.3)
            foot_c = "#3a2a20" if robe and C["era"] == "china" else skin
            pa.chain([(_capsule_path(pr(an), pr(toe), 0.12 * U, 0.09 * U), foot_c),
                      (_capsule_path(pr(calf), pr(an), 0.2 * U, 0.11 * U), skin),
                      (_capsule_path(pr(kn), pr(calf), 0.17 * U, 0.2 * U), skin),
                      (_capsule_path(pr(hp), pr(kn), 0.32 * U, 0.18 * U), skin)])
        parts.append((dep, leg))

    # ---- torso
    pel, nk = J["pelvis"], J["neck"]
    up = ((nk[0] - pel[0]) / B["torso"], (nk[1] - pel[1]) / B["torso"], (nk[2] - pel[2]) / B["torso"])
    secs = [(-0.06, B["hipw"] * 0.98, B["depth"] * 1.0, -0.04), (0.18, B["hipw"], B["depth"] * 1.02, -0.05),
            (0.42, B["waist"], B["depth"] * 0.88, 0.02),
            (0.66, B["chest"] * 0.95, B["depth"] * 1.0, 0.08 if female else 0.05),
            (0.84, B["chest"] * 1.04, B["depth"] * 0.98, 0.04), (0.95, B["sh"] * 0.92, B["depth"] * 0.8, 0.0),
            (1.03, 0.2, 0.2, 0.0)]

    def torso_pts(lo=0.0, hi=1.1, grow=1.0):
        L_, R_ = [], []
        for f, wx, wz, oz in secs:
            if f < lo - 1e-6 or f > hi + 1e-6:
                continue
            c3 = _add(pel, up, f * B["torso"])
            cx, cy = pr((c3[0], c3[1], c3[2] + oz))
            hw = math.hypot(wx * pr.c, wz * pr.s) * U * grow
            L_.append((cx - hw, cy))
            R_.append((cx + hw, cy))
        return R_ + L_[::-1]

    def torso():
        pa.shape(_poly_path(torso_pts(), True), skin)
        if not top:
            return
        kind, colr = top[0], top[1]
        if kind in ("robe_top", "shirt"):
            pa.shape(_poly_path(torso_pts(0.0, 1.0, 1.08), True), colr, sk=0.35)
            p0 = pr(_add(pel, up, 0.98 * B["torso"]))
            p1 = pr(_add(pel, up, 0.45 * B["torso"]))
            src(ctx, pa.col(mix(colr, "#f0e6d0", 0.6)))   # crossed collar
            ctx.set_line_width(max(1.5, U * 0.09))
            ctx.move_to(p0[0] - 0.25 * U, p0[1])
            ctx.line_to(p1[0] + 0.2 * U, p1[1])
            ctx.stroke()
            src(ctx, pa.col("#1c1410"))
            p2 = pr(_add(pel, up, 0.3 * B["torso"]))
            ctx.rectangle(p2[0] - B["waist"] * U * 1.1, p2[1] - 0.07 * U, B["waist"] * U * 2.2, 0.16 * U)
            ctx.fill()
        elif kind == "poncho":   # cloth with a head opening, as Chinese records describe for women
            pts = torso_pts(0.45, 1.0, 1.12)
            pa.shape(_poly_path(pts, True), colr, sk=0.3)
            _cloth_lines(ctx, pa, pts, colr, 3)
        elif kind == "uttariya":
            p0 = pr(_add(pel, up, 0.98 * B["torso"]))
            p1 = pr(_add(pel, up, 0.25 * B["torso"]))
            pa.shape(_poly_path([(p0[0] - 0.5 * U, p0[1]), (p0[0] - 0.1 * U, p0[1] - 0.05 * U),
                                 (p1[0] + 0.55 * U, p1[1]), (p1[0] + 0.15 * U, p1[1] + 0.15 * U)]), colr, sk=0.3)
        elif kind in ("thread", "sash"):
            p0 = pr(_add(pel, up, 0.97 * B["torso"]))
            p1 = pr(_add(pel, up, 0.2 * B["torso"]))
            src(ctx, pa.col(colr))
            ctx.set_line_width(max(1.2, U * (0.05 if kind == "thread" else 0.16)))
            ctx.move_to(p0[0] - 0.4 * U, p0[1])
            ctx.line_to(p1[0] + 0.45 * U, p1[1])
            ctx.stroke()
        elif kind == "robe_monk":
            pts = torso_pts(0.0, 1.0, 1.06)
            pa.shape(_poly_path(pts, True), colr, sk=0.3)
            sh_ = pr(J["r_sh"] if pr.c * pr.s >= 0 else J["l_sh"])
            pa.shape(_ell_path(sh_[0], sh_[1] + 0.2 * U, 0.3 * U, 0.26 * U), skin, sk=0.3)
    parts.append((0.0, torso))

    # ---- lower garment
    def garment():
        kind, colr = wrap[0], wrap[1]
        length = dict(loin=0.85, skirt_short=0.95, skirt_knee=1.75, skirt_long=2.45, robe=3.05)[kind]
        top_y = 0.2 * B["torso"]
        rx0, rz0 = B["hipw"] * 1.06, B["depth"] * 1.12
        c0 = _add(pel, up, top_y)
        knees = _lerp3(J["l_knee"], J["r_knee"], 0.5)
        seated = (PO.get("root") or {}).get("y") is not None
        if seated:
            c1 = (c0[0], max(knees[1], c0[1] - 1.2), (c0[2] + knees[2]) / 2 + 0.2)
            rx1, rz1 = B["hipw"] * 1.25, B["depth"] * 1.3
        else:
            dy = min(length, c0[1] - 0.15)
            kk = min(1.0, dy / max(0.1, c0[1] - knees[1])) if c0[1] - knees[1] > 0 else 1.0
            c1 = (c0[0], c0[1] - dy, c0[2] + (knees[2] - c0[2]) * kk * 0.7)
            spread = abs(J["l_knee"][2] - J["r_knee"][2]) * kk * 0.5
            rx1 = B["hipw"] * (1.08 + (0.1 if kind != "loin" else 0.0) + (0.25 if kind == "robe" else 0))
            rz1 = B["depth"] * 1.15 + spread
        p0, p1 = pr(c0), pr(c1)
        h0 = math.hypot(rx0 * pr.c, rz0 * pr.s) * U
        h1 = math.hypot(rx1 * pr.c, rz1 * pr.s) * U
        if kind == "loin":
            pts = [(p0[0] - h0, p0[1]), (p0[0] + h0, p0[1]), (p1[0] + h1 * 0.92, p1[1] - 0.25 * U),
                   (p1[0], p1[1] - 0.05 * U), (p1[0] - h1 * 0.92, p1[1] - 0.25 * U)]
        else:
            pts = [(p0[0] - h0, p0[1]), (p0[0] + h0, p0[1]), (p1[0] + h1, p1[1]),
                   ((p1[0] + h1 * 0.3), p1[1] + 0.05 * U), (p1[0] - h1, p1[1])]
        pa.shape(_poly_path(pts), colr, sk=0.38)
        if pa.sil:
            return
        if len(wrap) > 2 and wrap[2] == "stripes":
            ctx.save()
            _poly_path(pts)(ctx)
            ctx.clip()
            for k in range(1, 6):
                yy = p0[1] + (p1[1] - p0[1]) * k / 6
                src(ctx, pa.col(mix(colr, "#e8c890", 0.55)), 0.75)
                ctx.rectangle(p0[0] - 3 * U, yy, 6 * U, max(1.0, U * 0.05))
                ctx.fill()
            ctx.restore()
        else:
            _cloth_lines(ctx, pa, pts, colr, 5)
        src(ctx, pa.col(mix(colr, OUT, 0.45)))
        ctx.rectangle(p0[0] - h0, p0[1] - 0.03 * U, 2 * h0, max(1.5, U * 0.08))
        ctx.fill()
    parts.append((0.05 if not (PO.get("root") or {}).get("y") else 0.3, garment))

    # ---- arms
    bangles = [o for o in C["orn"] if "bangle" in o]
    sleeve = (top or ("",))[0] in ("robe_top", "shirt", "robe_monk")
    for side in ("l", "r"):
        sh, el, wr, hd = (J[side + k] for k in ("_sh", "_el", "_wr", "_hand"))
        dep = (D(el) + D(wr)) / 2 + 0.06 + (0.25 if D(wr) > 0.3 else 0.0)

        def arm(sh=sh, el=el, wr=wr, hd=hd):
            dl = _lerp3(sh, el, 0.25)
            sc = top[1] if sleeve else skin
            fa_c = top[1] if (sleeve and C["era"] == "china") else skin
            fr = 0.2 if (sleeve and C["era"] == "china") else 0.14
            pa.chain([(_capsule_path(pr(el), pr(wr), 0.15 * U, fr * U), fa_c),
                      (_capsule_path(pr(dl), pr(el), 0.19 * U, 0.135 * U), sc),
                      (_capsule_path(pr(sh), pr(dl), 0.2 * U, 0.19 * U), sc),
                      (_ell_path(*pr(hd), 0.12 * U, 0.15 * U), skin)])
            for b_ in bangles:
                wp = pr(_add(wr, (el[0] - wr[0], el[1] - wr[1], el[2] - wr[2]), 0.12))
                ang = math.atan2(pr(el)[1] - pr(wr)[1], pr(el)[0] - pr(wr)[0])
                for k in range(2):
                    off = k * 0.07 * U
                    pa.shape(_ell_path(wp[0] + math.cos(ang) * off, wp[1] + math.sin(ang) * off, 0.045 * U, 0.15 * U,
                                       ang), BRONZE if b_ == "bronze_bangle" else GOLD, sk=0.3)
        parts.append((dep, arm))

    # ---- props
    props = PO.get("props", {})
    for side in ("l", "r"):
        if side in props:
            name, dir3 = props[side]
            hd, wr = J[side + "_hand"], J[side + "_wr"]
            dep = D(hd) + 0.07 + (0.25 if D(wr) > 0.3 else 0.0)
            parts.append((dep, lambda name=name, dir3=dir3, hd=hd, el=J[side + "_el"]:
                          _prop(ctx, pa, pr, U, name, hd, el, dir3, C)))
    if props.get("head") == "pot":
        parts.append((5.0, lambda: _pot(ctx, pa, pr(_add(J["head"], (0, 1, 0), B["head_ry"] * 1.05)), U * 0.75, "#a8744a")))
    if props.get("both"):
        mid = _lerp3(J["l_hand"], J["r_hand"], 0.5)
        parts.append((D(mid) + 0.5, lambda mid=mid, k=props["both"]: _held(ctx, pa, pr, U, mid, k)))
    if props.get("pole"):
        parts.append((2.0, lambda: _pole_baskets(ctx, pa, pr, U, J)))

    # ---- head
    def head():
        _head(ctx, pa, pr, U, B, C, J, PO, expr, PO.get("hyaw", 0.0), skin, t, silhouette)
    parts.append((0.6 if pr.c > -0.2 else 0.3, head))
    for _, fn in sorted(parts, key=lambda q: q[0]):
        fn()


def _cloth_lines(ctx, pa, pts, colr, n):
    if pa.sil:
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ctx.save()
    _poly_path(pts)(ctx)
    ctx.clip()
    src(ctx, pa.col(mix(colr, OUT, 0.35)), 0.35)
    ctx.set_line_width(max(0.8, pa.U * 0.022))
    x0, x1 = min(xs), max(xs)
    for k in range(1, n + 1):
        yy = min(ys) + (max(ys) - min(ys)) * k / (n + 1)
        ctx.move_to(x0, yy + math.sin(k * 1.7) * pa.U * 0.04)
        ctx.curve_to(x0 + (x1 - x0) * 0.3, yy + pa.U * 0.05, x0 + (x1 - x0) * 0.7, yy - pa.U * 0.04, x1, yy)
        ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------------ head, face, hair
def _sphere_pt(c, r, v, yaw_extra, pr):
    a = math.radians(yaw_extra)
    x = v[0] * math.cos(a) + v[2] * math.sin(a)
    z = -v[0] * math.sin(a) + v[2] * math.cos(a)
    return pr((c[0] + x * r[0], c[1] + v[1] * r[1], c[2] + z * r[2])), pr.depth((x, 0, z))


BUN = dict(bun=(0, 0.45, -0.85), bun_grey=(0, 0.35, -0.9), topknot=(0, 0.95, -0.35), tied_back=(0, 0.1, -1.0),
           bun_side=(0.55, 0.55, -0.6), jata=(0, 1.05, -0.1))
BUN_R = dict(bun=0.24, bun_grey=0.22, topknot=0.2, tied_back=0.17, bun_side=0.22, jata=0.22)


def _head(ctx, pa, pr, U, B, C, J, PO, expr, hyaw, skin, t, silhouette):
    hc = J["head"]
    rx, ry = B["head_rx"], B["head_ry"]
    r = (rx, ry, rx * 1.12)
    F = C["face"]
    E = EXPR.get(expr or "neutral", EXPR["neutral"])
    blink = 0.1 if (t * 0.31 + len(C["en"]) * 0.13) % 1.0 < 0.025 else 1.0
    nk = J["neck"]
    pa.shape(_capsule_path(pr(nk), pr(_add(hc, (0, -1, 0), ry * 0.55)), 0.2 * U, 0.19 * U), skin)
    c2 = pr(hc)
    ears = [_sphere_pt(hc, r, (sg * 0.97, -0.05, -0.05), hyaw, pr) for sg in (1, -1)]
    for p, d in ears:
        if d < -0.15:
            pa.shape(_ell_path(p[0], p[1], 0.045 * U, 0.09 * U), skin, sk=0.5)
    hair = C["hair"]
    hcol = C["hair_c"]
    if hair in BUN:
        bp, bd = _sphere_pt(hc, r, BUN[hair], hyaw, pr)
        if bd < 0:
            pa.shape(_ell_path(bp[0], bp[1], BUN_R[hair] * U, BUN_R[hair] * U * (1.4 if hair == "jata" else 0.9)), hcol, sk=0.4)
    jaw = F.get("jaw", 1.0)
    yawr = math.atan2(pr.s, pr.c) + math.radians(hyaw)
    fs = math.sin(yawr)

    def skull(ctx):
        ctx.new_path()
        ctx.save()
        ctx.translate(c2[0], c2[1] - 0.05 * U)
        ctx.scale(math.hypot(rx * math.cos(yawr), r[2] * fs) * U, ry * 0.92 * U)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.new_sub_path()
        ctx.save()
        ctx.translate(c2[0] + fs * rx * 0.3 * U, c2[1] + ry * 0.36 * U)
        ctx.scale((0.2 + 0.1 * abs(math.cos(yawr))) * jaw * U, ry * 0.55 * U)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
    if pa.lw:
        skull(ctx)
        ctx.set_source_rgb(*pa.col(OUT))
        ctx.set_line_width(pa.lw * 2)
        ctx.stroke()
    skull(ctx)
    ctx.set_source_rgb(*pa.col(skin))
    ctx.fill()
    if not silhouette:
        ctx.save()
        skull(ctx)
        ctx.clip()
        src(ctx, pa.col(skin, -0.35), 0.55)
        ctx.save()
        ctx.translate(c2[0] + U * (0.46 - 0.3 * fs), c2[1] + 0.1 * U)
        ctx.scale(0.14 * U, 0.8 * U)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
        ctx.restore()
    nose_k = F.get("nose", 1.0)
    tip, td = _sphere_pt(hc, r, (0, -0.12, 1.12 + 0.06 * nose_k), hyaw, pr)
    root, _ = _sphere_pt(hc, r, (0, 0.12, 0.96), hyaw, pr)
    bot, _ = _sphere_pt(hc, r, (0, -0.26, 0.98), hyaw, pr)
    if td > 0.05:
        if abs(fs) > 0.62:
            pa.shape(_poly_path([root, (tip[0] + fs * 0.03 * U, tip[1]), bot]), skin, sk=0.25)
        elif not silhouette:
            src(ctx, pa.col(skin, -0.45))
            ctx.set_line_width(max(1, U * 0.035))
            ctx.move_to(root[0] - 0.02 * U, root[1] + 0.02 * U)
            ctx.curve_to(tip[0] - 0.05 * U, tip[1] - 0.05 * U, tip[0] - 0.08 * U * nose_k, tip[1] + 0.06 * U,
                         tip[0], tip[1] + 0.07 * U)
            ctx.stroke()
            for sg in (-1, 1):
                ellipse(ctx, tip[0] + sg * 0.06 * U * nose_k, tip[1] + 0.07 * U, 0.03 * U, 0.018 * U)
                ctx.fill()
    if not silhouette:
        for sg in (1, -1):
            ep, ed = _sphere_pt(hc, r, (sg * 0.42, 0.02, 0.9), hyaw, pr)
            if ed <= 0.12:
                continue
            fore = min(1.0, ed * 1.2)
            ew = 0.085 * U * (0.35 + 0.65 * fore)
            eh = 0.045 * U * E[4] * blink
            src(ctx, pa.col("#efe6d6"))
            ellipse(ctx, ep[0], ep[1], ew, max(eh, 0.006 * U))
            ctx.fill()
            if eh > 0.01 * U:
                src(ctx, pa.col("#1a110c"))
                ix = ep[0] + fs * 0.25 * ew
                ellipse(ctx, ix, ep[1], min(ew * 0.55, 0.045 * U), min(eh, 0.045 * U))
                ctx.fill()
                src(ctx, "#ffffff", 0.7)
                ctx.new_path()
                ctx.arc(ix - 0.012 * U, ep[1] - 0.012 * U, 0.01 * U, 0, 6.283)
                ctx.fill()
            src(ctx, pa.col(OUT), 0.9)
            ctx.set_line_width(max(1, U * 0.03))
            ctx.move_to(ep[0] - ew * 1.05, ep[1] + eh * 0.1)
            ctx.curve_to(ep[0] - ew * 0.4, ep[1] - eh * 1.25, ep[0] + ew * 0.4, ep[1] - eh * 1.25,
                         ep[0] + ew * 1.1, ep[1] - eh * 0.1)
            ctx.stroke()
            bp, _ = _sphere_pt(hc, r, (sg * 0.42, 0.24 + E[0] * 2, 0.92), hyaw, pr)
            tilt = E[1] * 0.06 * U
            inner = -sg * (1 if pr.c >= 0 else -1)
            src(ctx, pa.col(hcol if not F.get("age") else "#6a625a"))
            ctx.set_line_width(max(1.2, U * 0.045 * F.get("brow", 1.0)))
            ctx.move_to(bp[0] - ew * 1.1, bp[1] - (tilt if inner < 0 else 0))
            ctx.line_to(bp[0] + ew * 1.1, bp[1] - (tilt if inner > 0 else 0))
            ctx.stroke()
        mp, md = _sphere_pt(hc, r, (0, -0.52, 0.86), hyaw, pr)
        if md > 0.1:
            fore = min(1.0, md * 1.3)
            mw = 0.13 * U * (0.35 + 0.65 * fore) * F.get("lips", 1.0)
            op = max(E[3], PO.get("mouth", 0.0))
            curve = E[2] * 0.05 * U
            if op > 0.05:
                src(ctx, pa.col("#3a1612"))
                ellipse(ctx, mp[0] + fs * 0.02 * U, mp[1] + op * 0.03 * U, mw * 0.7, op * 0.06 * U + 0.01 * U)
                ctx.fill()
            src(ctx, pa.col("#5a2a20"), 0.9)
            ctx.set_line_width(max(1, U * 0.03))
            ctx.move_to(mp[0] - mw, mp[1] - curve)
            ctx.curve_to(mp[0] - mw * 0.3, mp[1] + curve * 0.8, mp[0] + mw * 0.3, mp[1] + curve * 0.8,
                         mp[0] + mw, mp[1] - curve)
            ctx.stroke()
        if F.get("beard"):
            bp, bd = _sphere_pt(hc, r, (0, -0.85, 0.62), hyaw, pr)
            if bd > -0.2:
                src(ctx, pa.col("#8c867e" if F.get("age") else "#2a201a"))
                ellipse(ctx, bp[0] + fs * 0.05 * U, bp[1], (0.1 + 0.1 * abs(math.cos(yawr))) * U, 0.12 * U)
                ctx.fill()
    _hair_cap(ctx, pa, pr, U, hc, r, hyaw, C, yawr)
    for p, d in ears:
        if d >= -0.15 and hair not in ("turban", "guan", "cloth_head"):
            pa.shape(_ell_path(p[0], p[1], 0.045 * U * (0.35 + 0.65 * min(1, abs(d) * 2 + 0.2)), 0.09 * U), skin, sk=0.5)
        if d >= -0.15 and "gold_ear" in C["orn"] and not silhouette:
            pa.shape(_ell_path(p[0], p[1] + 0.17 * U, 0.055 * U, 0.065 * U), GOLD, sk=0.3)
    if hair in BUN:
        bp, bd = _sphere_pt(hc, r, BUN[hair], hyaw, pr)
        if bd >= 0:
            pa.shape(_ell_path(bp[0], bp[1], BUN_R[hair] * U, BUN_R[hair] * U * (1.4 if hair == "jata" else 0.9)), hcol, sk=0.4)
        if hair == "bun_side" and not silhouette and bd >= -0.3:   # lotus-pink flower in the guide's hair
            for k in range(5):
                a = k * 1.256
                pa.shape(_ell_path(bp[0] + math.cos(a) * 0.1 * U, bp[1] - 0.12 * U + math.sin(a) * 0.1 * U,
                                   0.07 * U, 0.05 * U, a), "#e3a1a8", sk=0.2)
    neck_orn = [o for o in C["orn"] if o.endswith("_neck")]
    if neck_orn and not silhouette:
        kind = neck_orn[0]
        for i in range(15):
            a = -math.pi * 0.8 + i * (1.6 * math.pi) / 14
            v = (math.sin(a) * B["sh"] * 0.42, -0.12 - 0.3 * math.cos(a / 1.6) ** 2, math.cos(a) * B["depth"] * 0.9)
            if pr.depth(v) < 0:
                continue
            p = pr(_add(nk, v))
            c_ = {"shell_neck": SHELL, "gold_neck": GOLD}.get(kind, [CARNELIAN, GLASS, GOLD, "#e8a040", "#2a7a6a"][i % 5])
            pa.shape(_ell_path(p[0], p[1], 0.045 * U, 0.04 * U), c_, sk=0.25)


def _hair_cap(ctx, pa, pr, U, hc, r, hyaw, C, yawr):
    hair = C["hair"]
    hcol = C["hair_c"]
    c2 = pr(hc)
    if hair == "shaved":
        src(ctx, pa.col(hcol), 0.3)
        ellipse(ctx, c2[0], c2[1] - 0.12 * U, math.hypot(r[0] * math.cos(yawr), r[2] * math.sin(yawr)) * U * 0.98, r[1] * U * 0.8)
        ctx.fill()
        return
    if hair == "guan":   # Han/Wu official's cap: hair drawn up into a topknot under a small black crown
        C2 = dict(C, hair="topknot_hidden")
        _hair_cap(ctx, pa, pr, U, hc, r, hyaw, C2, yawr)
        top = pr(_add(hc, (0, 1, 0), r[1] * 0.95))
        pa.shape(_poly_path([(top[0] - 0.2 * U, top[1] + 0.12 * U), (top[0] + 0.2 * U, top[1] + 0.12 * U),
                             (top[0] + 0.26 * U, top[1] - 0.32 * U), (top[0] - 0.14 * U, top[1] - 0.36 * U)]), "#141414", sk=0.2)
        src(ctx, pa.col("#141414"))
        ctx.set_line_width(max(1, U * 0.02))
        ctx.move_to(top[0] - 0.15 * U, top[1] + 0.1 * U)
        ctx.line_to(c2[0] - 0.05 * U, c2[1] + 0.55 * U)
        ctx.stroke()
        return
    if hair == "turban":
        pa.shape(_ell_path(c2[0], c2[1] - 0.38 * U, math.hypot(r[0] * math.cos(yawr), r[2] * math.sin(yawr)) * U * 1.12,
                           r[1] * U * 0.55), hcol, sk=0.35)
        if not pa.sil:
            src(ctx, pa.col(mix(hcol, OUT, 0.3)), 0.5)
            ctx.set_line_width(max(1, U * 0.03))
            for k in range(3):
                ctx.move_to(c2[0] - 0.4 * U, c2[1] - (0.15 + 0.15 * k) * U)
                ctx.curve_to(c2[0] - 0.1 * U, c2[1] - (0.35 + 0.15 * k) * U, c2[0] + 0.2 * U, c2[1] - (0.3 + 0.15 * k) * U,
                             c2[0] + 0.42 * U, c2[1] - (0.45 + 0.12 * k) * U)
                ctx.stroke()
        return
    if hair == "cloth_head":
        pa.shape(_ell_path(c2[0], c2[1] - 0.36 * U, math.hypot(r[0] * math.cos(yawr), r[2] * math.sin(yawr)) * U * 1.06,
                           r[1] * U * 0.5), hcol, sk=0.35)
        return
    grow = 1.07
    rr = (r[0] * grow, r[1] * grow, r[2] * grow)
    front = dict(topknot_hidden=0.4, short=0.42, tied_back=0.4, bun=0.38, bun_grey=0.46, topknot=0.4, bun_side=0.34, jata=0.42).get(hair, 0.4)
    side = 0.08 if hair != "short" else 0.12
    back = -0.4
    pts_vis = []
    N = 72
    for i in range(N):
        az = -math.pi + 2 * math.pi * i / N
        ca = math.cos(az)
        hl = side + (front - side) * max(0, ca) ** 1.5 + (back - side) * max(0, -ca) ** 1.2
        rad_ = math.sqrt(max(0.0, 1 - hl * hl))
        p, d = _sphere_pt(hc, rr, (math.sin(az) * rad_, hl, math.cos(az) * rad_), hyaw, pr)
        pts_vis.append((p, d, i))
    vis = [q for q in pts_vis if q[1] > 0]
    ax = math.hypot(rr[0] * math.cos(yawr), rr[2] * math.sin(yawr)) * U
    ay = rr[1] * U
    if not vis:
        pa.shape(_ell_path(c2[0], c2[1], ax, ay), hcol, sk=0.4, hi=0.25)
        return
    idx = [q[2] for q in vis]
    start = 0
    for k in range(len(idx)):
        if (idx[k] - 1) % N not in idx:
            start = k
            break
    run = vis[start:] + vis[:start]
    pts = [q[0] for q in run]
    a1 = math.atan2((pts[-1][1] - c2[1]) / ay, (pts[-1][0] - c2[0]) / ax)
    a0 = math.atan2((pts[0][1] - c2[1]) / ay, (pts[0][0] - c2[0]) / ax)

    def norm(a):
        while a < -math.pi:
            a += 2 * math.pi
        while a > math.pi:
            a -= 2 * math.pi
        return a
    span = norm(a0 - a1)
    span2 = span - 2 * math.pi if span > 0 else span + 2 * math.pi
    use = span if abs(norm(a1 + span / 2 + math.pi / 2)) < abs(norm(a1 + span2 / 2 + math.pi / 2)) else span2
    for k in range(1, 25):
        a = a1 + use * k / 25
        pts.append((c2[0] + ax * math.cos(a), c2[1] + ay * math.sin(a)))
    pa.shape(_poly_path(pts), hcol, sk=0.45, hi=0.22)


# ------------------------------------------------------------------ props
def _prop(ctx, pa, pr, U, name, hd, el, dir3, C):
    h2 = pr(hd)
    d3 = dir3 if dir3 is not None else (hd[0] - el[0], hd[1] - el[1], hd[2] - el[2])
    n = math.sqrt(sum(v * v for v in d3)) or 1
    dv = pr.vec(tuple(v / n for v in d3))

    def along(k):
        return (h2[0] + dv[0] * k * U, h2[1] + dv[1] * k * U)
    if name in ("oar", "pole"):
        a, b = along(-1.2 if name == "oar" else -2.5), along(2.6 if name == "oar" else 4.5)
        pa.shape(_capsule_path(a, b, 0.05 * U, 0.045 * U), "#6a4a2c", sk=0.3)
        if name == "oar":
            c = along(2.9)
            pa.shape(_ell_path(c[0], c[1], 0.14 * U, 0.42 * U, math.atan2(dv[1], dv[0]) - 1.57), "#7a5a36", sk=0.3)
    elif name == "brush":
        a, b = along(-0.1), along(0.55)
        pa.shape(_capsule_path(a, b, 0.03 * U, 0.03 * U), "#3a2a1a", sk=0.3)
    elif name == "tablet":
        pa.shape(_poly_path([(h2[0] - 0.1 * U, h2[1] - 0.45 * U), (h2[0] + 0.5 * U, h2[1] - 0.4 * U),
                             (h2[0] + 0.45 * U, h2[1] + 0.25 * U), (h2[0] - 0.15 * U, h2[1] + 0.2 * U)]), "#d9c39a", sk=0.2)
    elif name == "hammer_small":
        a, b = along(-0.1), along(0.6)
        pa.shape(_capsule_path(a, b, 0.035 * U, 0.035 * U), "#6a4a2c", sk=0.3)
        c = along(0.7)
        pa.shape(_ell_path(c[0], c[1], 0.12 * U, 0.08 * U, math.atan2(dv[1], dv[0]) + 1.57), "#7a7a7a", sk=0.3)
    elif name == "sickle":
        src(ctx, pa.col("#6a6a6a"))
        ctx.set_line_width(max(1.5, U * 0.05))
        ctx.new_path()
        ctx.arc(h2[0] + dv[0] * 0.4 * U, h2[1] + dv[1] * 0.4 * U, 0.3 * U, -2.5, 0.5)
        ctx.stroke()
    elif name == "bow":
        src(ctx, pa.col("#5a3a22"))
        ctx.set_line_width(max(1.5, U * 0.07))
        ctx.new_path()
        ctx.arc(h2[0] - 0.3 * U, h2[1], 1.6 * U, -0.9, 0.9)
        ctx.stroke()


def _held(ctx, pa, pr, U, mid, kind):
    p = pr(mid)
    if kind == "tray":
        pa.shape(_ell_path(p[0], p[1] - 0.05 * U, 0.6 * U, 0.12 * U), "#d8aa4a", sk=0.3)
        for k in range(3):
            pa.shape(_ell_path(p[0] - 0.3 * U + k * 0.3 * U, p[1] - 0.2 * U, 0.13 * U, 0.12 * U),
                     ["#e3a1a8", "#f0d58a", "#efe6d2"][k], sk=0.2)
    elif kind == "scroll":
        pa.shape(_poly_path([(p[0] - 0.65 * U, p[1] - 0.35 * U), (p[0] + 0.65 * U, p[1] - 0.35 * U),
                             (p[0] + 0.65 * U, p[1] + 0.15 * U), (p[0] - 0.65 * U, p[1] + 0.15 * U)]), "#efe2c6", sk=0.15)
        for sx in (-0.68, 0.68):
            pa.shape(_capsule_path((p[0] + sx * U, p[1] - 0.42 * U), (p[0] + sx * U, p[1] + 0.22 * U), 0.06 * U, 0.06 * U),
                     "#7e3520", sk=0.3)
    elif kind == "box":
        pa.shape(_poly_path([(p[0] - 0.55 * U, p[1] - 0.6 * U), (p[0] + 0.55 * U, p[1] - 0.6 * U),
                             (p[0] + 0.55 * U, p[1] + 0.1 * U), (p[0] - 0.55 * U, p[1] + 0.1 * U)]), "#8a6a3c", sk=0.3)
    elif kind == "lotus":
        for k in range(8):
            a = k * 0.785
            pa.shape(_ell_path(p[0] + math.cos(a) * 0.14 * U, p[1] - 0.1 * U + math.sin(a) * 0.05 * U, 0.16 * U, 0.08 * U, a),
                     "#e3a1a8" if k % 2 else "#f2c4c8", sk=0.2)
        from core import glow
        glow(ctx, p[0], p[1] - 0.25 * U, 0.6 * U, "#ffd080", 0.6)


def _pole_baskets(ctx, pa, pr, U, J):
    sh = pr(J["r_sh"])
    pa.shape(_capsule_path((sh[0] - 2.4 * U, sh[1] - 0.3 * U), (sh[0] + 2.4 * U, sh[1] - 0.1 * U), 0.06 * U, 0.06 * U),
             "#6a4a2a", sk=0.3)
    for sg in (-1, 1):
        bx = sh[0] + 2.2 * U * sg
        src(ctx, pa.col("#3a2a1a"))
        ctx.set_line_width(max(1, U * 0.03))
        ctx.move_to(bx, sh[1] - 0.2 * U)
        ctx.line_to(bx, sh[1] + 1.3 * U)
        ctx.stroke()
        pa.shape(_ell_path(bx, sh[1] + 1.6 * U, 0.55 * U, 0.38 * U), "#9a7a4a", sk=0.3)


def _pot(ctx, pa, p, s, colr):
    x, y = p
    pts = [(x - 0.32 * s, y - 0.98 * s), (x + 0.32 * s, y - 0.98 * s), (x + 0.36 * s, y - 0.9 * s),
           (x + 0.62 * s, y - 0.55 * s), (x + 0.58 * s, y - 0.18 * s), (x + 0.3 * s, y), (x - 0.3 * s, y),
           (x - 0.58 * s, y - 0.18 * s), (x - 0.62 * s, y - 0.55 * s), (x - 0.36 * s, y - 0.9 * s)]
    pa.shape(_poly_path(pts, True), colr, sk=0.35, hi=0.15)


def pot(ctx, x, y, s, colr="#a8744a", P=None):
    pa = _Paint(ctx, s, P["light"] if P else "#fff2dc", P["shadow"] if P else "#3a3040", None, 0)
    _pot(ctx, pa, (x, y), s, colr)


def shadow(ctx, x, y, h, a=0.25):
    src(ctx, "#000000", a)
    ellipse(ctx, x, y, h * 0.14, h * 0.022)
    ctx.fill()


def head_offset(who, h, pose="idle", t=0.0):
    C = CAST[who]
    U = h / body_height(C["B"])
    J = skeleton(C["B"], pose_at(pose, t))
    return J["head"][0] * U, -J["head"][1] * U
