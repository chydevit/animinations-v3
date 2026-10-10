"""VoxCPM2 worker (runs inside .venv-vox). Loads the model once and processes a job file.

jobs.json: {"voices": [{"voice_id", "design", "sample_text", "out_wav", "seed"}],
            "lines":  [{"id", "text", "ref_wav", "ref_text", "out_wav", "seed", "cfg", "steps",
                        "clone_mode": "ref|prompt|both"}]}
Existing out_wav files are skipped (cache). Prints one JSON line per finished item.
"""
import json
import os
import sys
import time

import numpy as np
import soundfile as sf
import torch


def main(path):
    jobs = json.load(open(path))
    todo_v = [v for v in jobs.get("voices", []) if not os.path.exists(v["out_wav"])]
    todo_l = [l for l in jobs.get("lines", []) if not os.path.exists(l["out_wav"])]
    if not todo_v and not todo_l:
        print(json.dumps({"status": "nothing to do"}), flush=True)
        return
    from voxcpm import VoxCPM
    t0 = time.time()
    model = VoxCPM.from_pretrained(os.environ.get("VOXCPM_MODEL", "openbmb/VoxCPM2"), load_denoiser=False)
    sr = model.tts_model.sample_rate
    print(json.dumps({"status": "loaded", "secs": round(time.time() - t0, 1), "sr": sr}), flush=True)

    for v in todo_v:
        torch.manual_seed(int(v.get("seed", 1234)))
        text = "(%s)%s" % (v["design"], v["sample_text"]) if v.get("design") else v["sample_text"]
        t1 = time.time()
        wav = model.generate(text=text, cfg_value=float(v.get("cfg", 2.0)),
                             inference_timesteps=int(v.get("steps", 10)))
        wav = _trim(np.asarray(wav, dtype=np.float32), sr)
        os.makedirs(os.path.dirname(v["out_wav"]), exist_ok=True)
        sf.write(v["out_wav"], wav, sr)
        print(json.dumps({"voice": v["voice_id"], "secs": round(time.time() - t1, 1),
                          "dur": round(len(wav) / sr, 2)}), flush=True)

    for ln in todo_l:
        torch.manual_seed(int(ln.get("seed", 7)))
        kw = {}
        mode = ln.get("clone_mode", "ref")
        text = ln["text"]
        if ln.get("ref_wav"):
            if mode in ("ref", "both"):
                kw["reference_wav_path"] = ln["ref_wav"]
            if mode in ("prompt", "both"):
                kw["prompt_wav_path"] = ln["ref_wav"]
                kw["prompt_text"] = ln["ref_text"]
        elif ln.get("design"):
            text = "(%s)%s" % (ln["design"], text)
        t1 = time.time()
        wav = model.generate(text=text, cfg_value=float(ln.get("cfg", 2.0)),
                             inference_timesteps=int(ln.get("steps", 10)), **kw)
        wav = _trim(np.asarray(wav, dtype=np.float32), sr)
        os.makedirs(os.path.dirname(ln["out_wav"]), exist_ok=True)
        sf.write(ln["out_wav"], wav, sr)
        print(json.dumps({"line": ln["id"], "secs": round(time.time() - t1, 1),
                          "dur": round(len(wav) / sr, 2)}), flush=True)


def _trim(w, sr, thr=0.012, pad=0.06):
    if len(w) == 0:
        return w
    a = np.abs(w)
    idx = np.where(a > thr * max(a.max(), 1e-6) * 4)[0]
    if len(idx) == 0:
        return w
    s = max(0, idx[0] - int(pad * sr))
    e = min(len(w), idx[-1] + int(pad * 2 * sr))
    return w[s:e]


if __name__ == "__main__":
    main(sys.argv[1])
