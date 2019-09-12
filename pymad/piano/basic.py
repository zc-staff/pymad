import numpy as np
from math import pi
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

    def getNote(self, note, length):
        pitch = note2pitch(note) * self.pitch_ratio
        n = round(length * self.fs)
        t = np.arange(n) / self.fs * pitch + self.phase
        t = t - np.floor(t)
        if self.mode == 'sin':
            t = np.sin(2 * pi * t - pi / 2)
        elif self.mode == 'square':
            t = np.sign(t - 0.5)
        elif self.mode == 'sawtooth':
            t = 2.0 * t - 1.0
        elif self.mode == 'triangle':
            t = 1.0 - 4.0 * np.abs(t - 0.5)
        else:
            raise NotImplementedError()
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
