# Gotchas learned over five films

- **VoxCPM2 memory:** it runs in float32 on MPS (about 10 GB) and slows from about 35 s to about 120 s per line during a run.
  `make.py narrate` starts a fresh worker every 20 lines. Check `pgrep -fl tts_vox` first, so that no stale worker is running.
- **Waiting on jobs:** never wait with `pgrep -f "make.py video"`. That pattern matches the waiting shell's own command line, so the wait never ends.
- **Cache keys:** each clip is named `<key>_<sha1(text|seed|who)>.wav`. Old clips are not deleted, so clear
  `audio/narr/` of stale files before shipping.
- **ASR scoring:** Whisper outputs digits. `khnum.speak` turns them into Khmer words before scoring. A mean of 0.85 or more is good,
  and lines below 0.78 should be re-seeded.
- **ffmpeg:** never use `-shortest` together with subtitle streams, because it truncated the credits.
- **Cairo:** draw `OPERATOR_CLEAR` (punched holes) inside `push_group()`/`pop_group_to_source()`.
- **Layer cache:** set layers are cached as PNG files in `build/cache/layers/`, keyed by the `_key(...)` arguments. After you change a
  painter, change its key or delete the cache.
- **Chunks:** `build/chunks/` holds 10-second video chunks. After you edit a shot, delete only the chunks it covers
  (frame range = start × fps).
- **zsh:** use arrays for lists of IDs (`ids=(a1 a2); for i in $ids`).
- **Fonts:** if Khmer renders as boxes, `fc-list | grep Khmer` will show it is missing. Run setup.sh again.
- **Commons dates:** check the event date on the image's file page (for example, the ICJ Preah Vihear photos are from 1961, not 1962).
