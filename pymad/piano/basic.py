import numpy as np
from math import pi, floor
from . import note2pitch
from ..core import sequence, readWav

class GenericPiano(object):
    def load(self, **kwargs):
        raise NotImplementedError()

    def getNote(self, note, length):
        raise NotImplementedError()

class BasicPiano(GenericPiano):
    def __init__(self, fs=44100, phase=0, pitch_ratio=1, mode='sin'):
        self.fs = fs
        self.phase = phase
        self.pitch_ratio = pitch_ratio
        self.mode = mode
    
    def load(self, **kwargs):
        pass

    def getHarm(self, r):
        if self.mode == 'sin':
            return np.array([0, 1])
        t = np.arange(r)
        t[0] = 1
        if self.mode == 'square':
            t = 4 / pi / t
            t[::2] = 0
            return t
        elif self.mode == 'sawtooth':
            t = -2 / pi / t * (-1.0) ** t
            t[0] = 0
            return t
        elif self.mode == 'triangle':
            t = 8 / pi / pi / t / t * (-1.0) ** (t // 2)
            t[::2] = 0
            return t
        else:
            raise NotImplementedError()

    def getNote(self, note, length):
        pitch = note2pitch(note) * self.pitch_ratio
        n = round(length * self.fs)
        t = np.arange(n) / self.fs * pitch + self.phase
        
        r = floor(self.fs / pitch / 2)
        r = self.getHarm(r)
        h = np.arange(r.shape[0])
        t = np.sum(r[:, np.newaxis] * np.sin(h[:, np.newaxis] * t[np.newaxis, :] * 2 * pi), axis=0)

        return sequence(t, self.fs)

class Drum(GenericPiano):
    def __init__(self, fs=44100):
        self.fs = fs
    
    def load(self, beats, **kwargs):
        self.beats = beats
    
    def getNote(self, note, length):
        if note in self.beats:
            return self.beats[note]
        elif str(note) in self.beats:
            return self.beats[str(note)]
        else:
            return sequence(np.array([]), self.fs)

# def loadDrum(beatsFile):
#     beats = dict()
#     fs = 44100
#     for k, v in beatsFile.items():
#         t = readWav(v)
#         fs = t.fs
#         beats[k] = t
#     return Drum(fs, beats)

class PianoCache(GenericPiano):
    def __init__(self, parent):
        self.fs = parent.fs
        self.parent = parent
        self.cache = dict()
    
    def load(self, **kwargs):
        self.parent.load(**kwargs)
        self.cache.clear()
    
    def getNote(self, note, length):
        if not (note, length) in self.cache:
            self.cache[(note, length)] = self.parent.get_note(note, length)
        return self.cache[(note, length)]
