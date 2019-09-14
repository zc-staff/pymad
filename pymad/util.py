import numpy as np
import ctypes
from sdl2 import SDL_AudioCallback, c_float, SDL_Init, SDL_INIT_AUDIO
from sdl2 import SDL_AudioSpec, AUDIO_F32LSB, SDL_OpenAudio, SDL_PauseAudio
from sdl2 import SDL_CloseAudio, SDL_Quit

def play(seq):
    pos = 0
    @SDL_AudioCallback
    def cb(user, stream, length):
        nonlocal pos
        length = length // 8
        stream = ctypes.cast(stream, ctypes.POINTER(c_float))
        for i in range(length):
            if pos + i < seq.shape[0]:
                t = seq[pos + i]
                stream[2 * i], stream[2 * i + 1] = t[0], t[-1]
            else:
                stream[2 * i] = stream[2 * i + 1] = 0
        pos += length
    
    if seq.ndim < 2:
        seq = seq[..., np.newaxis]
    
    if SDL_Init(SDL_INIT_AUDIO) != 0:
        raise "failed"

    spec = SDL_AudioSpec(seq.fs, AUDIO_F32LSB, 2, 4096, cb)
    if SDL_OpenAudio(ctypes.byref(spec), None) != 0:
        raise "failed"
    SDL_PauseAudio(0)

    while (pos < seq.shape[0]):
        pass

    SDL_PauseAudio(1)
    SDL_CloseAudio()
    SDL_Quit()
