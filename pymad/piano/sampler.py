from math import ceil, log2
from . import note2pitch
from ..dsp import find_pitch, repeat2, resample2, filter4

class Sampler(object):
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