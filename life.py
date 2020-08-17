import os
import sys
import msvcrt
getwch = msvcrt.getwch
import colorama
sys.path.insert(0, os.path.abspath('../lib'))
import cmdArgs

class Life(object):
    CSI = '\033\133'
    DBG_NAME = "Life.dbg"
    DBG_FILE = open(DBG_NAME, "w")

    def __init__(self): #147 240 @ 8x8
        colorama.init(autoreset=True)
        self.COLORS = { 'BLACK':'0', 'RED':'1', 'GREEN':'2', 'YELLOW':'3', 'BLUE':'4', 'MAGENTA':'5', 'CYAN':'6', 'WHITE':'7' }
        self.STYLES = {'NORMAL':'22;', 'BRIGHT':'1;'}
        self.C_ALIVE = self.getColor('WHITE', 'YELLOW')
        self.C_DEAD  = self.getColor('RED', 'BLACK')
        self.C_TEXT  = self.getColor('WHITE', 'BLACK')
        self.DATA_SET = set('.*')
        self.XLATE = str.maketrans('.*', '01')
        print('DATA_SET={} XLATE={}'.format(self.DATA_SET, self.XLATE), file=Life.DBG_FILE)
        self.done = []
        self.undone = []
        self.shapes = {}
        self.stats = {}
        self.stats['S_INV_DNSTY'] = -1
        self.argMap = {}
        self.argMap = cmdArgs.parseCmdLine(dbg=1)
        self.nRows = 147
        self.nCols = 237
        self.inName = 'lexicon-no-wrap.txt'
        print('argMap={}'.format(self.argMap), file=Life.DBG_FILE)
        if 'f' in self.argMap and len(self.argMap['f']) > 0:
            self.inName = self.argMap['f'][0]
        print('inName={}'.format(self.inName), file=Life.DBG_FILE)
        if 'r' in self.argMap and len(self.argMap['r']) > 0:
            self.nRows = int(self.argMap['r'][0])
        print('nRows={}'.format(self.nRows), file=Life.DBG_FILE)
        if 'c' in self.argMap and len(self.argMap['c']) > 0:
            self.nCols = int(self.argMap['c'][0])
        print('nCols={}'.format(self.nCols), file=Life.DBG_FILE)
        print(file=Life.DBG_FILE)
        self.clear()
#        self.parse()
#        self.addShape('1-2-3')
#        self.printCells('init() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))
        self.printCells2()

    def addShape(self, key):
        rOff, cOff = 0, 0
        row = int(self.nRows/2 - 1 + rOff)
        col = int(self.nCols/2 - 1 - cOff)
        v = self.shapes[key]
        data = v[0]
        print('addShape({},{}) key={}'.format(row, col, key), file=Life.DBG_FILE)
        if data is None: return
#        print(data, file=Life.DBG_FILE)
        for (i,r) in enumerate(data):
            print(r, file=Life.DBG_FILE)
            for (j,c) in enumerate(r):
                self.cells[i+row][j+col] = int(data[i][j])
        self.done.append(self.cells)

    def parse(self):
        data, key, info, state = [], '', '', 0
        with open(self.inName, 'r') as self.inFile:
            for line in self.inFile:
                line = line.strip()
                if len(line) > 0:
                    dataSet = set(line)
                    if line[0] == ':': #state <= 1
                        p = line.find(':', 1)
                        if p != -1:
                            if state == 2:
                                self.shapes[key][0] = data
                                print('key=[{}] size=[{}x{}]\n[{}]'.format(key, len(data), len(data[0]), info), file=Life.DBG_FILE)
                            data = []
                            key = line[1:p]
                            info = line[p+1:].strip()
                            v = [None, info, None, None]
                            self.shapes[key] = v
                            state = 1
#                            print('{:>50} | state={} v0={} v3={} v2={} v1={}'.format(key, state, v[0], v[3], v[2], v[1]), file=Life.DBG_FILE)
                    elif dataSet <= self.DATA_SET: #state > 0
#                        print(line, file=Life.DBG_FILE)
                        line = line.translate(self.XLATE)
                        data.append(line)
                        state = 2
                        print('    {}'.format(line), file=Life.DBG_FILE)
                    elif state == 2:
                        self.shapes[key][0] = data
                        state = 0
                        print('key=[{}] size=[{}x{}]\n[{}]'.format(key, len(data), len(data[0]), info), file=Life.DBG_FILE)
                        data = []
        self.printShapes()

    def printShapes(self):
        print('printShapes(BGN) len={}'.format(len(self.shapes)), file=Life.DBG_FILE)
        for k in self.shapes:
            v = self.shapes[k]
            data = v[0]
            if data != None:
                print('[{}]'.format(k), file=Life.DBG_FILE)
                for d in data:
                    print(d, file=Life.DBG_FILE)
        print('printShapes(END)', file=Life.DBG_FILE)

#    '''
    def loadTest1(self):
        rOff, cOff = 10, 5
        r = int(self.nRows/2 - 1 + rOff)
        c = int(self.nCols/2 - 1 - cOff)
        print('loadTest1() r={} c={}'.format(r, c), file=Life.DBG_FILE)
        self.cells[r-1][c]   = 1
        self.cells[r][c-1]   = 1
        self.cells[r][c]     = 1
        self.cells[r][c+1]   = 1
        self.cells[r+1][c+1] = 1
        r = int(self.nRows/2 - 1 + rOff)
        c = int(self.nCols/2 - 1 + cOff)
        print('loadTest1() r={} c={}'.format(r, c), file=Life.DBG_FILE)
        self.cells[r-1][c]   = 1
        self.cells[r][c-1]   = 1
        self.cells[r][c]     = 1
        self.cells[r][c+1]   = 1
        self.cells[r+1][c-1] = 1
        self.done.append(self.cells)
#    '''

    def run(self):#            print('{}'.format(c), end=' ', flush=True)
        b, c, s = 0, '', []
        while True:
            c = getwch()
            b = ord(c)
            if   b == 13:                        self.update() # c == 'Enter'
            elif b == 85 or b == 117 or b == 75: self.undo()   # c == 'U' or c == 'u' or c == 'Left Arrow'
            elif b == 82 or b == 114 or b == 77: self.redo()   # c == 'R' or c == 'r' or c == 'Right Arrow'
            elif b == 71 or b == 103:            self.goTo()   # c == 'G' or c == 'g'
            elif b == 74 or b == 106:            self.jump()   # c == 'J' or c == 'j'
            elif b == 81 or b == 113: break                    # c == 'Q' or c == 'q'
            
    def clear(self):
        self.clearScreen()
        self.clearCells()

    @staticmethod
    def clearScreen(arg=2, file=None, reason=None, dbg=0):
        if dbg: print('clearScreen() arg={} file={} reason={}'.format(arg, file, reason), file=Life.DBG_FILE)
        print(Life.CSI + '{}J'.format(arg), file=file)

    def clearCells(self):
        self.cells = []
        for r in range(self.nRows):
            tmp = []
            for c in range(self.nCols):
                tmp.append(0)
            self.cells.append(tmp)

    def jump(self):
        jj, tmp = '', []
        while jj != 32:
            jj = getwch()
            if jj == '-' or '0' <= jj <= '9': tmp.append(jj)
            else: break
        print('jump({}) done[{}] undone[{}] BGN'.format(tmp, len(self.done), len(self.undone)), file=Life.DBG_FILE)
        if len(tmp):
            j = int(''.join(tmp))
            print('jump({})'.format(j), file=Life.DBG_FILE)
            if j > 0:
                for jj in range(j):
                    print('{}'.format(jj), file=Life.DBG_FILE, end=',')
                    self.update(pc=0)
            elif j < 0:
                for jj in range(-1, j-1, -1):
                    print('{}'.format(jj), file=Life.DBG_FILE, end=',')
                    self.undo(pc=0)
            self.printCells('jump({}) done[{}] undone[{}] END'.format(j, len(self.done), len(self.undone)))

    def goTo(self):
        gg, tmp = '', []
        while len(gg) != 32:
            gg = getwch()
            if gg != ' ' and '0' <= gg <= '9': tmp.append(gg)
            else: break
        if len(tmp):
            g = int(''.join(tmp))

    def undo(self, pc=1):
        if len(self.done) > 0:
            self.cells = self.done.pop(-1)
            self.undone.append(self.cells)
            if len(self.done) > 0: self.cells = self.done[-1]
            if pc == 1: self.printCells('undo() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))

    def redo(self):
        if len(self.undone) > 0:
            self.cells = self.undone.pop(-1)
            self.done.append(self.cells)
            if len(self.undone) > 0: self.cells = self.undone[-1]
            self.printCells('redo() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))

    def update(self, pc=1):
        self.updateCells()
        self.done.append(self.cells)
#        if pc == 1: self.printCells('update() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))
        if pc == 1: self.printCells2()
        
    def updateCells(self, dbg=0):
        cells = []
        for r in range(len(self.cells)):
            tmp = []
            for c in range(len(self.cells[0])): #r
                n = len(self.getNeighbors(r, c))
                if self.isAlive(r, c) == 1:
                    if n == 2 or n == 3: tmp.append(1)
                    else:                tmp.append(0)
                elif n == 3:             tmp.append(1)
                else:                    tmp.append(0)
            cells.append(tmp)
        self.cells = cells

    def printCells2(self):
        for r in range(self.nRows):
            for c in range(self.nCols): #r
                if self.cells[r][c] == 0:
                    self.prints(' ', r+1, c+1, self.C_DEAD)
#                    print(' ', file=Life.DBG_FILE, end='')
                else:
                    self.prints(' ', r+1, c+1, self.C_ALIVE)
#                    print('X', file=Life.DBG_FILE, end='')
#            print(file=Life.DBG_FILE)
#        print(file=Life.DBG_FILE)

    def printCells(self, reason=''):
        exit()
        liveCount = 0
        if len(reason) > 0: print(reason, file=Life.DBG_FILE)
        for r in range(len(self.cells)):
            for c in range(len(self.cells[0])): #r
                if self.cells[r][c] == 0:
                    self.prints(' ', r, c, self.C_DEAD, self.STYLES['NORMAL'])
                    print(' ', file=Life.DBG_FILE, end='')
                else:
                    self.prints(' ', r, c, self.C_ALIVE, self.STYLES['BRIGHT'])
                    print('X', file=Life.DBG_FILE, end='')
                    liveCount += 1
            print(file=Life.DBG_FILE)
        print(file=Life.DBG_FILE)
        self.printStats(liveCount)

    def getNeighbors(self, r, c, dbg=0):
        n = []
        if dbg: print('({},{})'.format(r, c), file=Life.DBG_FILE, end=' ')
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    if r+i >= 0 and c+j >= 0 and r+i < len(self.cells) and c+j < len(self.cells[0]):
                        if self.cells[r+i][c+j] != 0: n.append(1)
                        if dbg: print('({},{}) {} {}'.format(i, j, len(n), n), file=Life.DBG_FILE)
        return n

    def isAlive(self, r, c, dbg=0):
        if self.cells[r][c] == 0: return 0
        return 1

    def printStats(self, liveCount):
        self.stats['S_COUNT'] = liveCount
        self.stats['S_SIZE'] = len(self.cells) * len(self.cells[0]) #r
        if liveCount != 0: self.stats['S_INV_DNSTY'] = self.stats['S_SIZE'] // self.stats['S_COUNT']
        self.prints('{} {} {} {}'.format(len(self.done)-1, self.stats['S_COUNT'], self.stats['S_SIZE'], self.stats['S_INV_DNSTY']), len(self.cells), 0, self.C_TEXT, self.STYLES['NORMAL'])
        print('{} {} {} {}'.format(len(self.done)-1, self.stats['S_COUNT'], self.stats['S_SIZE'], self.stats['S_INV_DNSTY']), file=Life.DBG_FILE)

    def prints(self, s, row, col, style, dbg=0):
#        if dbg: print('{}'.format(s), file=Life.DBG_FILE, end='')
        print(Life.CSI + style + Life.CSI + '{};{}H{}'.format(row, col, s), end='')

    def getColor(self, FG, BG):
        return '3' + self.COLORS[FG] + ';4' + self.COLORS[BG] + 'm'

def main():
    life = Life()
    life.run()
    
if __name__ == "__main__":
    main()

'''
Colorama doc
ESC [ y;x H     # position cursor at x across, y down
ESC [ y;x f     # position cursor at x across, y down
ESC [ n A       # move cursor n lines up
ESC [ n B       # move cursor n lines down
ESC [ n C       # move cursor n characters forward
ESC [ n D       # move cursor n characters backward
'''
