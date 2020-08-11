import os
import sys
import msvcrt
getwch = msvcrt.getwch
import colorama

class Life(object):
    ESC = '\033'
    CSI = '\033\133'
    DBG_NAME = "Life.dbg"
    DBG_FILE = open(DBG_NAME, "w")

    def __init__(self):
        colorama.init(autoreset=True)
        Life.clearScreen()
        self.COLORS = { 'BLACK':'0', 'RED':'1', 'GREEN':'2', 'YELLOW':'3', 'BLUE':'4', 'MAGENTA':'5', 'CYAN':'6', 'WHITE':'7' }
        self.STYLES = {'NORMAL':'22;', 'BRIGHT':'1;'}
        self.C_ALIVE = self.getColor('WHITE', 'YELLOW')
        self.C_DEAD  = self.getColor('RED', 'BLACK')
        self.cells = []
        nRows, nCols = 10, 20 # get rid of these?
        for r in range(nRows):
            tmp = []
            for c in range(nCols):
                tmp.append(0)
            self.cells.append(tmp)
        self.cells[3][4] = 1
        self.cells[4][3] = 1
        self.cells[4][4] = 1
        self.cells[4][5] = 1
        self.cells[5][5] = 1
        self.printCells()

    def getColor(self, FG, BG):
        return '3' + self.COLORS[FG] + ';4' + self.COLORS[BG] + 'm'

    def run(self):
        b, c, s = 0, '', []
        while True:
            c = getwch()
            b = ord(c)
            if b == 81 or b == 113: break
            if b == 13: self.update()
#            print('{}'.format(c), end=' ', flush=True)

    def update(self):
        self.updateCells()
        self.printCells()
        
    def updateCells(self, dbg=0):
        cells = []
        for r in range(len(self.cells)):
            tmp = []
            for c in range(len(self.cells[0])):
                n = len(self.getNeighbors(r, c))
                if self.isAlive(r, c) == 1:
                    if n == 2 or n == 3: tmp.append(1)
                    else:                tmp.append(0)
                elif n == 3:             tmp.append(1)
                else:                    tmp.append(0)
            cells.append(tmp)
        self.cells = cells

    def printCells(self):
        for r in range(len(self.cells)):
            for c in range(len(self.cells[0])):
                if self.cells[r][c] == 0:
                    self.prints(' ', r, c, self.C_DEAD, self.STYLES['NORMAL'])
                else:
                    self.prints(' ', r, c, self.C_ALIVE, self.STYLES['BRIGHT'])
                print('{}'.format(self.cells[r][c]), file=Life.DBG_FILE, end='')
            print(file=Life.DBG_FILE)
        print(file=Life.DBG_FILE)

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

    def prints(self, s, row, col, style, bstyle, dbg=0):
        if dbg: print('{}'.format(s), file=Life.DBG_FILE, end='')
        print(Life.CSI + bstyle + style + Life.CSI + '{};{}H{}'.format(row + 1, col + 1, str(s)), end='')

    @staticmethod
    def clearScreen(arg=2, file=None, reason=None, dbg=0):
        if dbg: print('clearScreen() arg={} file={} reason={}'.format(arg, file, reason), file=Life.DBG_FILE)
        print(Life.CSI + '{}J'.format(arg), file=file)

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
