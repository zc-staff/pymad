import numpy as np
from math import floor, pi
from . import note2pitch
from .basic import GenericPiano

class Guitar(GenericPiano):
    def __init__(self, pluck, damping, fs=44100):
        self.fs = fs
        self.h, self.tau = pluck, damping
    
    def load(self, **kwargs):
        pass

    def getNote(self, note, length):
        pitch = note2pitch(note)
        n = round(length * self.fs)
        t = np.arange(n) / self.fs
        t = t[np.newaxis, :]

        r = floor(self.fs / 2 / pitch)
        if self.tau > 0:
            r = min(r, floor(1 / self.tau))
        r = np.arange(1, 1 + r)

        fn = r * self.tau
        fn = r * pitch * np.sqrt(1 - fn * fn)
        fn = fn[:, np.newaxis]

        bn = 2 / pi / r * np.sin(r * pi * self.h)
        bn = bn[:, np.newaxis]

        an = r * r * 2 * pi * pitch * self.tau
        an = an[:, np.newaxis]

        t = bn * np.cos(2 * pi * fn * t) * np.exp(-an * t)
        t = np.sum(t, axis=0)
        # t += self.h - 0.5
        # print(np.max(t) + np.min(t))
        return t
