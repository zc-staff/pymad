from math import log2, floor, ceil, pi
from tqdm import tqdm
import numpy as np
from .core import sequence
from .dsp import repeat2, resample2, filter4, find_pitch

class SimplePiano(object):
    def __init__(self, fs, phase=0):
        self.fs = fs
        self.phase = phase

    def get_note(self, pitch, length):
        n = ceil(length * self.fs)
        t = np.arange(n) / self.fs
        t = np.sin(2 * pi * pitch * t + self.phase)
        t *= np.hamming(n)
        return sequence(t, self.fs)

class Piano(object):
    def __init__(self, x, filter_ratio=4):
        self.fs = x.fs
        self.data = { 0: x.clone() }
        self.length = x.shape[0] / x.fs
        self.pitch = find_pitch(x)
        self.filter_ratio = filter_ratio
    
    def upsample(self, n):
        k = 1 if n > 0 else -1
        for i in range(k, n + k, k):
            if not i in self.data:
                if k > 0:
                    y = repeat2(self.data[i - k], 2)
                    y = resample2(self.data[i - k], 0.5)
                else:
                    y = resample2(self.data[i - k], 2)
                    y = repeat2(self.data[i - k], 0.5)
                self.data[i] = y
        return self.data[n].clone()
    
    def get_keynote(self, i, j):
        if i * j <= 0:
            x = self.upsample(0)
        else:
            if abs(i) > abs(j):
                t = j
            else:
                t = i
            i -= t
            j -= t
            x = self.upsample(t)
        for _ in range(i):
            x = repeat2(x, 2)
        for _ in range(-j):
            x = resample2(x, 2)
        for _ in range(-i):
            x = repeat2(x, 0.5)
        for _ in range(j):
            x = resample2(x, 0.5)
        return x        
    
    def get_note(self, pitch, length):
        pit = pitch
        len = length
        pitch /= self.pitch
        length /= self.length
        ii = length * pitch
        jj = pitch
        i = int(log2(ii))
        j = int(log2(jj))
        ii /= 2 ** i
        jj /= 2 ** j
        jj = 1 / jj
        x = self.get_keynote(i, j)
        if ii > 1:
            x = repeat2(x, ii)
        if jj > 1:
            x = resample2(x, jj)
        if ii < 1:
            x = repeat2(x, ii)
        if jj < 1:
            x = resample2(x, jj)
        nn = ceil(self.fs * len)
        x = filter4(x[:nn], pit, ratio=self.filter_ratio)
        return x

class PianoCache(object):
    def __init__(self, parent):
        self.fs = parent.fs
        self.parent = parent
        self.cache = dict()
    
    def get_note(self, pitch, length):
        if not (pitch, length) in self.cache:
            self.cache[(pitch, length)] = self.parent.get_note(pitch, length)
        return self.cache[(pitch, length)]

def synthesize(piano, track):
    end = 0
    for m in track:
        ed = m['offset'] + m['length']
        end = max(end, ed)
    fs = piano.fs
    n = ceil(end * fs)
    out = np.zeros(n, dtype=np.float32)
    for m in tqdm(track):
        note = piano.get_note(m['pitch'], m['length'])
        st = floor(m['offset'] * fs)
        out[st:(st + note.shape[0])] = note
    return sequence(out, fs)
