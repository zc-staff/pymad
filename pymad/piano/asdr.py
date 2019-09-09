import numpy as np
from math import floor

class GenericASDR(object):
    def __init__(self, piano):
        self.piano = piano
        self.fs = piano.fs
    
    def getEnvelope(self, len1):
        raise NotImplementedError
    
    def getNote(self, note, length):
        env = self.getEnvelope(length)
        len1 = env.shape[0] / self.fs
        note = self.piano.getNote(note, len1)
        return note * env

class LinearASDR(GenericASDR):
    def __init__(self, piano, attack, decay, sustain, release):
        super(LinearASDR, self).__init__(piano)
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
    
    def getEnvelope(self, len1):
        len2 = floor(self.fs * self.attack)
        len3 = floor(self.fs * self.decay)
        ret = np.ndarray(len2 + len3, dtype=np.float32)
        ret[:len2] = np.arange(len2) / len2
        ret[len2:(len2+len3)] = 1 - (1 - self.sustain) * np.arange(len3) / len3
        if len1 > len2 + len3:
            ret = np.pad(ret, (0, len1-len2-len3), constant_values=self.sustain)
        else:
            ret = ret[:len1]
        end = ret[-1]
        len4 = floor(self.fs * end * self.release)
        ret = np.pad(ret, (0, len4))
        ret[len1:(len1+len4)] = end * (1 - np.arange(len4) / len4)
        return ret
