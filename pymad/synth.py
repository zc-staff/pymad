from math import floor
from tqdm import tqdm
import numpy as np
from .core import sequence

def synthesize(piano, track, lenRatio=1, speedRatio=1, volRatio=1, quiet=True):
    fs = piano.fs
    wavs = []
    ed_max = 0
    notes = track['notes']
    if not quiet:
        notes = tqdm(notes)
    speedRatio *= 60 / track['bpm']

    for m in notes:
    # for m in track:
        st = m['offset'] * speedRatio
        le = m['length'] * lenRatio * speedRatio
        note = piano.getNote(m['note'], le)

        st_idx = floor(st * fs)
        ed_idx = st_idx + note.shape[0]
        wavs.append((st_idx, note))
        ed_max = max(ed_idx, ed_max)
    
    out = np.zeros(ed_max, dtype=np.float32)

    for st_idx, note in wavs:
        out[st_idx:(st_idx + note.shape[0])] += note * volRatio
    
    return sequence(out, fs)
