import sys, os, copy, math
import pyglet
import pyglet.window.key as pygwink
sys.path.insert(0, os.path.abspath('../lib'))
import cmdArgs

def fri(f): return int(math.floor(f+0.5))

class Life(pyglet.window.Window):
    def __init__(self):
        display = pyglet.canvas.get_display()
        self.screens = display.get_screens()
#        self.auxWin = pyglet.window.Window(width=900, height=500, resizable=True, screen=self.screens[0], visible=False)
#        self.auxWin.set_visible()
        super().__init__(resizable=True, screen=self.screens[1], visible=False)
        self.DATA_SET   = set('.*')
        self.XLATE      = str.maketrans('.*', '01')
        self.MIN, self.NOM, self.MAX = 0, 1, 2
#        self.MESH       = [(127, 191, 255), (255,   0,   0), (255, 255, 255)]
        self.MESH       = [(255, 0, 0), (0, 255, 0), (255, 255, 255)]
        self.ALIVE      = [(127, 255, 127), (127, 255, 255)]
        self.DEAD       = [(  0,   0,   0), (100,  80, 127)]
        self.ncolors    = 2
        self.prev,        self.batch     = None, pyglet.graphics.Batch()
        self.data,        self.cells,    =  [],  []
        self.clines,      self.rlines    =  [],  []
        self.savedData,   self.savedDone =  [],  []
        self.dispatch,    self.buffer    = None, ''
        self.genX,        self.period    = -1,   1/120
        self.gen,         self.pop       =  0,   0
        self.done,        self.undone    =  [],  []
        self.shapes,      self.stats     =  {},  {}
        self.gridLines,   self.dirty     = True, False
        self.x,           self.y         =  0,   0
        self.argMap     = cmdArgs.parseCmdLine(dbg=1)
        self.nc         =  200  # 100  # 51  # 221  # 11  # 101
        self.nr         =  120  #  50  # 31  # 121  #  7  #  57
        self.ww         = 1000  # 1900  # 950
        self.wh         =  600  # 1100  # 590
        self.fullScreen = False
        self.getNNCount = self.getNNCountWrap
        self.shapeKey   = 'TestOddOdd'  # 'MyShape_07'  # 'TestOddOdd'  # 'Gosper glider gun'
        self.inName     = 'lexicon-no-wrap.txt'
        print('argMap={}'.format(self.argMap), file=DBG_FILE)
        if 'c' in self.argMap and len(self.argMap['c'])  > 0: self.nc         = int(self.argMap['c'][0])
        if 'r' in self.argMap and len(self.argMap['r'])  > 0: self.nr         = int(self.argMap['r'][0])
        if 'w' in self.argMap and len(self.argMap['w'])  > 0: self.ww         = int(self.argMap['w'][0])
        if 'h' in self.argMap and len(self.argMap['h'])  > 0: self.wh         = int(self.argMap['h'][0])
        if 'n' in self.argMap and len(self.argMap['n']) == 0: self.getNNCount = self.getNNCountHard
        if 'k' in self.argMap and len(self.argMap['k'])  > 0: self.shapeKey   = self.argMap['k'][0]
        if 'f' in self.argMap and len(self.argMap['f'])  > 0: self.inName     = self.argMap['f'][0]
        if 'F' in self.argMap and len(self.argMap['F']) == 0: self.fullScreen = True
        print('nc={}'.format(self.nc), file=DBG_FILE)
        print('nr={}'.format(self.nr), file=DBG_FILE)
        print('ww={}'.format(self.ww), file=DBG_FILE)
        print('wh={}'.format(self.wh), file=DBG_FILE)
        print('getNNCount={}'.format(self.getNNCount), file=DBG_FILE)
        print('shapeKey={}'.format(self.shapeKey), file=DBG_FILE)
        print('inName={}'.format(self.inName), file=DBG_FILE)
        print('fullScreen={}'.format(self.fullScreen), file=DBG_FILE)
        self.set_size(self.ww, self.wh)
        if self.fullScreen:  self.set_fullscreen(self.fullScreen)
#        self.ww, self.wh = self.get_size()
        self.useOrderedGroup = True
        self.parse()
        self._initGrid()
        self.addShape(self.nc/2, self.nr/2, self.shapeKey)
        self.set_visible()

    def _initGroup(self, order=0, parent=None):
        if self.useOrderedGroup: return pyglet.graphics.OrderedGroup(order, parent)
        else:                    return pyglet.graphics.Group(parent)

    @staticmethod
    def getMeshColor(i, j, mesh):
        MIN, NOM, MAX = 0, 1, 2
        MESH = [(255, 0, 0), (0, 255, 0), (255, 255, 255)]
        if   (i-j)%mesh[MAX]==0: return MESH[MAX]
        elif (i-j)%mesh[NOM]==0: return MESH[NOM]
        elif (i-j)%mesh[MIN]==0: return MESH[MIN]

    def dumpGeom(self, reason, info=''):
        print('{:24} w[{:6.2f}] h[{:6.2f}] ww[{:4}] wh[{:4}] nc[{:3}] nr[{:3}] {}'.format(reason, self.w, self.h, self.ww, self.wh, self.nc, self.nr, info), file=DBG_FILE)

    def _alignGrid(self):
        sd            = self.shapes[self.shapeKey][0]
        sc,   sr      = len(sd[0]), len(sd)
        m2sc, m2sr    = sc % 2, sr % 2
        m2c,  m2r     = self.nc % 2,    self.nr % 2
        if   m2sc    == 1 and m2c == 0: self.nc += 1
        elif m2sc    == 0 and m2c == 1: self.nc -= 1
        if   m2sr    == 1 and m2r == 0: self.nr += 1
        elif m2sr    == 0 and m2r == 1: self.nr -= 1
        print('_alignGrid()              sc={} sr={} m2sc={} m2sr={} m2c={} m2r={} sk[{}]'.format(sc, sr, m2sc, m2sr, m2c, m2r, self.shapeKey), file=DBG_FILE)
        return self.nc, self.nr

    def _initGrid(self, dbg=1):
        self.cellGroup, self.lineGroup = self._initGroup(0), self._initGroup(1)
        mesh, color    = [1, 5, 25], self.DEAD[0]
        self.nc, self.nr = self._alignGrid()
        x, y, w, h, ww, wh, nc, nr = self._geom()
        self.dumpGeom('_initGrid() nest list comp', 'x={:6.2f} y={:6.2f} sk[{}]'.format(x, y, self.shapeKey))
        self.data, self.cells = zip(*[map(list, zip(*[[0, pyglet.shapes.Rectangle(fri(i*w+x), fri(wh-h-j*h+y), fri(w), fri(h), color=self.DEAD[(i+j)%self.ncolors], batch=self.batch, group=self.cellGroup)] for i in range(nc)])) for j in range(nr)])
        self.cells[0][0].color = (255, 127, 127)
        if nc % 2 == 0:
            p = fri(nc/2) % mesh[len(mesh)-1]
            if dbg: print('_initGrid() c={}=Even p={}'.format(nc, p), file=DBG_FILE)
            for i in range(nc+1):
                x1, x2, y1, y2 = i*w, i*w, 0, nr*h
                color = self.getMeshColor(i, p, mesh)
                self.clines.append(pyglet.shapes.Line(x1, y1, x2, y2, width=1, color=color, batch=self.batch, group=self.lineGroup))
                if dbg: print('i=[{:3}] x1={:7.2f} y1={:7.2f} x2={:7.2f} y2={:7.2f}'.format(i, x1, y1, x2, y2), file=DBG_FILE)
        else:
            p = fri(nc/2-1)
            if dbg: print('_initGrid() c={}=Odd p={}'.format(nc, p), file=DBG_FILE)
            for i in range(fri(nc/2)):
                x1, x2, y1, y2 = i*w, i*w, 0, nr*h
                color = self.getMeshColor(i, p, mesh)
                self.clines.append(pyglet.shapes.Line(x1, y1, x2, y2, width=1, color=color, batch=self.batch, group=self.lineGroup))
                if dbg: print('i=[{:3}] x1={:7.2f} y1={:7.2f} x2={:7.2f} y2={:7.2f}'.format(i, x1, y1, x2, y2), file=DBG_FILE)
            p = fri(nc/2)
            if dbg: print('_initGrid() c={}=Odd p={}'.format(nc, p), file=DBG_FILE)
            for i in range(fri(nc/2), nc+1):
                x1, x2, y1, y2 = i*w, i*w, 0, nr*h
                color = self.getMeshColor(i, p, mesh)
                self.clines.append(pyglet.shapes.Line(x1, y1, x2, y2, width=1, color=color, batch=self.batch, group=self.lineGroup))
                if dbg: print('i=[{:3}] x1={:7.2f} y1={:7.2f} x2={:7.2f} y2={:7.2f}'.format(i, x1, y1, x2, y2), file=DBG_FILE)
        if nr % 2 == 0:
            q = fri(nr/2) % mesh[len(mesh)-1]
            if dbg: print('_initGrid() r={}=Even q={}'.format(nr, q), file=DBG_FILE)
            for j in range(nr+1):
                x1, x2, y1, y2 = 0, nc*w, j*h, j*h
                color = self.getMeshColor(j, q, mesh)
                self.rlines.append(pyglet.shapes.Line(x1, y1, x2, y2, width=1, color=color, batch=self.batch, group=self.lineGroup))
                if dbg: print('j=[{:3}] x1={:7.2f} y1={:7.2f} x2={:7.2f} y2={:7.2f}'.format(j, x1, y1, x2, y2), file=DBG_FILE)
        else:
            q = fri(nr/2-1)
            if dbg: print('_initGrid() r={}=Odd q={}'.format(nr, q), file=DBG_FILE)
            for j in range(fri(nr/2)):
                x1, x2, y1, y2 = 0, nc*w, j*h, j*h
                color = self.getMeshColor(j, q, mesh)
                self.rlines.append(pyglet.shapes.Line(x1, y1, x2, y2, width=1, color=color, batch=self.batch, group=self.lineGroup))
                if dbg: print('j=[{:3}] x1={:7.2f} y1={:7.2f} x2={:7.2f} y2={:7.2f}'.format(j, x1, y1, x2, y2), file=DBG_FILE)
            q = fri(nr/2)
            if dbg: print('_initGrid() r={}=odd q={}'.format(nr, q), file=DBG_FILE)
            for j in range(fri(nr/2), nr+1):
                x1, x2, y1, y2 = 0, nc*w, j*h, j*h
                color = self.getMeshColor(j, q, mesh)
                self.rlines.append(pyglet.shapes.Line(x1, y1, x2, y2, width=1, color=color, batch=self.batch, group=self.lineGroup))
                if dbg: print('j=[{:3}] x1={:7.2f} y1={:7.2f} x2={:7.2f} y2={:7.2f}'.format(j, x1, y1, x2, y2), file=DBG_FILE)

    def _geom(self):
        self.w, self.h = self.ww/self.nc, self.wh/self.nr
        return self.x, self.y, self.w, self.h, self.ww, self.wh, self.nc, self.nr

    def on_resize(self, width, height, dbg=1):
        super().on_resize(width, height)
        self.ww, self.wh  = width, height
        x, y, w, h, ww, wh, nc, nr = self._geom()
        if dbg:   self.dumpGeom('on_resize(BGN)', 'x={:6.2f} y={:6.2f}'.format(x, y))
        for j in range(nr):
            for i in range(nc):
                self.cells[j][i].position = i*w+x, wh-h-j*h+y
                self.cells[j][i].width    = w
                self.cells[j][i].height   = h
        for i in range(nc+1):  # len(self.clines)):
            self.clines[i].position = i*w+x, y, i*w+x, nr*h+y
            if dbg: print('i={:4} w={:6.2f} x={:6.2f} i*w={:7.2f} {:4} i*w+x={:7.2f} {:4}'.format(i, w, x, i*w, fri(i*w), i*w+x, fri(i*w+x)), file=DBG_FILE)
        if dbg: print(file=DBG_FILE)
        for j in range(nr+1):  # len(self.rlines)):
            self.rlines[j].position = x, j*h+y, nc*w+x, j*h+y
            if dbg: print('j={:4} h={:6.2f} y={:6.2f} j*h={:7.2f} {:4} j*h+y={:7.2f} {:4}'.format(j, h, y, j*h, fri(j*h), j*h+y, fri(j*h+y)), file=DBG_FILE)
        if dbg: self.dumpGeom('on_resize(END)', 'x={:6.2f} y={:6.2f}'.format(x, y))

    def addShape(self, p, q, key='MyShape_07'):
        v = self.shapes[key]
        data = v[0]
        w, h = len(data[0]), len(data)
        c = fri(p-w/2)
        r = fri(q-h/2)
        a = w * h
        txt = 'p={} q={} c={} r={} [{}x{}={}] key={}'.format(p, q, c, r, w, h, a, key)
        print('addShape(BGN) {}'.format(txt), file=DBG_FILE)
        print('addShape() data={}'.format(data), file=DBG_FILE)
        print('info1={}'.format(v[1]), file=DBG_FILE)
        if v[2]: print('info2={}'.format(v[2]), file=DBG_FILE)
        if v[3]: print('info3={}'.format(v[3]), file=DBG_FILE)
        if data is None: print('addShape data={} is None Nothing to Add'.format(data), file=DBG_FILE); return
        for j in range(h):
            print('    ', file=DBG_FILE, end='')
            for i in range(w):
                print('{}'.format(data[j][i]), file=DBG_FILE, end='')
                if data[j][i] == 1: self.addCell(i+c, j+r)
            print(file=DBG_FILE)
        self.printData(self.data, 'addShape()')
        self.updateStats()
        print('addShape(END) {}'.format(txt), file=DBG_FILE)

    def addShapeA(self, c, r, dbg=0):  # checkerboard
        if dbg: print('addShapeA(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[j])):
                if (i+j) % 2: self.cells[j][i].color = self.DEAD[(i+j) % self.ncolors]
                else:         self.addCell(i, j)
        if dbg: self.printData(self.data, 'addShapeA() c={} r={}'.format(c, r))
        if dbg: print('addShapeA(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShapeB(self, c, r, dbg=0):  # odd odd
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
        for r in range(self.nr-1, -1, -1):
            for c in range(self.nc):
                self.updateDataCell(c, r, data)
        self.data = data

    def updateDataCell(self, c, r, data, dbg=0):
        n = self.getNNCount(c, r)
        if dbg:
            if n == 0: print(' ', file=DBG_FILE, end='')
            else: print('{}'.format(n), file=DBG_FILE, end='')
        if self.data[r][c] == 1:
            if n == 2 or n == 3: data[r][c] = 1; self.cells[r][c].color = self.ALIVE[0]
            else:                data[r][c] = 0; self.cells[r][c].color = self.DEAD[(r+c) % self.ncolors]; self.pop -= 1
        elif n == 3:             data[r][c] = 1; self.cells[r][c].color = self.ALIVE[0];                   self.pop += 1
        else:                    data[r][c] = 0; self.cells[r][c].color = self.DEAD[(r+c) % self.ncolors]

    def updateStats(self):
        assert self.gen >= 0
        assert self.pop >= 0
        assert self.nr  == len(self.cells)
        assert self.nc  == len(self.cells[0])
        self.stats['S_GEN']  = self.gen
        self.stats['S_POP']  = self.pop
        self.stats['S_AREA'] = self.nr * self.nc
        self.stats['S_DENS'] = 100 * self.stats['S_POP']   / self.stats['S_AREA']
        if self.stats['S_POP'] > 0:  self.stats['S_IDENS'] = self.stats['S_AREA'] / self.stats['S_POP']
        else:                        self.stats['S_IDENS'] = -1.0
        self.stats['S_FPS']  = pyglet.clock.get_fps()
        if self.stats['S_FPS'] > 0:  self.stats['S_IFPS']  = 1 / self.stats['S_FPS']
        else:                        self.stats['S_IFPS']  = -1.0
        self.displayStats()

    def removeCell(self, c, r, dbg=0):
        if dbg: print('removeCell(BGN) c={} r={} data[r][c]={}'.format(c, r, self.data[r][c]), file=DBG_FILE)
        if self.data[r][c] == 1: self.pop -= 1
        self.data[r][c] = 0
        self.cells[r][c].color = self.DEAD[(r+c) % self.ncolors]
        if dbg: print('removeCell(END) c={} r={} data[r][c]={}'.format(c, r, self.data[r][c]), file=DBG_FILE)

    def saveShape(self, dbg=0):
        if dbg: self.printInfo('saveShape(BGN)')
        self.savedData = copy.deepcopy(self.data)
        self.savedDone = copy.deepcopy(self.done)
        if dbg: self.printInfo('saveShape(END)')

    def recallShape(self, dbg=0):
        if dbg: self.printInfo('recallShape(BGN)')
        self.calcPop()
        self.done = copy.deepcopy(self.savedDone)
        self.gen = len(self.done)
        for r in range(len(self.savedData)):
            for c in range(len(self.savedData[0])):
                if self.savedData[r][c] == 1: self.addCell(c, r)
                else:                         self.removeCell(c, r)
        self.printData(self.data, 'recallShape()')
        self.updateStats()
        if dbg: self.printInfo('recallShape(END)')

    def calcPop(self, dbg=0):
        if dbg: print('calcPop(BGN) pop={}'.format(self.pop), file=DBG_FILE)
        self.pop = 0
        for r in range(self.nr):
            for c in range(self.nc):
                if self.data[r][c] == 1: self.pop += 1
        if dbg: print('calcPop(END) pop={}'.format(self.pop), file=DBG_FILE)

    def parse(self, dbg=0):
        print('parse(BGN)', file=DBG_FILE)
        data, key, state = [], '', 0
        info1, info2, info3 = '', '', ''
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
                                info2, info3 = '', ''
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
                        data.append([int(c) for c in line])
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

    def getNNCountWrap(self, c, r):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                n += self.data[(r+j+self.nr)%self.nr][(c+i+self.nc)%self.nc]
        n -= self.data[r][c]
        return n

    def getNNCountHard(self, c, r):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                if 0 <= r + j < self.nr and 0 <= c + i < self.nc:
                    n += self.data[r+j][c+i]
        n -= self.data[r][c]
        return n

    def displayStats(self, dbg=0):  # [{:3}x{:3}]=[{:7,}]   # , self.nc, self.nr, self.stats['S_AREA']
        txt = 'Gen[{:4,}] Pop[{:6,}] Done[{:4,}] Undone[{:4,}] Dens[{:6.3}]% IDens[{:7,.0f}] FPS[{:6,.0f}] IFPS[{:6.3}] shapeKey[{}]'.\
            format(self.stats['S_GEN'], self.stats['S_POP'], len(self.done), len(self.undone),
                   self.stats['S_DENS'], self.stats['S_IDENS'], self.stats['S_FPS'], self.stats['S_IFPS'], self.shapeKey)
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
        rows, cols = len(data), len(data[0])
        area = rows * cols
        print('{:24} data[{}x{}={:,}]'.format(reason, rows, cols, area), file=DBG_FILE)
        for r in range(rows):
            for c in range(cols):
                if   data[r][c] == 0: print(' ', file=DBG_FILE, end='')
                elif data[r][c] == 1: print('X', file=DBG_FILE, end='')
                else:                 print('printData() ERROR Illegal Value data[{}][{}]={}'.format(r, c, data[r][c]), file=DBG_FILE); exit()
            print(file=DBG_FILE)
        print('{:24} data[{}x{}={:,}]'.format(reason, rows, cols, area), file=DBG_FILE)

    def printInfo(self, reason, info=''):
        print('{:24} gen[{:4,}] pop[{:6,}] done[{:4,}] undone[{:4,}] {}'.format(reason, self.gen, self.pop, len(self.done), len(self.undone), info), file=DBG_FILE)

    @staticmethod
    def flush():
        print('flush()', file=DBG_FILE, flush=True)

    def erase(self):
        self.printInfo('erase(BGN)')
        self.gen,  self.pop    = 0, 0
        self.done, self.undone = [], []
        self.stats = {}
        for r in range(self.nr):
            for c in range(self.nc):
                self.data[r][c] = 0
                self.cells[r][c].color = self.DEAD[(r+c) % self.ncolors]
        self.updateStats()
        self.printInfo('erase(END)')

    def reset(self):
        self.printInfo('reset(BGN)')
        self.erase()
        self.addShape(self.nc//2, self.nr//2, self.shapeKey)
        self.printInfo('reset(END)')

    def toggleWrapEdges(self, dbg=0):
        if dbg: print('toggleWrapEdges(BGN) {}'.format(self.getNNCount), file=DBG_FILE)
        if self.getNNCount == self.getNNCountHard: self.getNNCount = self.getNNCountWrap
        else:                                      self.getNNCount = self.getNNCountHard
        if dbg: print('toggleWrapEdges(END) {}'.format(self.getNNCount), file=DBG_FILE)

    def toggleFullScreen(self):
        if   self.fullScreen: self.fullScreen = False
        else:                 self.fullScreen = True
        self.set_fullscreen(self.fullScreen)

    def toggleCell(self, c, r):
        if self.data[r][c] == 0: self.addCell(c, r)
        else:                    self.removeCell(c, r)
        self.updateStats()
        self.dirty = True

    def toggleNColors(self, dbg=0):
        if dbg: print('toggleNColors(BGN) ncolors={}'.format(self.ncolors), file=DBG_FILE)
        if self.ncolors == 2: self.ncolors = 1
        else:                 self.ncolors = 2
        self.updateCellColors()
        if dbg: print('toggleNColors(END) ncolors={}'.format(self.ncolors), file=DBG_FILE)

    def toggleGridLines(self, dbg=1):
        if dbg: print('toggleGridLines(BGN) gridLines={}'.format(self.gridLines), file=DBG_FILE)
        self.gridLines = not self.gridLines
        for i in range(len(self.clines)): self.clines[i].visible = self.gridLines
        for j in range(len(self.rlines)): self.rlines[j].visible = self.gridLines
        if dbg: print('toggleGridLines(END) gridLines={}'.format(self.gridLines), file=DBG_FILE)

####################################################################################################
    def updateCellColors(self, dbg=0):
        if dbg: print('updateCellColors(BGN) ncolors={}'.format(self.ncolors), file=DBG_FILE)
        for j in range(self.nr):
            for i in range(self.nc):
                if self.data[j][i] == 0: self.cells[j][i].color = self.DEAD[(i+j) % self.ncolors]
                else:                    self.cells[j][i].color = self.ALIVE[0]
        if dbg: print('updateCellColors(END) ncolors={}'.format(self.ncolors), file=DBG_FILE)

    def undo(self, dt=-1.0, reason=''):
        if self.dirty: self.printData(self.data, 'dirty undo()'); self.dirty = False
        self.printInfo('undo(BGN)', 'genX[{:4,}] dt[{:6.3}] reason={}'.format(self.genX, dt, reason))
        if self.gen > 0 and len(self.done) > 0:
            self.gen -= 1
            self.data = self.done.pop()
            self.undone.append(self.data)
            self.pop = 0
            for r in range(self.nr):
                for c in range(self.nc):
                    if   self.data[r][c] == 0: self.cells[r][c].color = self.DEAD[(r+c) % self.ncolors]
                    elif self.data[r][c] == 1: self.cells[r][c].color = self.ALIVE[0]; self.pop += 1
                    else:                      print('undo() ERROR Illegal Value data[{}][{}]={}'.format(r, c, self.data[r][c]), file=DBG_FILE); exit()
            if self.gen == self.genX:
                self.stop(self.undo, reason)
                self.genX = -1
            self.updateStats()
            self.printData(self.data, 'undo()')
        else: print('undo() Nothing to Undo done[{}]'.format(len(self.done)), file=DBG_FILE)
        self.printInfo('undo(END)', 'genX[{:4,}] dt[{:6.3}] reason={}'.format(self.genX, dt, reason))

    def update(self, dt=-1.0, reason='', dbg=0):
        if self.dirty: self.printData(self.data, 'dirty update()'); self.dirty = False
        if dbg: self.printInfo('update(BGN)', 'genX[{:4,}] dt[{:6.3}] reason={}'.format(self.genX, dt, reason))
        if self.pop == 0: print('update() pop={} Nothing Left Alive'.format(self.pop), file=DBG_FILE); return
        if self.steadyState(): self.stop(self.update, 'steadyState {}'.format(reason))
        self.prev = copy.deepcopy(self.data)
        self.gen += 1
        self.done.append(self.data)
        self.updateDataCells()
        if dbg: self.printInfo('update()', 'genX[{:4,}] dt[{:6.3}] reason={}'.format(self.genX, dt, reason))
        if self.gen == self.genX:
            self.stop(self.update, 'gen[{}]==genX[{}] {}'.format(self.gen, self.genX, reason))
            self.genX = -1
        self.updateStats()
        if dbg: self.printData(self.data, 'update()')
        if dbg: self.printInfo('update(END)', 'genX[{:4,}] dt[{:6.3}] reason={}'.format(self.genX, dt, reason))

    def steadyState(self):
        if self.prev is None:                          return False
        if self.pop != self.stats['S_POP']:            return False
        for j in range(self.nr):
            for i in range(self.nc):
                if self.prev[j][i] != self.data[j][i]: return False
        print('steadyState() Data is Unchanged'.format(), file=DBG_FILE)
        self.prev, self.genX = None, -1
        return True

    @staticmethod
    def stop(func, reason):
        print('stop()                  func={} reason={}'.format(func, reason), file=DBG_FILE)
        pyglet.clock.unschedule(func)

    @staticmethod
    def run(func, period, reason):
        print('run()                   func={} period[{:6.3}] reason={}'.format(func, period, reason), file=DBG_FILE)
        pyglet.clock.schedule_interval(func, period, reason)

    def absGenX(self, dbg=0):  # timeTravel() jump() skip() evolve() age()?
        self.genX = int(self.buffer)
        self.buffer = ''
        reason = 'gen={} genX={}'.format(self.gen, self.genX)
        if   dbg:           print('absGenX(BGN)             {}'.format(reason), file=DBG_FILE)
        if   self.genX < 0: print('absGenX() ERROR @ {} Negative Values Are Not Allowed'.format(reason), file=DBG_FILE); return
        if   self.genX > self.gen: func = self.update
        elif self.genX < self.gen: func = self.undo
        else:               print('absGenX() SKIP @ {} Already Equals gen={}'.format(reason, self.gen), file=DBG_FILE); return
        self.run(func, self.period, reason='absGenX() {}'.format(reason))
        if   dbg:           print('absGenX(END)             {}'.format(reason), file=DBG_FILE)

    def relGenX(self, dbg=0):
        genR = int(self.buffer)
        self.buffer = ''
        self.genX = self.gen + genR
        reason = 'gen={} genR={} genX={}'.format(self.gen, genR, self.genX)
        if dbg:             print('relGenX(BGN)             {}'.format(reason), file=DBG_FILE)
        if   self.genX < 0: print('relGenX() ERROR @ {} Negative Values Are Not Allowed'.format(reason), file=DBG_FILE); return
        if   self.genX > self.gen: func = self.update
        elif self.genX < self.gen: func = self.undo
        else:               print('relGenX() SKIP @ genR is Zero {}'.format(reason), file=DBG_FILE); return
        self.run(func, self.period, reason='relGenX() {}'.format(reason))
        if dbg:             print('relGenX(END)             {}'.format(reason), file=DBG_FILE)

    def register(self, func, dbg=0):
        if dbg: print('register(BGN)           buffer[{}] dispatch={}'.format(self.buffer, self.dispatch), file=DBG_FILE)
        self.buffer = ''
        self.dispatch = func
        if dbg: print('register(END)           buffer[{}] dispatch={}'.format(self.buffer, self.dispatch), file=DBG_FILE)
####################################################################################################
    def on_key_press(self, symbol, modifiers, dbg=0):
        super().on_key_press(symbol, modifiers)
        symStr, modStr = pygwink.symbol_string(symbol), pygwink.modifiers_string(modifiers)
        if dbg: print('\non_key_press(BGN)       {:5}    {:12} {} {:12} dispatch={}'.format(symbol, symStr, modifiers, modStr, self.dispatch), file=DBG_FILE)
        if self.dispatch:
            if symbol == pygwink.SPACE or symbol == pygwink.ENTER:
                self.dispatch()
                self.dispatch = None
            else: 
                self.buffer += chr(symbol)
                if dbg: print('on_key_press()         a(symbol)={!a} buffer={}'.format(symbol, self.buffer), file=DBG_FILE)
        elif symbol == pygwink.Q and modifiers == pygwink.MOD_CTRL:  exit()
        elif symbol == pygwink.A and modifiers == pygwink.MOD_CTRL:  self.addShape(self.nc//2, self.nr//2, self.shapeKey)
        elif symbol == pygwink.C and modifiers == pygwink.MOD_CTRL:  self.toggleNColors()
        elif symbol == pygwink.E and modifiers == pygwink.MOD_CTRL:  self.erase()
        elif symbol == pygwink.F and modifiers == pygwink.MOD_CTRL:  self.toggleFullScreen()
        elif symbol == pygwink.G and modifiers == pygwink.MOD_CTRL:  self.register(self.absGenX)
        elif symbol == pygwink.J and modifiers == pygwink.MOD_CTRL:  self.register(self.relGenX)
        elif symbol == pygwink.R and modifiers == pygwink.MOD_CTRL:  self.recallShape()
        elif symbol == pygwink.S and modifiers == pygwink.MOD_CTRL:  self.saveShape()
        elif symbol == pygwink.N and modifiers == pygwink.MOD_CTRL:  self.toggleWrapEdges()
        elif symbol == pygwink.F and modifiers == pygwink.MOD_SHIFT: self.flush()
        elif symbol == pygwink.G and modifiers == pygwink.MOD_SHIFT: self.toggleGridLines()
        elif symbol == pygwink.R and modifiers == pygwink.MOD_SHIFT: self.reset()
        elif symbol == pygwink.SPACE:                                self.stop(self.update, 'on_key_press(SPACE)')  # ; self.stop(self.undo, 'on_key_press(SPACE)')
        elif symbol == pygwink.ENTER:                                self.run(self.update, self.period, reason='on_key_press(ENTER)')
        elif symbol == pygwink.RIGHT:                                self.update(reason='on_key_press(RIGHT)')
        elif symbol == pygwink.LEFT:                                 self.undo(reason='on_key_press(LEFT)')
        if dbg: print('on_key_press(END)       {:5}    {:12} {} {:12} dispatch={}'.format(symbol, symStr, modifiers, modStr, self.dispatch), file=DBG_FILE)

    def on_mouse_release(self, x, y, button, modifiers):  # pyglet.window.mouse.MIDDLE #pyglet.window.mouse.LEFT #pyglet.window.mouse.RIGHT
        y = self.wh - y
        c, r = int(x / self.w), int(y / self.h)
#        self.dumpGeom('on_mouse_release(BGN)', 'x={:4} y={:4} b={} m={} c={} r={} data[r][c]={}'.format(x, y, button, modifiers, c, r, self.data[r][c]))
        self.toggleCell(c, r)
#        self.dumpGeom('on_mouse_release(END)', 'x={:4} y={:4} b={} m={} c={} r={} data[r][c]={}'.format(x, y, button, modifiers, c, r, self.data[r][c]))

    def on_draw(self):
        super().clear()
        self.batch.draw()

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log.txt", 'w')
    life = Life()
    pyglet.app.run()
