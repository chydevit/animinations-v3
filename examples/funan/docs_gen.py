"""Write docs/: script_km_en.md, storyboard.md, artifact_list.md, references.md (from the live shot list)."""
import os, sys, json, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "engine"), ROOT]
import script_src as SS
from narration import N, WHO

SCENES = {
    "make_delta": "Mekong delta: banded paper sky, Ba Thê hill, nipa and sugar palms, water ripples, lotus foreground, drifting boats",
    "make_lowland": "Delta rice plain with stilt houses (pre-Funan); optional rising flood water",
    "make_puppet": "Sbek-style shadow screen lit by a flickering lamp; leather silhouettes with punched patterns",
    "make_port": "Oc Eo waterfront: stilt houses, brick shrine, jetty with goods, sailing ships and Funan oared ships",
    "make_sea": "Open sea at golden hour: fleet of Funan oared ships and sailing traders",
    "make_palace": "Walled town with wooden palisade; raised timber hall with tiered, perforated roof",
    "make_temple": "Brick sanctuary with an inscribed stele, sugar palms, incense smoke, lotus pond",
    "make_workshop": "Craft quarter under a perforated awning: bead and gold workers, pots",
    "make_monastery": "Lamp-lit monastery hall in Jiankang (Nanjing) with lattice windows; monks translating",
    "make_chenla": "Inland brick towers in Sambor Prei Kuk style",
    "museum_card": "MUSEUM CARD: authentic object photo in gold frame on textile wall + label (name, date, holder, credit)",
    "zh_excerpt": "CHINESE TEXT CARD: classical Chinese in vertical columns on silk paper, translation and source beside it",
    "map_scene": "ANIMATED MAP: paper-layered terrain of Southeast Asia, routes with moving ships, soft zones (no borders)",
    "photo": "AUTHENTIC PHOTO: slow Ken Burns move",
    "claim_board": "LABEL BOARD: palm-leaf cards tagged legend / record / inscription / archaeology / debated",
    "text_card": "TEXT CARD over darkened scene", "title_card": "TITLE CARD with unfolding lotus emblem",
    "chapter_card": "CHAPTER CARD (Khmer + English) with lotus emblem over the chapter's set",
    "scrolling_credits": "CREDITS: sources, image credits, notes"}


def describe(fn, depth=0):
    found = []
    if fn is None or depth > 3:
        return found
    code = getattr(fn, "__code__", None)
    if code:
        for n in code.co_names:
            if n in SCENES and n not in found:
                found.append(n)
        for c in (fn.__closure__ or ()):
            try:
                v = c.cell_contents
            except ValueError:
                continue
            if callable(v):
                for n in describe(v, depth + 1):
                    if n not in found:
                        found.append(n)
    return found


def tc(t):
    return "%d:%04.1f" % (t // 60, t % 60)


shots, pl, cues = SS.build()
total = shots[-1]["start"] + shots[-1]["dur"]
chap_titles = {}
for i in SS.CHAPTERS:
    chap_titles[i] = True

# ---------------- script
L = ["# Funan – Kingdom of the Mountain: narration and dialogue (Khmer / English)", "",
     "Times are taken from the synthesised voices. **NAR** = narrator; **NEANG TONLE** = the fictional guide.",
     "English word count: %d. Runtime %d:%02d (credits included)." % (sum(len(v[1].split()) for v in N.values()), total // 60, total % 60), ""]
CH_NAMES = ["Opening", "1. The Land Before Funan", "2. The Founding Legend", "3. Oc Eo, Port of the World", "4. Masters of Water",
            "5. Fan Shiman's Expansion", "6. Envoys from China", "7. Faith and Ideas from India", "8. Life, Art and Society",
            "9. The Last Great Kings", "10. Decline and the Rise of Chenla", "Closing: Legacy"]
bounds = [0] + SS.CHAPTERS + [len(shots)]
for k in range(len(bounds) - 1):
    a, b = bounds[k], bounds[k + 1]
    L += ["", "## %s  (%s – %s)" % (CH_NAMES[k] if k < len(CH_NAMES) else "", tc(shots[a]["start"]), tc(shots[b - 1]["start"] + shots[b - 1]["dur"]) if b - 1 < len(shots) else ""), ""]
    for p in pl:
        if shots[a]["start"] - 0.01 <= p["t"] < (shots[b]["start"] if b < len(shots) else 1e9):
            who = "NEANG TONLE" if WHO[p["key"]] == "tonle" else "NAR"
            L.append("**%s** · %s · `%s`  " % (tc(p["t"]), who, p["key"]))
            L.append("%s  " % N[p["key"]][0])
            L.append("_%s_" % N[p["key"]][1])
            L.append("")
open(os.path.join(ROOT, "docs", "script_km_en.md"), "w").write("\n".join(L))

# ---------------- storyboard
B = ["# Storyboard and shot list", "",
     "One row per shot. Camera: (x, y, zoom) in set pixels from start → end; parallax layers move at different rates.",
     "Contact sheets of real frames: `film/storyboard/`.", ""]
for i, s in enumerate(shots):
    if i in chap_titles:
        B += ["", "---", ""]
    sc = SS.SHOTS[i]
    names = describe(sc["vis"])
    cam = s["cam"]
    B.append("**Shot %d** · %s · %.1fs · badge: %s · transition in: %s" % (i, tc(s["start"]), s["dur"], s.get("badge") or "–",
                                                                         s.get("trans") or "fade"))
    B.append("- Setting: " + ("; ".join(SCENES[n] for n in names) or "card"))
    B.append("- Camera: (%d, %d, %.2f) → (%d, %d, %.2f)" % (*cam["a"], *cam.get("b", cam["a"])))
    if s.get("badge_note"):
        B.append("- On-screen caption: " + s["badge_note"])
    for k in s["lines"]:
        B.append("- %s: %s" % ("NEANG TONLE" if WHO[k] == "tonle" else "NAR", N[k][1]))
    B.append("")
open(os.path.join(ROOT, "docs", "storyboard.md"), "w").write("\n".join(B))

# ---------------- artifact list
man = SS.man()
A = ["# Authentic images used in the film", "", "Every item is public domain or openly licensed; credits appear on screen and in the end credits.", "",
     "| File | Object / subject | Date | Held by / place | Licence | Author / credit | Source | Notes |", "|---|---|---|---|---|---|---|---|"]
for f in sorted(SS.USED):
    e = man.get(f, {})
    A.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (f, e.get("object_name", ""), e.get("object_date", ""),
             e.get("holding_institution", ""), e.get("licence", ""), e.get("attribution_line", ""), e.get("source_page_url", ""),
             (e.get("authenticity_note", "") or "").replace("|", "/")))
A += ["", "Full archive (90 items, including unused ones): `archive/manifest.json`, `archive/contact_sheet.md`."]
open(os.path.join(ROOT, "docs", "artifact_list.md"), "w").write("\n".join(A))

# ---------------- references (from the fact sheet)
fs = open(os.path.join(ROOT, "docs", "fact_sheet.md")).read()
ref = fs[fs.index("## 18. References"):]
open(os.path.join(ROOT, "docs", "references.md"), "w").write("# References\n\n" + ref.split("\n", 1)[1])
print("docs written")
