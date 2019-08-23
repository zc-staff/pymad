def note2pitch(note):
    return 440 * (2 ** ((note - 69) / 12))

from .basic import BasicPiano, PianoCache, Drum, load_drum
from .sampler import Sampler
