import json
from mido import MidiFile

def dump_midi(midi, prefix, charset='utf-8'):
    midi = MidiFile(midi, charset=charset)
    tempo = 500000
    bar = 4

    for idx, t in enumerate(midi.tracks):
        outs = dict()
        keys = dict()
        now = 0.0
        for m in t:
            now += m.time / midi.ticks_per_beat
            if m.type == 'set_tempo':
                tempo = m.tempo
            elif m.type == 'time_signature':
                bar = m.numerator
            if m.type != 'note_on' and m.type != 'note_off':
                continue
            ch = m.channel
            if not ch in outs:
                outs[ch] = list()
                keys[ch] = dict()
            if m.type == 'note_off' or m.velocity == 0:
                st = keys[ch][m.note]
                # pitch = 440 * (2 ** ((m.note - 69) / 12))
                note = { "offset": st, "note": m.note, "length": now - st }
                outs[ch].append(note)
                keys[ch].pop(m.note)
            else:
                keys[ch][m.note] = now
        for ch, v in outs.items():
            path = prefix + '-' + str(idx) + '-' + str(ch) + '.json'
            with open(path, 'w') as f:
                json.dump({
                    'bpm': 60000000.0 / tempo,
                    'bar': bar, 'notes': v
                }, f, indent=2)

def load_track(path):
    with open(path, 'r') as f:
        ret = json.load(f)
    return ret
