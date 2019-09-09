import numpy as np
from math import pi
from . import note2pitch
from .asdr import LinearASDR
from ..core import sequence, readWav

class BasicPiano(object):
    def __init__(self, fs, phase=0, pitch_ratio=1, mode='sin'):
        self.fs = fs
        self.phase = phase
        self.pitch_ratio = pitch_ratio
        self.mode = mode

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

class Drum(object):
    def __init__(self, fs, beats):
        self.fs = 44100
        self.beats = beats
    
    def getNote(self, note, length):
        return self.beats[note]

# def loadDrum(beatsFile):
#     beats = dict()
#     fs = 44100
#     for k, v in beatsFile.items():
#         t = readWav(v)
#         fs = t.fs
#         beats[k] = t
#     return Drum(fs, beats)

class PianoCache(object):
    def __init__(self, parent):
        self.fs = parent.fs
        self.parent = parent
        self.cache = dict()
    
    def getNote(self, note, length):
        if not (note, length) in self.cache:
            self.cache[(note, length)] = self.parent.get_note(note, length)
        return self.cache[(note, length)]
