# Khmer History Documentary Builder (`khmer-history-doc`)

This is a Claude Code skill that makes **narrated Cambodian history documentaries**: Khmer voices, English subtitles,
a paper-cut / Sbek shadow-puppet look, real-terrain maps, and authentic archival images. Every shot is labelled as
reconstruction, legend, record or evidence.

📘 **Guide:** [`docs/Khmer_History_Documentary_Guide.pdf`](docs/Khmer_History_Documentary_Guide.pdf)

## Install

```bash
git clone https://github.com/chydevit/animinations-v3.git ~/.claude/skills/khmer-history-doc
~/.claude/skills/khmer-history-doc/scripts/setup.sh
```

Requirements: macOS (Apple Silicon, 16 GB RAM or more recommended), Homebrew and Python 3.12. Setup installs ffmpeg, cairo,
pango, the Khmer fonts, a render environment and the VoxCPM2 voice environment (the model is about 5 GB).

## Use it with Claude Code

Just ask:

> Make a 15-minute Khmer documentary about Sambor Prei Kuk, with a child guide.

Claude follows `SKILL.md`: research and fact sheet → project → narration → shot list → previews → voices → ASR check → render.

## Use it by hand

```bash
SK=~/.claude/skills/khmer-history-doc
$SK/.venv/bin/python $SK/scripts/new_doc.py ~/animation-2D/my_film --title-en "My Film" --title-km "ខ្សែភាពយន្តខ្ញុំ"
cd ~/animation-2D/my_film
.venv/bin/python make.py info          # runtime + shot list
.venv/bin/python make.py shotstills    # preview sheets in build/shots/
.venv/bin/python make.py voices        # candidate voices -> listen
.venv/bin/python make.py lock nar 23   # lock the narrator; same for the guide
.venv/bin/python make.py narrate       # synthesise all lines
.venv/bin/python make.py asr           # Khmer Whisper QC
.venv/bin/python make.py all           # subtitles + mix + render -> film/<name>.mp4
```

## Contents

| path | what |
|---|---|
| `SKILL.md` | instructions Claude follows |
| `engine/` | drawing, maps, cast, cards, film renderer, audio, VoxCPM2 + ASR workers |
| `template/` | starter project (a short sample about Sambor Prei Kuk) |
| `examples/funan/` | the complete 15-minute *Funan – Kingdom of the Mountain* source, fact sheet and research |
| `scripts/` | `setup.sh`, `new_doc.py`, `fetch_geo.py`, `make_guide_pdf.py` |
| `references/` | workflow, engine API, accuracy rules, gotchas |

## Credits and licences of data

Map data: Natural Earth (public domain) and SRTM-derived terrarium tiles (Mapzen / AWS Open Data). Voices: VoxCPM2
(OpenBMB). ASR check: `seanghay/whisper-small-khmer-v2`. Archival images keep their own licences, recorded in each project's
`archive/manifest.json`.

Khmer narration generated with this tool should be reviewed by a native-speaking historian before publication.
