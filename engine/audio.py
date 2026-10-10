"""Score, ambience and mix.  Instruments come from sound.py's synthesised pinpeat set
(roneat, kong, khloy, tro, chapei, skor, ching) plus a soft string-like pad.  Each chapter has its own motif
(a short pentatonic cell) and instrument colour; music ducks under the voices; master at -16 LUFS."""
import math
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound as S  # noqa: E402

SR = S.SR


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or len(x) == 0:
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += np.asarray(x[:j - i], dtype=np.float64) * g


def _fade(y, fi=2.0, fo=3.0):
    n = len(y)
    a, b = min(n // 2, int(fi * SR)), min(n // 2, int(fo * SR))
    if a:
        y[:a] *= np.linspace(0, 1, a)
    if b:
        y[-b:] *= np.linspace(1, 0, b)
    return y


# motif = scale-degree cell; lead instrument; tempo; extras
MOTIFS = {
    "opening": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[4, 3, 2, 0, 1, 2], lead="khloy", bpm=60, pad=1.0, gong=True),
    "land": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[0, 2, 3, 2, 4, 3], lead="chapei", bpm=72, pad=0.7, perc="ching"),
    "legend": dict(root=52, scale=[0, 3, 5, 7, 10], cell=[0, 1, 3, 2, 1, 0], lead="tro", bpm=58, pad=0.8, skor=True),
    "port": dict(root=60, scale=[0, 2, 4, 7, 9], cell=[2, 4, 5, 4, 2, 3], lead="roneat", bpm=96, pad=0.6, perc="ching",
                 skor=True),
    "water": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 4, 3, 1, 2, 0], lead="roneat", bpm=66, pad=0.9, bells=True),
    "fleet": dict(root=50, scale=[0, 2, 3, 7, 9], cell=[0, 0, 2, 3, 4, 2], lead="kong", bpm=88, pad=0.8, skor=True,
                  gong=True),
    "envoys": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[4, 2, 1, 2, 0, 1], lead="kong", bpm=70, pad=0.8, gong=True),
    "india": dict(root=52, scale=[0, 1, 4, 5, 7], cell=[0, 2, 3, 4, 3, 1], lead="khloy", bpm=64, pad=1.0, bells=True),
    "life": dict(root=60, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 2, 3, 1], lead="chapei", bpm=100, pad=0.5,
                 perc="ching"),
    "kings": dict(root=55, scale=[0, 2, 4, 7, 9], cell=[4, 4, 3, 2, 3, 0], lead="kong", bpm=66, pad=1.0, gong=True),
    "decline": dict(root=50, scale=[0, 3, 5, 7, 10], cell=[3, 2, 0, 1, 0, 0], lead="khloy", bpm=56, pad=1.0, tro=True),
    "legacy": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[4, 3, 2, 0, 1, 2], lead="roneat", bpm=70, pad=1.0, gong=True,
                   bells=True),
    "credits": dict(root=57, scale=[0, 2, 4, 7, 9], cell=[0, 2, 4, 3, 2, 0], lead="khloy", bpm=64, pad=1.0),
}


def score(mood, d, seed=0):
    m = MOTIFS[mood]
    r = np.random.default_rng(seed + sum(map(ord, mood)))
    n = int(d * SR) + SR * 6
    y = np.zeros(n)
    beat = 60.0 / m["bpm"]
    sc, sl = m["scale"], len(m["scale"])

    def note(deg, octv=0):
        o, k = divmod(deg, sl)
        return _midi(m["root"] + 12 * (o + octv) + sc[k])
    t = 1.0
    phrase = 0
    while t < d:
        cell = list(m["cell"])
        if phrase % 4 == 2:      # variation: invert the tail
            cell = cell[:3] + [max(0, 2 * cell[2] - c) for c in cell[3:]]
        if phrase % 4 == 3:
            cell = [c + 1 for c in cell]
        for i, deg in enumerate(cell):
            tp = t + i * beat
            f = note(deg, 1)
            if m["lead"] == "khloy":
                _place(y, S.khloy(f, beat * 1.8, 0.4, seed=i + phrase), tp)
            elif m["lead"] == "roneat":
                _place(y, S.roneat(f, 0.8, 0.45), tp)
                _place(y, S.roneat(f * 2, 0.5, 0.1), tp + beat / 2)
            elif m["lead"] == "kong":
                _place(y, S.kong(f / 2, 1.8, 0.45), tp)
            elif m["lead"] == "chapei":
                _place(y, S.chapei(f / 2, 0.9, 0.5, seed=i), tp)
            elif m["lead"] == "tro":
                _place(y, S.tro(f, beat * 1.9, 0.3), tp)
        if m.get("pad"):
            root = note(0, -1) if phrase % 2 == 0 else note(3, -1)
            _place(y, S.pad([root, root * 1.5, root * 2], beat * len(cell) + 1.5, 0.45 * m["pad"]), t)
        if m.get("tro"):
            _place(y, S.tro(note(0, 0), beat * len(cell), 0.18), t)
        if m.get("perc") == "ching":
            for b in range(len(cell)):
                _place(y, S.ching(b % 2 == 0, 0.25), t + b * beat)
        if m.get("skor"):
            for b in range(len(cell)):
                if b % 2 == 0:
                    _place(y, S.skor(0.4, 110, 0.35), t + b * beat)
        if m.get("gong") and phrase % 4 == 0:
            _place(y, S.sfx_gong(_midi(m["root"] - 24), 6.0) * 0.35, t)
        if m.get("bells") and phrase % 2 == 1:
            _place(y, S.sfx_bell(note(4, 2), 3.0) * 0.12, t + beat * 2)
        t += beat * (len(cell) + 2 + (2 if phrase % 2 else 0))   # breathing space between phrases
        phrase += 1
    y = y[:int(d * SR)]
    pk = np.max(np.abs(y)) or 1
    return _fade(y / pk * 0.6, 2.5, 3.0)


def ambience(kind, d, seed=0):
    d = max(d, 0.6)
    if kind in (None, "none"):
        return np.zeros(int(d * SR))
    if kind == "delta":
        y = S.ambience("river", d, seed) * 0.8 + S._scatter(d, seed + 1, S.sfx_bird, 0.35, 0.35)
    elif kind == "port":
        y = S.ambience("market", d, seed) * 0.6 + S.ambience("river", d, seed + 2) * 0.5
    elif kind == "sea":
        y = S._wind(d, seed, 1.2) * 0.8 + S._water(d, seed + 1) * 1.2
    elif kind == "lamp":
        y = S.ambience("night", d, seed) * 0.4 + S._scatter(d, seed + 1, S.sfx_fire, 0.2, 0.25)
    elif kind == "workshop":
        y = S.ambience("market", d, seed) * 0.4 + S._scatter(d, seed + 1, S.sfx_tool_hit, 0.9, 0.18)
    else:
        y = S.ambience(kind, d, seed)
    return _fade(np.asarray(y, dtype=np.float64), 1.0, 1.2)


def _load(path):
    w, sr = sf.read(path, dtype="float64")
    if w.ndim > 1:
        w = w.mean(1)
    if sr != SR:
        w = signal.resample_poly(w, SR, sr)
    return w


def mix(shots, placements, total, out_wav, log=print):
    n = int((total + 1.0) * SR)
    voice = np.zeros(n)
    music = np.zeros(n)
    amb = np.zeros(n)
    sfx = np.zeros(n)
    for p in placements:
        if os.path.exists(p["wav"]):
            w = S.hp(_load(p["wav"]), 70)
            g = 0.8 if p.get("who", "nar") == "nar" else 0.74
            _place(voice, w / (np.max(np.abs(w)) or 1) * g, p["t"])
        else:
            log("  missing voice %s" % p["key"])
    cues = [(s["start"], s["music"]) for s in shots if s.get("music")]
    for i, (t0, mood) in enumerate(cues):
        t1 = cues[i + 1][0] + 3.0 if i + 1 < len(cues) else total
        if mood != "silence":
            _place(music, score(mood, t1 - t0, seed=i), t0)
    cur = None
    for s in shots:
        cur = s.get("amb") or cur
        if s.get("tag") == "credits":
            cur = "none"
        _place(amb, ambience(cur, s["dur"] + 1.5, seed=int(s["start"])), max(0, s["start"] - 0.5))
        tr = s.get("trans")
        if tr == "ripple":
            _place(sfx, S.sfx_splash(int(s["start"])) * 0.35, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "lotus":
            _place(sfx, S.sfx_chime(int(s["start"])) * 0.4, max(0, s["start"] - s.get("xin", 1)))
        elif tr == "ink":
            _place(sfx, S.sfx_whoosh(int(s["start"]), 0.8) * 0.3, max(0, s["start"] - s.get("xin", 1)))
        if s.get("tag") == "chapter":
            _place(sfx, S.sfx_gong(98, 6.0) * 0.3, s["start"] + 0.3)
        for name in s.get("sfx") or []:
            if name == "hit":
                _place(sfx, S.sfx_drum_hit(int(s["start"])) * 0.8, s["start"])
            elif name == "bell":
                _place(sfx, S.sfx_bell(660, 3.0) * 0.4, s["start"] + 0.3)
        if s.get("badge") in ("text", "inscription"):
            _place(sfx, S.sfx_paper(1) * 0.25, s["start"] + 0.2)
    env = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    active = np.convolve((env > 0.01).astype(float), np.ones(int(0.6 * SR)) / int(0.6 * SR), mode="same")
    duck_m = 1.0 - 0.72 * np.clip(active, 0, 1)
    duck_a = 1.0 - 0.55 * np.clip(active, 0, 1)
    mixd = voice + music * 0.30 * duck_m + amb * 0.16 * duck_a + sfx * 0.5
    import pyloudnorm as pyln
    L = pyln.Meter(SR).integrated_loudness(mixd)
    g = 10 ** ((-16.0 - L) / 20)
    mixd = mixd * g
    if np.max(np.abs(mixd)) > 0.89:
        mixd = np.tanh(mixd / 0.89) * 0.89
    log("  mix loudness %.1f LUFS -> -16, peak %.2f" % (L, np.max(np.abs(mixd))))
    sf.write(out_wav, np.stack([mixd, mixd], 1).astype(np.float32), SR)


def envelope(wav_path, fps=24):
    """Per-frame mouth opening (0..1) from a voice clip, for the guide's lip-sync."""
    w = _load(wav_path)
    hop = SR // fps
    n = len(w) // hop + 1
    e = np.array([np.sqrt(np.mean(w[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(w) else 0 for i in range(n)])
    e = e / (np.percentile(e, 95) or 1)
    return np.clip(e * 1.1 - 0.08, 0, 1)
