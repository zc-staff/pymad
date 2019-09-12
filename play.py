from argparse import ArgumentParser
import ctypes
from sdl2 import *
from pymad import readWav

seq = None
pos = 0

@SDL_AudioCallback
def cb(user, stream, length):
    global seq, pos
    length = length // 4
    stream = ctypes.cast(stream, ctypes.POINTER(c_float))
    for i in range(length):
        if pos + i < seq.shape[0]:
            stream[i] = c_float(seq[pos + i])
        else:
            stream[i] = 0
    pos += length

def run(path):
    global seq, pos

    if SDL_Init(SDL_INIT_AUDIO) != 0:
        raise "failed"

    seq = readWav(path)
    spec = SDL_AudioSpec(seq.fs, AUDIO_F32LSB, 1, 4096, cb)
    if SDL_OpenAudio(ctypes.byref(spec), None) != 0:
        raise "failed"
    SDL_PauseAudio(0)

    while (pos < seq.shape[0]):
        pass

    SDL_PauseAudio(1)
    SDL_CloseAudio()
    SDL_Quit()
    

if __name__ == "__main__":
    parser = ArgumentParser("play", description="play wav")
    parser.add_argument("wav", help="wav path")
    args = parser.parse_args()
    run(args.wav)
