from math import log2, floor, ceil, pi
from tqdm import tqdm
import numpy as np
from .core import sequence, readWav
from .dsp import repeat2, resample2, filter4, find_pitch

def note2pitch(note):
    return 440 * (2 ** ((note - 69) / 12))

class SimplePiano(object):
    def __init__(self, fs, phase=0, pitch_ratio=1):
        self.fs = fs
        self.phase = phase
        self.pitch_ratio = pitch_ratio

    def get_note(self, note, length):
        pitch = note2pitch(note) * self.pitch_ratio
        n = ceil(length * self.fs)
        t = np.arange(n) / self.fs
        t = np.sin(2 * pi * pitch * t + self.phase)
        t *= np.hamming(n)
        return sequence(t, self.fs)

class Piano(object):
    def __init__(self, x, filter_ratio=4, pitch_ratio=1):
        self.fs = x.fs
        self.data = { 0: x.clone() }
        self.length = x.shape[0] / x.fs
        self.pitch = find_pitch(x)
        self.filter_ratio = filter_ratio
        self.pitch_ratio = pitch_ratio
    
    def upsample(self, n):
        k = 1 if n > 0 else -1
        for i in range(k, n + k, k):
            if not i in self.data:
                if k > 0:
                    y = repeat2(self.data[i - k], 2)
                    y = resample2(y, 0.5)
                else:
                    y = resample2(self.data[i - k], 2)
                    y = repeat2(y, 0.5)
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
    
    def get_note(self, note, length):
        pitch = note2pitch(note) * self.pitch_ratio
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

class Drum(object):
    def __init__(self, beats):
        self.fs = 44100
        for _, v in beats.items():
            self.fs = v.fs
            break
        self.beats = beats
    
    def get_note(self, note, length):
        return self.beats[note]

def load_drum(beatsFile):
    beats = dict()
    for k, v in beatsFile.items():
        t = readWav(v)
        beats[k] = t
    return Drum(beats)

class PianoCache(object):
    def __init__(self, parent):
        self.fs = parent.fs
        self.parent = parent
        self.cache = dict()
    
    def get_note(self, note, length):
        if not (note, length) in self.cache:
            self.cache[(note, length)] = self.parent.get_note(note, length)
        return self.cache[(note, length)]

def synthesize(piano, track, len_ratio=1, speed_ratio=1, vol_ratio=1):
    fs = piano.fs
    notes = []
    ed_max = 0

    for m in tqdm(track):
    # for m in track:
        st = m['offset'] * speed_ratio
        le = m['length'] * len_ratio * speed_ratio
        note = piano.get_note(m['note'], le)

        st_idx = floor(st * fs)
        ed_idx = st_idx + note.shape[0]
        notes.append((st_idx, note))
        ed_max = max(ed_idx, ed_max)
    
    out = np.zeros(ed_max, dtype=np.float32)

    for st_idx, note in notes:
        out[st_idx:(st_idx + note.shape[0])] += note * vol_ratio
    
    return sequence(out, fs)
