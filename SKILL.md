---
name: khmer-history-doc
description: Khmer History Documentary Builder. Turns a Cambodian history, archaeology or heritage topic into a finished narrated 2D documentary MP4. Each film uses a paper-cut / Sbek shadow-puppet look and a fictional child guide with lip-sync. It includes animated paper-terrain maps from real elevation data, authentic archival photos and museum cards with licences, Khmer narration in locked VoxCPM2 voices, original pinpeat-style music, and burned English plus soft Khmer/English subtitles. Every shot is labelled as reconstruction, legend, record, inscription or debate. Use it whenever the user wants a Khmer or Cambodian history documentary, educational history film, heritage video or "doc" about a kingdom, temple, province or era (Funan, Chenla, Angkor, Sambor Prei Kuk, Preah Vihear, Khmer Rouge and so on), even if they don't name the skill. Also use it to continue, fix or re-render a project made with it. For chibi cartoon stories, use khmer-2d-animation instead.
---

# Khmer History Documentary Builder

This skill produces 10–20-minute educational documentaries in Khmer, with English subtitles, in a hand-made paper-cut style. The engine was refined over five films (Kampong Cham, Khmer Rouge, Preah Vihear, Ta Moan and Funan). The Funan film (15:41) is the full worked example in `examples/funan/`.

**The rule above all others: accuracy beats drama.** Never invent history. Every narrated claim must come from `docs/fact_sheet.md`, with a tag such as DOCUMENTED, INSCRIPTION, ARCHAEOLOGY, LEGEND, DEBATED or HYPOTHESIS. Every picture that is not authentic evidence carries an on-screen badge (`recon`, `legend`, `map_recon`, `guide`, …). The guide character is always labelled fictional.

## Layout

```
khmer-history-doc/
  engine/        drawing + film engine (copied into every project, patch it freely there)
  template/      new-project files: narration.py, script_src.py, make.py, project.json, docs/, archive/, build/
  examples/funan full Funan film source: narration, shot list, fact sheet, research docs, image manifest
  scripts/       setup.sh · new_doc.py · fetch_geo.py
  references/    workflow.md · engine-api.md · accuracy.md · gotchas.md
  docs/          How-to-use guide (PDF)
```

## Setup (once)

```bash
~/.claude/skills/khmer-history-doc/scripts/setup.sh
```

This installs ffmpeg, cairo, pango and the fonts (Noto Sans/Serif Khmer, Moul, Cormorant Garamond). It creates `.venv` for rendering and `.venv-vox` for VoxCPM2 and Khmer Whisper; when khmer-2d-animation is installed, it reuses that skill's `.venv-vox`. It also downloads the VoxCPM2 model, about 5 GB.

## Workflow

Read `references/workflow.md` for the full checklist. In short:

1. **Research first.** Collect Khmer and English sources into `source/`. Write `docs/fact_sheet.md`, with tags and a DO-NOT-SAY list. Run research and archive subagents in parallel: one verifies facts, one finds freely licensed images (Wikimedia Commons, museums) and fills in `archive/manifest.json` plus `archive/img/`.
2. **Create the project:**
   `~/.claude/skills/khmer-history-doc/.venv/bin/python ~/.claude/skills/khmer-history-doc/scripts/new_doc.py ~/animation-2D/<slug> --title-en "…" --title-km "…"`
   This also fetches the map data. For a region outside Cambodia, pass `--local lon0 lat0 lon1 lat1 8` to `fetch_geo.py`.
3. **Write `narration.py`.** Use `L(key, km, en)` for the narrator and `T(key, km, en)` for the guide. Keep sentences short, one idea per line, with Khmer digits. Set up `VOICES` (a design prompt and a sample sentence for each speaker).
4. **Write `script_src.py`.** Replace only the SHOTS section. Start with a cold-open teaser of about 37 s (hook cards plus highlights), then the title card. Each chapter is `CH(...)` followed by its shots. Credits come last. Put chapter timings from the brief in `TARGETS`, and the total length in `end_target` in project.json.
5. **Preview:** run `make.py info`, then `make.py shotstills`, and look at `build/shots/sheet_*.jpg`. Fix layout, badges and camera moves before any voice work.
6. **Voices:** run `make.py voices`, listen to `audio/voices/cand_*.wav`, run `make.py lock nar <seed>` and `make.py lock <guide> <seed>`, then `make.py narrate`. This takes about 35–120 s per line, in batches of 20 on fresh workers.
7. **QC:** run `make.py asr`. It runs Khmer Whisper on every line. For low lines, run `make.py reseed <keys>` and then `make.py narrate` again.
8. **Render:** run `make.py all` (subtitles, then the audio mix, then the picture, then the mux) to get `film/<name>.mp4`. Then run `make.py web` for a smaller copy and `make.py docs` for the script and shot list.
9. **Report:** give the runtime, the output paths and the ASR mean. Remind the user that the Khmer text needs review by a native-speaking historian before publication.

## Creating new visuals

The sets in `engine/sets.py` are delta, lowland, puppet screen, port, sea, palace, temple, workshop, monastery and chenla (brick towers). The cast in `engine/cast.py` includes the guide "tonle", Funan-era villagers, envoys, monks and others. For a new era, add `make_*` set builders and `CAST` entries in the project's own `engine/` copy. Follow the paper-sheet idiom: `sheet(ctx, path, colour, shadow, seed)`, layers cached by key, and a `dyn` function for anything that moves. Check every new piece with `make.py stills <t>` before rendering. `references/engine-api.md` lists the helpers.

## Gotchas (read references/gotchas.md)

- VoxCPM2 slows down as it runs. `make.py narrate` already uses batches of 20 under `caffeinate`. Never run two workers at once.
- Narration clips are keyed by a hash of the text, the seed and the speaker. Editing a line re-synthesises only that line; reordering shots re-synthesises nothing.
- Whisper writes digits, so ASR normalises them with `khnum.speak` before scoring.
- Never add `-shortest` to the mux: it cuts the credits when subtitle tracks are present.
- Draw Cairo `OPERATOR_CLEAR` inside `push_group`, or it punches through the whole frame.
