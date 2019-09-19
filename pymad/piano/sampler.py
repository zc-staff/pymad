from math import log2
from . import note2pitch
from .basic import GenericPiano
from ..dsp import findPitch, repeat2, resample2, filter4

class Sampler(GenericPiano):
    def __init__(self, filter_ratio=4, pitch_ratio=1):
        self.filter_ratio = filter_ratio
        self.pitch_ratio = pitch_ratio
    
    def load(self, sample, pitch=None, **kwargs):
        self.fs = sample.fs
        self.data = { 0: sample.clone() }
        self.length = sample.shape[0] / self.fs
        if pitch == None:
            self.pitch = findPitch(sample)
        else:
            self.pitch = pitch
        print(self.pitch)
    
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
    
    def getNote(self, note, length):
        pitch = note2pitch(note) * self.pitch_ratio
        pit = pitch
        len0 = length
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
        nn = round(self.fs * len0)
        x = filter4(x[:nn], pit, ratio=self.filter_ratio)
        return x