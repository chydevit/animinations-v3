"""Procedural audio: sound effects, ambience beds and original Cambodian-inspired music.

Everything is synthesised (no copyrighted material). 48 kHz mono float32 numpy arrays.
Instruments are loose imitations of Khmer pinpeat / mahori colours: roneat (xylophone),
kong vong (gong circle), tro (fiddle), khloy (flute), skor (drum), ching/chap (small cymbals).
"""
import math
import zlib

import numpy as np
from scipy import signal

SR = 48000


def _t(d):
    return np.arange(int(d * SR)) / SR


def _rng(seed):
    return np.random.default_rng(seed)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR / 2 - 100)], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    sos = signal.butter(order, min(f, SR / 2 - 100), btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def hp(x, f, order=2):
    sos = signal.butter(order, f, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def env_ad(n, a, d, curve=4.0):
    na = max(1, int(a * SR))
    out = np.zeros(n)
    out[:min(na, n)] = np.linspace(0, 1, na)[:min(na, n)]
    if n > na:
        tt = np.arange(n - na) / SR
        out[na:] = np.exp(-tt * curve / max(d, 1e-3))
    return out


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) if len(x) else 0
    return x * (peak / m) if m > 0 else x


def place(buf, x, start, gain=1.0):
    s = int(start * SR)
    if s >= len(buf) or s + len(x) <= 0:
        return
    a = max(0, -s)
    e = min(len(buf), s + len(x))
    buf[s + a:e] += x[a:e - s] * gain


# --------------------------------------------------------------------------- SFX

def sfx_footstep(seed=0, surface="dirt"):
    r = _rng(seed)
    n = int(0.12 * SR)
    noise = r.standard_normal(n)
    f = {"dirt": (300, 2200), "wood": (150, 1500), "stone": (500, 4000), "grass": (800, 5000)}.get(surface, (300, 2200))
    x = bp(noise, *f) * env_ad(n, 0.004, 0.06, 5)
    thump = np.sin(2 * np.pi * (90 + r.uniform(-10, 10)) * _t(0.12)) * env_ad(n, 0.002, 0.05, 5)
    return norm(x + thump * 0.6, 0.5)


def sfx_whoosh(seed=0, d=0.35):
    r = _rng(seed)
    n = int(d * SR)
    x = r.standard_normal(n)
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    lo = np.linspace(400, 1800, n)
    y = np.zeros(n)
    for k in range(0, n, 2400):
        seg = slice(k, min(n, k + 2400))
        y[seg] = bp(x[seg], lo[k], lo[k] * 2.5)
    return norm(lp(y, 6000) * e, 0.45)


def sfx_cloth(seed=0):
    return sfx_whoosh(seed, 0.25) * 0.6


def sfx_bell(f=520.0, d=3.5, seed=0):
    t = _t(d)
    parts = [(1.0, 1.0, 1.0), (2.76, 0.5, 1.6), (5.40, 0.25, 2.6), (8.93, 0.12, 4.0), (0.5, 0.3, 0.8)]
    y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dec / d * 3) for m, a, dec in parts)
    return norm(y * env_ad(len(t), 0.003, d, 1.2), 0.55)


def sfx_gong(f=110.0, d=5.0):
    t = _t(d)
    y = (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.004 * t) + 0.4 * np.sin(2 * np.pi * f * 2.41 * t)
         + 0.25 * np.sin(2 * np.pi * f * 3.87 * t))
    return norm(y * env_ad(len(t), 0.01, d, 2.0), 0.6)


def sfx_chime(seed=0):
    out = np.zeros(int(1.4 * SR))
    for k, f in enumerate((1568, 2093, 2637, 3136)):
        place(out, sfx_bell(f, 1.0) * 0.5, k * 0.07)
    return norm(out, 0.4)


def sfx_thud(seed=0):
    t = _t(0.25)
    f = 70 + 60 * np.exp(-t * 30)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)
    y += lp(_rng(seed).standard_normal(len(t)), 1200) * np.exp(-t * 40) * 0.4
    return norm(y, 0.7)


def sfx_tool_hit(seed=0):
    y = sfx_thud(seed)
    n = int(0.3 * SR)
    g = bp(_rng(seed + 1).standard_normal(n), 1500, 6000) * env_ad(n, 0.001, 0.12, 5) * 0.4
    out = np.zeros(n)
    out[:len(y)] += y
    return norm(out + g, 0.7)


def sfx_clang(seed=0):
    t = _t(0.8)
    y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((1240, 6), (2980, 9), (4410, 12), (5870, 15)))
    return norm(y, 0.5)


def sfx_splash(seed=0):
    r = _rng(seed)
    n = int(0.9 * SR)
    y = hp(r.standard_normal(n), 900) * env_ad(n, 0.005, 0.4, 4)
    for k in range(10):
        f = r.uniform(500, 1400)
        tt = _t(0.08)
        place(y, np.sin(2 * np.pi * f * tt * (1 + tt * 6)) * np.exp(-tt * 40) * 0.2, r.uniform(0.05, 0.6))
    return norm(y, 0.6)


def sfx_door(seed=0):
    t = _t(0.7)
    f = 180 + 120 * np.sin(2 * np.pi * 3 * t)
    creak = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.05, 0.6, 2)
    out = bp(creak, 300, 2500) * 0.4
    full = np.zeros(int(1.0 * SR))
    full[:len(out)] += out
    place(full, sfx_thud(seed), 0.7)
    return norm(full, 0.6)


def sfx_swish(seed=0):
    r = _rng(seed)
    n = int(0.22 * SR)
    x = r.standard_normal(n)
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 3
    return norm(hp(x, 2500) * e, 0.5)


def sfx_pop(seed=0):
    t = _t(0.12)
    f = 900 * np.exp(-t * 20) + 300
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35), 0.5)


def sfx_boing(seed=0):
    t = _t(0.6)
    f = 220 + 140 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5), 0.5)


def sfx_bird(seed=0):
    r = _rng(seed)
    out = np.zeros(int(0.6 * SR))
    for k in range(r.integers(2, 5)):
        d = r.uniform(0.05, 0.12)
        tt = _t(d)
        f0 = r.uniform(2800, 4200)
        f = f0 + r.uniform(-1500, 1500) * (tt / d)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 2
        place(out, y, k * r.uniform(0.08, 0.14))
    return norm(out, 0.3)


def sfx_cluck(seed=0):
    r = _rng(seed)
    out = np.zeros(int(0.8 * SR))
    for k in range(r.integers(2, 4)):
        tt = _t(0.07)
        f = 420 + 300 * np.exp(-tt * 40)
        y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30)
        place(out, bp(y, 400, 2500), k * 0.16)
    return norm(out, 0.35)


def sfx_moo(seed=0):
    t = _t(1.4)
    f = 120 + 25 * np.sin(np.pi * t / 1.4)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    y = bp(y, 200, 900) * np.sin(np.pi * t / 1.4) ** 0.7
    return norm(y, 0.5)


def sfx_horse(seed=0, d=1.6):
    out = np.zeros(int(d * SR))
    k = 0.0
    while k < d - 0.1:
        for off in (0, 0.09, 0.18):
            place(out, sfx_thud(int(k * 100)) * 0.6, k + off)
        k += 0.42
    return norm(bp(out, 200, 4000), 0.6)


def sfx_crowd_gasp(seed=0):
    r = _rng(seed)
    n = int(1.0 * SR)
    y = bp(r.standard_normal(n), 500, 2500) * env_ad(n, 0.08, 0.6, 3)
    return norm(y, 0.4)


def sfx_magic(seed=0):
    out = np.zeros(int(1.6 * SR))
    for k in range(10):
        f = 1200 * 2 ** (k / 6)
        place(out, sfx_bell(f, 0.6) * 0.25, k * 0.05)
    return norm(out, 0.4)


def sfx_drum_hit(seed=0):
    return skor(0.4) * 1.2


def sfx_chisel(seed=0):
    out = np.zeros(int(0.9 * SR))
    for k in range(3):
        t = _t(0.18)
        y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dk) for f, dk in ((2350, 30), (4100, 45), (6200, 60)))
        y += hp(_rng(seed + k).standard_normal(len(t)), 3000) * np.exp(-t * 80) * 0.6
        place(out, y, k * 0.28)
    return norm(out, 0.5)


def sfx_mallet(seed=0):
    t = _t(0.2)
    y = np.sin(2 * np.pi * 320 * t) * np.exp(-t * 35) + bp(_rng(seed).standard_normal(len(t)), 500, 3000) * np.exp(-t * 60)
    return norm(y, 0.6)


def sfx_elephant(seed=0):
    t = _t(1.3)
    f = 420 + 260 * np.sin(np.pi * t / 1.3) + 30 * np.sin(2 * np.pi * 7 * t)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 1.3) ** 0.6
    y = bp(y, 300, 3500) + 0.3 * bp(_rng(seed).standard_normal(len(t)), 800, 3000) * np.sin(np.pi * t / 1.3)
    return norm(y, 0.6)


def sfx_cart(seed=0, d=2.0):
    r = _rng(seed)
    t = _t(d)
    rumble = lp(r.standard_normal(len(t)), 180) * (0.7 + 0.3 * np.sin(2 * np.pi * 2.2 * t))
    out = rumble * 2.0
    for k in range(int(d * 2)):
        f = 300 + r.uniform(-60, 60)
        tt = _t(0.25)
        cr = signal.sawtooth(2 * np.pi * np.cumsum(f + 80 * np.sin(2 * np.pi * 9 * tt)) / SR) * np.sin(np.pi * tt / 0.25)
        place(out, bp(cr, 250, 2000) * 0.25, k * 0.5 + r.uniform(0, 0.2))
    return norm(out, 0.5)


def sfx_rope(seed=0):
    t = _t(0.6)
    f = 160 + 60 * np.sin(2 * np.pi * 2 * t)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.6)
    return norm(bp(y, 200, 1800), 0.35)


def sfx_flag(seed=0, d=1.5):
    r = _rng(seed)
    t = _t(d)
    x = bp(r.standard_normal(len(t)), 300, 2500)
    am = np.clip(np.sin(2 * np.pi * 6.5 * t + 2 * np.sin(2 * np.pi * 0.7 * t)), 0, 1) ** 2
    return norm(x * (0.3 + am), 0.4)


def sfx_camera(seed=0):
    out = np.zeros(int(0.25 * SR))
    for k, off in enumerate((0.0, 0.07)):
        t = _t(0.03)
        place(out, hp(_rng(seed + k).standard_normal(len(t)), 1500) * np.exp(-t * 150), off)
    return norm(out, 0.5)


def sfx_paper(seed=0):
    r = _rng(seed)
    n = int(0.8 * SR)
    y = bp(r.standard_normal(n), 1500, 8000) * env_ad(n, 0.05, 0.5, 3) * (0.5 + 0.5 * (r.random(n) > 0.97))
    return norm(lp(y, 9000), 0.35)


def sfx_fire(seed=0):
    r = _rng(seed)
    n = int(1.2 * SR)
    y = lp(r.standard_normal(n), 900) * 0.4
    for _ in range(14):
        tt = _t(0.01)
        place(y, r.standard_normal(len(tt)) * np.exp(-tt * 400), r.uniform(0, 1.1))
    return norm(y, 0.35)


SFX = {
    "footstep": sfx_footstep, "whoosh": sfx_whoosh, "cloth": sfx_cloth, "bell": lambda s=0: sfx_bell(),
    "temple_bell": lambda s=0: sfx_bell(440, 4.5), "gong": lambda s=0: sfx_gong(), "chime": sfx_chime,
    "sparkle": sfx_chime, "thud": sfx_thud, "basket": sfx_thud, "tool_hit": sfx_tool_hit, "hoe": sfx_tool_hit,
    "clang": sfx_clang, "sword": sfx_swish, "swish": sfx_swish, "splash": sfx_splash, "water": sfx_splash,
    "door": sfx_door, "pop": sfx_pop, "boing": sfx_boing, "bird": sfx_bird, "chicken": sfx_cluck,
    "cow": sfx_moo, "horse": sfx_horse, "crowd_gasp": sfx_crowd_gasp, "gasp": sfx_crowd_gasp,
    "magic": sfx_magic, "drum": sfx_drum_hit, "chisel": sfx_chisel, "mallet": sfx_mallet, "hammer": sfx_mallet,
    "elephant": sfx_elephant, "cart": sfx_cart, "rope": sfx_rope, "flag": sfx_flag, "flag_flap": sfx_flag,
    "camera": sfx_camera, "shutter": sfx_camera, "paper": sfx_paper, "scroll": sfx_paper, "fire": sfx_fire,
    "incense": sfx_fire,
}


def make_sfx(name, seed=0):
    fn = SFX.get(name)
    if fn is None:
        raise KeyError("unknown sfx '%s'. Available: %s" % (name, ", ".join(sorted(SFX))))
    try:
        return fn(seed)
    except TypeError:
        return fn()


# --------------------------------------------------------------------------- ambience

def _wind(d, seed, level=1.0):
    r = _rng(seed)
    n = int(d * SR)
    x = lp(r.standard_normal(n), 500)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * _t(d) + r.uniform(0, 6))
    return x * lfo * 0.5 * level


def _scatter(d, seed, fn, rate, gain):
    r = _rng(seed)
    out = np.zeros(int(d * SR))
    k = r.uniform(0, 1.0 / rate)
    i = 0
    while k < d:
        place(out, fn(int(seed * 1000 + i)) * gain * r.uniform(0.5, 1.0), k)
        k += r.exponential(1.0 / rate)
        i += 1
    return out


def _murmur(d, seed, voices=8):
    r = _rng(seed)
    n = int(d * SR)
    out = np.zeros(n)
    tt = _t(d)
    for v in range(voices):
        x = bp(r.standard_normal(n), r.uniform(300, 500), r.uniform(1200, 2200))
        syl = np.clip(np.sin(2 * np.pi * r.uniform(3, 5.5) * tt + r.uniform(0, 6)), 0, 1)
        phrase = np.clip(np.sin(2 * np.pi * r.uniform(0.1, 0.25) * tt + r.uniform(0, 6)), 0, 1)
        out += x * syl * phrase
    return out / voices


def _crickets(d, seed):
    r = _rng(seed)
    tt = _t(d)
    out = np.zeros(len(tt))
    for k in range(4):
        f = r.uniform(4200, 5200)
        pulse = (np.sin(2 * np.pi * r.uniform(28, 40) * tt) > 0.3).astype(float)
        chirp = (np.sin(2 * np.pi * r.uniform(0.6, 1.2) * tt + r.uniform(0, 6)) > 0).astype(float)
        out += np.sin(2 * np.pi * f * tt) * lp(pulse * chirp, 300)
    return out * 0.08


def _insects(d, seed):
    r = _rng(seed)
    n = int(d * SR)
    x = bp(r.standard_normal(n), 3800, 7000)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 11 * _t(d))
    return x * am * 0.15


def _water(d, seed):
    r = _rng(seed)
    n = int(d * SR)
    x = bp(r.standard_normal(n), 200, 2500)
    am = 0.7 + 0.3 * lp(r.standard_normal(n), 3) * 20
    return x * np.clip(am, 0.2, 1.4) * 0.35


def ambience(kind, d, seed=0):
    d = max(d, 0.5)
    k = kind or "village"
    if k == "village":
        y = _wind(d, seed) + _scatter(d, seed + 1, sfx_bird, 0.5, 0.5) + _scatter(d, seed + 2, sfx_cluck, 0.08, 0.5) \
            + _murmur(d, seed + 3, 6) * 0.05
    elif k == "forest":
        y = _wind(d, seed, 0.6) + _insects(d, seed + 1) + _scatter(d, seed + 2, sfx_bird, 0.9, 0.6)
    elif k == "temple":
        y = _wind(d, seed, 0.5) + _scatter(d, seed + 1, sfx_bird, 0.25, 0.4) \
            + _scatter(d, seed + 2, lambda s: sfx_bell(660, 3.0), 0.05, 0.25)
    elif k == "market":
        y = _murmur(d, seed, 14) * 0.6 + _scatter(d, seed + 1, sfx_footstep, 1.5, 0.15) + _wind(d, seed + 2, 0.3)
    elif k in ("farm", "rice_field"):
        y = _wind(d, seed, 1.2) + _scatter(d, seed + 1, sfx_bird, 0.4, 0.5) + _scatter(d, seed + 2, sfx_moo, 0.03, 0.3)
    elif k == "palace":
        y = lp(_rng(seed).standard_normal(int(d * SR)), 300) * 0.15 + _scatter(d, seed + 1, lambda s: sfx_gong(90, 4), 0.03, 0.2)
    elif k in ("river", "pond"):
        y = _water(d, seed) + _scatter(d, seed + 1, sfx_bird, 0.4, 0.4) + _wind(d, seed + 2, 0.4)
    elif k == "night":
        y = _crickets(d, seed) + _wind(d, seed + 1, 0.3)
    elif k == "interior":
        y = lp(_rng(seed).standard_normal(int(d * SR)), 250) * 0.12 + _scatter(d, seed + 1, sfx_bird, 0.2, 0.12)
    elif k == "town":
        y = _murmur(d, seed, 10) * 0.4 + lp(_rng(seed).standard_normal(int(d * SR)), 200) * 0.3
    elif k == "rain":
        y = hp(_rng(seed).standard_normal(int(d * SR)), 1500) * 0.4 + _wind(d, seed + 1, 0.8)
    elif k == "battle":
        y = _murmur(d, seed, 18) * 0.7 + _scatter(d, seed + 1, sfx_clang, 0.8, 0.3)
    elif k == "construction":
        y = _murmur(d, seed, 10) * 0.35 + _scatter(d, seed + 1, sfx_chisel, 0.8, 0.35) \
            + _scatter(d, seed + 2, sfx_mallet, 0.6, 0.35) + _wind(d, seed + 3, 0.5) \
            + _scatter(d, seed + 4, sfx_rope, 0.15, 0.3)
    elif k == "crowd":
        y = _murmur(d, seed, 12) * 0.45 + _scatter(d, seed + 1, sfx_footstep, 1.2, 0.12) \
            + _scatter(d, seed + 2, sfx_bird, 0.3, 0.35) + _wind(d, seed + 3, 0.4)
    elif k == "worship":
        y = _wind(d, seed, 0.3) + _scatter(d, seed + 1, sfx_fire, 0.25, 0.25) \
            + _scatter(d, seed + 2, lambda s_: sfx_bell(700, 3.0), 0.06, 0.2) + _scatter(d, seed + 3, sfx_bird, 0.15, 0.2)
    elif k == "flag":
        y = _wind(d, seed, 1.4) + _scatter(d, seed + 1, sfx_flag, 0.7, 0.6)
    elif k == "none":
        y = np.zeros(int(d * SR))
    else:
        y = _wind(d, seed)
    return norm(y, 0.5)


AMBIENCE_FOR_ENV = {"village": "village", "rice_field": "farm", "rice_field_harvest": "farm", "farm": "farm",
                    "forest": "forest", "temple": "temple", "market": "market", "palace": "palace",
                    "palace_hall": "palace", "river": "river", "pond": "pond", "mountain": "forest",
                    "house_interior": "interior", "angkor": "temple", "school": "village", "town": "town"}


# --------------------------------------------------------------------------- instruments

def _tail(y, ms=25):
    k = min(len(y), int(ms / 1000 * SR))
    if k > 1:
        y[-k:] *= np.linspace(1, 0, k)
    return y


def roneat(f, d=0.7, vel=1.0):
    t = _t(d)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 5.5) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 14) \
        + 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 30)
    y[:int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
    return _tail(y) * vel


def kong(f, d=1.6, vel=1.0):
    t = _t(d)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.42 * t) * np.exp(-t * 2)
         + 0.3 * np.sin(2 * np.pi * f * 1.003 * t)) * np.exp(-t * 2.2)
    return _tail(y, 60) * vel * 0.8


def tro(f, d, vel=1.0):
    t = _t(d)
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 2, 0, 1)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f * vib) / SR)
    y = lp(y, f * 5)
    e = np.minimum(1, t / 0.12) * np.minimum(1, (d - t) / 0.15).clip(0, 1)
    return y * e * vel * 0.5


def khloy(f, d, vel=1.0, seed=0):
    t = _t(d)
    vib = 1 + 0.01 * np.sin(2 * np.pi * 5 * t) * np.clip(t * 1.5, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    y = np.sin(ph) + 0.15 * np.sin(2 * ph)
    breath = bp(_rng(seed).standard_normal(len(t)), f, f * 3) * 0.08
    e = np.minimum(1, t / 0.06) * np.minimum(1, (d - t) / 0.12).clip(0, 1)
    return (y + breath) * e * vel * 0.6


def chapei(f, d=1.2, vel=1.0, seed=0):
    n = int(d * SR)
    p = max(2, int(SR / f))
    buf = _rng(seed).uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out = lp(out, 3500)
    out[:int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
    return _tail(out, 60) * vel * 0.6


def skor(d=0.4, f0=140, vel=1.0):
    t = _t(d)
    f = f0 * 0.45 + f0 * 0.55 * np.exp(-t * 25)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return _tail(y) * vel


def ching(open_=True, vel=1.0):
    d = 0.6 if open_ else 0.08
    t = _t(d)
    y = sum(np.sin(2 * np.pi * f * t) for f in (3150, 4730, 6230, 7900)) / 4
    y *= np.exp(-t * (6 if open_ else 60))
    return y * vel * 0.25


def pad(freqs, d, vel=1.0):
    t = _t(d)
    y = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.001 * t) for f in freqs) / len(freqs)
    e = np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5).clip(0, 1)
    return lp(y, 1500) * e * vel * 0.2


# --------------------------------------------------------------------------- music

def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


MOODS = {
    #           bpm, root midi, scale degrees (semitones), lead, density, percussion
    "opening": dict(bpm=84, root=62, scale=[0, 2, 4, 7, 9], lead="roneat", perc="ching", pad=True, bass=True),
    "happy": dict(bpm=112, root=64, scale=[0, 2, 4, 7, 9], lead="roneat", perc="full", pad=False, bass=True),
    "playful": dict(bpm=120, root=67, scale=[0, 2, 4, 7, 9], lead="chapei", perc="full", pad=False, bass=True),
    "calm": dict(bpm=70, root=60, scale=[0, 2, 4, 7, 9], lead="khloy", perc="ching_soft", pad=True, bass=False),
    "sad": dict(bpm=62, root=57, scale=[0, 3, 5, 7, 10], lead="khloy", perc=None, pad=True, bass=False, tro=True),
    "danger": dict(bpm=96, root=45, scale=[0, 1, 5, 7, 8], lead=None, perc="drums", pad=True, bass=True, tro=True),
    "tension": dict(bpm=88, root=47, scale=[0, 1, 5, 7, 10], lead=None, perc="drums_soft", pad=True, bass=False, tro=True),
    "royal": dict(bpm=72, root=60, scale=[0, 2, 4, 7, 9], lead="kong", perc="ching", pad=True, bass=True, gong=True),
    "temple": dict(bpm=60, root=57, scale=[0, 2, 5, 7, 9], lead="kong", perc="ching_soft", pad=True, bass=False),
    "ending": dict(bpm=76, root=62, scale=[0, 2, 4, 7, 9], lead="khloy", perc="ching_soft", pad=True, bass=True, roneat2=True),
    "mysterious": dict(bpm=66, root=57, scale=[0, 3, 5, 7, 10], lead="khloy", perc="ching_soft", pad=True, bass=False,
                       gong=True),
    "historic": dict(bpm=100, root=55, scale=[0, 2, 3, 7, 9], lead="roneat", perc="full", pad=True, bass=True,
                     tro=True, gong=True),
    "inspire": dict(bpm=84, root=62, scale=[0, 2, 4, 7, 9], lead="roneat", perc="ching", pad=True, bass=True,
                    roneat2=True),
    "none": None,
}


def _melody(r, nsteps, scale_len):
    """Random-walk pentatonic melody with phrase structure (degree index, +octave)."""
    phrase = []
    deg = r.integers(0, scale_len)
    for i in range(nsteps):
        step = r.choice([-2, -1, -1, 0, 1, 1, 2])
        deg = int(np.clip(deg + step, 0, scale_len * 2 - 1))
        phrase.append(deg)
    phrase[-1] = 0 if phrase[-1] < scale_len else scale_len
    return phrase


def music(mood, d, seed=0):
    m = MOODS.get(mood or "none")
    n = int(max(d, 1.0) * SR)
    if not m:
        return np.zeros(n)
    r = _rng(seed + zlib.crc32(mood.encode()) % 1000)
    beat = 60.0 / m["bpm"]
    bar = beat * 4
    loop_bars = 8
    loop_d = bar * loop_bars
    L = np.zeros(int(loop_d * SR) + SR * 3)
    scale = m["scale"]
    sl = len(scale)

    def note(deg, octv=0):
        o, k = divmod(deg, sl)
        return _midi(m["root"] + 12 * (o + octv) + scale[k])

    # rhythm patterns in eighths
    pats = [[1, 0, 1, 0, 1, 1, 1, 0], [1, 1, 1, 0, 1, 0, 1, 0], [1, 0, 1, 1, 1, 0, 1, 0], [1, 0, 0, 1, 1, 0, 1, 1]]
    if m["lead"]:
        A = _melody(r, 16, sl)
        B = _melody(r, 16, sl)
        form = [A, A, B, A]
        for pi, ph in enumerate(form):
            pat = pats[r.integers(0, len(pats))] * 2
            ni = 0
            for e in range(16):
                if not pat[e]:
                    continue
                tpos = pi * 2 * bar + e * beat / 2
                deg = ph[ni % len(ph)]
                ni += 1
                f = note(deg, 1 if m["lead"] in ("roneat", "kong", "chapei") else 1)
                if m["lead"] == "roneat":
                    place(L, roneat(f, 0.8, 0.5), tpos)
                    place(L, roneat(f * 2, 0.5, 0.12), tpos + 0.01)
                elif m["lead"] == "kong":
                    place(L, kong(f / 2, 1.8, 0.5), tpos)
                elif m["lead"] == "chapei":
                    place(L, chapei(f / 2, 0.8, 0.6, seed=e), tpos)
                elif m["lead"] == "khloy":
                    dur = beat * (2 if e % 4 == 0 else 1)
                    if e % 2 == 0:
                        place(L, khloy(f, dur * 0.95, 0.45, seed=e), tpos)
        if m.get("roneat2"):
            for b in range(loop_bars * 4):
                place(L, roneat(note(r.integers(0, sl), 2), 0.5, 0.12), b * beat + beat / 2)
    if m.get("tro"):
        for b in range(0, loop_bars, 2):
            f1 = note(r.integers(0, sl), 0)
            place(L, tro(f1, bar * 2 * 0.95, 0.35), b * bar)
            if mood in ("danger", "tension"):
                place(L, tro(f1 * 2 ** (1 / 12), bar * 2 * 0.95, 0.15), b * bar)
    if m.get("pad"):
        for b in range(0, loop_bars, 2):
            root = note(0, -1) if b % 4 == 0 else note(3 if sl > 3 else 1, -1)
            place(L, pad([root, root * 1.5], bar * 2 + 1.0, 0.5), b * bar)
    if m.get("bass"):
        for b in range(loop_bars * 2):
            deg = [0, 0, 3, 4][b % 4] if sl > 4 else 0
            place(L, chapei(note(deg, -2), beat * 2, 0.6, seed=b) if mood != "danger" else skor(0.5, 70, 0.7),
                  b * beat * 2)
    perc = m.get("perc")
    if perc:
        for b in range(loop_bars * 4):
            tb = b * beat
            if perc in ("ching", "full", "ching_soft"):
                v = 0.5 if perc == "ching_soft" else 1.0
                place(L, ching(False, v), tb)
                place(L, ching(True, v), tb + beat / 2)
            if perc in ("full",):
                if b % 4 in (0, 2):
                    place(L, skor(0.4, 150, 0.6), tb)
                if b % 4 == 3:
                    place(L, skor(0.3, 220, 0.35), tb + beat / 2)
            if perc in ("drums", "drums_soft"):
                v = 0.8 if perc == "drums" else 0.45
                place(L, skor(0.5, 90, v), tb)
                if b % 2:
                    place(L, skor(0.3, 120, v * 0.6), tb + beat * 0.5)
                    place(L, skor(0.3, 120, v * 0.5), tb + beat * 0.75)
    if m.get("gong"):
        for b in range(0, loop_bars, 4):
            place(L, sfx_gong(98, 5) * 0.4, b * bar)
    L = L[: int(loop_d * SR) + SR * 2]
    # tile with crossfade
    out = np.zeros(n + SR * 3)
    step = int(loop_d * SR)
    pos = 0
    xf = int(0.05 * SR)
    while pos < n:
        seg = L.copy()
        if pos > 0:
            seg[:xf] *= np.linspace(0, 1, xf)
        place(out, seg, pos / SR)
        pos += step
    out = out[:n]
    fi = min(n, int(1.5 * SR))
    out[:fi] *= np.linspace(0, 1, fi)
    fo = min(n, int(2.0 * SR))
    out[-fo:] *= np.linspace(1, 0, fo)
    return norm(out, 0.6)
