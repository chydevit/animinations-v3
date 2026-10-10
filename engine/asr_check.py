"""Khmer Whisper round-trip QC (runs in the skill's .venv-vox).
usage: asr_check.py jobs.json out.json   jobs: [{"id", "wav", "text"}]
Prints one JSON line per job (so partial progress survives) and writes out.json at the end."""
import json, os, sys, difflib, re
import numpy as np, soundfile as sf, torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import scipy.signal as ss

M = "seanghay/whisper-small-khmer-v2"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from khnum import speak  # noqa


def norm(s):
    return re.sub(r"[\s​។៕,.!?\-–—:;\"'«»()]+", "", s)


def main(jp, op):
    jobs = json.load(open(jp))
    proc = WhisperProcessor.from_pretrained(M)
    model = WhisperForConditionalGeneration.from_pretrained(M).eval()
    if torch.backends.mps.is_available():
        model = model.to("mps")
    dev = next(model.parameters()).device
    out = []
    for j in jobs:
        w, sr = sf.read(j["wav"], dtype="float32")
        if w.ndim > 1:
            w = w.mean(1)
        if sr != 16000:
            w = ss.resample_poly(w, 16000, sr).astype(np.float32)
        feats = proc(w[:16000 * 30], sampling_rate=16000, return_tensors="pt").input_features.to(dev)
        with torch.no_grad():
            ids = model.generate(feats, max_new_tokens=440)
        hyp = proc.batch_decode(ids, skip_special_tokens=True)[0]
        score = difflib.SequenceMatcher(None, norm(speak(j["text"])), norm(speak(hyp))).ratio()
        out.append({"id": j["id"], "score": round(score, 3), "hyp": hyp})
        print(json.dumps(out[-1], ensure_ascii=False), flush=True)
    json.dump(out, open(op, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
