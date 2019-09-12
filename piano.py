from math import sin, pi
import ctypes
from sdl2 import *
from pymad.piano import note2pitch

eps = 1e-6

class Key(object):
    def __init__(self, fs, note, synth):
        self.synth = synth
        self.ts = 2 * pi * note2pitch(note) / fs
        self.note = note
        self.trigger = False
        self.gate = 0.0
        self.velocity = 0.0
        self.sustain = 0
        self.attack = 0.2 * fs
        self.decay = 5 * fs
        self.release = 0.2 * fs
        self.state = 0
        self.phase = 0
    
    def tick(self):
        self.phase += self.ts
        if self.trigger:
            self.state = 1
            self.trigger = False
        if self.state == 1:
            if self.velocity >= self.gate:
                self.state = 2
            else:
                self.velocity += self.gate / self.attack
        if self.state == 2:
            if self.velocity > self.gate:
                self.velocity -= 1.0 / self.release
            elif self.velocity > self.gate * self.sustain:
                self.velocity -= 1.0 / self.decay
            elif self.velocity <= 0:
                del keys[self.note]
    
    def getNext(self):
        ans = self.velocity * self.synth(self.phase)
        self.tick()
        return ans
    
    def press(self, gate):
        self.gate = gate
        self.trigger = True

fs = 44100
keys = dict()
keyBinds = {
    SDL_SCANCODE_A: 60,
    SDL_SCANCODE_S: 62,
    SDL_SCANCODE_D: 64,
    SDL_SCANCODE_F: 65,
    SDL_SCANCODE_G: 67,
    SDL_SCANCODE_H: 69,
    SDL_SCANCODE_J: 71,
    SDL_SCANCODE_Q: 72,
    SDL_SCANCODE_W: 74,
    SDL_SCANCODE_E: 76,
    SDL_SCANCODE_R: 77,
    SDL_SCANCODE_T: 79,
    SDL_SCANCODE_Y: 81,
    SDL_SCANCODE_U: 83,
    SDL_SCANCODE_Z: 48,
    SDL_SCANCODE_X: 50,
    SDL_SCANCODE_C: 52,
    SDL_SCANCODE_V: 53,
    SDL_SCANCODE_B: 55,
    SDL_SCANCODE_N: 57,
    SDL_SCANCODE_M: 59,
}

@SDL_AudioCallback
def cb(user, stream, len):
    len = len // 4
    stream = ctypes.cast(stream, ctypes.POINTER(c_float))
    for i in range(len):
        ans = 0.0
        # stream[i] = sin(2 * pi * 440 * i / fs)
        for _, k in list(keys.items()):
            ans += k.getNext()
        stream[i] = c_float(ans)
    # print(stream[0])

def run():
    if SDL_Init(SDL_INIT_EVERYTHING) != 0:
        raise "failed"

    spec = SDL_AudioSpec(fs, AUDIO_F32LSB, 1, 4096, cb)
    if SDL_OpenAudio(ctypes.byref(spec), None) != 0:
        raise "failed"
    SDL_PauseAudio(0)

    window = SDL_CreateWindow(b"Hello World",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              592, 460, SDL_WINDOW_SHOWN)
    running = True
    event = SDL_Event()

    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN or event.type == SDL_KEYUP:
                code = event.key.keysym.scancode
                if code in keyBinds and event.key.repeat == 0:
                    SDL_LockAudio()
                    note = keyBinds[code]
                    if event.key.keysym.mod & KMOD_SHIFT != 0:
                        note += 1
                    if note in keys:
                        key = keys[note]
                    else:
                        key = Key(fs, note, sin)
                        keys[note] = key
                    key.press(1 if event.type == SDL_KEYDOWN else 0)
                    SDL_UnlockAudio()
    SDL_DestroyWindow(window)
    SDL_CloseAudio()
    SDL_Quit()

if __name__ == "__main__":
    run()
