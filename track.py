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

def note2name(note):
    ret = NOTES[(note - C) % len(NOTES)]
    ret = ret + str((note - C) // len(NOTES) + CENTER)
    return ret

def beat2time(bpm, beat):
    return beat * 60.0 / bpm

def pad(s, chs, ch=' '):
    return s + ch * (chs - len(s))

def lockRange(x, a, b):
    return max(min(x, b), a)

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
        self.lastWrite = 1.0
        self.savePath = None
        self.bpm = 120
    
    def drawNote(self):
        self.redraw = True
        lines = self.size[0] - YOFFSET - 1
        for i in range(lines):
            self.scr.addstr(YOFFSET + i, 0, ' ' * NOTEOFFSET)
            label = note2name(self.yoffset - i)
            self.scr.addstr(YOFFSET + i, XOFFSET, label)
        
        self.ycur = lockRange(self.ycur, self.yoffset - lines + 1, self.yoffset)
        self.scr.addstr(YOFFSET - self.ycur + self.yoffset, 1, '▶')
    
    def drawTimeline(self):
        self.redraw = True
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
            st = floor(n['offset'] * self.scale) - self.xoffset
            ed = ceil((n['offset'] + n['length']) * self.scale) - self.xoffset
            st = lockRange(st, 0, chs - 1)
            ed = lockRange(ed, 0, chs - 1)
            nt = self.yoffset - n['note']
            if ed - st > 0 and nt >= 0 and nt < lines:
                self.scr.addstr(YOFFSET + nt, NOTEOFFSET + st, '█' * (ed - st - 1))
                self.scr.addstr(YOFFSET + nt, NOTEOFFSET + ed - 1, '▊')
    
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
        self.scr.addstr(self.size[0] - 1, 0, pad(line, chs))
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
        return { 'bpm': self.bpm, 'bar': self.bar, 'notes': self.notes }

    def trackInHash(self):
        return list(map(lambda x : {
            'offset': beat2time(self.bpm, x['offset']),
            'note': x['note'],
            'length': beat2time(self.bpm, x['length'])
        }, self.notes))
    
    def saveScore(self, args, track=False):
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
                json.dump(t, fp, indent=2)
            self.message = 'written to ' + p
    
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
            pass
        else:
            self.message = 'unknown command'
    
    def onKey(self):
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
        elif key == ord('j'):
            if self.xoffset > 0:
                self.xoffset -= 1
            self.drawTimeline()
        elif key == ord('l'):
            self.xoffset += 1
            self.drawTimeline()
        elif key == ord('i'):
            if self.yoffset < 128:
                self.yoffset += 1
            self.drawNote()
            self.drawTimeline()
        elif key == ord('k'):
            if self.yoffset > 0:
                self.yoffset -=1
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
        elif key == ord('a'):
            self.xcur -= 1
            self.drawTimeline()
        elif key == ord('d'):
            self.xcur += 1
            self.drawTimeline()
        elif key == ord('w'):
            self.ycur += 1
            self.drawNote()
        elif key == ord('s'):
            self.ycur -= 1
            self.drawNote()
        elif key == ord('q'):
            self.notes.append({
                'offset': self.xcur / self.scale,
                'length': self.lastWrite,
                'note': self.ycur,
            })
            self.drawTimeline()

def main(scr):
    editor = Editor(scr)
    editor.drawEverything()
    while not editor.quit:
        editor.refresh()
        editor.onKey()

curses.wrapper(main)
