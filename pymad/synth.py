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
    ch = 0

    for m in notes:
    # for m in track:
        st = m['offset'] * speedRatio
        le = m['length'] * lenRatio * speedRatio
        note = piano.getNote(m['note'], le)
        if note.ndim > 1:
            ch = max(ch, note.shape[1])

        st_idx = floor(st * fs)
        ed_idx = st_idx + note.shape[0]
        wavs.append((st_idx, note))
        ed_max = max(ed_idx, ed_max)
    
    if ch > 0:
        out = np.zeros((ed_max, ch), dtype=np.float32)
    else:
        out = np.zeros(ed_max, dtype=np.float32)

    for st_idx, note in wavs:
        if ch > 0 and note.ndim < 2:
            note = note[:, np.newaxis]
        out[st_idx:(st_idx + note.shape[0])] += note * volRatio
    
    return sequence(out, fs)
