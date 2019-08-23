from math import ceil, floor
import json
import curses

# C4 = 64, same as midi
NOTES = [ 'C ', 'C#', 'D ', 'D#', 'E ', 'F ', 'F#', 'G ', 'G#', 'A ', 'A#', 'B ' ]
C = 64
CENTER = 4

NOTEOFFSET = 8
YOFFSET = 3
XOFFSET = 2
EPS = 1e-6

def note2name(note):
    ret = NOTES[(note - C) % len(NOTES)]
    ret = ret + str((note - C) // len(NOTES) + CENTER)
    return ret

def beat2time(bpm, beat):
    return beat * 60.0 / bpm

def padOrTrunc(s, chs, ch=' '):
    if chs > len(s):
        return s + ch * (chs - len(s))
    else:
        return s[:chs]

def lockRange(x, a, b):
    return max(min(x, b), a)

def isLow(x):
    return x > 96

def toLow(x):
    if isLow(x):
        return x
    else:
        return x + 32

def upScale(x, s):
    return 1 if isLow(x) else s

class Editor(object):
    def __init__(self, scr):
        self.scr = scr
        # how many characters per beat
        self.scale = 8
        # offset in character
        self.xoffset = 0
        # note of the first line
        self.yoffset = C + len(NOTES)
        # how many beats per bar
        self.bar = 4
        # window size in (height, width)
        self.size = scr.getmaxyx()
        self.number = False
        self.redraw = False
        self.input = ''
        self.message = ''
        self.quit = False
        self.cursor = 0
        self.xcur = 0
        self.ycur = C
        self.showBeat = True
        self.notes = []
        self.lastNote = { 'length': 1.0 }
        self.savePath = None
        self.bpm = 120
        self.yank = []
        self.yankPos = (self.xcur / self.scale, self.ycur)
    
    def drawNote(self):
        self.redraw = True
        lines = self.size[0] - YOFFSET - 1
        self.yoffset = lockRange(self.yoffset, lines - 1, 128)
        for i in range(lines):
            self.scr.addstr(YOFFSET + i, 0, ' ' * NOTEOFFSET)
            label = note2name(self.yoffset - i)
            self.scr.addstr(YOFFSET + i, XOFFSET, label)
        
        self.ycur = lockRange(self.ycur, self.yoffset - lines + 1, self.yoffset)
        self.scr.addstr(YOFFSET - self.ycur + self.yoffset, 1, '▶')
    
    def drawHead(self):
        self.redraw = True
        chs = self.size[1] - NOTEOFFSET
        if self.savePath != None:
            lin1 = padOrTrunc(self.savePath, chs)
            self.scr.addstr(0, NOTEOFFSET, lin1)
        lin2 = padOrTrunc('bpm={}, beats={}, scale={}, nextLen={}, notes={}, selected={}, yanked={}'
            .format(self.bpm, self.bar, self.scale,
                    self.lastNote['length'], len(self.notes),
                    len(list(filter(lambda x: x.get('selected', False), self.notes))),
                    len(self.yank)), chs)
        self.scr.addstr(1, NOTEOFFSET, lin2)
    
    def drawTimeline(self):
        self.drawHead()
        self.redraw = True
        self.xoffset = max(0, self.xoffset)

        chs = self.size[1] - NOTEOFFSET
        sc = self.bar * self.scale
        st = ceil(self.xoffset / sc) * sc - self.xoffset

        lines = self.size[0] - YOFFSET - 1
        for i in range(-1, lines):
            self.scr.addstr(YOFFSET + i, NOTEOFFSET, ' ' * chs)
        
        if self.showBeat:
            st2 = ceil(self.xoffset / self.scale) * self.scale - self.xoffset
            for i in range(st2, chs, self.scale):
                for j in range(lines):
                    self.scr.addstr(YOFFSET + j, NOTEOFFSET + i, '▏')
        
        for i in range(st, chs, sc):
            ch = str((i + self.xoffset) // sc)
            if len(ch) > sc or len(ch) + i > chs:
                ch = '*'
            self.scr.addstr(2, NOTEOFFSET + i, ch)
            for j in range(lines):
                self.scr.addstr(YOFFSET + j, NOTEOFFSET + i, '▎')
        
        self.xcur = lockRange(self.xcur, self.xoffset, self.xoffset + chs - 1)
        self.scr.addstr(2, NOTEOFFSET + self.xcur - self.xoffset, '▼')
        
        # sorted()
        self.notes.sort(key=lambda n: n['offset'])
        for n in self.notes:
            st = floor((n['offset'] + EPS) * self.scale) - self.xoffset
            ed = ceil(((n['offset'] - EPS) + n['length']) * self.scale) - self.xoffset
            st = lockRange(st, 0, chs - 1)
            ed = lockRange(ed, 0, chs - 1)
            nt = self.yoffset - n['note']
            if ed - st > 0 and nt >= 0 and nt < lines:
                if n.get('selected', False):
                    color = curses.color_pair(1)
                else:
                    color = curses.color_pair(0)
                self.scr.addstr(YOFFSET + nt, NOTEOFFSET + st, '█' * (ed - st - 1),
                    color)
                self.scr.addstr(YOFFSET + nt, NOTEOFFSET + ed - 1, '▊',
                    color)
    
    def drawInput(self):
        self.redraw = True
        chs = self.size[1] - 1
        line = ''
        if len(self.input) > 0:
            self.message = ''
            self.input = self.input[:chs]
            line = self.input
        elif len(self.message) > 0:
            line = self.message
        self.scr.addstr(self.size[0] - 1, 0, padOrTrunc(line, chs))
        self.cursor = len(line)
    
    def drawEverything(self):
        self.drawNote()
        self.drawTimeline()
        self.drawInput()
    
    def refresh(self):
        if self.redraw:
            self.scr.addstr(self.size[0] - 1, self.cursor, '')
            self.scr.refresh()
        self.redraw = False
    
    def scoreInHash(self):
        return { 'bpm': self.bpm, 'bar': self.bar, 'notes':
            list(map(lambda x: {
                'offset': x['offset'],
                'note': x['note'],
                'length': x['length'],
            }, self.notes))}

    def trackInHash(self):
        return list(map(lambda x: {
            'offset': beat2time(self.bpm, x['offset']),
            'note': x['note'],
            'length': beat2time(self.bpm, x['length']),
        }, self.notes))
    
    def saveScore(self, args, track=False):
        p = None
        if not track:
            p = self.savePath
        if len(args) >= 2:
            p = args[1]
        if p == None:
            self.message = 'no save path given'
        else:
            with open(p, 'w') as fp:
                if track:
                    t = self.trackInHash()
                else:
                    t = self.scoreInHash()
                    self.savePath = p
                json.dump(t, fp, indent=2)
            self.message = 'written to ' + p
        self.drawHead()
    
    def findNote(self):
        t = None
        for n in self.notes:
            xcur = self.xcur / self.scale
            if n['note'] == self.ycur and n['offset'] <= xcur and n['offset'] + n['length'] > xcur:
                t = n
        return t

    def loadScore(self, path):
        with open(path, 'r') as fp:
            t = json.load(fp)
            self.bpm = t['bpm']
            self.bar = t['bar']
            self.notes = t['notes']
        self.savePath = path
        self.drawEverything()
        self.message = 'load {} notes from {}'.format(len(self.notes), path)
    
    def onCommand(self):
        args = self.input[1:].split()
        if len(args) == 0:
            return
        cmd = args[0]
        if cmd == 'q':
            self.quit = True
        elif cmd == 'w':
            self.saveScore(args)
        elif cmd == 'e':
            self.saveScore(args, True)
        elif cmd == 'l':
            if len(args) < 2:
                self.message = 'no load path given'
            else:
                self.loadScore(args[1])
        elif cmd == 'bpm':
            if len(args) < 2:
                self.message = 'no bpm given'
            else:
                self.bpm = float(args[1])
                self.message = 'set bpm to {}'.format(self.bpm)
                self.drawHead()
        elif cmd == 'beat':
            if len(args) < 2:
                self.message = 'no beat given'
            else:
                self.bar = int(args[1])
                self.message = 'set beat to {}'.format(self.bar)
                self.drawTimeline()
        else:
            self.message = 'unknown command'
    
    def onKey(self):
        skip = self.scale if self.showBeat else self.scale * self.bar
        key = self.scr.getch()
        if key == -1:
            self.size = self.scr.getmaxyx()
            self.drawEverything()
        elif len(self.input) > 0:
            if key >= 32 and key < 127:
                self.input = self.input + chr(key)
                self.drawInput()
            elif key == 127:
                self.input = self.input[:-1]
                self.drawInput()
            elif key == 10 or key == 13:
                self.onCommand()
                self.input = ''
                self.drawInput()
        elif key == 27:
            self.quit = True
        elif key == ord(':'):
            self.input = ':'
            self.drawInput()
        elif toLow(key) == ord('j'):
            self.xoffset -= upScale(key, skip)
            self.drawTimeline()
        elif toLow(key) == ord('l'):
            self.xoffset += upScale(key, skip)
            self.drawTimeline()
        elif toLow(key) == ord('i'):
            self.yoffset += upScale(key, len(NOTES))
            self.drawNote()
            self.drawTimeline()
        elif toLow(key) == ord('k'):
            self.yoffset -= upScale(key, len(NOTES))
            self.drawNote()
            self.drawTimeline()
        elif key == ord('u'):
            if self.scale > 1:
                self.scale = self.scale // 2
                self.xoffset = self.xoffset // 2
                self.xcur = self.xcur // 2
            self.drawTimeline()
        elif key == ord('o'):
            self.scale = self.scale * 2
            self.xoffset = self.xoffset * 2
            self.xcur = self.xcur * 2
            self.drawTimeline()
        elif key == ord('\\'):
            self.showBeat = not self.showBeat
            self.drawTimeline()
        elif toLow(key) == ord('a'):
            self.xcur -= upScale(key, skip)
            self.drawTimeline()
        elif toLow(key) == ord('d'):
            self.xcur += upScale(key, skip)
            self.drawTimeline()
        elif toLow(key) == ord('w'):
            self.ycur += upScale(key, len(NOTES))
            self.drawNote()
        elif toLow(key) == ord('s'):
            self.ycur -= upScale(key, len(NOTES))
            self.drawNote()
        elif toLow(key) == ord('q'):
            self.lastNote = {
                'offset': self.xcur / self.scale,
                'length': self.lastNote['length'],
                'note': self.ycur,
                'selected': not isLow(key),
            }
            self.notes.append(self.lastNote)
            self.drawTimeline()
        elif key == 9:
            t = self.findNote()
            if t != None:
                t['selected'] = not t.get('selected', False)
            self.drawTimeline()
        elif key == 353:
            for n in self.notes:
                n['selected'] = False
            self.drawTimeline()
        elif key == ord('r'):
            t = self.findNote()
            if t != None:
                self.notes.remove(t)
            self.drawTimeline()
        elif key == ord('R'):
            self.notes[:] = filter(lambda x: not x.get('selected', False), self.notes)
            self.drawTimeline()
        elif toLow(key) == ord('z'):
            step = 1 / self.scale if isLow(key) else 1
            for n in filter(lambda x: x.get('selected', False), self.notes):
                if n['length'] > step:
                    n['length'] -= step
            self.drawTimeline()
        elif toLow(key) == ord('x'):
            step = 1 / self.scale if isLow(key) else 1
            for n in filter(lambda x: x.get('selected', False), self.notes):
                n['length'] += step
            self.drawTimeline()
        elif key == ord('y'):
            self.yank = list(filter(lambda x: x.get('selected', False), self.notes))
            self.yankPos = (self.xcur / self.scale, self.ycur)
            self.message = 'yanked {} notes'.format(len(self.yank))
            self.drawHead()
            self.drawInput()
        elif toLow(key) == ord('p'):
            for n in self.yank:
                x = n['offset'] + self.xcur / self.scale - self.yankPos[0]
                y = n['note'] + self.ycur - self.yankPos[1]
                self.notes.append({
                    'offset': x, 'note': y,
                    'length': n['length'],
                    'selected': not isLow(key),
                })
            self.message = 'paste {} notes'.format(len(self.yank))
            self.drawTimeline()
            self.drawInput()

def main(scr):
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    editor = Editor(scr)
    editor.drawEverything()
    while not editor.quit:
        editor.refresh()
        editor.onKey()

curses.wrapper(main)
