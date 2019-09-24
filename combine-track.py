import json
import sys
from argparse import ArgumentParser
from pymad import loadTrack

if __name__ == "__main__":
    parser = ArgumentParser('combine-track', 'combine tracks')
    parser.add_argument('track', help='track path')
    parser.add_argument('-o', '--orchestra', action='append', nargs=2, metavar=('id', 'path'), help='add an orchestra')

    args = parser.parse_args()
    tracks = { int(o[0]): loadTrack(o[1]) for o in args.orchestra }
    track = loadTrack(args.track)

    notes = []
    for n0 in track['notes']:
        if n0['note'] in tracks:
            for n in tracks[n0['note']]['notes']:
                notes.append({ 'note': n['note'], 'length': n['length'], 'offset': n0['offset'] + n['offset'] })
    
    json.dump({ 'bpm': track['bpm'], 'bar': track['bar'], 'notes': notes }, sys.stdout)
    
