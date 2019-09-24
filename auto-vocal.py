from math import ceil
import re
from argparse import ArgumentParser
import numpy as np
import cv2
from tqdm import tqdm

gana = {
    'a': ["あ", "か", "が", "さ", "ざ", "た", "だ", "な", "は", "ば", "ぱ", "ま", "や", "ら", "わ", "じゃ", "ちゃ"],
    'i': ["い", "き", "ぎ", "し", "じ", "ち", "ぢ", "に", "ひ", "び", "ぴ", "み", "り", "ん"],
    'u': ["う", "く", "ぐ", "す", "ず", "つ", "づ", "ぬ", "ふ", "ぶ", "ぷ", "む", "ゆ", "る", "じゅ"],
    'e': ["え", "け", "げ", "せ", "ぜ", "て", "で", "ね", "へ", "べ", "ぺ", "め", "れ"],
    'o': ["お", "こ", "ご", "そ", "ぞ", "と", "ど", "の", "ほ", "ぼ", "ぽ", "も", "よ", "ろ", "を", "しょ", "ちょ", "りょ"],
    'R': ['R'],
}

ganaRev = {}
for k, vs in gana.items():
    for v in vs:
        assert not v in ganaRev
        ganaRev[v] = k

tpb = 480
fps = 30

def getVocals(vocal):
    with open(vocal, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()

    notes = []
    cur = {}
    bpm = 0
    for l in lines:
        if re.search(r'^\[#\d+\]$', l):
            if 'length' in cur and 'lyric' in cur:
                notes.append(cur)
                cur = {}
        
        ma = re.search(r'^Tempo=([\d\.]+)$', l)
        if ma != None:
            bpm = float(ma.group(1))
        
        ma = re.search(r'^Lyric=(.+)$', l)
        if ma != None:
            cur['lyric'] = ma.group(1)
        
        ma = re.search(r'^Length=(\d+)$', l)
        if ma != None:
            cur['length'] = int(ma.group(1))
    
    if 'length' in cur and 'lyric' in cur:
        notes.append(cur)
    return notes, bpm

def work(vocal, path, out):
    imgs = { k: cv2.imread(path % k, cv2.IMREAD_UNCHANGED).astype(np.float64) / 255 for k in gana }

    vol, bpm = getVocals(vocal)
    size = 0
    spt = 60 / bpm / tpb

    for v in vol:
        assert v['lyric'] in ganaRev, v['lyric']
        v['lyric'] = ganaRev[v['lyric']]
        size += v['length'] * spt
    
    size = ceil(size * fps)
    l = 0
    cur = 0
    for t in tqdm(range(size)):
        while l < len(vol) and (cur + vol[l]['length']) * spt <= t / fps:
            cur += vol[l]['length']
            l += 1
        x = 'R'
        if l < len(vol):
            x = vol[l]['lyric']
        pic = imgs[x]
        cv2.imwrite(out % t, (pic * 255).astype(np.uint8))


if __name__ == "__main__":
    parser = ArgumentParser('auto-vocal')
    parser.add_argument('vocal')
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--out')
    args = parser.parse_args()

    work(args.vocal, args.input, args.out)
