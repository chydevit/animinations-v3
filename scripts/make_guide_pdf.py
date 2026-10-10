"""Build docs/Khmer_History_Documentary_Guide.pdf (HTML printed by headless Chrome, which shapes Khmer correctly).
usage: python3 scripts/make_guide_pdf.py"""
import html
import os
import subprocess

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(SK, "docs")
OUT = os.path.join(DOCS, "Khmer_History_Documentary_Guide.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def code(s):
    return "<pre>%s</pre>" % html.escape(s.strip("\n"))


def img(name, cap, cls=""):
    return '<figure class="%s"><img src="img/%s.jpg"><figcaption>%s</figcaption></figure>' % (cls, name, cap)


def table(head, rows):
    h = "".join("<th>%s</th>" % c for c in head)
    b = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r) for r in rows)
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (h, b)


CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
body { font-family: 'Helvetica Neue', 'Noto Sans Khmer', sans-serif; font-size: 10.2pt; line-height: 1.5; color: #2a2018; }
.km { font-family: 'Noto Sans Khmer'; }
h1 { font-family: 'Cormorant Garamond', serif; font-size: 25pt; color: #7e3520; margin: 0 0 4mm; border-bottom: 2px solid #d8aa4a; padding-bottom: 2mm; page-break-before: always; }
h2 { break-after: avoid; page-break-after: avoid; font-family: 'Cormorant Garamond', serif; font-size: 16pt; color: #1f5b4f; margin: 6mm 0 2mm; }
p { margin: 0 0 2.5mm; }
pre { background: #1c1410; color: #f0d58a; padding: 3mm 4mm; border-radius: 2mm; font-family: Menlo, 'Noto Sans Khmer', monospace;
      font-size: 8.4pt; line-height: 1.45; white-space: pre-wrap; page-break-inside: avoid; }
code { font-family: Menlo, monospace; font-size: 8.8pt; background: #f1e6cf; padding: 0 1mm; border-radius: 1mm; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4mm; font-size: 9pt; page-break-inside: avoid; }
th { background: #7e3520; color: #fff4dc; text-align: left; padding: 1.5mm 2mm; }
td { border-bottom: 1px solid #e0d2b4; padding: 1.4mm 2mm; vertical-align: top; }
tr:nth-child(even) td { background: #faf4e8; }
figure { margin: 3mm 0 4mm; page-break-inside: avoid; }
figure img { width: 100%; border-radius: 1.5mm; box-shadow: 0 1px 4px rgba(0,0,0,.25); }
figcaption { font-size: 8.5pt; color: #6a5a42; margin-top: 1mm; font-style: italic; }
.two { display: flex; gap: 4mm; } .two figure { flex: 1; }
.note { background: #f6ecd6; border-left: 4px solid #d8aa4a; padding: 2.5mm 4mm; margin: 3mm 0; page-break-inside: avoid; }
.warn { background: #f7e1dc; border-left: 4px solid #b5562f; padding: 2.5mm 4mm; margin: 3mm 0; page-break-inside: avoid; }
ol li, ul li { margin-bottom: 1.2mm; }
.cover { height: 255mm; display: flex; flex-direction: column; justify-content: center; text-align: center;
         background: linear-gradient(#efe2c6, #d9c39a); margin: -16mm -15mm 0; padding: 0 18mm; }
.cover .kmt { font-family: 'Moul'; font-size: 30pt; color: #7e3520; margin-bottom: 3mm; }
.cover .t { font-family: 'Cormorant Garamond'; font-size: 34pt; font-weight: 700; color: #1c1410; line-height: 1.1; }
.cover .s { font-size: 12.5pt; color: #4a3a2a; margin: 5mm 0 7mm; }
.cover img { width: 100%; border-radius: 2mm; box-shadow: 0 2px 8px rgba(0,0,0,.35); }
.cover .meta { margin-top: 7mm; font-size: 9.5pt; color: #6a5a42; }
.toc { columns: 2; font-size: 10.5pt; } .toc div { margin-bottom: 1.5mm; }
"""

S = []
S.append("""<div class="cover">
<div class="kmt">ការបង្កើតភាពយន្តឯកសារប្រវត្តិសាស្ត្រខ្មែរ</div>
<div class="t">Khmer History Documentary Builder</div>
<div class="s">How to use the <b>khmer-history-doc</b> skill for Claude Code<br>
Paper-cut 2D documentaries · Khmer narration · real maps · authentic evidence</div>
<img src="img/funan_title.jpg">
<div class="meta">Version 1.0 · October 2026 · github.com/chydevit/animinations-v3</div>
</div>""")

S.append("<h1>Contents</h1><div class='toc'>" + "".join("<div>%d. %s</div>" % (i + 1, t) for i, t in enumerate([
    "What the skill makes", "Installation", "Quick start with Claude", "Quick start by hand", "Inside a project",
    "Step-by-step workflow", "Writing the narration", "Building the shot list", "Maps", "Evidence: photos and records",
    "Voices and quality check", "Rendering and outputs", "Accuracy rules and labels", "Customising the look",
    "Troubleshooting", "Command cheat sheet"])) + "</div>")
S.append("""<div class="note"><b>In one sentence:</b> you give Claude a Cambodian history topic. It researches the facts,
writes a Khmer and English script, draws paper-cut scenes, maps and evidence cards, records Khmer voices, mixes original
music, and renders a finished, subtitled MP4 in which every claim and every picture is labelled honestly.</div>""")

# 1
S.append("<h1>1. What the skill makes</h1>")
S.append("<p>This skill packages the documentary engine built over five films (Kampong Cham, Khmer Rouge, Preah Vihear, "
         "Ta Moan and Funan). Each film is a 10–20 minute educational documentary with:</p><ul>"
         "<li><b>Paper-cut / Sbek shadow-puppet scenes</b>: layered paper sets with parallax and camera moves, film grain and transitions (ripple, lotus, ink).</li>"
         "<li><b>A fictional child guide</b> (default: Neang Tonle). She asks a question at the start of each chapter. She is lip-synced to her own voice and always labelled fictional.</li>"
         "<li><b>Animated maps</b> built from real elevation data and Natural Earth rivers, with markers, routes, moving ships and soft zones.</li>"
         "<li><b>Authentic evidence</b>: Ken Burns photos, museum cards and classical Chinese text cards, each with licence and credit.</li>"
         "<li><b>Khmer narration</b> in two locked VoxCPM2 voices (narrator and guide), checked with Khmer Whisper.</li>"
         "<li><b>Original music</b> in pinpeat style (roneat, kong, khloy, tro, chapei), with ambience and SFX, mixed to −16 LUFS.</li>"
         "<li><b>Subtitles</b>: English burned into the picture, plus soft English and Khmer tracks in the MP4.</li>"
         "<li><b>Documents</b>: fact sheet, Khmer/English script, shot list, image manifest and ASR report.</li></ul>")
S.append("<div class='two'>%s%s</div>" % (img("funan_guide", "The guide introduces herself (badge: FICTIONAL GUIDE)."),
                                         img("funan_legend", "A legend told as a shadow-puppet play (badge: LEGEND).")))
S.append("<div class='two'>%s%s</div>" % (img("funan_museum", "Museum card: a real object with its date, museum and licence."),
                                         img("funan_record", "Chinese dynastic record with a translation and its source.")))

# 2
S.append("<h1>2. Installation</h1>")
S.append("<p><b>You need:</b> a Mac (Apple Silicon, 16 GB RAM or more recommended), <a>Homebrew</a>, Python 3.12, about 15 GB of free disk space, and Claude Code.</p>")
S.append(code("""
# 1. get the skill into Claude Code's skills folder
git clone https://github.com/chydevit/animinations-v3.git ~/.claude/skills/khmer-history-doc

# 2. one-time setup (tools, fonts, Python environments, VoxCPM2 model ~5 GB)
~/.claude/skills/khmer-history-doc/scripts/setup.sh
"""))
S.append(table(["Setup step", "What it installs"], [
    ["System tools", "ffmpeg, cairo, pango (Homebrew)"],
    ["Fonts", "Noto Sans Khmer, Noto Serif Khmer, Moul, Cormorant Garamond"],
    ["<code>.venv</code>", "render environment: cairocffi, numpy, scipy, pillow, soundfile, pyloudnorm, pyshp"],
    ["<code>.venv-vox</code>", "VoxCPM2 + PyTorch (MPS) + transformers for the Khmer Whisper check. If <code>khmer-2d-animation</code> is installed, its environment is reused."],
]))
S.append("<div class='note'>To skip the voice environment, for example on a machine that only renders, run "
         "<code>SKIP_VOX=1 scripts/setup.sh</code>. Running setup again is always safe.</div>")

# 3
S.append("<h1>3. Quick start with Claude</h1>")
S.append("<p>Open Claude Code in your animation folder and describe the film. The skill starts automatically for any "
         "Khmer or Cambodian history documentary request. You can also type <code>/khmer-history-doc</code>.</p>")
S.append(code("""
cd ~/animation-2D
claude
> Make a 15-minute Khmer documentary about Sambor Prei Kuk and the Chenla kingdom,
  with Neang Tonle as the guide. Chapters: 0:45 the land, 3:00 Isanavarman I,
  6:00 the temples, 9:30 inscriptions, 12:30 legacy.
"""))
S.append("<p>Claude then works through these stages:</p><ol>"
         "<li>Researches Khmer and English sources and writes <code>docs/fact_sheet.md</code>, with a tag on every claim.</li>"
         "<li>Finds freely licensed images and records them in <code>archive/manifest.json</code>.</li>"
         "<li>Creates the project, writes <code>narration.py</code> and <code>script_src.py</code>, and shows you preview sheets.</li>"
         "<li>Designs voice candidates for you to choose from, then synthesises and checks every line.</li>"
         "<li>Renders <code>film/&lt;name&gt;.mp4</code> plus a web copy, and reports the runtime and QC results.</li></ol>")
S.append("<p><b>Useful follow-up requests:</b></p>")
S.append(table(["Say", "What happens"], [
    ["“Show me the storyboard first”", "Claude renders <code>make.py shotstills</code> and shows you the contact sheets"],
    ["“Let me pick the voices”", "Claude runs <code>make.py voices</code>, and you listen to <code>audio/voices/cand_*.wav</code>"],
    ["“Line k3 sounds wrong”", "Claude runs <code>make.py reseed k3</code> and then <code>make.py narrate</code>"],
    ["“Make chapter 2 longer / add a map of the trade route”", "Claude edits <code>script_src.py</code>, then previews before rendering"],
    ["“Re-render only the changed part”", "Claude deletes the affected chunks in <code>build/chunks/</code> and renders again"],
]))

# 4
S.append("<h1>4. Quick start by hand</h1>")
S.append("<p>Every step can also be run without Claude. Each film is a self-contained folder with its own copy of the engine.</p>")
S.append(code("""
SK=~/.claude/skills/khmer-history-doc
$SK/.venv/bin/python $SK/scripts/new_doc.py ~/animation-2D/sambor_prei_kuk \\
    --title-en "Sambor Prei Kuk" --title-km "សំបូរព្រៃគុក"
cd ~/animation-2D/sambor_prei_kuk

.venv/bin/python make.py info          # runtime and shot list
.venv/bin/python make.py shotstills    # build/shots/sheet_00.jpg
.venv/bin/python make.py voices        # 4 candidate voices per speaker
.venv/bin/python make.py lock nar 11   # choose the narrator
.venv/bin/python make.py lock tonle 23 # choose the guide
.venv/bin/python make.py narrate       # synthesise every line
.venv/bin/python make.py asr           # Khmer Whisper check
.venv/bin/python make.py all           # subtitles + audio + video -> film/sambor_prei_kuk.mp4
"""))
S.append("<p>A new project contains a short working sample about Sambor Prei Kuk (about 70 seconds), so you can test the whole pipeline at once. "
         "To start from the complete 15-minute Funan film instead, add <code>--example funan</code>.</p>")
S.append(img("contact_sheet", "make.py shotstills on the sample project: one frame per shot, labelled with its badge and subtitle."))

# 5
S.append("<h1>5. Inside a project</h1>")
S.append(code("""
my_film/
  project.json      name, Khmer/English title, fps, end_target (total length in seconds, optional)
  narration.py      every spoken line (Khmer + English) and the VOICES of each speaker
  script_src.py     the shot list: what is on screen while each line is spoken
  make.py           the driver (all commands)
  engine/           private copy of the engine: patch freely for this film
  docs/             fact_sheet.md, script_km_en.md, shot_list.md, asr_report.md
  source/           saved source texts (Khmer and English)
  archive/          img/ + manifest.json  (authentic images with licences)
  geo/              Natural Earth shapes + elevation (dem_sea.npz, dem_delta.npz)
  audio/            voices/ (locked reference voices), narr/ (one wav per line), seeds.json
  build/            cache/, shots/, stills/, chunks/, mix.wav, logs
  subtitles/        <name>_en.srt, <name>_km.srt
  film/             <name>.mp4 (master), <name>_web.mp4, character_sheets/
"""))
S.append(table(["File", "You edit it to…"], [
    ["<code>narration.py</code>", "change what is said, or the voice design of a speaker"],
    ["<code>script_src.py</code>", "change what is shown: sets, camera, maps, photos, cards, music, transitions"],
    ["<code>project.json</code>", "change the title, the output file name, or the target length"],
    ["<code>engine/sets.py</code>, <code>cast.py</code>", "add new places, buildings or people for a new era"],
    ["<code>archive/manifest.json</code>", "register authentic images (licence, credit, museum, date)"],
]))

# 6
S.append("<h1>6. Step-by-step workflow</h1>")
S.append(table(["#", "Step", "Command / file", "Check"], [
    ["1", "Research the facts", "<code>source/</code>, <code>docs/fact_sheet.md</code>", "every claim tagged; DO-NOT-SAY list"],
    ["2", "Collect images", "<code>archive/img</code>, <code>manifest.json</code>", "free licence, correct caption"],
    ["3", "Create the project", "<code>new_doc.py</code>", "<code>make.py info</code> runs"],
    ["4", "Write the narration", "<code>narration.py</code>", "short sentences, Khmer digits"],
    ["5", "Build the shot list", "<code>script_src.py</code>", "cold open, chapters, badges, credits"],
    ["6", "Preview", "<code>make.py shotstills</code>", "look at every sheet"],
    ["7", "Voices", "<code>voices</code> → <code>lock</code> → <code>narrate</code>", "listen to candidates"],
    ["8", "Quality check", "<code>make.py asr</code>", "mean ≥ 0.85; reseed lines &lt; 0.78"],
    ["9", "Render", "<code>make.py all</code>, <code>make.py web</code>", "watch the whole film"],
    ["10", "Hand-off", "<code>make.py docs</code>", "native-speaker review of the Khmer"],
]))
S.append("<div class='note'><b>Preview before voices.</b> Until the voice clips exist, line lengths are estimated from the "
         "text, so <code>info</code> and <code>shotstills</code> work from the first minute. After narration the timeline "
         "adjusts itself to the real clip lengths.</div>")
S.append("<div class='note'><b>Render time.</b> About 0.35 s per frame on 6 workers, so a 15-minute film takes "
         "about 40–60 minutes. Voices take about 35–120 s per line, roughly 2–3 hours for 120 lines.</div>")

# 7
S.append("<h1>7. Writing the narration</h1>")
S.append("<p><code>narration.py</code> holds every spoken line. <code>L()</code> is the narrator and <code>T()</code> is the guide. "
         "The key (for example <code>a2</code>) links the line to a shot in <code>script_src.py</code>.</p>")
S.append(code("""
VOICES = {
    "nar":   dict(label_en="", label_km="",
                  design="A warm, calm Cambodian man in his forties, documentary narrator ...",
                  sample="នៅសតវត្សរ៍ទីប្រាំពីរ ទឹកដីកម្ពុជា មានរាជធានីដ៏ធំមួយ ..."),
    "tonle": dict(label_en="NEANG TONLE: ", label_km="នាងទន្លេ៖ ",
                  design="A bright, curious Cambodian girl about twelve years old ...",
                  sample="សួស្តី! ខ្ញុំឈ្មោះ នាងទន្លេ។ ..."),
}

T("t0", "សួស្តី! ខ្ញុំឈ្មោះ នាងទន្លេ។ ខ្ញុំជាតួអង្គប្រឌិត។ ថ្ងៃនេះ យើងទៅលេង សំបូរព្រៃគុក!",
  "Hello! I'm Neang Tonle, a made-up guide. Today we are visiting Sambor Prei Kuk!")
L("a2", "អ្នកប្រវត្តិវិទូ យល់ថា ទីនេះ គឺជាទីក្រុង ឦសានបុរៈ ... នៅសតវត្សរ៍ទី ៧។",
  "Historians identify it as Isanapura, the capital of King Isanavarman I in the 7th century.")
"""))
S.append("<h2>Writing tips</h2><ul>"
         "<li>One idea per line, and about 10–25 Khmer words. Spaces between clauses become natural pauses in the voice.</li>"
         "<li>Write numbers with Khmer digits (<span class='km'>៦១១</span>). <code>khnum.speak()</code> turns them into words for the voice.</li>"
         "<li>Put the type of evidence into the sentence: “A legend tells…”, “Chinese records say…”, “Historians still debate…”.</li>"
         "<li>Begin each chapter with a question from the guide, and let the narrator answer it.</li>"
         "<li>Editing a line re-synthesises only that line, because clips are keyed by a hash of the text, the seed and the speaker.</li></ul>")

# 8
S.append("<h1>8. Building the shot list</h1>")
S.append("<p><code>script_src.py</code> is a list of shots in order. Each shot shows a picture while its lines are "
         "spoken, so the length of the shot comes from the voice clips. Edit only the SHOTS section; the helpers and the "
         "timeline assembly stay the same.</p>")
S.append(code("""
CH(1, "ទីក្រុងឦសានបុរៈ", "The City of Isanapura", "7th century CE",
   under=lambda: X.make_chenla("day"), music="kings", amb="forest")

GUIDE("t0", lambda m: X.make_chenla("golden", people=[grp(0.6, guide(1500, 1150, 330, "wave"))],
                                     mouth_fn=m),
      cam((1450, 900, 1.5), (1450, 880, 1.6)), note=GUIDE_NOTE, trans="lotus")

S(["a3"], lambda: X.make_chenla("golden"), cam((1250, 900, 1.3), (1250, 860, 1.6)), badge="recon")

S(["a2"], lambda: cards.claim_board("អ្វីដែលយើងដឹង", "What we know", [
    ("inscription", "សិលាចារឹក ...", "Inscriptions name King Isanavarman I"),
    ("debated", "ទំហំពិតនៃទីក្រុង", "The city's true extent")]))
"""))
S.append(table(["Helper", "Shows"], [
    ["<code>S(lines, vis, cam, badge, …)</code>", "any scene: a set, a card or a custom drawing"],
    ["<code>GUIDE(key, scene_fn, cam)</code>", "the guide speaking, with lip-sync from her clip"],
    ["<code>CH(num, km, en, years, …)</code>", "chapter card over the chapter's set"],
    ["<code>M(lines, view_a, view_b, elements)</code>", "animated map (see section 9)"],
    ["<code>PH(file, lines)</code> / <code>MC(file, lines, …)</code>", "authentic photo / museum card"],
    ["<code>ZH(lines, zh, en, source)</code>", "classical Chinese text card"],
]))
S.append("<div class='two'>%s%s</div>" % (img("chapter", "Chapter card (CH)."), img("claims", "Claim board: what we know and what is debated.")))
S.append("<h2>Camera, timing and sound options</h2>")
S.append(table(["Option", "Meaning"], [
    ["<code>cam((x, y, zoom), (x, y, zoom))</code>", "move across the 2400×1350 set; zoom 1.0 shows 1920 px of it"],
    ["<code>pre</code> / <code>post</code> / <code>min_d</code>", "seconds before the first line / after the last line / minimum length"],
    ["<code>xin</code>, <code>trans</code>", "overlap with the previous shot; transition: fade, cut, ripple, lotus, ink"],
    ["<code>fade_in</code>, <code>fade_out</code>", "fade from or to black"],
    ["<code>music</code>", "starts a mood: opening, land, legend, port, water, fleet, envoys, india, life, kings, decline, legacy, credits"],
    ["<code>amb</code>", "ambience: delta, river, forest, market, port, sea, lamp, workshop, temple, village, night, none"],
    ["<code>sfx</code>", "extra sounds, for example <code>(\"hit\",)</code> or <code>(\"bell\",)</code>"],
    ["<code>TARGETS</code>, <code>end_target</code>", "chapter start times and total length: holds stretch to meet them, and narration is never cut"],
]))
S.append("<h2>Sets and people</h2>")
S.append("<p>Sets: <code>make_delta</code>, <code>make_lowland</code>, <code>make_puppet</code>, <code>make_port</code>, "
         "<code>make_sea</code>, <code>make_palace</code>, <code>make_temple</code>, <code>make_workshop</code>, "
         "<code>make_monastery</code>, <code>make_chenla</code>. Each one takes a time of day: dawn, day, golden, dusk, night or lamp. "
         "Figures are placed with <code>F(x, y, height, who, pose, yaw)</code> inside <code>grp(depth, …)</code>.</p>")
S.append(img("cast_lineup", "The built-in cast (build/character_sheet.py). Add new people for other eras in engine/cast.py."))

# 9
S.append("<h1>9. Maps</h1>")
S.append("<p>Maps are drawn as layers of paper terrain cut from real elevation data, with Natural Earth rivers and lakes. "
         "Modern borders appear only faintly. A view is <code>(longitude, latitude, width in degrees)</code>, and the camera "
         "glides from <code>view_a</code> to <code>view_b</code>.</p>")
S.append(code("""
M(["a1"], (104.9, 12.5, 9.0), (104.9, 12.5, 7.5), [
    dict(k="marker", lon=105.043, lat=12.871, km="សំបូរព្រៃគុក", en="Sambor Prei Kuk", at=1.0, pulse=True),
    dict(k="blob", pts=[(104.6, 12.4), (105.6, 12.3), (106.1, 15.3)], fill="#d8aa4a", at=2.0),
    dict(k="line", pts=[(104.97, 10.95), (105.04, 12.87)], at=1.5, ships=2),
    dict(k="note", km="...", en="Extent approximate", cls="debated", at=3.0),
    dict(k="era", text="7th century", km="សតវត្សរ៍ទី ៧", at=0.5)])
"""))
S.append(img("map", "Map shot from the sample project: paper terrain, a pulsing marker and an era label."))
S.append("<div class='note'>The default map data covers mainland Southeast Asia (wide view) and Cambodia plus the Mekong delta "
         "(close view, used when the view is narrower than 9°). For another region, run<br>"
         "<code>.venv/bin/python ~/.claude/skills/khmer-history-doc/scripts/fetch_geo.py . --local 99 12 106 18 8</code></div>")

# 10
S.append("<h1>10. Evidence: photos and records</h1>")
S.append("<p>Use only freely licensed images (public domain, CC0, CC BY, CC BY-SA), checked on the source page. Put the file in "
         "<code>archive/img/</code> and add an entry to <code>archive/manifest.json</code>:</p>")
S.append(code("""
{ "file": "img/spk_prasat_yeai_poeun.jpg",
  "object_name": "Prasat Yeay Poan, Sambor Prei Kuk",  "object_name_km": "ប្រាសាទយាយព៌ន",
  "object_date": "7th century CE (photo 2015)",      "holding_institution": "in situ",
  "licence": "CC BY-SA 4.0",
  "attribution_line": "Author / CC BY-SA 4.0 / via Wikimedia Commons",
  "authenticity_note": "what the image really shows, and what it does not" }
"""))
S.append(code("""
PH("spk_prasat_yeai_poeun.jpg", ["a3"])                      # photo with a slow Ken Burns move
MC("spk_lintel.jpg", ["a5"], date="7th c.", inst="National Museum of Cambodia")   # museum card
ZH(["k2"], "扶南國...", "“The kingdom of Funan ...”", "Liang shu 54 (636 CE)")   # Chinese record
"""))
S.append("<p>The credits list every image that was used, with its licence. If an image file is missing, <code>PH</code> falls back "
         "to a text card, so a missing download never breaks the render.</p>")

# 11
S.append("<h1>11. Voices and quality check</h1>")
S.append("<h2>Choose and lock the voices</h2>")
S.append(code("""
.venv/bin/python make.py voices          # audio/voices/cand_nar_11.wav … cand_tonle_51.wav
open audio/voices                        # listen
.venv/bin/python make.py lock nar 23     # copies cand_nar_23.wav -> nar.wav
.venv/bin/python make.py lock tonle 37
"""))
S.append("<p>Each speaker is cloned from one locked reference clip, so the voice stays the same through the whole film, and "
         "across films if you copy <code>audio/voices/</code>.</p>")
S.append("<h2>Synthesise</h2>")
S.append(code(".venv/bin/python make.py narrate     # resumable; 20 lines per fresh worker; keeps the Mac awake"))
S.append("<h2>Check with Khmer Whisper</h2>")
S.append(code("""
.venv/bin/python make.py asr
#  mean 0.912 low [('k3', 0.71)]
#  fix: make.py reseed k3 && make.py narrate
"""))
S.append("<p><code>asr</code> transcribes every clip with a Khmer Whisper model and compares the result with the script. "
         "The full table is in <code>docs/asr_report.md</code>. A low score usually means a skipped or garbled word, so "
         "re-seed the line and synthesise it again.</p>")
S.append("<div class='warn'><b>Native review is still required.</b> The ASR check catches pronunciation failures, but not "
         "awkward or wrong Khmer. Have a native-speaking historian read <code>docs/script_km_en.md</code> before you publish.</div>")

# 12
S.append("<h1>12. Rendering and outputs</h1>")
S.append(code("""
WORKERS=6 .venv/bin/python make.py all   # subs + audio mix + video + mux
.venv/bin/python make.py web             # smaller H.264 copy for YouTube / Facebook
.venv/bin/python make.py docs            # docs/script_km_en.md, docs/shot_list.md
.venv/bin/python build/character_sheet.py tonle   # character sheets
"""))
S.append(table(["Output", "Contents"], [
    ["<code>film/&lt;name&gt;.mp4</code>", "1920×1080, 24 fps, burned English subtitles, AAC 256k, soft en + km subtitle tracks"],
    ["<code>film/&lt;name&gt;_web.mp4</code>", "same film at a smaller size (CRF 24)"],
    ["<code>subtitles/*.srt</code>", "English and Khmer subtitle files"],
    ["<code>build/mix.wav</code>", "the final mix: voices, music, ambience and SFX at −16 LUFS"],
    ["<code>docs/</code>", "fact sheet, script, shot list, ASR report"],
]))
S.append("<p>The video is rendered in 10-second chunks (<code>build/chunks/</code>) in parallel. If the render stops, run the "
         "same command again and it continues where it stopped. After a visual change, delete the affected chunks "
         "(or all of them) before rendering again.</p>")
S.append("<p>You can change one part of the film without starting over:</p>")
S.append(table(["You changed…", "Run"], [
    ["a narration line", "<code>make.py narrate</code> → <code>make.py all</code> (delete the chunks after that point)"],
    ["a picture only", "delete the chunks for that shot → <code>make.py render</code>"],
    ["music or ambience", "<code>make.py audio</code> → <code>make.py mux</code>"],
    ["subtitle text", "<code>make.py subs</code> → delete the chunks (subtitles are burned in) → <code>make.py render</code>"],
]))

# 13
S.append("<h1>13. Accuracy rules and labels</h1>")
S.append("<p>The engine is built around one rule: <b>accuracy beats drama</b>. The audience must always know whether they "
         "are looking at evidence or at an artist's reconstruction.</p>")
S.append(table(["Fact-sheet tag", "How it is narrated"], [
    ["DOCUMENTED (source, year)", "“According to the Book of Liang (636)…”"],
    ["INSCRIPTION (K. number)", "“An inscription carved in stone says…”"],
    ["ARCHAEOLOGY", "“Archaeologists have found…”"],
    ["LEGEND", "“A legend tells…”"],
    ["DEBATED", "“Historians still debate…” (give both sides)"],
    ["HYPOTHESIS", "“Some historians think…”"],
    ["UNVERIFIED", "not narrated"],
]))
S.append(table(["On-screen badge", "Use for"], [
    ["recon", "paper-cut reconstructions (artistic interpretation)"],
    ["legend", "legends and origin stories"],
    ["guide", "every shot of the fictional guide"],
    ["photo / artifact / inscription / satellite", "authentic images, always with a credit line"],
    ["text", "historical records (translated)"],
    ["map / map_recon / schematic", "maps: approximate positions or reconstructed extents"],
    ["comparison", "an object from another place or period, shown for comparison"],
]))
S.append("<ul><li>Ancient kingdoms are drawn as soft zones, never with hard borders.</li>"
         "<li>Contested topics are given with each side's claim and its source, in a neutral tone.</li>"
         "<li>Every fact sheet ends with a <b>DO NOT SAY</b> list of popular myths found during research.</li></ul>")
S.append(img("recon", "Every reconstruction carries its badge in the top-left corner."))

# 14
S.append("<h1>14. Customising the look</h1>")
S.append("<p>Every project has its own copy of <code>engine/</code>, so you can change it freely without affecting other films.</p>")
S.append(table(["To add…", "Edit", "How"], [
    ["a new place", "<code>engine/sets.py</code>", "write <code>make_myplace(tod, people, mouth_fn)</code> that returns paper layers (see make_chenla)"],
    ["a new person or costume", "<code>engine/cast.py</code>", "add a <code>CAST</code> entry: body, skin, hair, wrap, top, ornaments"],
    ["a new music mood", "<code>engine/audio.py</code>", "add to <code>MOTIFS</code>: root note, scale, cell, lead instrument, tempo"],
    ["a new badge", "<code>script_src.py</code>", "<code>cards.BADGES['key'] = (colour, km, en)</code>"],
    ["colours", "<code>engine/core.py</code>", "<code>PAL</code> palette (terracotta, ochre, lotus, jade, gold…)"],
    ["a different guide", "<code>narration.py</code> + <code>cast.py</code>", "new VOICES entry and CAST entry; set <code>GUIDE</code>"],
]))
S.append(code("""
def make_myplace(tod="golden", people=None, mouth_fn=None):
    P = TOD[tod]
    def bg(ctx):
        PP.sky(ctx, P, 0.55, (0.3, 0.35), 70, 7, 140)
        PP.ridge(ctx, P, 720, 90, mix(P["far"], P["haze"], 0.3), 141)
    def ground(ctx):
        sheet(ctx, path_poly(jag([(-30, 940), (SW + 30, 940)], 3, 160) + [(SW + 30, SH + 30), (-30, SH + 30)]),
              "#9a8a5a", shadow=0.6, seed=160)
        PP.palm(ctx, P, 400, 1000, 600, "sugar", 3, P["near"])
    layers = [(_key("mp_bg", tod=tod), bg, 0.25), (_key("mp_g", tod=tod), ground, 0.6)]
    return dict(layers=layers, dyn=people_dyn(people or [], P, mouth_fn), dyn_depths=[0.25, 0.6])
"""))
S.append("<p>Layers are cached as PNG files by key. After you change a painter, delete <code>build/cache/layers/</code>. "
         "Check new pictures with <code>make.py stills 12.0</code> before rendering.</p>")
S.append(img("guide_sheet", "Character sheet for the guide: turnaround, expressions, walk cycle and actions."))

# 15
S.append("<h1>15. Troubleshooting</h1>")
S.append(table(["Problem", "Fix"], [
    ["Khmer shows as boxes", "fonts are missing: run <code>fc-list | grep Khmer</code>, then run setup.sh again"],
    ["“VoxCPM2 environment not found”", "run setup.sh, or set <code>KHDOC_VOX_PY=/path/to/python</code>"],
    ["“no locked voice for ['tonle']”", "run <code>make.py voices</code>, then <code>make.py lock tonle &lt;seed&gt;</code>"],
    ["Voice synthesis gets very slow", "normal for VoxCPM2 on MPS; <code>narrate</code> restarts the worker every 20 lines. Close other apps; never run two workers"],
    ["A line skips or garbles words", "<code>make.py reseed &lt;key&gt;</code> → <code>make.py narrate</code>"],
    ["The credits are cut off at the end", "never add <code>-shortest</code> to ffmpeg when subtitle tracks are present"],
    ["An old picture still appears after an edit", "delete <code>build/chunks/</code> (and <code>build/cache/layers/</code> if a painter changed)"],
    ["A punched hole cuts through the whole frame", "draw Cairo OPERATOR_CLEAR inside <code>push_group()</code>"],
    ["A map is blank or flat", "run <code>scripts/fetch_geo.py &lt;project&gt;</code>; check <code>geo/dem_*.npz</code>"],
    ["Chapters start at the wrong times", "set <code>TARGETS</code> (one per chapter) and <code>end_target</code>; holds stretch but never shrink"],
]))

# 16
S.append("<h1>16. Command cheat sheet</h1>")
S.append(table(["Command", "Does"], [
    ["<code>scripts/setup.sh</code>", "one-time install"],
    ["<code>scripts/new_doc.py &lt;dir&gt; --title-en … --title-km …</code>", "new project (add <code>--example funan</code> for the full example)"],
    ["<code>scripts/fetch_geo.py &lt;dir&gt; [--local …]</code>", "map data"],
    ["<code>make.py info</code>", "runtime, chapter times, shot list"],
    ["<code>make.py shotstills [i …]</code>", "preview frames + contact sheets"],
    ["<code>make.py stills t …</code>", "frames at given times"],
    ["<code>make.py voices</code> / <code>lock who seed</code>", "design / lock voices"],
    ["<code>make.py narrate</code>", "synthesise missing lines"],
    ["<code>make.py asr</code> / <code>reseed key …</code>", "QC / redo lines"],
    ["<code>make.py subs</code> / <code>audio</code>", "subtitles / music + voice mix"],
    ["<code>make.py render</code> / <code>video</code> / <code>mux</code>", "full render / picture only / final mux"],
    ["<code>make.py all</code>", "subs + audio + render"],
    ["<code>make.py web</code> / <code>docs</code>", "web copy / script and shot-list docs"],
    ["<code>build/character_sheet.py [who]</code>", "character sheets"],
]))
S.append(img("funan_storyboard", "Storyboard sheet from the Funan film (15:41), the full example in examples/funan/."))
S.append("<p style='margin-top:6mm;color:#6a5a42;font-size:9pt'>Map data: Natural Earth (public domain) and SRTM-derived terrarium "
         "tiles (Mapzen / AWS Open Data). Voices: VoxCPM2 (OpenBMB). ASR check: seanghay/whisper-small-khmer-v2. "
         "Archival images in the screenshots keep their own licences, as credited on screen.</p>")

doc = "<!doctype html><html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (CSS, "\n".join(S))
src = os.path.join(DOCS, "guide.html")
open(src, "w").write(doc)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=" + OUT,
                "file://" + src], check=True, stderr=subprocess.DEVNULL)
print(OUT)
