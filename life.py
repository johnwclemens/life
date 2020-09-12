import sys, os, copy
sys.path.insert(0, os.path.abspath('C:/Python36/my/lib/pyglet'))
import pyglet
import pyglet.window     as pygwin
import pyglet.window.key as pygwink
sys.path.insert(0, os.path.abspath('C:/Python36/my/lib'))
import cmdArgs

def fri(f): return int(round(f))

class Life(pygwin.Window):
    def __init__(self):
        display = pyglet.canvas.get_display()
        self.screens = display.get_screens()
#        self.auxWin = pygwin.Window(width=900, height=500, resizable=True, screen=self.screens[0], visible=False)
#        self.auxWin.set_visible()
        super().__init__(resizable=True, screen=self.screens[1], visible=False)
        self.MIN, self.NOM, self.MAX = 0, 1, 2
        self.ALIVE      = [(127, 255, 127), (127, 255, 255)]
        self.DEAD       = [(  0,   0,   0), (100,  80, 127)]
        self.MESH       = [(  0,   0,   0), (255,   0,   0), (255, 255, 255)]
        self.DATA_SET   = set('.*')
        self.XLATE      = str.maketrans('.*', '01')
        self.batch      = pyglet.graphics.Batch()
        self.data,        self.cells,      self.clines, self.rlines = [], [], [], []
        self.savedData,   self.savedDone =  [],  []
        self.dispatch,    self.buffer    = None, ''
        self.genx,        self.period    = -1,   1/120
        self.gen,         self.pop       =  0,   0
        self.done,        self.undone    =  [],  []
        self.shapes,      self.stats     =  {},  {}
        self.x,           self.y         =  0,   0
        self.argMap     = cmdArgs.parseCmdLine(dbg=1)
        self.wc         = 101  # 11#101
        self.wr         =  51  # 7#57
        self.ww         = 950  # 1900
        self.wh         = 575  # 1150
        self.cw         = self.ww / self.wc
        self.ch         = self.wh / self.wr
        self.fullScreen = False
        self.getNNCount = self.getNNCountHard
        self.shapeKey   = 'MyShape_1'  # 'TestOddOdd'  # 'Gosper glider gun'
        self.inName     = 'lexicon-no-wrap.txt'
        print('init(BGN) ww={} wh={} wc={} wr={} cw={:6.2f} ch={:6.2f} fullScreen={} getNNCount={} shapeKey={} inName={}'.format(self.ww, self.wh, self.wc, self.wr, self.cw, self.ch, self.fullScreen, self.getNNCount, self.shapeKey, self.inName), file=DBG_FILE)
        print('argMap={}'.format(self.argMap), file=DBG_FILE)
        if 'c' in self.argMap and len(self.argMap['c'])  > 0: self.wc         = int(self.argMap['c'][0])
        if 'r' in self.argMap and len(self.argMap['r'])  > 0: self.wr         = int(self.argMap['r'][0])
        if 'W' in self.argMap and len(self.argMap['W'])  > 0: self.ww         = int(self.argMap['W'][0])
        if 'H' in self.argMap and len(self.argMap['H'])  > 0: self.wh         = int(self.argMap['H'][0])
        if 'w' in self.argMap and len(self.argMap['w'])  > 0: self.cw         = int(self.argMap['w'][0])
        if 'h' in self.argMap and len(self.argMap['h'])  > 0: self.ch         = int(self.argMap['h'][0])
        if 'F' in self.argMap and len(self.argMap['F']) == 0: self.fullScreen = True
        if 'n' in self.argMap and len(self.argMap['n']) == 0: self.getNNCount = self.getNNCountWrap
        if 'k' in self.argMap and len(self.argMap['k'])  > 0: self.shapeKey   = self.argMap['k'][0]
        if 'f' in self.argMap and len(self.argMap['f'])  > 0: self.inName     = self.argMap['f'][0]
        print('wc={}'.format(self.wc), file=DBG_FILE)
        print('wr={}'.format(self.wr), file=DBG_FILE)
        print('ww={}'.format(self.ww), file=DBG_FILE)
        print('wh={}'.format(self.wh), file=DBG_FILE)
        print('cw={:6.2f}'.format(self.cw), file=DBG_FILE)
        print('ch={:6.2f}'.format(self.ch), file=DBG_FILE)
        print('fullScreen={}'.format(self.fullScreen), file=DBG_FILE)
        print('getNNCount={}'.format(self.getNNCount), file=DBG_FILE)
        print('shapeKey={}'.format(self.shapeKey), file=DBG_FILE)
        print('inName={}'.format(self.inName), file=DBG_FILE)
        self.set_size(self.ww, self.wh)
        if self.fullScreen:  self.set_fullscreen(self.fullScreen)
        self.ww, self.wh = self.get_size()
        self.cw = self.ww / self.wc
        self.ch = self.wh / self.wr
        print('init(END) ww={} wh={} wc={} wr={} cw={:6.2f} ch={:6.2f} fullScreen={} getNNCount={} shapeKey={} inName={} tick={}'.format(self.ww, self.wh, self.wc, self.wr, self.cw, self.ch, self.fullScreen, self.getNNCount, self.shapeKey, self.inName, pyglet.clock.tick()), file=DBG_FILE)
        self.addGrid(self.wc, self.wr, self.ww, self.wh)
#        self.addGrid(c=37, r=19) # odd odd
#        self.addGrid(c=20, r=12) # even even
#        self.addGrid(c=20, r=11) # even odd
#        self.addGrid(c=13, r=10) # odd even
        self.set_visible()
        self.parse()
        self.addShape(self.wc//2, self.wr//2, self.shapeKey)
#        self.addShapeA(self.wc//2, self.wr//2)

    def addGrid(self, c, r, ww, wh, dbg=1):
        self.wc, self.wr = c, r
        self.ww, self.wh = ww, wh
        mesh, color = [1, 10, 50], self.DEAD[0]
        p, q = fri(c/2) % mesh[self.MAX], fri(r/2) % mesh[self.MAX]
        w = self.cw = self.ww / self.wc
        h = self.ch = self.wh / self.wr
        x, y = self.x, self.y
        if dbg: print('addGrid(BGN) ww={} wh={} c={} r={} w={:6.2f} h={:6.2f} x={:6.2f} y={:6.2f} p={} q={}'.format(ww, wh, c, r, w, h, x, y, p, q), file=DBG_FILE)
        for j in range(r):
            tmp1, tmp2 = [], []
            for i in range(c):
                tmp1.append(0)
                color = self.DEAD[(i+j)%2]
                s = (pyglet.shapes.Rectangle(fri(i*w+x), fri(j*h+y), fri(w), fri(h), color=color, batch=self.batch))
                s.opacity = 200
                tmp2.append(s)
            self.data.append(tmp1)
            self.cells.append(tmp2)
        for i in range(c+1):
            print('i={:4} w={:6.2f} x={:6.2f} i*w={:7.2f} {:4} i*w+x={:7.2f} {:4}'.format(i, w, x, i*w, fri(i*w), i*w+x, fri(i*w+x)), file=DBG_FILE, end=' ')
            if   (i-p) % mesh[self.MAX] == 0: color = self.MESH[self.MAX]; print('(i-p)%{}={}'.format(mesh[self.MAX], (i-p) % mesh[self.MAX]), file=DBG_FILE)
            elif (i-p) % mesh[self.NOM] == 0: color = self.MESH[self.NOM]; print('(i-p)%{}={}'.format(mesh[self.NOM], (i-p) % mesh[self.NOM]), file=DBG_FILE)
            elif (i-p) % mesh[self.MIN] == 0: color = self.MESH[self.MIN]; print('(i-p)%{}={}'.format(mesh[self.MIN], (i-p) % mesh[self.MIN]), file=DBG_FILE)
            self.clines.append(pyglet.shapes.Line(fri(i*w+x), fri(y), fri(i*w+x), fri(r*h+y), width=1, color=color, batch=self.batch))
        print(file=DBG_FILE)
        for j in range(r+1):
            print('j={:4} h={:6.2f} y={:6.2f} j*h={:7.2f} {:4} j*h+y={:7.2f} {:4}'.format(j, h, y, j*h, fri(j*h), j*h+y, fri(j*h+y)), file=DBG_FILE, end=' ')
            if   (j-q) % mesh[self.MAX] == 0: color = self.MESH[self.MAX]; print('(j-q)%{}={}'.format(mesh[self.MAX], (j-q) % mesh[self.MAX]), file=DBG_FILE)
            elif (j-q) % mesh[self.NOM] == 0: color = self.MESH[self.NOM]; print('(j-q)%{}={}'.format(mesh[self.NOM], (j-q) % mesh[self.NOM]), file=DBG_FILE)
            elif (j-q) % mesh[self.MIN] == 0: color = self.MESH[self.MIN]; print('(j-q)%{}={}'.format(mesh[self.MIN], (j-q) % mesh[self.MIN]), file=DBG_FILE)
            self.rlines.append(pyglet.shapes.Line(fri(x), fri(j*h+y), fri(c*w+x), fri(j*h+y), width=1, color=color, batch=self.batch))
        if dbg: print('addGrid(END) ww={} wh={} c={} r={} w={:6.2f} h={:6.2f} x={:6.2f} y={:6.2f} p={} q={}'.format(ww, wh, c, r, w, h, x, y, p, q), file=DBG_FILE)

    def on_resize(self, width, height, dbg=1):
        super().on_resize(width, height)
        ww = self.ww = width
        wh = self.wh = height
        m, n = 0, 0  # 1, 1
        x, y = self.x, self.y
        if dbg: print('on_resize(BGN) width={} height={} ww={} wh={} wc={} wr={} cw={:6.2f} ch={:6.2f}'.format(width, height, self.ww, self.wh, self.wc, self.wr, self.cw, self.ch), file=DBG_FILE)
        c, r = self.wc, self.wr
        w = self.cw = ww / c
        h = self.ch = wh / r
        if dbg: print('on_resize() ww={} wh={} c={} r={} w={:6.2f} h={:6.2f} x={:6.2f} y={:6.2f} m={} n={}'.format(ww, wh, c, r, w, h, x, y, m, n), file=DBG_FILE)
        for j in range(r):
            for i in range(c):
                self.cells[j][i].position = (fri(i*w+x), fri(j*h+y))
                self.cells[j][i].width    = fri(w)
                self.cells[j][i].height   = fri(h)
        for i in range(c+1):  # len(self.clines)):
            self.clines[i].position = (fri(i*w+x), fri(y), fri(i*w+x), fri(r*h+y))
            if dbg: print('i={:4} w={:6.2f} x={:6.2f} i*w={:7.2f} {:4} i*w+x={:7.2f} {:4}'.format(i, w, x, i*w, fri(i*w), i*w+x, fri(i*w+x)), file=DBG_FILE)
        print(file=DBG_FILE)
        for j in range(r+1):  # len(self.rlines)):
            self.rlines[j].position = (fri(x), fri(j*h+y), fri(c*w+x), fri(j*h+y))
            if dbg: print('j={:4} h={:6.2f} y={:6.2f} j*h={:7.2f} {:4} j*h+y={:7.2f} {:4}'.format(j, h, y, j*h, fri(j*h), j*h+y, fri(j*h+y)), file=DBG_FILE)
        if dbg: print('on_resize(END) width={} height={} ww={} wh={} wc={} wr={} cw={:6.2f} ch={:6.2f}'.format(width, height, self.ww, self.wh, self.wc, self.wr, self.cw, self.ch), file=DBG_FILE)

    def addShape(self, c, r, key='MyShape_1'):
        v = self.shapes[key]
        data = v[0]
        w, h = len(data[0]), len(data)
        cc = c - w//2
        rr = r + h//2
        a = w * h
        txt = 'wc={} wr={} c={} r={} cc={} rr={} [{}x{}={}]'.format(self.wc, self.wr, c, r, cc, rr, w, h, a)
        print('addShape(BGN) {}'.format(txt), file=DBG_FILE)
        print('info1={}'.format(v[1]), file=DBG_FILE)
        if v[2]: print('info2={}'.format(v[2]), file=DBG_FILE)
        if v[3]: print('info3={}'.format(v[3]), file=DBG_FILE)
        if data is None: return  # print something?
        for j in range(h):
            print('    ', file=DBG_FILE, end='')
            for i in range(w):
                print('{}'.format(data[j][i]), file=DBG_FILE, end='')
                if data[j][i] == 1: self.addCell(cc+i, rr-j)
            print(file=DBG_FILE)
        self.printData(self.data, 'addShape()')
        self.updateStats()
        print('addShape(END) {}'.format(txt), file=DBG_FILE)

    def addShapeA(self, c, r, dbg=1):  # checkerboard
        if dbg: print('addShapeA(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[j])):
                if (i+j) % 2: self.cells[j][i].color = self.DEAD[(i+j)%2]
                else:         self.addCell(i, j)
        if dbg: self.printData(self.data, 'addShapeA() c={} r={}'.format(c, r))
        if dbg: print('addShapeA(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShapeB(self, c, r, dbg=1):  # odd odd
        if dbg: print('addShapeB(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        self.addCell(c,   r+1)
        self.addCell(c-1, r)
        self.addCell(c,   r)
        self.addCell(c+1, r)
        self.addCell(c+1, r-1)
        if dbg: self.printData(self.data, 'addShapeB() c={} r={}'.format(c, r))
        if dbg: print('addShapeB(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addCell(self, c, r, dbg=0):
        if dbg: print('\naddCell(BGN) c={} r={} data[r][c]={} pop={}'.format(c, r, self.data[r][c], self.pop), file=DBG_FILE)
        if self.data[r][c] == 0: self.pop += 1
        self.data[r][c] = 1
        self.cells[r][c].color = self.ALIVE[0]
        if dbg: print(  'addCell(END) c={} r={} data[r][c]={} pop={}'.format(c, r, self.data[r][c], self.pop), file=DBG_FILE)

    def updateDataCells(self):
        data = copy.deepcopy(self.data)
        for r in range(self.wr-1, -1, -1):
            for c in range(self.wc):
                self.updateDataCell(c, r, data)
        self.data = data

    def updateDataCell(self, c, r, data, dbg=0):
        n = self.getNNCount(c, r)
        if dbg:
            if n == 0: print(' ', file=DBG_FILE, end='')
            else: print('{}'.format(n), file=DBG_FILE, end='')
        if self.data[r][c] == 1:
            if n == 2 or n == 3: data[r][c] = 1; self.cells[r][c].color = self.ALIVE[0]
            else:                data[r][c] = 0; self.cells[r][c].color = self.DEAD[(r+c)%2]; self.pop -= 1
        elif n == 3:             data[r][c] = 1; self.cells[r][c].color = self.ALIVE[0];      self.pop += 1
        else:                    data[r][c] = 0; self.cells[r][c].color = self.DEAD[(r+c)%2]

    def updateStats(self):
        assert self.gen >= 0
        assert self.pop >= 0
        assert self.wr  == len(self.cells)
        assert self.wc  == len(self.cells[0])
        self.stats['S_GEN']  = self.gen
        self.stats['S_POP']  = self.pop
        self.stats['S_AREA'] = self.wr * self.wc
        self.stats['S_DENS'] = 100 * self.stats['S_POP'] / self.stats['S_AREA']
        if self.stats['S_POP'] > 0:  self.stats['S_IDENS'] = self.stats['S_AREA'] / self.stats['S_POP']
        else:                        self.stats['S_IDENS'] = -1.0
        self.stats['S_FPS']  = pyglet.clock.get_fps()
        if self.stats['S_FPS'] > 0:  self.stats['S_IFPS'] = 1 / self.stats['S_FPS']
        else:                        self.stats['S_IFPS'] = -1.0
        self.displayStats()

    def removeCell(self, c, r, dbg=0):
        if dbg: print('removeCell(BGN) c={} r={} data[r][c]={}'.format(c, r, self.data[r][c]), file=DBG_FILE)
        if self.data[r][c] == 1: self.pop -= 1
        self.data[r][c] = 0
        self.cells[r][c].color = self.DEAD[(r+c)%2]
        if dbg: print('removeCell(END) c={} r={} data[r][c]={}'.format(c, r, self.data[r][c]), file=DBG_FILE)

    def saveShape(self):
        print('saveShape(BGN)', file=DBG_FILE)
        self.savedData = copy.deepcopy(self.data)
        self.savedDone = copy.deepcopy(self.done)
        print('saveShape(END)', file=DBG_FILE)

    def recallShape(self):
        print('recallShape(BGN) current pop={}'.format(self.pop), file=DBG_FILE)
        self.calcPop()
        self.done = copy.deepcopy(self.savedDone)
        for r in range(len(self.savedData)):
            for c in range(len(self.savedData[0])):
                if self.savedData[r][c] == 1: self.addCell(c, r)
                else:                         self.removeCell(c, r)
        self.printData(self.data, 'recallShape()')
        self.updateStats()
        print('recallShape(END) recalled pop={}'.format(self.pop), file=DBG_FILE)

    def calcPop(self, dbg=0):
        if dbg: print('calcPop(BGN) pop={}'.format(self.pop), file=DBG_FILE)
        self.pop = 0
        for r in range(self.wr):
            for c in range(self.wc):
                if self.data[r][c] == 1: self.pop += 1
        if dbg: print('calcPop(END) pop={}'.format(self.pop), file=DBG_FILE)

    def parse(self, dbg=0):
        print('parse(BGN)', file=DBG_FILE)
        data, key, state = [], '', 0
        info1 = info2 = info3 = ''
        with open(self.inName, 'r') as inFile:
            for line in inFile:
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
                                info2 = info3 = ''
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
                        for c in line: tmp.append(int(c))  # list comprehension?
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

    def getNNCountHard(self, c, r):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                n += self.data[(r+j+self.wr)%self.wr][(c+i+self.wc)%self.wc]
        n -= self.data[r][c]
        return n

    def getNNCountWrap(self, c, r):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                if 0 <= r + j < self.wr and 0 <= c + i < self.wc:
                    n += self.data[r+j][c+i]
        n -= self.data[r][c]
        return n

    def displayStats(self, dbg=1):
        txt = 'Gen={} Pop={} Area={:,} [{}x{}] done={} undone={} Dens={:6.3}% IDens={:7,.0f} FPS={:7,.0f} IFPS={:6.3}'.\
            format(self.stats['S_GEN'], self.stats['S_POP'], self.stats['S_AREA'], self.wc, self.wr, len(self.done), len(self.undone),
                   self.stats['S_DENS'], self.stats['S_IDENS'], self.stats['S_FPS'], self.stats['S_IFPS'])
        self.set_caption(txt)
        if dbg: print('{}'.format(txt), file=DBG_FILE)

    def printShapes(self):
        print('printShapes(BGN) len(shapes)={}'.format(len(self.shapes)), file=DBG_FILE)
        noneKeys, dataKeys = [], []
        for k in self.shapes:
            v = self.shapes[k]
            data = v[0]
            if data is not None:
                print('[{}]'.format(k), file=DBG_FILE)
                dataKeys.append(k)
#                for d in data:
#                    print(d, file=DBG_FILE)
            else: noneKeys.append(k)
        for k in noneKeys: print('noneKeys=[{}]\ninfo1=[{}]\ninfo2=[{}]\ninfo3=[{}]'.format(k, self.shapes[k][1], self.shapes[k][2], self.shapes[k][3]), file=DBG_FILE)
        for k in dataKeys: print('dataKeys=[{}] size=[{}x{}={}]'.format(k, len(self.shapes[k][0]), len(self.shapes[k][0][0]), len(self.shapes[k][0])*len(self.shapes[k][0][0])), file=DBG_FILE)
        print('printShapes(END) len(shapes)={} len(noneKeys)={} len(valKeys)={}'.format(len(self.shapes), len(noneKeys), len(dataKeys)), file=DBG_FILE)

    @staticmethod
    def printData(data, reason=''):
        rows, cols = len(data), len(data[0]); area = rows * cols
        print('printData({}) data[{}x{}={:,}]'.format(reason, rows, cols, area), file=DBG_FILE)
        for r in range(rows-1, -1, -1):
            for c in range(cols):
                if data[r][c] == 0: print(' ', file=DBG_FILE, end='')
                else:               print('X', file=DBG_FILE, end='')
            print(file=DBG_FILE)
        print('printData({}) data[{}x{}={:,}]'.format(reason, rows, cols, area), file=DBG_FILE)

    @staticmethod
    def flush():
        print('flush()', file=DBG_FILE, flush=True)

    def erase(self):
        print('erase(BGN)'.format(self.gen, self.pop, len(self.done), len(self.undone)), file=DBG_FILE)
        self.gen   = self.pop    = 0
        self.done  = self.undone = []
        self.stats = {}
        for r in range(self.wr):
            for c in range(self.wc):
                self.data[r][c] = 0
                self.cells[r][c].color = self.DEAD[(r+c)%2]
        self.updateStats()
        print('erase(END)'.format(self.gen, self.pop, len(self.done), len(self.undone)), file=DBG_FILE)

    def reset(self):
        print('reset(BGN)'.format(self.gen, self.pop, len(self.done), len(self.undone)), file=DBG_FILE)
        self.erase()
        self.addShape(self.wc//2, self.wr//2, self.shapeKey)
        print('reset(END)'.format(self.gen, self.pop, len(self.done), len(self.undone)), file=DBG_FILE)

    def toggleWrapEdges(self):
        print('toggleWrapEdges(BGN) {}'.format(self.getNNCount), file=DBG_FILE)
        if self.getNNCount == self.getNNCountHard: self.getNNCount = self.getNNCountWrap
        else:                                      self.getNNCount = self.getNNCountHard
        print('toggleWrapEdges(END) {}'.format(self.getNNCount), file=DBG_FILE)

    def toggleFullScreen(self):
        if   self.fullScreen: self.fullScreen = False
        else:                 self.fullScreen = True
        self.set_fullscreen(self.fullScreen)

    def toggleCell(self, c, r):
        if self.data[r][c] == 0: self.addCell(c, r)
        else: self.removeCell(c, r)
        self.updateStats()

#    def toggleColorList():
#        if self.colorList: self.colorList = 0
#            else:          self.colorList = 1

####################################################################################################
    def undo(self, dt=-1.0, reason=''):
        print('undo(BGN) gen={} genx={} done[{}] undone[{}] dt={:6.3} reason={}'.format(self.gen, self.genx, len(self.done), len(self.undone), dt, reason), file=DBG_FILE)
        if len(self.done) > 0:
            self.gen -= 1
            self.data = self.done.pop(-1)
            self.undone.append(self.data)
            for r in range(self.wr):
                for c in range(self.wc):
                    if self.data[r][c] == 0: self.cells[r][c].color = self.DEAD[(r+c)%2]
                    else:                    self.cells[r][c].color = self.ALIVE[0]
        self.calcPop()
        if self.gen == self.genx:
            self.stop(self.undo, reason=reason)
            self.genx = -1
        self.updateStats()
        self.printData(self.data, 'undo()')
        print('undo(END) gen={} genx={} done[{}] undone[{}] dt={:6.3} reason={}'.format(self.gen, self.genx, len(self.done), len(self.undone), dt, reason), file=DBG_FILE)

    def update(self, dt=-1.0, reason=''):
        print('update(BGN) gen={} genx={} done[{}] undone[{}] dt={:6.3} reason={}'.format(self.gen, self.genx, len(self.done), len(self.undone), dt, reason), file=DBG_FILE)
        self.gen += 1
        self.done.append(self.data)
        self.updateDataCells()
        print('update() gen={} genx={} done=[{}]'.format(self.gen, self.genx, len(self.done)), file=DBG_FILE)
        if self.gen == self.genx:
            self.stop(self.update, reason=reason)
            self.genx = -1
        self.updateStats()
        self.printData(self.data, 'update()')
        print('update(END) gen={} genx={} done[{}] undone[{}] dt={:6.3} reason={}'.format(self.gen, self.genx, len(self.done), len(self.undone), dt, reason), file=DBG_FILE)

    @staticmethod
    def stop(func, reason):
        print('stop() func={} reason={}'.format(func, reason), file=DBG_FILE)
        pyglet.clock.unschedule(func)

    @staticmethod
    def run(func, period, reason):
        print('run() func={} period={:6.3} reason={}'.format(func, period, reason), file=DBG_FILE)
        pyglet.clock.schedule_interval(func, period, reason)

    def go2genx(self, dbg=1):  # timeTravel() jump() skip()?
        self.genx = int(self.buffer)
        self.buffer = ''
        if self.genx < 0: print('go2genx(ERROR @ gen={}) genx={} Negative Values Are Not Allowed'.format(self.gen, self.genx), file=DBG_FILE, flush=True); return
        self.dispatch = None
        if dbg:           print('go2genx(BGN) gen={} genx={}'.format(self.gen, self.genx), file=DBG_FILE, flush=True)
        if   self.genx > self.gen: func = self.update
        elif self.genx < self.gen: func = self.undo
        else:             print('go2genx(SKIP @ gen={}) genx={} Already Equals gen={}'.format(self.gen, self.genx, self.gen), file=DBG_FILE, flush=True); return
        reason = 'go2genx()'
        self.run(func, self.period, reason=reason)
        if dbg:           print('go2genx(END) reason={}'.format(reason), file=DBG_FILE, flush=True)

    def register(self, func, dbg=1):
        if dbg: print('register(BGN) buffer={} dispatch={}'.format(self.buffer, self.dispatch), file=DBG_FILE)
        self.buffer = ''
        self.dispatch = func
        if dbg: print('register(END) buffer={} dispatch={}'.format(self.buffer, self.dispatch), file=DBG_FILE)
####################################################################################################
    def on_key_press(self, symbol, modifiers, dbg=1):
        super().on_key_press(symbol, modifiers)
        symStr, modStr = pygwink.symbol_string(symbol), pygwink.modifiers_string(modifiers)
        if dbg: print('on_key_press(BGN) {:5} {:12} {} {:12} dispatch={}'.format(symbol, symStr, modifiers, modStr, self.dispatch), flush=True)
        if dbg: print('on_key_press(BGN) {:5} {:12} {} {:12} dispatch={}'.format(symbol, symStr, modifiers, modStr, self.dispatch), file=DBG_FILE, flush=True)
        if self.dispatch:
            if symbol == pygwink.SPACE or symbol == pygwink.ENTER:
                self.dispatch()
                self.dispatch = None
            else: 
                self.buffer += chr(symbol)
                if dbg: print('on_key_press() a(symbol)={!a} buffer={}'.format(symbol, self.buffer), flush=True)
                if dbg: print('on_key_press() a(symbol)={!a} buffer={}'.format(symbol, self.buffer), file=DBG_FILE, flush=True)
        elif symbol == pygwink.Q and modifiers == pygwink.MOD_CTRL:  exit()
        elif symbol == pygwink.A and modifiers == pygwink.MOD_CTRL:  self.addShape(self.wc, self.wr, self.shapeKey)
        elif symbol == pygwink.E and modifiers == pygwink.MOD_CTRL:  self.erase()
        elif symbol == pygwink.F and modifiers == pygwink.MOD_CTRL:  self.toggleFullScreen()
        elif symbol == pygwink.G and modifiers == pygwink.MOD_CTRL:  self.register(self.go2genx)
        elif symbol == pygwink.R and modifiers == pygwink.MOD_CTRL:  self.recallShape()
        elif symbol == pygwink.S and modifiers == pygwink.MOD_CTRL:  self.saveShape()
        elif symbol == pygwink.N and modifiers == pygwink.MOD_CTRL:  self.toggleWrapEdges()
        elif symbol == pygwink.F and modifiers == pygwink.MOD_SHIFT: self.flush()
        elif symbol == pygwink.R and modifiers == pygwink.MOD_SHIFT: self.reset()
        elif symbol == pygwink.SPACE:                                self.stop(self.update, 'on_key_press(SPACE)')  # ; self.stop(self.undo, 'on_key_press(SPACE)')
        elif symbol == pygwink.ENTER:                                self.run(self.update, self.period, reason='on_key_press(ENTER)')
        elif symbol == pygwink.RIGHT:                                self.update(reason='on_key_press(RIGHT)')
        elif symbol == pygwink.LEFT:                                 self.undo(reason='on_key_press(LEFT)')
        if dbg: print('on_key_press(END) {:5} {:12} {} {:12} dispatch={}'.format(symbol, symStr, modifiers, modStr, self.dispatch), flush=True)
        if dbg: print('on_key_press(END) {:5} {:12} {} {:12} dispatch={}'.format(symbol, symStr, modifiers, modStr, self.dispatch), file=DBG_FILE, flush=True)

    def on_mouse_release(self, x, y, button, modifiers):  # pygwin.mouse.MIDDLE #pygwin.mouse.LEFT #pygwin.mouse.RIGHT
        c, r = int(x / self.cw), int(y / self.ch)
        print('on_mouse_release() b={} m={} x={:4} y={:4} cw={:6.2f} ch={:6.2f} c={} r={} d[r][c]={}'.format(button, modifiers, x, y, self.cw, self.ch, c, r, self.data[r][c]), flush=True)
        print('on_mouse_release() b={} m={} x={:4} y={:4} cw={:6.2f} ch={:6.2f} c={} r={} d[r][c]={}'.format(button, modifiers, x, y, self.cw, self.ch, c, r, self.data[r][c]), file=DBG_FILE)
        self.toggleCell(c, r)

    def on_draw(self):
        super().clear()
        self.batch.draw()

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log.txt", 'w')
    life = Life()
    pyglet.app.run()
