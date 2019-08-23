import numpy as np
from math import ceil, pi
from . import note2pitch
from ..core import sequence, readWav

class BasicPiano(object):
    def __init__(self, fs, phase=0, pitch_ratio=1, mode='sin'):
        self.fs = fs
        self.phase = phase
        self.pitch_ratio = pitch_ratio
        self.mode = mode

    def get_note(self, note, length):
        pitch = note2pitch(note) * self.pitch_ratio
        n = ceil(length * self.fs)
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
        t *= np.hamming(n)
        return sequence(t, self.fs)

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
