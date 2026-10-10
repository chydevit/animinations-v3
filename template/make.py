"""Driver.  .venv/bin/python make.py <cmd>

  info                     runtime, chapter starts and the shot list
  voices                   design 4 candidate reference voices per speaker (audio/voices/cand_<who>_<seed>.wav)
  lock <who> <seed>        lock a candidate as the speaker's voice (audio/voices/<who>.wav)
  narrate                  synthesise all missing lines, 20 per fresh worker (VoxCPM2 slows down over time)
  asr                      Khmer Whisper round-trip check of every line -> docs/asr_report.md
  reseed <key> ...         give lines a new seed (re-synthesised by the next `narrate`)
  shotstills [i ...]       one still per shot + contact sheets in build/shots/
  stills t ...             stills at times t (s) in build/stills/
  audio                    music + ambience + SFX + voices -> build/mix.wav (-16 LUFS)
  subs                     subtitles/<name>_en.srt and _km.srt
  docs                     docs/script_km_en.md and docs/shot_list.md from the live shot list
  render                   video (burned English subtitles), then mux -> film/<name>.mp4
  video | mux              only the picture | only the final mux
  web                      smaller H.264 copy -> film/<name>_web.mp4
  all                      subs, audio, render
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, ROOT)
PROJECT = json.load(open(os.path.join(ROOT, "project.json")))
NAME = PROJECT["name"]
FPS = PROJECT.get("fps", 24)


def srt_time(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return "%02d:%02d:%02d,%03d" % (h, m, int(s), int(round((s - int(s)) * 1000)) % 1000)


def _still_job(j):
    import film
    film.still("script_src", j[1], j[2])


def _grid(paths, out, cols=4, label=True):
    from PIL import Image, ImageDraw
    paths = [p for p in paths if os.path.exists(p)]
    if not paths:
        return
    ims = [Image.open(p).convert("RGB").resize((640, 360)) for p in paths]
    g = Image.new("RGB", (640 * cols, 360 * ((len(ims) + cols - 1) // cols)))
    d = ImageDraw.Draw(g)
    for i, im in enumerate(ims):
        g.paste(im, ((i % cols) * 640, (i // cols) * 360))
        if label:
            d.text(((i % cols) * 640 + 8, (i // cols) * 360 + 8), os.path.basename(paths[i]), fill="yellow")
    g.save(out, quality=82)


def narrate_loop(batch=20):
    from narrate import jobs
    while True:
        todo = [ln for ln in jobs()["lines"] if not os.path.exists(ln["out_wav"])]
        print("remaining %d" % len(todo), flush=True)
        if not todo:
            return
        cmd = [sys.executable, os.path.join(ROOT, "engine", "narrate.py")]
        if sys.platform == "darwin":
            cmd = ["caffeinate", "-i"] + cmd
        subprocess.run(cmd, check=True, env=dict(os.environ, LIMIT=str(batch)))
        if len([ln for ln in jobs()["lines"] if not os.path.exists(ln["out_wav"])]) == len(todo):
            sys.exit("no progress: check the VoxCPM2 worker output above")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    if cmd == "voices":
        subprocess.run([sys.executable, os.path.join(ROOT, "engine", "narrate.py"), "voices"], check=True)
        print("listen to audio/voices/cand_*.wav, then: make.py lock <who> <seed>")
        return
    if cmd == "lock":
        import shutil
        who, sd = sys.argv[2], sys.argv[3]
        shutil.copy(os.path.join(ROOT, "audio", "voices", "cand_%s_%s.wav" % (who, sd)),
                    os.path.join(ROOT, "audio", "voices", "%s.wav" % who))
        print("locked %s = seed %s" % (who, sd))
        return
    if cmd == "narrate":
        narrate_loop()
        return
    if cmd == "reseed":
        from narrate import SEEDS_FILE, seeds
        sd = seeds()
        for k in sys.argv[2:]:
            sd[k] = sd.get(k, 7) + 101
        os.makedirs(os.path.dirname(SEEDS_FILE), exist_ok=True)
        json.dump(sd, open(SEEDS_FILE, "w"), indent=1)
        print("new seeds:", {k: sd[k] for k in sys.argv[2:]})
        return

    import script_src as SS
    shots, pl, cues = SS.build()
    total = shots[-1]["start"] + shots[-1]["dur"]
    if cmd == "info":
        print("runtime %d:%02d, shots %d" % (total // 60, total % 60, len(shots)))
        for i in SS.CHAPTERS:
            print("  chapter at %d:%02d" % (shots[i]["start"] // 60, shots[i]["start"] % 60))
        for i, s in enumerate(shots):
            print("%3d %6.1f %5.1f %-11s %s" % (i, s["start"], s["dur"], s.get("badge") or "", ",".join(s["lines"])))
    elif cmd == "shotstills":
        from multiprocessing import Pool
        d = os.path.join(ROOT, "build", "shots")
        os.makedirs(d, exist_ok=True)
        sel = [int(x) for x in sys.argv[2:]] or range(len(shots))
        jobs = [(i, shots[i]["start"] + shots[i]["dur"] * 0.6, os.path.join(d, "s%03d.png" % i)) for i in sel]
        with Pool(int(os.environ.get("WORKERS", "4"))) as p:
            p.map(_still_job, jobs)
        outs = [j[2] for j in jobs]
        for k in range(0, len(outs), 24):
            _grid(outs[k:k + 24], os.path.join(d, "sheet_%02d.jpg" % (k // 24)))
        print(d)
    elif cmd == "stills":
        import film
        d = os.path.join(ROOT, "build", "stills")
        os.makedirs(d, exist_ok=True)
        outs = []
        for a in sys.argv[2:]:
            o = os.path.join(d, "t%07.1f.png" % float(a))
            film.still("script_src", float(a), o)
            outs.append(o)
        _grid(outs, os.path.join(d, "grid.jpg"), 3)
        print(d)
    elif cmd == "audio":
        import audio
        audio.mix(shots, pl, total, os.path.join(ROOT, "build", "mix.wav"))
    elif cmd == "subs":
        write_subs(pl, cues)
    elif cmd == "asr":
        asr()
    elif cmd == "docs":
        write_docs(SS, shots)
    elif cmd in ("render", "video", "mux", "all"):
        if cmd == "all":
            write_subs(pl, cues)
            import audio
            audio.mix(shots, pl, total, os.path.join(ROOT, "build", "mix.wav"))
        import film
        out = os.path.join(ROOT, "build", "video_burned.mp4")
        if cmd != "mux":
            film.render("script_src", out, os.path.join(ROOT, "build", "chunks"), int(total * FPS),
                        workers=int(os.environ.get("WORKERS", "6")), burn=True)
        if cmd == "video":
            return
        mux(out)
    elif cmd == "web":
        src = os.path.join(ROOT, "film", NAME + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-map", "0:v", "-map", "0:a", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", os.path.join(ROOT, "film", NAME + "_web.mp4")], check=True)
    else:
        sys.exit(__doc__)


def write_subs(pl, cues):
    from narration import N, VOICES
    os.makedirs(os.path.join(ROOT, "subtitles"), exist_ok=True)
    with open(os.path.join(ROOT, "subtitles", NAME + "_en.srt"), "w") as f:
        for i, c in enumerate(cues, 1):
            txt = VOICES.get(c.get("who"), {}).get("label_en", "") + c["en"]
            f.write("%d\n%s --> %s\n%s\n\n" % (i, srt_time(c["start"]), srt_time(c["end"]), txt))
    with open(os.path.join(ROOT, "subtitles", NAME + "_km.srt"), "w") as f:
        for i, p in enumerate(pl, 1):
            txt = VOICES.get(p["who"], {}).get("label_km", "") + N[p["key"]][0]
            f.write("%d\n%s --> %s\n%s\n\n" % (i, srt_time(p["t"]), srt_time(p["t"] + p["dur"] + 0.15), txt))
    print("subtitles written")


def mux(video):
    os.makedirs(os.path.join(ROOT, "film"), exist_ok=True)
    final = os.path.join(ROOT, "film", NAME + ".mp4")
    # no -shortest: with subtitle tracks it cuts the credits
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", os.path.join(ROOT, "build", "mix.wav"),
                    "-i", os.path.join(ROOT, "subtitles", NAME + "_en.srt"),
                    "-i", os.path.join(ROOT, "subtitles", NAME + "_km.srt"),
                    "-map", "0:v", "-map", "1:a", "-map", "2", "-map", "3", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "256k", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                    "-metadata:s:s:1", "language=khm", "-metadata", "title=" + PROJECT["title_en"],
                    "-movflags", "+faststart", final], check=True)
    print(final)


def asr():
    from narration import N
    from narrate import vox_python, wav_for
    from khnum import speak
    jobs = [{"id": k, "wav": wav_for(k), "text": speak(N[k][0])} for k in N if os.path.exists(wav_for(k))]
    if not jobs:
        sys.exit("no narration yet: run make.py narrate")
    jp, op = os.path.join(ROOT, "build", "asr_jobs.json"), os.path.join(ROOT, "build", "asr_out.json")
    json.dump(jobs, open(jp, "w"), ensure_ascii=False)
    with open(os.path.join(ROOT, "build", "asr_progress.log"), "w") as lf:
        subprocess.run([vox_python(), os.path.join(ROOT, "engine", "asr_check.py"), jp, op], check=True, stdout=lf,
                       stderr=subprocess.DEVNULL)
    res = json.load(open(op))
    thr = float(os.environ.get("ASR_THR", "0.78"))
    low = [r for r in res if r["score"] < thr]
    md = ["# Narration ASR round-trip check", "",
          "Khmer Whisper (seanghay/whisper-small-khmer-v2) transcribes each line; score = character similarity.",
          "", "Lines: %d · mean %.3f · below %.2f: %d" % (len(res), sum(r["score"] for r in res) / len(res), thr,
                                                         len(low)), "", "| line | score | heard |", "|---|---|---|"]
    for r in sorted(res, key=lambda r: r["score"]):
        md.append("| %s | %.3f | %s |" % (r["id"], r["score"], r["hyp"].replace("|", "/")))
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    open(os.path.join(ROOT, "docs", "asr_report.md"), "w").write("\n".join(md))
    print("mean %.3f low %s" % (sum(r["score"] for r in res) / len(res), [(r["id"], r["score"]) for r in low]))
    if low:
        print("fix: make.py reseed %s && make.py narrate" % " ".join(r["id"] for r in low))


def write_docs(SS, shots):
    from narration import N, WHO, VOICES
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    md = ["# %s · %s — script (Khmer / English)" % (PROJECT["title_km"], PROJECT["title_en"]), ""]
    for k, (km, en) in N.items():
        who = WHO.get(k, "nar")
        lab = VOICES.get(who, {}).get("label_en", "").strip(" :") or "NARRATOR"
        md += ["**%s** · `%s`" % (lab, k), "", km, "", "_%s_" % en, ""]
    open(os.path.join(ROOT, "docs", "script_km_en.md"), "w").write("\n".join(md))
    md = ["# Shot list", "", "| # | start | dur | badge | lines | note |", "|---|---|---|---|---|---|"]
    for i, s in enumerate(shots):
        md.append("| %d | %d:%04.1f | %.1f | %s | %s | %s |" % (i, s["start"] // 60, s["start"] % 60, s["dur"],
                                                              s.get("badge") or "", ", ".join(s["lines"]),
                                                              (s.get("badge_note") or "").replace("|", "/")))
    open(os.path.join(ROOT, "docs", "shot_list.md"), "w").write("\n".join(md))
    print("docs/script_km_en.md, docs/shot_list.md")


if __name__ == "__main__":
    main()
