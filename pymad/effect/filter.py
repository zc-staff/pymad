import scipy.signal as signal
from ..core import sequence
from .basic import GenericEffect

class Filter(GenericEffect):
    def getFilter(self, src):
        raise NotImplementedError

    def process(self, src):
        b, a, bi = self.getFilter(src)
        if bi:
            return sequence(signal.filtfilt(b, a, src), src.fs)
        else:
            return sequence(signal.lfilter(b, a, src), src.fs)

class LowpassFilter(Filter):
    def __init__(self, cutoff, rank=101):
        self.cutoff = cutoff
        self.rank = rank
    
    def getFilter(self, src):
        return signal.firwin(self.rank, self.cutoff, fs=src.fs), (1, ), True

class HighpassFilter(Filter):
    def __init__(self, cutoff, rank=101):
        self.cutoff = cutoff
        self.rank = rank
    
    def getFilter(self, src):
        b = -signal.firwin(self.rank, self.cutoff, fs=src.fs)
        b[self.rank // 2] += 1
        return b, (1, ), True
