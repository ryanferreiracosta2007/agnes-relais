# -*- coding: utf-8 -*-
"""Musique et bruitages générés par programme + mixage."""
import numpy as np, wave, math
SR = 48000
rng = np.random.default_rng(7)

def t_(d): return np.arange(int(d * SR)) / SR

def envd(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)

def noise(d): return rng.uniform(-1, 1, int(d * SR))

def lp(x, k):  # passe-bas simple
    y = np.empty_like(x); acc = 0.0
    a = k
    # filtre vectorisé via cumul exponentiel
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x)

def hp(x, k):
    return x - lp(x, k)

def sfx(name):
    if name == 'pop':
        t = t_(0.15); f = 900 * np.exp(-t * 18) + 300
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * envd(len(t), 0.002, 0.05)
    if name == 'whoosh':
        n = noise(0.45); t = t_(0.45)
        e = np.sin(np.pi * t / 0.45) ** 2
        return hp(lp(n, 0.25), 0.02) * e * 0.9
    if name == 'swipe':
        return sfx('whoosh')[: int(0.3 * SR)] * 0.8
    if name == 'ding':
        t = t_(0.8)
        return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)) * envd(len(t), 0.002, 0.25) * 0.5
    if name == 'heart':
        t = t_(0.9)
        return sum(np.sin(2 * np.pi * f * t) * envd(len(t), 0.003, 0.35) * 0.25 for f in (1046, 1568))
    if name == 'sparkle':
        out = np.zeros(int(1.0 * SR))
        for i, f in enumerate((1568, 2093, 2637, 3136, 4186)):
            s = int(i * 0.07 * SR); t = t_(0.5)
            out[s:s + len(t)] += np.sin(2 * np.pi * f * t) * envd(len(t), 0.002, 0.15) * 0.25
        return out
    if name == 'scratch':
        t = t_(0.5); f = 200 + 900 * np.abs(np.sin(t * 22))
        return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + hp(noise(0.5), 0.3) * 0.4) * envd(len(t), 0.005, 0.25)
    if name == 'boing':
        t = t_(0.6); f = 180 + 120 * np.sin(t * 40) * np.exp(-t * 4)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * envd(len(t), 0.003, 0.3) * 0.8
    if name == 'stamp':
        t = t_(0.4); f = 120 * np.exp(-t * 10) + 45
        return np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * envd(len(t), 0.001, 0.12) + lp(noise(0.4), 0.3) * envd(len(t), 0.001, 0.03)
    if name == 'coins':
        out = np.zeros(int(1.2 * SR))
        for i in range(9):
            s = int(rng.uniform(0, 0.7) * SR); t = t_(0.4); f = rng.uniform(2500, 4200)
            out[s:s + len(t)] += np.sin(2 * np.pi * f * t) * envd(len(t), 0.001, 0.08) * 0.3
        return out
    if name == 'pschht':
        n = noise(1.0); t = t_(1.0)
        e = np.minimum(1, t / 0.03) * np.exp(-t / 0.35)
        return hp(n, 0.35) * e * 0.8
    if name == 'wah':
        out = []
        for f0, d in ((392, 0.35), (370, 0.35), (349, 0.7)):
            t = t_(d); f = f0 * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
            ph = 2 * np.pi * np.cumsum(f) / SR
            out.append((np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)) * np.minimum(1, t / 0.03) * np.exp(-t / (d * 1.5)) * 0.3)
        return np.concatenate(out)
    if name == 'rewind':
        t = t_(0.9); f = 300 + 2500 * (t / 0.9) ** 2
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.2 * (1 - t / 0.9) + hp(noise(0.9), 0.2) * 0.25 * np.sin(np.pi * t / 0.9)
    if name == 'bells':
        out = np.zeros(int(1.5 * SR))
        for i in range(10):
            s = int(i * 0.12 * SR); n = hp(noise(0.25), 0.6) * envd(int(0.25 * SR), 0.001, 0.05) * 0.35
            out[s:s + len(n)] += n
        return out
    if name == 'wink':
        t = t_(0.25); f = 1200 + 1800 * t / 0.25
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * envd(len(t), 0.002, 0.08) * 0.4
    if name == 'drumroll':
        out = np.zeros(int(1.0 * SR))
        for i in range(30):
            s = int(i * 0.033 * SR); n = lp(noise(0.05), 0.4) * envd(int(0.05 * SR), 0.001, 0.02) * (0.2 + 0.5 * i / 30)
            e = min(len(out), s + len(n)); out[s:e] += n[:e - s]
        return out
    if name == 'buzz':
        t = t_(0.9); f = 190 + 6 * np.sin(2 * np.pi * 7 * t)
        ph = np.cumsum(f) / SR; saw = 2 * (ph % 1.0) - 1
        return lp(saw, 0.35) * (0.7 + 0.3 * np.sin(2 * np.pi * 31 * t)) * np.minimum(1, t / 0.03) * np.minimum(1, (0.9 - t) / 0.1) * 0.35
    if name == 'sniff':
        out = np.zeros(int(0.5 * SR))
        for k in range(2):
            n = hp(lp(noise(0.12), 0.35), 0.08) * np.sin(np.linspace(0, np.pi, int(0.12 * SR))) * 0.7
            s = int(k * 0.18 * SR); out[s:s + len(n)] += n
        return out
    if name == 'spit':
        t = t_(0.5); n = lp(noise(0.5), 0.5) * np.minimum(1, t / 0.01) * np.exp(-t / 0.12)
        f = 180 * np.exp(-t * 6) + 90
        return n * 0.9 + np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.1) * 0.4
    raise KeyError(name)

def music(dur, bpm=96, bright=False):
    """beat lo-fi chaud : Am7 - Fmaj7 - Cmaj7 - G6"""
    n = int(dur * SR); out = np.zeros(n)
    beat = 60 / bpm; bar = 4 * beat
    chords = [(57, [57, 60, 64, 67]), (53, [53, 57, 60, 64]), (48, [55, 59, 60, 64]), (55, [55, 59, 62, 64])]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    nb = int(dur / bar) + 1
    for b in range(nb):
        root, notes = chords[b % 4]; s0 = int(b * bar * SR)
        L = int(bar * SR); t = np.arange(L) / SR
        pad = sum(np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(4 * np.pi * hz(m) * t) for m in notes)
        pad *= np.minimum(1, t / 0.05) * np.exp(-t / 1.6) * 0.06
        # notes "piano" arpégées
        for k in range(8):
            m = notes[(k * 3 + b) % 4] + 12; st = int(k * beat / 2 * SR); tt = np.arange(int(0.6 * SR)) / SR
            tone = (np.sin(2 * np.pi * hz(m) * tt) + 0.25 * np.sin(4 * np.pi * hz(m) * tt)) * np.exp(-tt / 0.18) * 0.04
            e = min(L, st + len(tt)); pad[st:e] += tone[:e - st]
        bass = np.sin(2 * np.pi * hz(root - 12) * t) * 0.16 * (np.exp(-(t % (2 * beat)) / 0.6))
        seg = pad + bass
        e = min(n, s0 + L); out[s0:e] += seg[:e - s0]
        for q in range(4):  # batterie
            p = s0 + int(q * beat * SR)
            if p >= n: break
            if q in (0, 2):
                tt = np.arange(int(0.3 * SR)) / SR; f = 110 * np.exp(-tt * 25) + 45
                k_ = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12) * 0.45
                e = min(n, p + len(k_)); out[p:e] += k_[:e - p]
            else:
                s_ = hp(noise(0.25), 0.4) * envd(int(0.25 * SR), 0.001, 0.07) * 0.2
                e = min(n, p + len(s_)); out[p:e] += s_[:e - p]
            for h in (0, 0.5):
                ph = p + int(h * beat * SR); hh = hp(noise(0.05), 0.7) * envd(int(0.05 * SR), 0.001, 0.015) * 0.08
                e = min(n, ph + len(hh)); out[ph:e] += hh[:e - ph] if ph < n else 0
    fade = int(1.0 * SR); out[-fade:] *= np.linspace(1, 0, fade)
    return out

def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() > 1: a = a.reshape(-1, w.getnchannels()).mean(1)
    if sr != SR:
        x = np.arange(int(len(a) * SR / sr)) * sr / SR
        a = np.interp(x, np.arange(len(a)), a)
    return a

def mix(dur, voices, effects, clipdir, bpm=96, mute=None, mus_gain=0.5):
    n = int(dur * SR) + SR
    vo = np.zeros(n); fx = np.zeros(n)
    for clip, at in voices:
        a = read_wav(f'{clipdir}/{clip}.wav'); a = a / (np.max(np.abs(a)) + 1e-6) * 0.9
        s = int(at * SR); e = min(n, s + len(a)); vo[s:e] += a[:e - s]
    for name, at, g in effects:
        a = sfx(name) * g; s = int(at * SR); e = min(n, s + len(a)); fx[s:e] += a[:e - s]
    mu = music(n / SR, bpm)
    if mute:
        a0, a1 = int(mute[0] * SR), int(mute[1] * SR); mu[a0:a1] = 0
        f = int(0.03 * SR); mu[a1:a1 + f] *= np.linspace(0, 1, f)
    # ducking de la musique sous la voix
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    lev = uniform_filter1d(maximum_filter1d(np.abs(vo), int(0.15 * SR)), int(0.2 * SR))
    duck = 1 - 0.55 * np.clip(lev / 0.2, 0, 1)
    out = vo * 1.0 + fx * 0.45 + mu * mus_gain * duck
    out = out[: int(dur * SR)]
    return out

def write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())
