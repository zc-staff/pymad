import json
from mido import MidiFile, MidiTrack, MetaMessage, Message

def dumpMidi(midi, prefix, charset='utf-8'):
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

def writeMidi(track):
    mid = MidiFile()
    midiTrack = MidiTrack()
    mid.tracks.append(midiTrack)
    tpb = mid.ticks_per_beat

    midiTrack.append(MetaMessage('set_tempo', tempo=round(60000000.0 / track['bpm'])))
    midiTrack.append(MetaMessage('time_signature', numerator=track['bar']))
    events = [ ('note_on', n['note'], n['offset']) for n in track['notes'] ]
    events.extend( ('note_off', n['note'], n['offset'] + n['length']) for n in track['notes'] )
    events.sort(key=lambda x: x[2])
    now = 0

    for e in events:
        time = round((e[2] - now) * tpb)
        midiTrack.append(Message(e[0], note=int(e[1]), velocity=127, time=time))
        now = e[2]

    return mid

def loadTrack(path):
    with open(path, 'r') as f:
        ret = json.load(f)
    return ret
