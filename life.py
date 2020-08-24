import pyglet
import pyglet.gl
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key
import sys, os, copy
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
        print('\n:BGN: init()', file=DBG_FILE)
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
        self.nCols = 175#383#79#140#11
        self.nRows = 115#235#43 #80 #7
        self.cellW = 10
        self.cellH = 10
        self.width  = self.nCols * self.cellW + 4
        self.height = self.nRows * self.cellH + 4
        self.fullScreen = False
        self.shapeKey = 'TestMe'
        self.inName = 'lexicon-no-wrap.txt'
        print('argMap={}'.format(self.argMap), file=DBG_FILE)
        if 'c' in self.argMap and len(self.argMap['c']) > 0:
            self.nCols = int(self.argMap['c'][0])
        if 'r' in self.argMap and len(self.argMap['r']) > 0:
            self.nRows = int(self.argMap['r'][0])
        if 's' in self.argMap and len(self.argMap['s']) > 0:
            self.shapeKey = self.argMap['s'][0]
        if 'f' in self.argMap and len(self.argMap['f']) > 0:
            self.inName = self.argMap['f'][0]
        print('shapeKey={}'.format(self.shapeKey), file=DBG_FILE)
        print('inName={}'.format(self.inName), file=DBG_FILE)
        print('nCols={}'.format(self.nCols), file=DBG_FILE)
        print('nRows={}'.format(self.nRows), file=DBG_FILE)
        print('cellW={}'.format(self.cellW), file=DBG_FILE)
        print('cellH={}'.format(self.cellH), file=DBG_FILE)
        print('width={}'.format(self.width), file=DBG_FILE)
        print('height={}'.format(self.height), file=DBG_FILE)
        self.window = window
        if self.fullScreen == False: self.window.set_size(self.width, self.height)
        else: window.set_fullscreen()
        self.window.set_visible()
        self.batch = pyglet.graphics.Batch()
        (self.data, self.cells, self.lines) = self.grid(c=self.nCols, r=self.nRows, w=self.cellW, h=self.cellH, p=1, q=0)
        self.parse()
        self.addShape(self.shapeKey)
        self.updateStats()
        print(':END: init()\n', file=DBG_FILE)

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

    def addShape(self, key):
        p, q = 0, -20
        c = int(self.nCols/2 - 1 - p)
        r = int(self.nRows/2 - 1 + q)
        v = self.shapes[key]
        data = v[0]
        w, h = len(data[0]), len(data)
        a = w * h
        txt = 'addShape() c={} r={} key={} [{}x{}={}]'.format(c, r, key, w, h, a)
        print('\n:BGN: {}'.format(txt), file=DBG_FILE)
        print('info1={}'.format(v[1]), file=DBG_FILE)
        if v[2]: print('info2={}'.format(v[2]), file=DBG_FILE)
        if v[3]: print('info3={}'.format(v[3]), file=DBG_FILE)
        if data is None: return
        for j in range(h):
            print('    ', file=DBG_FILE, end='')
            for i in range(w):
                print('{}'.format(data[j][i]), file=DBG_FILE, end='')
                if data[j][i] == 0: self.cells[r-j][c+i].color = self.DEAD
                else:
                    self.pop += 1
                    self.cells[r-j][c+i].color = self.ALIVE
                self.data[r-j][c+i] = int(data[j][i])
            print(file=DBG_FILE)
        self.done.append(self.data)
        self.printData('{}'.format(txt))
        print(  ':END: {}\n'.format(txt), file=DBG_FILE)

    def addShape2(self, c=None, r=None):
        if c is None: c = int(self.nCols/2)
        if r is None: r = int(self.nRows/2)
        print('\n:BGN: addShape2() c={} r={}'.format(c, r))
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
        self.printData('addShape2() c={} r={}'.format(c, r))
        print(':END: addShape2() c={} r={}\n'.format(c, r))

    def addCell(self, c, r):
        print('\n:BGN: addCell() c={} r={} data[r][c]={}'.format(c, r, self.data[r][c]), file=DBG_FILE)
        if self.data[r][c] == 0: self.pop += 1
        self.data[r][c] = 1
        self.cells[r][c].color = self.ALIVE
        print(':END: addCell() c={} r={} data[r][c]={}\n'.format(c, r, self.data[r][c]), file=DBG_FILE)

    def update(self, dbg=1):
        self.updateDataCells()
        self.done.append(self.data)
        self.updateStats()
        if dbg: self.printData('update() done[{}] undone[{}]'.format(len(self.done), len(self.undone)))

    def updateDataCells_OLD(self, dbg=1):
        data = []
        for r in range(self.nRows):
            tmp = []
            for c in range(self.nCols):
                n = self.getNeighborCount(c, r)
                if dbg:
                    if n == 0: print(' ', file=DBG_FILE, end='')
                    else: print('{}'.format(n), file=DBG_FILE, end='')
                if self.data[r][c] == 1: #                if self.isAlive(r, c) == 1:
                    if n == 2 or n == 3: tmp.append(1); self.cells[r][c].color = self.ALIVE
                    else:                tmp.append(0); self.cells[r][c].color = self.DEAD
                elif n == 3:             tmp.append(1); self.cells[r][c].color = self.ALIVE
                else:                    tmp.append(0); self.cells[r][c].color = self.DEAD
            if dbg: print(file=DBG_FILE)
            data.append(tmp)
        self.data = data

    def updateDataCells(self, dbg=1):
        data = copy.deepcopy(self.data)
        for r in range(self.nRows-1, -1, -1):
            for c in range(self.nCols):
                self.updateDataCell(c, r, data)
            if dbg: print(file=DBG_FILE)
        self.data = data

    def updateDataCell(self, c, r, data, dbg=1):
        n = self.getNeighborCount(c, r)
        if dbg:
            if n == 0: print(' ', file=DBG_FILE, end='')
            else: print('{}'.format(n), file=DBG_FILE, end='')
        if self.data[r][c] == 1: #                if self.isAlive(r, c) == 1:
            if n == 2 or n == 3:
                data[r][c] = 1
                self.cells[r][c].color = self.ALIVE
            else:
                data[r][c] = 0
                self.cells[r][c].color = self.DEAD
                self.pop -= 1
        elif n == 3:
            data[r][c] = 1
            self.cells[r][c].color = self.ALIVE
            self.pop += 1
        else:
            data[r][c] = 0
            self.cells[r][c].color = self.DEAD

    def getNeighborCount(self, c, r, dbg=0):
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
        print('\n:BGN: printData({}) data[{}x{}={:,}]'.format(reason, self.nRows, self.nCols, self.nRows*self.nCols), file=DBG_FILE)
        for r in range(self.nRows-1, -1, -1):
            for c in range(self.nCols):
                if self.data[r][c] == 0:
                    print(' ', file=DBG_FILE, end='')
                else:
                    print('X', file=DBG_FILE, end='')
            print(file=DBG_FILE)
        print(':END: printData({}) data[{}x{}={:,}]\n'.format(reason, self.nRows, self.nCols, self.nRows*self.nCols), file=DBG_FILE)

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
        print('\n:BGN: parse()', file=DBG_FILE)
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
                        if dbg: print('info2={}'.format(info2), file=DBG_FILE)
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
        print(':END: parse() len(shapes)={}\n'.format(len(self.shapes)), file=DBG_FILE)
        if dbg: self.printShapes()

    def printShapes(self):
        print('\n:BGN printShapes() len(shapes)={}'.format(len(self.shapes)), file=DBG_FILE)
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
        print(':END: printShapes() len(shapes)={} len(noneKeys)={} len(valKeys)={}\n'.format(len(self.shapes), len(noneKeys), len(dataKeys)), file=DBG_FILE)

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
#        if symbol < 256: print('on_key_press() symbol={}({}) modifiers={}'.format(symbol, chr(symbol), modifiers), flush=True)
#        else: print('on_key_press() symbol={} modifiers={}'.format(symbol, modifiers), flush=True)
        if   symbol == key.Q and modifiers == key.MOD_CTRL: exit()
        elif symbol == key.SPACE:                           self.update()
        elif symbol == key.ENTER:                           self.run()
        elif symbol == key.BACKSPACE:                       self.stop()
        elif symbol == key.F and modifiers == key.MOD_CTRL: self.toggleFullScreen()

#pyglet.window.mouse.LEFT
#pyglet.window.mouse.MIDDLE
#pyglet.window.mouse.RIGHT
    def on_mouse_release(self, x, y, button, modifiers):
#        print('on_mouse_release() x={} y={} b={} m={}'.format(x, y, button, modifiers), flush=True)#, file=DBG_FILE)
        r, c = int(y/self.cellH), int(x/self.cellW)
        print('on_mouse_release() x={} y={} b={} m={} d[{}][{}]={}'.format(x, y, button, modifiers, r, c, self.data[r][c]), file=DBG_FILE)
        if  self.data[r][c] == 0: self.addCell(c, r)
        else:
            self.data[r][c] = 0
            self.cells[r][c].color = self.DEAD

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        print('on_resize() width={} height={}'.format(width, height), file=DBG_FILE)

####################################################################################################
@window.event
def on_key_press(symbol, modifiers): life.on_key_press(symbol, modifiers)

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
