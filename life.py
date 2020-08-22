import pyglet
import pyglet.gl
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key
import sys, os
sys.path.insert(0, os.path.abspath('../lib'))
import cmdArgs

#event_logger = pyglet.window.event.WindowEventLogger()
#window.push_handlers(event_logger)
#window = pyglet.window.Window(resizable=True, visible=False) #move to Life class? #fullscreen=True

screen_number = 0
display = pyglet.canvas.get_display()
screen = display.get_screens()[screen_number]
window = pyglet.window.Window(resizable=True, screen=screen)

class Life(object):
    def __init__(self, window):
        self.ALIVE = (100, 192, 100)
        self.DEAD = (90, 16, 26)
        self.DATA_SET = set('.*')
        self.XLATE = str.maketrans('.*', '01')
        print('DATA_SET={} XLATE={}'.format(self.DATA_SET, self.XLATE), file=DBG_FILE)
        self.pop = 0
        self.done = []
        self.undone = []
        self.shapes = {}
        self.stats = {}
        self.argMap = {}
        self.argMap = cmdArgs.parseCmdLine(dbg=1)
        self.nRows = 115#235#43 #80 #7
        self.nCols = 175#383#79#140#11
        self.shapeKey = 'TestMe'
        self.cellH = 10
        self.cellW = 10
        self.height = self.nRows * self.cellH + 4
        self.width  = self.nCols * self.cellW + 4
        self.fullScreen = False
        self.inName = 'lexicon-no-wrap.txt'
        print('argMap={}'.format(self.argMap), file=DBG_FILE)
        if 'f' in self.argMap and len(self.argMap['f']) > 0:
            self.inName = self.argMap['f'][0]
        print('inName={}'.format(self.inName), file=DBG_FILE)
        if 'r' in self.argMap and len(self.argMap['r']) > 0:
            self.nRows = int(self.argMap['r'][0])
        print('nRows={}'.format(self.nRows), file=DBG_FILE)
        if 'c' in self.argMap and len(self.argMap['c']) > 0:
            self.nCols = int(self.argMap['c'][0])
        print('nCols={}'.format(self.nCols), file=DBG_FILE)
        if 's' in self.argMap and len(self.argMap['s']) > 0:
            self.shapeKey = self.argMap['s'][0]
        print('shapeKey={}'.format(self.shapeKey), file=DBG_FILE)
        print('cellH={}'.format(self.cellH), file=DBG_FILE)
        print('cellW={}'.format(self.cellW), file=DBG_FILE)
        print('height={}'.format(self.height), file=DBG_FILE)
        print('width={}'.format(self.width), file=DBG_FILE)
        print(file=DBG_FILE)
        self.window = window
        if self.fullScreen == False: self.window.set_size(self.width, self.height)
        else: window.set_fullscreen()
        self.window.set_visible()
        self.batch = pyglet.graphics.Batch()
        print('batch={}'.format(self.batch), file=DBG_FILE)
        (self.data, self.cells, self.lines) = self.grid(c=self.nCols, r=self.nRows, w=self.cellW, h=self.cellH, p=1, q=0)
        self.parse()
        self.addShape(self.shapeKey)
        self.updateStats()

    def grid(self, c=100, r=70, w=10, h=10, p=0, q=0): #c=nCols r=nRows w=cellW h=cellH p=xOff q yOff
        data, cells, lines = [], [], []
        for j in range(r):
            tmp1, tmp2 = [], []
            for i in range(c):
                tmp1.append(0)
                tmp2.append(shapes.Rectangle(i*w+p, j*h+q, w, h, color=self.DEAD, batch=self.batch))
            data.append(tmp1)
            cells.append(tmp2)
        for i in range(c+1):
            if i%10 == 0: lines.append(shapes.Line(i*w+p, q, i*w+p, r*h+q, width=1, color=(255, 255, 255), batch=self.batch))
            else:         lines.append(shapes.Line(i*w+p, q, i*w+p, r*h+q, width=1, color=(255, 30, 30), batch=self.batch))
        for j in range(r+1):
            if j%10 == 0: lines.append(shapes.Line(p, j*h+q, c*w+p, j*h+q, width=1, color=(255, 255, 255), batch=self.batch))
            else:         lines.append(shapes.Line(p, j*h+q, c*w+p, j*h+q, width=1, color=(255, 30, 30), batch=self.batch))
        return (data, cells, lines)

    def addShape2(self, c=None, r=None):
        if c is None: c = int(self.nCols/2)
        if r is None: r = int(self.nRows/2)
        self.data[r+1][c+0] = 1
        self.data[r+0][c-1] = 1
        self.data[r+0][c+0] = 1
        self.data[r+0][c+1] = 1
        self.data[r-1][c+1] = 1
        self.cells[r+1][c+0].color = self.ALIVE
        self.cells[r+0][c-1].color = self.ALIVE
        self.cells[r+0][c+0].color = self.ALIVE
        self.cells[r+0][c+1].color = self.ALIVE
        self.cells[r-1][c+1].color = self.ALIVE
        self.printData('addShape2() r={} c={}'.format(r, c))

    def addShape(self, key):
        p, q = 0, -20
        c = int(self.nCols/2 - 1 - p)
        r = int(self.nRows/2 - 1 + q)
        v = self.shapes[key]
        data = v[0]
        print('addShape({},{}) key={}'.format(r, c, key), file=DBG_FILE)
        print('addShape({},{}) v={}'.format(r, c, v), file=DBG_FILE)
        if data is None: return
        for j in range(len(data)):
            print('[{}]{}'.format(j, data[j]), file=DBG_FILE)
            for i in range(len(data[j])):
                if data[j][i] == 0: self.cells[r-j][c+i].color = self.DEAD
                else:
                    self.pop += 1
                    self.cells[r-j][c+i].color = self.ALIVE
                self.data[r-j][c+i] = int(data[j][i])
        self.done.append(self.data)
        self.printData('addShape() r={} c={}'.format(r, c))

    def update(self, dbg=1):
        self.updateDataCells()
        self.done.append(self.data)
        self.updateStats()
        if dbg: self.printData('update() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))

    def updateDataCells(self, dbg=0):
        data, self.pop = [], 0
        for r in range(self.nRows):
            tmp = []
            for c in range(self.nCols):
                n = self.getNeighbors(r, c)
                if dbg: print('{}'.format(n), file=DBG_FILE, end='')
                if self.isAlive(r, c) == 1:
                    self.pop += 1
                    if n == 2 or n == 3: tmp.append(1); self.cells[r][c].color = self.ALIVE
                    else:                tmp.append(0); self.cells[r][c].color = self.DEAD
                elif n == 3:             tmp.append(1); self.cells[r][c].color = self.ALIVE
                else:                    tmp.append(0); self.cells[r][c].color = self.DEAD
            if dbg: print(file=DBG_FILE)
            data.append(tmp)
        self.data = data

    def getNeighbors(self, r, c, dbg=0):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                if i != 0 or j != 0:
                    if r+j >= 0 and c+i >= 0 and r+j < self.nRows and c+i < self.nCols:
                        if self.data[r+j][c+i] != 0: n += 1
#                        if dbg: print('({},{},{})'.format(r+j, c+i, n), file=DBG_FILE, end=' ')
#            if dbg: print(file=DBG_FILE)
#        if dbg: print('({},{})[{}]'.format(r, c, n), file=DBG_FILE, end=' ')
        return n

    def isAlive(self, r, c, dbg=0):
        if self.data[r][c] == 0: return 0
        return 1

    def printData(self, reason=''):
#        print('printData({}) data[{}x{}={}]'.format(reason, len(self.data), len(self.data[0]), len(self.data)*len(self.data[0])), file=DBG_FILE)
        print('printData({}) data[{}x{}={}]'.format(reason, self.nRows, self.nCols, self.nRows*self.nCols), file=DBG_FILE)
        for r in range(self.nRows-1, -1, -1):
            for c in range(self.nCols):
                if self.data[r][c] == 0:
                    print(' ', file=DBG_FILE, end='')
                else:
                    print('X', file=DBG_FILE, end='')
            print(file=DBG_FILE)
        print(file=DBG_FILE)

    def updateStats(self):
        assert self.pop >= 0
        assert self.nRows == len(self.cells)
        assert self.nCols == len(self.cells[0])
        self.stats['S_POP'] = self.pop
        self.stats['S_GEN'] = len(self.done) - 1
        self.stats['S_AREA'] = self.nRows * self.nCols
        self.stats['S_DENS'] = 100 * self.stats['S_POP'] / self.stats['S_AREA']
        if self.pop > 0: self.stats['S_IDENS'] = int(self.stats['S_AREA'] / self.stats['S_POP'])
        else:            self.stats['S_IDENS'] = -1
        self.displayStats()

    def displayStats(self, dbg=1):
        txt = 'Gen={} Pop={} Area={:,} Dens={:6.3}% Idens={:,}'.format(self.stats['S_GEN'], self.stats['S_POP'], self.stats['S_AREA'], self.stats['S_DENS'], self.stats['S_IDENS'])
        self.window.set_caption(txt)
        if dbg: print('{}'.format(txt), file=DBG_FILE)

    def parse(self, dbg=0):
        print('parse(BGN)', file=DBG_FILE)
        data, key, state = [], '', 0
        info1 = info2 = info3 = ''
        with open(self.inName, 'r') as self.inFile:
            for line in self.inFile:
                line = line.strip()
                if len(line) > 0:
                    dataSet = set(line)
                    if line[0] == ':':
                        p = line.find(':', 1)
                        if p != -1:
                            if state == 2:
                                self.shapes[key][0] = data
                                if dbg:
                                    print('key=[{}] size=[{} x {}={}]]'.format(key, len(data), len(data[0]), len(data)*len(data[0])), file=DBG_FILE)
                                    print('info1=[{}]\ninfo2=[{}]\ninfo3=[{}]'.format(info1, info2, info3), file=DBG_FILE)
                                info1 = info2 = info3 = ''
                            data = []
                            key = line[1:p]
                            info1 = line[p+1:].strip()
                            v = [None, info1, None, None]
                            self.shapes[key] = v
                            state = 1
                            if dbg: print('[{:.^50}] state={} v0={} v3={} v2={} v1={}'.format(key, state, v[0], v[3], v[2], v[1]), file=DBG_FILE)
                    elif dataSet >  self.DATA_SET:
                        info2 += line
                        if dbg: print('#info2={}'.format(info2), file=DBG_FILE)
                    elif dataSet <= self.DATA_SET:
                        line = line.translate(self.XLATE)
                        tmp = []
                        for c in line: tmp.append(int(c)) #list comprehension?
                        data.append(tmp)
                        state = 2
                        if dbg: print('    {}'.format(line), file=DBG_FILE)
                    elif state == 2:
                        info3 += line
                        self.shapes[key][0] = data
                        state = 0
                        if dbg:
                            print('key=[{}] size=[{} x {}={}]]'.format(key, len(data), len(data[0]), len(data)*len(data[0])), file=DBG_FILE)
                            print('info1=[{}]\ninfo2=[{}]\ninfo3=[{}]'.format(info1, info2, info3), file=DBG_FILE)
                        data = []
        print('parse(END) len(shapes)={}'.format(len(self.shapes)), file=DBG_FILE)
        if dbg: self.printShapes()

    def printShapes(self):
        print('printShapes(BGN) len={}'.format(len(self.shapes)), file=DBG_FILE)
        noneKeys, dataKeys = [], []
        for k in self.shapes:
            v = self.shapes[k]
            data = v[0]
            if data != None:
                print('[{}]'.format(k), file=DBG_FILE)
                dataKeys.append(k)
#                for d in data:
#                    print(d, file=DBG_FILE)
            else: noneKeys.append(k)
        for k in noneKeys: print('noneKeys=[{}]\ninfo1=[{}]\ninfo2=[{}]\ninfo3=[{}]'.format(k, self.shapes[k][1], self.shapes[k][2], self.shapes[k][3]), file=DBG_FILE)
        for k in dataKeys: print('dataKeys=[{}] size=[{} x {}={}]'.format(k, len(self.shapes[k][0]), len(self.shapes[k][0][0]), len(self.shapes[k][0])*len(self.shapes[k][0][0])), file=DBG_FILE)
        print('printShapes(END) len(shapes)={} len(noneKeys)={} len(valKeys)={}'.format(len(self.shapes), len(noneKeys), len(dataKeys)), file=DBG_FILE)

    def toggleFullScreen(self):
        if   self.fullScreen == True: self.fullScreen = False
        else:                         self.fullScreen = True
        self.window.set_fullscreen(self.fullScreen)

####################################################################################################
    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/120.0)

    def stop(self):
        pyglet.clock.unschedule(self.update)
####################################################################################################

    def on_key_press(self, symbol, modifiers):
        if   symbol == key.Q and modifiers == key.MOD_CTRL: exit()
        elif symbol == key.SPACE:                           self.update()
        elif symbol == key.ENTER:                           self.run()
        elif symbol == key.BACKSPACE:                       self.stop()
        elif symbol == key.F and modifiers == key.MOD_CTRL: self.toggleFullScreen()
        if symbol < 256: print('on_key_press() symbol={}({}) modifiers={}'.format(symbol, chr(symbol), modifiers), flush=True)
        else: print('on_key_press() symbol={} modifiers={}'.format(symbol, modifiers), flush=True)

#pyglet.window.mouse.LEFT
#pyglet.window.mouse.MIDDLE
#pyglet.window.mouse.RIGHT
    def on_mouse_press(self, x, y, button, modifiers):
        pass
#        print('on_mouse_press() x={} y={} button={} modifiers={}'.format(x, y, button, modifiers), file=DBG_FILE)

    def on_mouse_release(self, x, y, button, modifiers):
        print('on_mouse_release() x={} y={} button={} modifiers={}'.format(x, y, button, modifiers), flush=True)#, file=DBG_FILE)
        r, c = int(y/self.cellH), int(x/self.cellW)
        print('on_mouse_release() data[{}][{}]={}'.format(r, c, self.data[r][c]), flush=True)#, file=DBG_FILE)
        if  self.data[r][c] == 0:
            self.data[r][c] = 1
            self.cells[r][c].color = self.ALIVE
        else:
            self.data[r][c] = 0
            self.cells[r][c].color = self.DEAD

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        print('on_resize() width={} height={}'.format(width, height), flush=True)

####################################################################################################
@window.event
def on_key_press(symbol, modifiers): life.on_key_press(symbol, modifiers)

@window.event
def on_mouse_press(x, y, button, modifiers): life.on_mouse_press(x, y, button, modifiers)

@window.event
def on_mouse_release(x, y, button, modifiers): life.on_mouse_release(x, y, button, modifiers)

@window.event
def on_draw(): life.on_draw()

@window.event
def on_resize(width, height): life.on_resize(width, height)
####################################################################################################

if __name__ == "__main__":
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    life = Life(window)
    pyglet.app.run()

'''
import sys, os
sys.path.insert(0, os.path.abspath('../lib'))
import cmdArgs
import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key

class Life(object):
    DBG_NAME = "Life.dbg"
    DBG_FILE = open(DBG_NAME, "w")

    def __init__(self): #147 240 @ 8x8
        self.ALIVE = (100, 192, 100)
        self.DEAD = (90, 16, 26)
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
#        self.clear()
        self.parse()
#        self.addShape('1-2-3')
        self.printCells('init() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))

    def grid(self, n=100, m=70, w=10, h=10, p=0, q=0):
        cells, lines = [], []
        for i in range(n):
            tmp = []
            for j in range(m):
                tmp.append(shapes.Rectangle(i*w+p, j*h+q, w, h, color=DEAD, batch=batch))
            cells.append(tmp)
        for i in range(n+1):
            lines.append(shapes.Line(i*w+p, q, i*w+p, m*h+q, width=1, color=(255, 255, 255), batch=batch))
        for j in range(m+1):
            lines.append(shapes.Line(p, j*h+q, n*w+p, j*h+q, width=1, color=(255, 255, 255), batch=batch))
        return (cells, lines)

    def addShape():
        cells[2][0].color = ALIVE
        cells[0][1].color = ALIVE
        cells[1][1].color = ALIVE
        cells[2][1].color = ALIVE
        cells[1][2].color = ALIVE

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

    def printCells(self, reason=''):
        liveCount = 0
        if len(reason) > 0: print(reason, file=Life.DBG_FILE)
        for r in range(self.nRows):
            for c in range(self.nCols):
                if self.cells[r][c] == 0:
                    print(' ', file=Life.DBG_FILE, end='')
                else:
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
#        self.prints('{} {} {} {}'.format(len(self.done)-1, self.stats['S_COUNT'], self.stats['S_SIZE'], self.stats['S_INV_DNSTY']), len(self.cells), 0, self.C_TEXT, self.STYLES['NORMAL'])
        print('{} {} {} {}'.format(len(self.done)-1, self.stats['S_COUNT'], self.stats['S_SIZE'], self.stats['S_INV_DNSTY']), file=Life.DBG_FILE)

def main():
    life = Life()
#    life.run()
    
if __name__ == "__main__":
    pyglet.app.run()
    main()
'''