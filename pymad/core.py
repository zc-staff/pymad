import numpy as np
import scipy.io.wavfile as wavfile
import librosa

class Sequence(np.ndarray):
    def __new__(cls, *args, fs=None, **kwargs):
        ret = super(Sequence, cls).__new__(cls, *args, **kwargs)
        ret.fs = fs
        return ret
    
    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.fs = getattr(obj, "fs", None)
    
    def writeWav(self, file):
        wavfile.write(file, self.fs, self)
    
    def clone(self):
        y = np.copy(self)
        return sequence(y, self.fs)

def sequence(x, fs):
    x = x.astype(np.float32)
    x = x.view(Sequence)
    x.fs = fs
    return x

def readWav(file):
    data, fs = librosa.load(file, sr=None)

    ret = data.view(Sequence)
    ret.fs = fs
    return ret
