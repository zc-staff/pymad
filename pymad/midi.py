import json
from mido import MidiFile

def dump_midi(midi, prefix, charset='utf-8'):
    midi = MidiFile(midi, charset=charset)
    tempo = 500000

    for idx, t in enumerate(midi.tracks):
        outs = dict()
        keys = dict()
        now = 0
        for m in t:
            now += m.time * tempo / midi.ticks_per_beat / 1000000
            if m.type == 'set_tempo':
                tempo = m.tempo
            if m.type != 'note_on' and m.type != 'note_off':
                continue
            ch = m.channel
            if not ch in outs:
                outs[ch] = list()
                keys[ch] = dict()
            if m.type == 'note_off' or m.velocity == 0:
                st = keys[ch][m.note]
                pitch = 440 * (2 ** ((m.note - 69) / 12))
                note = { "offset": st, "pitch": pitch, "length": now - st }
                outs[ch].append(note)
                keys[ch].pop(m.note)
            else:
                keys[ch][m.note] = now
        for ch, v in outs.items():
            path = prefix + '-' + str(idx) + '-' + str(ch) + '.json'
            with open(path, 'w') as f:
                json.dump(v, f, indent=2)

def load_track(path):
    with open(path, 'r') as f:
        ret = json.load(f)
    return ret
