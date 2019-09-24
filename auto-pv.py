from math import floor, ceil
from argparse import ArgumentParser
import numpy as np
import cv2
from pymad import loadTrack
from tqdm import tqdm

fps = 30

def test(path, n, track, out, filterNote=None, pas=None):
    imgs = [ cv2.imread(path % i, cv2.IMREAD_UNCHANGED).astype(np.float64) / 255 for i in range(n) ]
    tpb = 60 / track['bpm']

    notes = track['notes']
    if filterNote != None:
        notes = list(filter(lambda x: x['note'] == filterNote, notes))
    notes.sort(key=lambda x: (x['offset'], x['note']))

    end = 0
    for nt in notes:
        end = max(end, nt['length'] + nt['offset'])
    end = ceil(end * tpb * fps)
    # print(end / fps)

    l = r = 0
    m = len(notes)
    # for i in tqdm(range(end)):
    for i in range(end):
        b = i / fps / tpb
        while l < m and notes[l]['offset'] + notes[l]['length'] <= b:
            l += 1
        while r < m and notes[r]['offset'] <= b:
            r += 1

        if pas == None:
            assert r - l <= 1, (l, r)
            lt = l
        else:
            lt = l + pas

        t = n-1
        if r - lt > 0:
            t = (b - notes[lt]['offset']) * min(tpb * fps, n / notes[lt]['length'])
            # t = (b - notes[l]['offset']) * tpb * fps
        t = min(t, n-1)
        # print(t)
        ll = floor(t)
        # t -= ll
        pic = imgs[ll]
        # assert r - l <= 2
        cv2.imwrite(out % i, (pic * 255).astype(np.uint8))

if __name__ == "__main__":
    parser = ArgumentParser('test', 'test')
    parser.add_argument('-i', '--input')
    parser.add_argument('-c', '--count', type=int)
    parser.add_argument('-o', '--out')
    parser.add_argument('-f', '--filter', type=int, default=None)
    parser.add_argument('-p', '--pas', type=int, default=None)
    parser.add_argument('track')
    args = parser.parse_args()

    test(args.input, args.count, loadTrack(args.track), args.out, filterNote=args.filter, pas=args.pas)
