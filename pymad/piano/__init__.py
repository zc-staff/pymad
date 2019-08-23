def note2pitch(note):
    return 440 * (2 ** ((note - 69) / 12))

from .basic import SimplePiano, PianoCache, Drum, load_drum
from .sampler import Sampler
