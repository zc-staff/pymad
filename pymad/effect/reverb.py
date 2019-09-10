from math import ceil, log10
import numpy as np
from ..core import sequence
from .basic import GenericEffect
from .filter import Filter

class AllpassFilter(Filter):
    def __init__(self, rank, gain):
        self.rank = rank
        self.gain = gain
    
    def getFilter(self, src):
        b = np.zeros(self.rank + 1, dtype=np.float32)
        b[0] = -self.gain
        b[self.rank] = 1
        a = np.zeros(self.rank + 1, dtype=np.float32)
        a[0] = 1
        a[self.rank] = -self.gain
        return b, a, False

class CombFilter(Filter):
    def __init__(self, rank, gain):
        self.rank = rank
        self.gain = gain
    
    def getFilter(self, src):
        a = np.zeros(self.rank + 1, dtype=np.float32)
        a[0] = 1
        a[self.rank] = -self.gain
        return (1, ), a, False

class Reverb(GenericEffect):
    PRESETS = {
        'schroeder': (
            ( (347, 0.7), (113, 0.7), (37, 0.7) ),
            ( (1687, 0.773), (1601, 0.802), (2053, 0.753), (2251, 0.733) ),
            ((0.25, 0.25, 0.25, 0.25), (0.25, -0.25, 0.25, -0.25))
        )
    }

    def rankTest(self, rank, gain, silence=-30):
        return rank * ceil(silence / 20 / log10(gain))

    def __init__(self, mixer, aps=None, cfs=None, mm=None, preset=None):
        if preset != None:
            aps, cfs, mm = self.PRESETS[preset]
        tot = 0
        for r, g in cfs:
            tot = max(tot, self.rankTest(r, g))
        for r, g in aps:
            tot += self.rankTest(r, g)
        self.tot = tot
        self.aps = [ AllpassFilter(r, g) for r, g in aps ]
        self.cfs = [ CombFilter(r, g) for r, g in cfs ]
        self.mm = np.transpose(mm)
        self.mixer = mixer
    
    def process(self, src):
        fs = src.fs
        src = sequence(np.pad(src, (0, self.tot)), fs)
        stack = src
        for ap in self.aps:
            stack = ap.process(stack)
        stack = [ cf.process(src) for cf in self.cfs ]
        stack = np.stack(stack, axis=1)
        stack = np.dot(stack, self.mm)
        if stack.ndim > 1:
            src = np.reshape(src, (-1, 1))
        stack = self.mixer[0] * src + self.mixer[1] * stack
        return sequence(stack, fs)
