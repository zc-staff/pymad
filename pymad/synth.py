from math import floor
from tqdm import tqdm
import numpy as np
from .core import sequence

def synthesize(piano, track, len_ratio=1, speed_ratio=1, vol_ratio=1, quiet=False):
    fs = piano.fs
    notes = []
    ed_max = 0
    notes = track['notes']
    if not quiet:
        notes = tqdm(notes)
    speed_ratio *= 60 / track['bpm']

    for m in notes:
    # for m in track:
        st = m['offset'] * speed_ratio
        le = m['length'] * len_ratio * speed_ratio
        note = piano.get_note(m['note'], le)

        st_idx = floor(st * fs)
        ed_idx = st_idx + note.shape[0]
        notes.append((st_idx, note))
        ed_max = max(ed_idx, ed_max)
    
    out = np.zeros(ed_max, dtype=np.float32)

    for st_idx, note in notes:
        out[st_idx:(st_idx + note.shape[0])] += note * vol_ratio
    
    return sequence(out, fs)
