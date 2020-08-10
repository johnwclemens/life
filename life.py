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
        self.bStyle = self.STYLES['NORMAL']
        self.C_ALIVE = self.getColor('WHITE', 'YELLOW')
        self.C_DEAD  = self.getColor('RED', 'BLACK')
        self.cells = []
        nRows, nCols = 50, 150 # get rid of these?
        for r in range(nRows):
            tmp = []
            for c in range(nCols):
                tmp.append(0)
            self.cells.append(tmp)
        self.cells[2][2] = 1
        self.cells[2][3] = 1
        self.cells[3][3] = 1

    def getColor(self, FG, BG):
        return '3' + self.COLORS[FG] + ';4' + self.COLORS[BG] + 'm'

    def run(self):
        b, c, s = 0, '', []
        while True:
            self.printCells()
            c = getwch()
            b = ord(c)
            if b == 13: break
#            print('{}'.format(c), end=' ', flush=True)

    def printCells(self, dbg=1):
        if dbg: print('printCells() len(cells)={} len(len(cells)={})'.format(len(self.cells), len(self.cells[0])), file=Life.DBG_FILE)
        for r in range(len(self.cells)):
            for c in range(len(self.cells[r])):
                if self.cells[r][c] == 0:
                    self.prints(' ', r, c, self.C_DEAD)
                else:
                    self.prints(' ', r, c, self.C_ALIVE)
            if dbg: print(file=Life.DBG_FILE)

    def prints(self, s, row, col, style, dbg=1):
        if dbg: print('{}'.format(s), end='', file=Life.DBG_FILE)
        print(Life.CSI + self.bStyle + style + Life.CSI + '{};{}H{}'.format(row + 1, col + 1, str(s)), end='')

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
