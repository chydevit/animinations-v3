"""VoxCPM2 synthesis.  Every speaker is cloned from ONE locked reference clip: audio/voices/<who>.wav.
Speakers are declared in the project's narration.py as VOICES = {who: dict(label, design, sample)}.

usage: narrate.py            synthesise missing lines (LIMIT env = max lines this run)
       narrate.py voices     design candidate reference clips (audio/voices/cand_<who>_<seed>.wav)"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, ENGINE)
from khnum import speak  # noqa
import narration  # noqa
from narration import N, WHO  # noqa

VOICES = getattr(narration, "VOICES", {})
SEEDS_FILE = os.path.join(ROOT, "audio", "seeds.json")
CAND_SEEDS = (11, 23, 37, 51)


def vox_python():
    """Python of the VoxCPM2 environment: $KHDOC_VOX_PY, this skill's .venv-vox, or khmer-2d-animation's."""
    cands = [os.environ.get("KHDOC_VOX_PY", ""),
             os.path.expanduser("~/.claude/skills/khmer-history-doc/.venv-vox/bin/python"),
             os.path.expanduser("~/.claude/skills/khmer-2d-animation/.venv-vox/bin/python")]
    for c in cands:
        if c and os.path.exists(c):
            return c
    sys.exit("VoxCPM2 environment not found: run the skill's setup.sh (or set KHDOC_VOX_PY)")


def voice_wav(who):
    return os.path.join(ROOT, "audio", "voices", "%s.wav" % who)


def seeds():
    return json.load(open(SEEDS_FILE)) if os.path.exists(SEEDS_FILE) else {}


def wav_for(key):
    km = N[key][0]
    who = WHO.get(key, "nar")
    sd = seeds().get(key, 7)
    h = hashlib.sha1(("%s|%s|%s" % (speak(km), sd, who)).encode()).hexdigest()[:10]
    return os.path.join(ROOT, "audio", "narr", "%s_%s.wav" % (key, h))


def jobs():
    out = {"voices": [], "lines": []}
    for key, (km, en) in N.items():
        who = WHO.get(key, "nar")
        out["lines"].append({"id": key, "text": speak(km), "ref_wav": voice_wav(who), "ref_text": "",
                             "out_wav": wav_for(key), "seed": seeds().get(key, 7), "cfg": 2.0, "steps": 10,
                             "clone_mode": "ref"})
    return out


def run(j, name="narr_jobs.json"):
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    p = os.path.join(ROOT, "build", name)
    json.dump(j, open(p, "w"), ensure_ascii=False, indent=1)
    subprocess.run([vox_python(), os.path.join(ENGINE, "tts_vox.py"), p], check=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "audio", "narr"), exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "voices":
        v = []
        for who, spec in VOICES.items():
            for sd in CAND_SEEDS:
                v.append({"voice_id": "%s_%d" % (who, sd), "design": spec["design"], "sample_text": speak(spec["sample"]),
                          "out_wav": os.path.join(ROOT, "audio", "voices", "cand_%s_%d.wav" % (who, sd)), "seed": sd})
        run({"voices": v, "lines": []}, "voice_jobs.json")
        sys.exit(0)
    missing = sorted({WHO.get(k, "nar") for k in N if not os.path.exists(voice_wav(WHO.get(k, "nar")))})
    if missing:
        sys.exit("no locked voice for %s: run `make.py voices`, then `make.py lock <who> <seed>`" % missing)
    j = jobs()
    todo = [ln for ln in j["lines"] if not os.path.exists(ln["out_wav"])]
    print("lines: %d, to synthesise: %d" % (len(j["lines"]), len(todo)), flush=True)
    lim = int(os.environ.get("LIMIT", "0"))
    j["lines"] = todo[:lim] if lim else todo
    if j["lines"]:
        run(j)
