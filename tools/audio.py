"""Original soundtrack for "Make the logo bigger". Everything is synthesised here: no samples, no recordings.
One theme in C major at 120 BPM, re-orchestrated for each era, plus sound cues read from timeline.json."""
import json
import pathlib

import numpy as np
from scipy import signal
from scipy.io import wavfile

REPO = pathlib.Path(__file__).resolve().parent.parent
(REPO / 'out').mkdir(exist_ok=True)
SR = 48000
DUR = 110.0
N = int(SR * DUR)
BEAT = 0.5
rng = np.random.default_rng(7)


def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(SR * d)) / SR
def phase(f): return 2 * np.pi * np.cumsum(f) / SR
def sine(f, d): return np.sin(2 * np.pi * f * tt(d))
def square(f, d, duty=.5): return np.where((f * tt(d)) % 1 < duty, 1.0, -1.0) - (2 * duty - 1)   # no DC offset
def tri(f, d): return 2 * np.abs(2 * ((f * tt(d)) % 1) - 1) - 1
def noise(d): return rng.standard_normal(int(SR * d))
def hann(n): return np.hanning(n) if n > 2 else np.ones(n)
def glide(f0, f1, d, curve=1.0): return np.sin(phase(f0 + (f1 - f0) * np.linspace(0, 1, int(SR * d)) ** curve))


def env(n, a=.005, r=.03):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na > 1: e[:na] = np.linspace(0, 1, na)
    if nr > 1: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def filt(x, lo=None, hi=None, order=2):
    if lo and hi: sos = signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos')
    elif lo: sos = signal.butter(order, lo, 'highpass', fs=SR, output='sos')
    else: sos = signal.butter(order, hi, 'lowpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def saw(f, d, nh=10, roll=1.0, vib=0.0):
    t = tt(d)
    ph = phase(f * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - .12) / .2, 0, 1))) if vib else 2 * np.pi * f * t
    x = np.zeros_like(t)
    for k in range(1, nh + 1):
        if f * k > SR / 2.4: break
        x += np.sin(k * ph) / k ** roll
    return x * .6


def bell(f, d=.8, bright=1.0):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + .5 * bright * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-6 * t) + .25 * bright * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-10 * t)
    return x * np.exp(-t * 5 / d) * env(len(t), .002, .02)


def pluck(f, d=.3):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (4 + 3 * k)) for k in range(1, 9) if f * k < SR / 2.4)
    return x * env(len(t), .002, .02)


def marimba(f, d=.6):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + .35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 18) + .12 * np.sin(2 * np.pi * 10 * f * t) * np.exp(-t * 40)
    return x * env(len(t), .002, .03)


def epiano(f, d=.4):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 6) * env(len(t), .004, .03)


def kick(g=1.0):
    t = tt(.24)
    return np.sin(phase(45 + 80 * np.exp(-t * 32))) * np.exp(-t * 13) * g


def snare():
    t = tt(.16)
    return filt(noise(.16), 1500, 6000) * np.exp(-t * 28) * .7 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * .5


def hat():
    t = tt(.05)
    return filt(noise(.05), lo=7000) * np.exp(-t * 90)


def clap():
    t = tt(.2)
    e = np.exp(-t * 20) * (1 + .8 * (np.sin(2 * np.pi * 55 * t) > 0) * (t < .03))
    return filt(noise(.2), 900, 3500) * e


def place(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i < 0: return
    x = x[:len(buf) - i]
    buf[i:i + len(x)] += x * g


def reverb(x, wet=.3, decay=3.5, length=1.6):
    t = tt(length)
    ir = filt(rng.standard_normal(len(t)) * np.exp(-t * decay), hi=5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    return x + wet * signal.fftconvolve(x, ir)[:len(x)]


# ---------------- the theme ----------------
CH = {'C': [60, 64, 67], 'Am': [57, 60, 64], 'F': [53, 57, 60], 'G': [55, 59, 62]}
ROOT = {'C': 36, 'Am': 33, 'F': 41, 'G': 43}
BARMEL = [  # one bar each: (beat, length in beats, midi note)
    [(0, 1, 76), (1, 1, 79), (2, 1.5, 84), (3.5, .5, 83)],
    [(0, 2, 79), (2, 1, 76), (3, 1, 79)],
    [(0, 1, 81), (1, 1, 84), (2, 1.5, 88), (3.5, .5, 86)],
    [(0, 2, 84), (2, 1, 81), (3, 1, 84)],
    [(0, 1, 81), (1, 1, 84), (2, 1.5, 89), (3.5, .5, 88)],
    [(0, 2, 84), (2, 1, 81), (3, 1, 84)],
    [(0, 1, 86), (1, 1, 83), (2, 1, 79), (3, 1, 83)],
]


def melody(bars):
    out = []
    for i, b in enumerate(bars):
        if b is None: continue
        out += [(i * 4 + bt, ln, m) for bt, ln, m in BARMEL[b]]
    return out


SEVEN = ['C', 'C', 'Am', 'Am', 'F', 'F', 'G']
MEL_AB = melody([0, 1, 2, None, None, None, 6])   # the lead rests while the second voice speaks


def era_chip(chords, mel):
    L = len(chords) * 4 * BEAT
    b = np.zeros(int(SR * (L + 1)))
    for bt, ln, m in mel:
        d = ln * BEAT * .92
        place(b, square(midi(m), d, .25) * env(int(SR * d), .003, .02), bt * BEAT, .20)
    for i, c in enumerate(chords):
        for e in range(8):
            f = midi(ROOT[c] + 12 + (12 if e % 2 else 0))
            place(b, tri(f, .21) * env(int(SR * .21), .003, .03), (i * 4 + e * .5) * BEAT, .30)
            if e % 2: place(b, np.sign(noise(.03)) * np.exp(-tt(.03) * 120), (i * 4 + e * .5) * BEAT, .05)
        for bt in (1, 3): place(b, np.sign(noise(.07)) * np.exp(-tt(.07) * 60), (i * 4 + bt) * BEAT, .09)
    return filt(filt(b, hi=9000), lo=40)


def era_midi(chords, mel):
    L = len(chords) * 4 * BEAT
    b = np.zeros(int(SR * (L + 1)))
    for bt, ln, m in mel:
        d = ln * BEAT * .95
        place(b, saw(midi(m), d, 8, 1.2, .006) * env(int(SR * d), .03, .06), bt * BEAT, .21)
    for i, c in enumerate(chords):
        for bt in range(4):
            for m in CH[c]: place(b, epiano(midi(m), .34), (i * 4 + bt + .5) * BEAT, .075)
        for bt in (0, 2):
            f = midi(ROOT[c] + 12)
            place(b, (sine(f, .45) + .3 * sine(2 * f, .45)) * env(int(SR * .45), .005, .08), (i * 4 + bt) * BEAT, .30)
            place(b, kick(), (i * 4 + bt) * BEAT, .45)
        for bt in (1, 3): place(b, snare(), (i * 4 + bt) * BEAT, .2)
        for e in range(8): place(b, hat(), (i * 4 + e * .5) * BEAT, .05)
    return b


def era_pop(chords, mel):
    L = len(chords) * 4 * BEAT
    n = int(SR * (L + 1))
    b, pad = np.zeros(n), np.zeros(n)
    for i, c in enumerate(chords):
        d = 4 * BEAT
        for m in CH[c]:
            for cents in (-8, 0, 8):
                place(pad, saw(midi(m) * 2 ** (cents / 1200), d, 8, 1.1) * env(int(SR * d), .02, .05), i * d, .05)
        for e in range(8):
            f = midi(ROOT[c] + 12)
            place(pad, filt(saw(f, .22, 4), hi=400) * env(int(SR * .22), .005, .04), (i * 4 + e * .5) * BEAT, .32)
        for bt in range(4): place(b, kick(), (i * 4 + bt) * BEAT, .5)
        for bt in (1, 3): place(b, clap(), (i * 4 + bt) * BEAT, .22)
        for bt in range(4): place(b, hat(), (i * 4 + bt + .5) * BEAT, .06)
    t = np.arange(n) / SR
    pump = .35 + .65 * np.clip(((t % BEAT) / .3), 0, 1)
    lead = np.zeros(n)
    for bt, ln, m in mel:
        d = ln * BEAT * .9
        place(lead, tri(midi(m), d) * env(int(SR * d), .004, .05), bt * BEAT, .17)
    dl = int(.375 * SR)
    echo = np.zeros(n); echo[dl:] = lead[:-dl] * .3
    return b + filt(pad, hi=3500) * pump + lead + echo


def era_clean(chords, mel):
    L = len(chords) * 4 * BEAT
    b = np.zeros(int(SR * (L + 1)))
    for i, c in enumerate(chords):
        tones = [m + 12 for m in CH[c]]
        for s in range(16): place(b, pluck(midi(tones[[0, 1, 2, 1][s % 4]]), .26), (i * 4 + s * .25) * BEAT, .12)
        for bt in range(4): place(b, filt(kick(), hi=180), (i * 4 + bt) * BEAT, .5)
        for bt in (1, 3): place(b, sine(1800, .015) * np.exp(-tt(.015) * 200), (i * 4 + bt) * BEAT, .08)
        for bt in (0, 1.5, 2): place(b, sine(midi(ROOT[c] + 12), .4) * env(int(SR * .4), .005, .08), (i * 4 + bt) * BEAT, .28)
    for bt, ln, m in mel:
        d = ln * BEAT * .8
        f = midi(m)
        place(b, (sine(f, d) + .2 * sine(2 * f, d)) * env(int(SR * d), .005, .05), bt * BEAT, .17)
    return b


def era_groove(chords, mel):
    L = len(chords) * 4 * BEAT
    b = np.zeros(int(SR * (L + 1)))
    for bt, ln, m in mel: place(b, marimba(midi(m), max(.4, ln * BEAT)), bt * BEAT, .30)
    for i, c in enumerate(chords):
        for bt in (0, 1.5):
            for m in CH[c]: place(b, epiano(midi(m), .5), (i * 4 + bt) * BEAT, .07)
            place(b, saw(midi(ROOT[c] + 12), .3, 5) * np.exp(-tt(.3) * 9) * env(int(SR * .3), .004, .03), (i * 4 + bt) * BEAT, .30)
        for bt in (0, 1.5, 2): place(b, kick(), (i * 4 + bt) * BEAT, .42)
        for bt in (1, 3): place(b, clap(), (i * 4 + bt) * BEAT, .17)
        for e in range(8):
            sh = filt(noise(.06), lo=5000) * hann(int(SR * .06))
            place(b, sh, (i * 4 + e * .5 + (.06 if e % 2 else 0)) * BEAT, .07 if e % 2 else .04)
    return b


def era_ambient(chords, mel=None, bells=True, swell=None):
    L = len(chords) * 4 * BEAT
    n = int(SR * (L + 2.5))
    b = np.zeros(n)
    for i, c in enumerate(chords):
        d = 4 * BEAT + 1.2
        for m in CH[c]:
            f = midi(m)
            x = sine(f * 1.002, d) + sine(f * .998, d) + .25 * sine(2 * f, d)
            place(b, x * env(int(SR * d), .7, 1.2), i * 4 * BEAT, .055)
        place(b, sine(midi(ROOT[c] + 12), d) * env(int(SR * d), .5, 1.0), i * 4 * BEAT, .12)
    if bells and mel:
        for bt, ln, m in mel:
            if bt % 2 == 0: place(b, bell(midi(m), 1.6, .6), bt * BEAT, .13)
    b = reverb(filt(b, hi=4500), .35)
    if swell is not None:
        t = np.arange(n) / SR
        b *= np.interp(t, *swell)
    return b


def era_end():
    chords = ['C', 'C', 'Am', 'Am', 'F', 'G', 'C', 'C']
    mel = melody([0, 1, 2, 3, 4, 6]) + [(24, 4, 84)]
    L = len(chords) * 4 * BEAT
    n = int(SR * (L + 2.5))
    b = np.zeros(n)
    for bt, ln, m in mel:
        place(b, marimba(midi(m), max(.5, ln * BEAT)), bt * BEAT, .28)
        d = ln * BEAT * .9
        place(b, square(midi(m), d, .25) * env(int(SR * d), .004, .03), bt * BEAT, .035)
    for i, c in enumerate(chords):
        last = i >= 6
        if not last:
            tones = [m + 12 for m in CH[c]]
            for s in range(8): place(b, pluck(midi(tones[[0, 1, 2, 1][s % 4]]), .3), (i * 4 + s * .5) * BEAT, .09)
            for bt in range(4): place(b, filt(kick(), hi=200), (i * 4 + bt) * BEAT, .42)
            for bt in (1, 3): place(b, clap(), (i * 4 + bt) * BEAT, .12)
            for bt in (0, 1.5, 2): place(b, sine(midi(ROOT[c] + 12), .4) * env(int(SR * .4), .005, .08), (i * 4 + bt) * BEAT, .26)
    for k, m in enumerate([72, 76, 79, 84, 88]): place(b, bell(midi(m), 2.2, .6), 12 + k * .16, .13)
    return b + era_ambient(chords, None, False)[:n] * .9


def norm(x, target, t0=0, t1=None):
    seg = x[int(t0 * SR):int(t1 * SR) if t1 else len(x)]
    rms = np.sqrt(np.mean(seg ** 2)) + 1e-9
    return x * (target / rms)


def edge(x, length, fade_out=.14):
    """keep an era inside its slot: short fade at the boundary so the next era lands clean"""
    n = int(length * SR)
    y = x[:n + int(.3 * SR)].copy()
    k = int(fade_out * SR)
    y[n - k:n] *= np.linspace(1, .25, k)
    y[n:] *= np.linspace(.25, 0, len(y) - n)
    return y


music = np.zeros(N + SR * 4)
MEL5 = melody([0, 1, 2, 4, 6])
TGT = .05
hook = norm(era_ambient(['C', 'C'], None, False), .022, 0, 4)[:201600]
hook[-14400:] *= np.linspace(1, 0, 14400)
place(music, hook, 0)
place(music, edge(norm(era_chip(['C', 'C', 'Am', 'F', 'G'], MEL5), TGT * .72, 0, 10), 10), 4)   # squares sound louder than they measure
place(music, edge(norm(era_midi(SEVEN, MEL_AB), TGT, 0, 14), 14), 14)
place(music, edge(norm(era_pop(SEVEN, MEL_AB), TGT, 0, 14), 14), 28)
place(music, edge(norm(era_clean(SEVEN, MEL_AB), TGT, 0, 14), 14), 42)
place(music, edge(norm(era_groove(SEVEN, MEL_AB), TGT, 0, 14), 14), 56)
place(music, edge(norm(era_ambient(SEVEN, MEL_AB), .034, 0, 14), 14, .3), 70)
# the punchline: C, Am, F, then two bars of G that swell into the end card
sw = ([0, 6, 7.2, 9.8, 10.2], [1, 1, 1.3, 2.6, 2.6])
pl = norm(era_ambient(['C', 'Am', 'F', 'G', 'G'], None, False, sw), .034, 0, 6)
arp = np.zeros(len(pl))
for s in range(24):   # rising plucks under the growing logo, 91.0 to 94.0
    m = [55, 59, 62, 67, 71, 74, 79, 83][s % 8] + (12 if s >= 16 else 0)
    place(arp, pluck(midi(m), .3), 7 + s * .125, .02 + .05 * (s / 24) ** 1.5)
place(music, edge(pl + arp, 10, .08), 84)
place(music, norm(era_end(), TGT, 0, 12), 94)
music = music[:N]
t = np.arange(N) / SR
music *= np.interp(t, [0, 86.7, 86.95, 89.0, 89.5, 107.8, 110], [1, 1, .4, .45, 1, 1, 0])   # the hesitation, then the final fade
m = np.interp(t, [0, 87.6, 88.1, 88.9, 89.35, 110], [0, 0, 1, 1, 0, 0])   # the laptop lid muffles the music
music = music * (1 - m) + filt(music, hi=420) * m * 1.1

# ---------------- sound cues ----------------
def typing(d=1.0):
    out = np.zeros(int(d * SR) + 2400)
    k = max(2, int(d / .068))
    for i in range(k):
        at = max(0, i * d / k + rng.uniform(-.008, .008))
        place(out, filt(noise(.014), 1500, 6000) * np.exp(-tt(.014) * 330), at, rng.uniform(.5, 1))
        place(out, sine(rng.uniform(1700, 2300), .008) * np.exp(-tt(.008) * 500), at, .25)
    return out


def sigh():
    n = int(.7 * SR)
    r = np.linspace(0, 1, n)
    x = filt(noise(.7), 800, 2500)[:n] * (1 - r) + filt(noise(.7), 300, 900)[:n] * r
    k = int(.08 * SR)
    return x * np.r_[np.linspace(0, 1, k), np.linspace(1, 0, n - k) ** 1.5]


def click(f=1200):
    return sine(f, .014) * np.exp(-tt(.014) * 280) + np.r_[noise(.004) * .5, np.zeros(len(tt(.014)) - len(tt(.004)))]


def seq(parts):
    """parts: (offset seconds, array, gain)"""
    L = max(o + len(a) / SR for o, a, g in parts)
    out = np.zeros(int(L * SR) + 8)
    for o, a, g in parts: place(out, a, o, g)
    return out


def band_sweep(d, lo_band, hi_band):
    n = int(d * SR)
    a, b = filt(noise(d), *lo_band), filt(noise(d), *hi_band)
    r = np.linspace(0, 1, n)
    return (a * (1 - r) + b * r) * hann(n)


def robot(k=1, gap=.13, groups=None):
    syl = lambda: filt(saw(110, .11, 14, .7), 500, 1300) * env(int(SR * .11), .01, .03)
    if groups:
        parts, o = [], 0.0
        for g in groups:
            for _ in range(g): parts.append((o, syl(), 1)); o += gap
            o += .12
        return seq(parts)
    return seq([(i * gap, syl(), 1) for i in range(k)])


def modem():
    d1 = [(i * .09, (sine(f1, .06) + sine(f2, .06)) * env(int(SR * .06), .004, .004), .5) for i, (f1, f2) in enumerate([(697, 1209), (770, 1336), (852, 1477), (697, 1477)])]
    t2 = tt(.5)
    car = (np.sin(phase(1650 + 180 * np.sign(np.sin(2 * np.pi * 14 * t2)))) + .7 * np.sin(2 * np.pi * 980 * t2)) * env(len(t2), .02, .05)
    hiss = filt(noise(.35), 1000, 3200) * hann(int(SR * .35))
    return seq(d1 + [(.38, car, .5), (.62, hiss, .9)])


def shimmer(d=1.0):
    parts = []
    for _ in range(12):
        L = rng.uniform(.3, .6)
        parts.append((rng.uniform(0, d - L), sine(rng.uniform(2000, 6000), L) * hann(int(SR * L)), .12))
    parts.append((0, filt(noise(d), lo=6000) * np.linspace(0, 1, int(SR * d)) ** 2 * hann(int(SR * d)), .12))
    return seq(parts)


def fax(d=1.0):
    fs = [1100, 2100, 1300, 1900, 1100, 2100, 1500, 2100, 1300, 1900, 1100, 2100]
    step = d / len(fs)
    return seq([(i * step, sine(f, step) * env(int(SR * step), .004, .004), 1) for i, f in enumerate(fs)])


def drag8(d=.9):
    step = d / 8
    return filt(seq([(i * step, square(220 * 2 ** (i / 8), step) * env(int(SR * step), .003, .003), 1) for i in range(8)]), hi=3000)


SF = {
    'pop': lambda d: glide(420, 880, .07) * np.exp(-tt(.07) * 40),
    'popsoft': lambda d: glide(330, 600, .07) * np.exp(-tt(.07) * 45),
    'type': lambda d: typing(d or 1.0),
    'crt': lambda d: seq([(0, glide(150, 2400, .14, 2) * hann(int(SR * .14)), .6), (0, sine(60, .2) * np.exp(-tt(.2) * 20), 1)]),
    'fax': lambda d: fax(d or 1.0),
    'drag8': lambda d: drag8(d or .9),
    'beep8': lambda d: filt(square(880, .09) * env(int(SR * .09), .003, .01), hi=5000),
    'tap': lambda d: sine(160, .05) * np.exp(-tt(.05) * 70) + np.r_[filt(noise(.03), hi=2000) * np.exp(-tt(.03) * 150) * .5, np.zeros(len(tt(.05)) - len(tt(.03)))],
    'click8': lambda d: filt(square(660, .035) * env(int(SR * .035), .002, .01), hi=5000),
    'bonk': lambda d: filt(seq([(0, square(196, .11) * env(int(SR * .11), .003, .01), 1), (.11, square(131, .17) * env(int(SR * .17), .003, .04), 1)]), hi=3000),
    'job': lambda d: seq([(0, bell(784, .5), .8), (.11, bell(1047, .7), 1)]),
    'modem': lambda d: modem(),
    'mail': lambda d: filt(seq([(0, square(659, .08) * env(int(SR * .08), .003, .01), 1), (.08, square(784, .15) * env(int(SR * .15), .003, .05), 1)]), hi=4000),
    'boing': lambda d: np.sin(phase(300 + 2000 * tt(.2) + 60 * np.sin(2 * np.pi * 30 * tt(.2)))) * np.exp(-tt(.2) * 12),
    'robot': lambda d: robot(1),
    'robot3': lambda d: robot(4),
    'robot4': lambda d: robot(groups=[2, 2]),
    'success8': lambda d: filt(seq([(i * .07, square(f, .07) * env(int(SR * .07), .003, .01), 1) for i, f in enumerate([523, 659, 784, 1047])]), hi=5000),
    'swoosh': lambda d: band_sweep(.55, (400, 1200), (1500, 5000)),
    'whoosh': lambda d: band_sweep(.7, (250, 900), (900, 3000)),
    'flip': lambda d: band_sweep(.3, (500, 1500), (1500, 4500)),
    'bubble': lambda d: seq([(0, glide(300, 760, .08) * np.exp(-tt(.08) * 25), 1), (.07, glide(760, 560, .06) * np.exp(-tt(.06) * 30), .6)]),
    'shrink': lambda d: glide(880, 300, .85, .7) * hann(int(SR * .85)) * (1 + .3 * np.sin(2 * np.pi * 18 * tt(.85))),
    'tapfail': lambda d: seq([(0, sine(130, .07) * np.exp(-tt(.07) * 40), 1), (.02, filt(square(98, .2), hi=900) * env(int(SR * .2), .005, .08), .5)]),
    'rumble': lambda d: filt(noise(d or 1.9), hi=110) * (.7 + .3 * np.sin(2 * np.pi * 3.2 * tt(d or 1.9))) * hann(int(SR * (d or 1.9))) ** .5,
    'reflow': lambda d: seq([(i * .07, bell(f, .5), 1) for i, f in enumerate([523, 659, 784, 1047])]),
    'tapok': lambda d: seq([(0, click(), .7), (.02, bell(1319, .6), 1)]),
    'ripple': lambda d: seq([(0, glide(220, 520, .35) * hann(int(SR * .35)), .8), (0, filt(noise(.3), 2000, 6000) * hann(int(SR * .3)), .25)]),
    'grow': lambda d: glide(300, 620, .4) * hann(int(SR * .4)),
    'ticks': lambda d: seq([(i / 22, sine(2100, .008) * np.exp(-tt(.008) * 400), 1) for i in range(int((d or 1.2) * 22))]),
    'stamp': lambda d: seq([(0, glide(95, 48, .2) * np.exp(-tt(.2) * 18), 1), (0, filt(noise(.07), hi=1500) * np.exp(-tt(.07) * 60), .7)]),
    'buzz': lambda d: filt(square(147, .24), hi=1100) * env(int(SR * .24), .01, .06),
    'click': lambda d: click(),
    'ding': lambda d: bell(1319, .8),
    'sparkle': lambda d: seq([(i * .045, bell(f, .35), 1) for i, f in enumerate([2093, 2637, 3136, 4186])]),
    'swarm': lambda d: seq([(i * .09, glide(f, f * 1.6, .05) * np.exp(-tt(.05) * 50), 1) for i, f in enumerate(rng.uniform(500, 1100, 14))]),
    'stick': lambda d: seq([(0, filt(noise(.06), 700, 5000) * np.exp(-tt(.06) * 70), 1), (0, sine(220, .04) * np.exp(-tt(.04) * 80), .4)]),
    'toggle': lambda d: seq([(0, click(700), 1), (.07, click(1000), 1)]),
    'tickok': lambda d: bell(1568, .3),
    'shimmer': lambda d: shimmer(1.0),
    'send': lambda d: glide(600, 1300, .09) * np.exp(-tt(.09) * 20),
    'sparklerun': lambda d: seq([(o, bell(f, .25), 1) for o, f in zip(np.sort(rng.uniform(0, .6, 12)), rng.choice([1568, 1760, 2093, 2349, 2637, 3136], 12))]),
    'inflate': lambda d: seq([(0, glide(160, 520, .85, 1.5) * np.linspace(.2, 1, int(SR * .85)) * env(int(SR * .85), .02, .05), 1), (0, filt(noise(.85), 800, 2500) * np.linspace(0, 1, int(SR * .85)) * env(int(SR * .85), .02, .05), .2)]),
    'popback': lambda d: seq([(0, filt(noise(.03), 500, 4000) * np.exp(-tt(.03) * 120), 1), (0, glide(420, 180, .09) * np.exp(-tt(.09) * 30), .8)]),
    'scan': lambda d: glide(1250, 950, d or 1.2) * (.6 + .4 * np.sin(2 * np.pi * 11 * tt(d or 1.2))) * hann(int(SR * (d or 1.2))) ** .4,
    'tally': lambda d: seq([(0, sine(330, .07) * env(int(SR * .07), .004, .01), 1), (.1, sine(330, .07) * env(int(SR * .07), .004, .01), 1), (.2, sine(880, .16) * env(int(SR * .16), .004, .05), 1)]),
    'ship': lambda d: seq([(i * .085, bell(f, .9), 1) for i, f in enumerate([1047, 1319, 1568, 2093])]),
    'sigh': lambda d: sigh(),
    'liddown': lambda d: seq([(0, glide(320, 200, .22) * hann(int(SR * .22)), .25), (.2, sine(70, .16) * np.exp(-tt(.16) * 25), 1), (.2, filt(noise(.05), hi=800) * np.exp(-tt(.05) * 80), .5)]),
    'lidup': lambda d: seq([(0, glide(200, 330, .22) * hann(int(SR * .22)), .5), (.22, click(900), .6)]),
    'dragslow': lambda d: glide(330, 415, d or 1.6) * hann(int(SR * (d or 1.6))) ** .5 * (.8 + .2 * np.sin(2 * np.pi * 6 * tt(d or 1.6))),
    'riser': lambda d: seq([(0, filt(noise(d or 2.6), lo=1500) * np.linspace(0, 1, int(SR * (d or 2.6))) ** 2, .5), (0, glide(196, 784, d or 2.6, 2) * np.linspace(0, 1, int(SR * (d or 2.6))) ** 1.5, .5)]) * np.r_[np.ones(int(SR * (d or 2.6)) - 480), np.linspace(1, 0, 488)],
    'boom': lambda d: seq([(0, glide(70, 42, .9) * np.exp(-tt(.9) * 5), 1), (0, filt(noise(1.2), hi=2500) * np.exp(-tt(1.2) * 4), .25)]),
    'ticksoft': lambda d: click(900),
    'signoff': lambda d: seq([(0, bell(1047, 1.4), 1), (.12, bell(1568, 1.4), .6)]),
}
GAIN = {'stamp': .45, 'boom': .5, 'crt': .3, 'modem': .2, 'fax': .11, 'type': .2, 'job': .3, 'ship': .32, 'riser': .3, 'sigh': .32, 'rumble': .4,
        'swarm': .22, 'pop': .24, 'popsoft': .16, 'robot': .22, 'robot3': .22, 'robot4': .22, 'buzz': .18, 'ticks': .1, 'scan': .09, 'shimmer': .2,
        'inflate': .22, 'dragslow': .1, 'liddown': .4, 'lidup': .28, 'ticksoft': .12, 'signoff': .26, 'drag8': .12, 'beep8': .14, 'click8': .14, 'bonk': .2,
        'mail': .16, 'success8': .16, 'boing': .2, 'tickok': .16, 'sparkle': .16, 'sparklerun': .16, 'ding': .24, 'tapok': .26, 'reflow': .22}

tl = json.loads((REPO / 'tools' / 'timeline.json').read_text())
sfxL, sfxR = np.zeros(N), np.zeros(N)
for ev in tl['sfx']:
    tm, name = ev[0], ev[1]
    d = ev[2] if len(ev) > 2 else None
    x = np.asarray(SF[name](d), dtype=float)
    x = x / (np.max(np.abs(x)) + 1e-9) * GAIN.get(name, .26)
    pan = rng.uniform(-.25, .25)
    place(sfxL, x, tm, 1 - max(0, pan)); place(sfxR, x, tm, 1 + min(0, pan))

L, R = music + sfxL, music + sfxR
for name, x in (('music', music), ('sfx', (sfxL + sfxR) / 2), ('mix', (L + R) / 2)):
    print(f'{name:6s} peak {20 * np.log10(np.max(np.abs(x)) + 1e-9):6.1f} dBFS   rms {20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9):6.1f} dBFS')
cuts = tl['cuts']
for a, b in zip(cuts[:-1], cuts[1:]):
    seg = music[int(a * SR):int(b * SR)]
    print(f'  music {a:5.1f}-{b:5.1f}s rms {20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9):6.1f} dBFS  peak {20 * np.log10(np.max(np.abs(seg)) + 1e-9):6.1f}')
st = np.stack([filt(L, lo=30), filt(R, lo=30)], 1)
st = np.tanh(st * 1.0)
wavfile.write(REPO / 'out' / 'audio_raw.wav', SR, (st * 32767 * .98).astype(np.int16))
wavfile.write(REPO / 'out' / 'music_only.wav', SR, (np.tanh(music) * 32767 * .98).astype(np.int16))
print(f'wrote out/audio_raw.wav  {len(st) / SR:.1f} s')
