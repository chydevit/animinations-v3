# Workflow checklist

## 0. Brief
- Topic, period, length (default 15 min), audience (default: students aged 12 and up, and general Cambodian viewers).
- Chapter plan with target start times. These go into `TARGETS` in script_src.py.
- Guide character: who they are and why they are there. Default: Neang Tonle, a curious girl. Always labelled fictional.

## 1. Research (before any drawing)
- `source/`: save the Khmer sources (Khmer Wikipedia, RFA Khmer, VOA Khmer, Kampuchea Thmey, ministry pages) and the English sources as .txt files.
- `docs/fact_sheet.md`: tag every claim (see accuracy.md). Add a **DO NOT SAY** list of popular myths.
- `docs/khmer_sources_summary.md`: what the Khmer-language sources say, and where they differ from the scholarship.
- Archive agent: freely licensed images only. Record each one in `archive/manifest.json` (see archive/README.md) and make a contact sheet. Check that each image really shows what the caption says.

## 2. Script
- `narration.py`: about 12–14 lines per 5 minutes. Use short Khmer clauses separated by spaces, which gives the voice natural pauses. Write numbers with Khmer digits.
- The guide asks a question at the start of each chapter, then the narrator answers it.
- Put legend, record and debate into the words themselves: "A legend tells…", "Chinese records say…", "Historians still debate…".

## 3. Shot list (script_src.py)
- Cold open of about 37 s: three or four striking images, each with a one-line hook card, then the title.
- Each chapter: `CH(n, km, en, years, under=…, music=…, amb=…)`, then `GUIDE` (the question), then evidence shots (`PH`, `MC`, `ZH`, `M`) mixed with reconstructions (`S` with a set and badge="recon").
- Use a claim board (`cards.claim_board`) whenever sources disagree.
- Credits list the primary sources, the scholarship, every archival image with its licence, and the map data.

## 4. Preview loop
`make.py info` → `make.py shotstills` → look at the sheets → fix → repeat. `make.py stills 12.5 40 300` checks single moments.

## 5. Voices
`make.py voices` → listen → `make.py lock nar 23` → `make.py lock tonle 37` → `make.py narrate` (resumable) → `make.py asr` → `make.py reseed k3 p7` → `make.py narrate`.

## 6. Render
`make.py all` renders at about 0.35 s per frame on 6 workers, so a 15-minute film takes about 40–60 minutes. Chunks are cached in `build/chunks/`. Delete the chunks after any visual change, or only the ones affected.
`make.py web` writes the smaller copy for upload. `make.py docs` writes the script and shot-list documents.

## 7. Hand-off
Report the runtime, the files, the ASR mean and any low lines, and the list of facts that still need native-speaker or historian review.
