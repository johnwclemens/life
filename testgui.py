import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key
import sys, os, copy
sys.path.insert(0, os.path.abspath('../lib'))
import cmdArgs

def fri(f): return int(round(f))

#display = pyglet.canvas.get_display()
#screens = display.get_screens()
#windows = []
#for screen in screens:
#    windows.append(pyglet.window.Window(screen=screen))

window = pyglet.window.Window(visible=False, resizable=True)
#image = pyglet.image.SolidColorImagePattern((255,255,255,255)).create_image(200, 150)

class TestGui(object):
    def __init__(self, window):
        self.ALIVE  = (127, 255, 127)
        self.ALIVE2 = (191, 255, 127)
        self.DEAD   = ( 31,   0, 127)
        self.DEAD2  = ( 15,  15,  63)
        self.MIN_GRID_LINE = (  0,   0,   0)
        self.NOM_GRID_LINE = (255,   0,   0)
        self.MAJ_GRID_LINE = (  0,   0, 255)
        self.DATA_SET = set('.*')
        self.XLATE = str.maketrans('.*', '01')
        self.pop = 0
        self.done = []
        self.undone = []
        self.testShape = 0
        self.shapeKey = 'TestMe' #'Gosper glider gun'#
        self.shapes = {}
        self.stats = {}
        self.argMap = {}
        self.argMap = cmdArgs.parseCmdLine(dbg=1)
        self.nCols = 11
        self.nRows =  7
        self.ww = 1900
        self.wh = 1150
        self.cellW = self.ww/self.nCols
        self.cellH = self.wh/self.nRows
        self.width  = int(self.nCols * self.cellW + 4)
        self.height = int(self.nRows * self.cellH + 4)
        self.inName = 'lexicon-no-wrap.txt'
        self.getNNCount = self.getNNCountHard
        print('argMap={}'.format(self.argMap), file=DBG_FILE)
        if 'c' in self.argMap and len(self.argMap['c'])  > 0: self.nCols      = int(self.argMap['c'][0])
        if 'r' in self.argMap and len(self.argMap['r'])  > 0: self.nRows      = int(self.argMap['r'][0])
        if 'w' in self.argMap and len(self.argMap['w'])  > 0: self.cellW      = int(self.argMap['w'][0])
        if 'h' in self.argMap and len(self.argMap['h'])  > 0: self.cellH      = int(self.argMap['h'][0])
        if 'W' in self.argMap and len(self.argMap['W'])  > 0: self.width      = int(self.argMap['W'][0])
        if 'H' in self.argMap and len(self.argMap['H'])  > 0: self.height     = int(self.argMap['H'][0])
        if 't' in self.argMap and len(self.argMap['t'])  > 0: self.testShape  = int(self.argMap['t'][0])
        if 'k' in self.argMap and len(self.argMap['k'])  > 0: self.shapeKey   = self.argMap['k'][0]
        if 'f' in self.argMap and len(self.argMap['f'])  > 0: self.inName     = self.argMap['f'][0]
        if 'n' in self.argMap and len(self.argMap['n']) == 0: self.getNNCount = self.getNNCountWrap
        print('nCols={}'.format(self.nCols), file=DBG_FILE)
        print('nRows={}'.format(self.nRows), file=DBG_FILE)
        print('cellW={}'.format(self.cellW), file=DBG_FILE)
        print('cellH={}'.format(self.cellH), file=DBG_FILE)
        print('width={}'.format(self.width), file=DBG_FILE)
        print('height={}'.format(self.height), file=DBG_FILE)
        print('shapeKey={}'.format(self.shapeKey), file=DBG_FILE)
        print('inName={}'.format(self.inName), file=DBG_FILE)
        print('getNNCount={}'.format(self.getNNCount), file=DBG_FILE)
        self.window = window
        self.addGrid(c=37, r=19)  # odd odd
#        self.addGrid(c=20, r=12) # even even
#        self.addGrid(c=20, r=11) # even odd
#        self.addGrid(c=13, r=10) # odd even
        if self.testShape == 1:
#            self.addGrid(c=11, r=7)  # odd odd
            self.addShape1(self.c//2, self.r//2)
        elif self.testShape == 2:
#            self.addGrid(c=20, r=12) # even even
            self.addShape2A(self.c//2, self.r//2)
        elif self.testShape == 3:
#            self.addGrid(c=20, r=11) # even odd
            self.addShape3(self.c//2, self.r//2)
        elif self.testShape == 4:
#            self.addGrid(c=13, r=10) # odd even
            self.addShape4(self.c//2, self.r//2)
        self.window.set_visible()
        self.parse()
        self.addShape(self.c//2, self.r//2, self.shapeKey)
        self.printData(self.data, 'addShape()')
#        self.updateStats()

    def addGrid(self, c=100, r=60, ww=1900, wh=1150, dbg=1):
        self.c, self.r = c, r
        self.ww, self.wh = ww, wh
        self.batch = pyglet.graphics.Batch()
        gmax, gnom, gmin = 10, 5, 1
        p, q = fri(c/2) % gmax, fri(r/2) % gmax
        m, n,  = 0, 0 #1, 1
        self.window.set_size(ww+m, wh+n)
        w = self.w = self.ww / self.c
        h = self.h = self.wh / self.r
        x = self.x = 0
        y = self.y = 0
        self.data, self.cells, self.clines, self.rlines = [], [], [], []
        if dbg: print('addGrid(BGN) c={} r={} ww={} wh={} w={:6.2f} h={:6.2f} x={:6.2f} y={:6.2f} p={} q={} m={} n={}'.format(c, r, ww, wh, w, h, x, y, p, q, m, n), file=DBG_FILE)
        for j in range(r):
            tmp1, tmp2 = [], []
            for i in range(c):
                tmp1.append(0)
                if (i+j) % 2: color = self.DEAD
                else:         color = self.DEAD2
                tmp2.append(shapes.Rectangle(fri(i*w+x), fri(j*h+y), fri(w), fri(h), color=color, batch=self.batch))
            self.data.append(tmp1)
            self.cells.append(tmp2)
        for i in range(c+1):
            print('i={:4} w={:6.2f} x={:6.2f} i*w={:7.2f} {:4} i*w+x={:7.2f} {:4}'.format(i, w, x, i*w, fri(i*w), i*w+x, fri(i*w+x)), file=DBG_FILE, end=' ')
            if   (i-p) % gmax == 0:
                self.clines.append(shapes.Line(fri(i*w+x), fri(y), fri(i*w+x), fri(r*h+y), width=1, color=self.MAJ_GRID_LINE, batch=self.batch))
                print('(i-p)%{}={}'.format(gmax, (i-p) % gmax), file=DBG_FILE)
            elif (i-p) % gnom == 0:
                self.clines.append(shapes.Line(fri(i*w+x), fri(y), fri(i*w+x), fri(r*h+y), width=1, color=self.NOM_GRID_LINE, batch=self.batch))
                print('(i-p)%{}={}'.format(gnom, (i-p) % gnom), file=DBG_FILE)
            elif (i-p) % gmin == 0:
                self.clines.append(shapes.Line(fri(i*w+x), fri(y), fri(i*w+x), fri(r*h+y), width=1, color=self.MIN_GRID_LINE, batch=self.batch))
                print('(i-p)%{}={}'.format(gmin, (i-p) % gmin), file=DBG_FILE)
        print(file=DBG_FILE)
        for j in range(r+1):
            print('j={:4} h={:6.2f} y={:6.2f} j*h={:7.2f} {:4} j*h+y={:7.2f} {:4}'.format(j, h, y, j*h, fri(j*h), j*h+y, fri(j*h+y)), file=DBG_FILE, end=' ')
            if   (j-q) % gmax == 0:
                self.rlines.append(shapes.Line(fri(x), fri(j*h+y), fri(c*w+x), fri(j*h+y), width=1, color=self.MAJ_GRID_LINE, batch=self.batch))
                print('(j-q)%{}={}'.format(gmax, (j-q) % gmax), file=DBG_FILE)
            elif (j-q) % gnom == 0:
                self.rlines.append(shapes.Line(fri(x), fri(j*h+y), fri(c*w+x), fri(j*h+y), width=1, color=self.NOM_GRID_LINE, batch=self.batch))
                print('(j-q)%{}={}'.format(gnom, (j-q) % gnom), file=DBG_FILE)
            elif (j-q) % gmin == 0:
                self.rlines.append(shapes.Line(fri(x), fri(j*h+y), fri(c*w+x), fri(j*h+y), width=1, color=self.MIN_GRID_LINE, batch=self.batch))
                print('(j-q)%{}={}'.format(gmin, (j-q) % gmin), file=DBG_FILE)
        if dbg: print('addGrid(END) w={:6.2f} h={:6.2f} c={} r={} ww={} wh={} x={:6.2f} y={:6.2f}'.format(self.w, self.h, self.c, self.r, self.ww, self.wh, x, y), file=DBG_FILE)

    def on_resize(self, width, height, dbg=1):
        ww = self.ww = width
        wh = self.wh = height
        m, n = 0, 0 #1, 1
        x, y = self.x, self.y
        if dbg: print('on_resize(BGN) width={} height={} ww={} wh={} w={:6.2f} h={:6.2f}'.format(width, height, self.ww, self.wh, self.w, self.h), file=DBG_FILE)
        c, r = self.c, self.r
        w = self.w = self.ww / self.c
        h = self.h = self.wh / self.r
        if dbg: print('on_resize() w={:6.2f} h={:6.2f} c={} r={} ww={} wh={} x={:6.2f} y={:6.2f} m={} n={}'.format(w, h, c, r, ww, wh, x, y, m, n), file=DBG_FILE)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[j])):
                self.cells[j][i].position = (fri(i*w+x), fri(j*h+y))
                self.cells[j][i].width    = fri(w)
                self.cells[j][i].height   = fri(h)
        for i in range(len(self.clines)):
            self.clines[i].position = (fri(i*w+x), fri(y), fri(i*w+x), fri(r*h+y))
            if dbg: print('i={:4} w={:6.2f} x={:6.2f} i*w={:7.2f} {:4} i*w+x={:7.2f} {:4}'.format(i, w, x, i*w, fri(i*w), i*w+x, fri(i*w+x)), file=DBG_FILE)
        print(file=DBG_FILE)
        for j in range(len(self.rlines)):
            self.rlines[j].position = (fri(x), fri(j*h+y), fri(c*w+x), fri(j*h+y))
            if dbg: print('j={:4} h={:6.2f} y={:6.2f} j*h={:7.2f} {:4} j*h+y={:7.2f} {:4}'.format(j, h, y, j*h, fri(j*h), j*h+y, fri(j*h+y)), file=DBG_FILE)
        if dbg: print('on_resize(END) ww={} wh={} w={:6.2f} h={:6.2f}'.format(self.ww, self.wh, self.w, self.h), file=DBG_FILE)

    def addShape_OLD(self, key='TestMe'):
        self.done.append(self.data)
        v = self.shapes[key]
        data = v[0]
        w, h = len(data[0]), len(data)
#        p, q = int(w-1)/2+1), int((h-1)/2+1)
#        c1 = int((self.nCols - 1)/2 + 1)
#        r1 = int((self.nRows - 1)/2 + 1)
        c = int((self.nCols - 1)/2 - (len(data[0]) - 1)/2)
        r = int((self.nRows - 1)/2 + (len(data) - 1)/2)
        a = w * h
        txt = 'addShape() nc={} nr={} c1={} r1={} p={} q={} key={} c={} r={} [{}x{}={}]'.format(self.nCols, self.nRows, c1, r1, p, q, key, c, r, w, h, a)
        print('\n:BGN: {}'.format(txt), file=DBG_FILE)
        print('info1={}'.format(v[1]), file=DBG_FILE)
        if v[2]: print('info2={}'.format(v[2]), file=DBG_FILE)
        if v[3]: print('info3={}'.format(v[3]), file=DBG_FILE)
        if data is None: return #print something?
        for j in range(h):
            print('    ', file=DBG_FILE, end='')
            for i in range(w):
                print('{}'.format(data[j][i]), file=DBG_FILE, end='')
                if data[j][i] == 0:
                    self.cells[r-j][c+i].color = self.DEAD
                    self.data[r-j][c+i] = 0
                else: self.addCell(c+i, r-j, dbg=0)
            print(file=DBG_FILE)
        txt += ' done[{}] undone[{}]'.format(len(self.done), len(self.undone))
        print(  ':END: {}\n'.format(txt), file=DBG_FILE)

    def addCell(self, c, r, state=1, dbg=1):
        if dbg: print('\n:BGN: addCell() c={} r={}'.format(c, r), file=DBG_FILE)
#        if self.data[r][c] == 0: self.pop += 1
        if state == 0:
            self.data[r][c] = 0
            if (c+r) % 2: color = self.DEAD
            else:         color = self.DEAD2
            self.cells[r][c].color = color
        elif state == 1:
            self.data[r][c] = 1
            self.cells[r][c].color = self.ALIVE
        if dbg: print(':END: addCell() c={} r={} data[r][c]={}\n'.format(c, r, self.data[r][c]), file=DBG_FILE)

    def addShape(self, c, r, key='TestMe'):
        self.done.append(self.data)
        v = self.shapes[key]
        data = v[0]
        w, h = len(data[0]), len(data)
        cc = c - w//2
        rr = r + h//2
        a = w * h
        txt = 'addShape() nc={} nr={} c={} r={} cc={} rr={} [{}x{}={}]'.format(self.nCols, self.nRows, c, r, cc, rr, w, h, a)
        print('\n:BGN: {}'.format(txt), file=DBG_FILE)
        print('info1={}'.format(v[1]), file=DBG_FILE)
        if v[2]: print('info2={}'.format(v[2]), file=DBG_FILE)
        if v[3]: print('info3={}'.format(v[3]), file=DBG_FILE)
        if data is None: return #print something?
        for j in range(h):
            print('    ', file=DBG_FILE, end='')
            for i in range(w):
                print('{}'.format(data[j][i]), file=DBG_FILE, end='')
                self.addCell(cc+i, rr-j, data[j][i])
            print(file=DBG_FILE)
        txt += ' done[{}] undone[{}]'.format(len(self.done), len(self.undone))
        print(  ':END: {}\n'.format(txt), file=DBG_FILE)

    def addShape1(self, c, r, dbg=1): #odd odd
        if dbg: print('addShape1(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        self.addCell(c,   r+1)
        self.addCell(c-1, r)
        self.addCell(c,   r)
        self.addCell(c+1, r)
        self.addCell(c+1, r-1)
        if dbg: self.printData(self.data, 'addShape1() c={} r={}'.format(c, r))
        if dbg: print('addShape1(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShape2(self, c, r, dbg=1): #even even
        if dbg: print('addShape2(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        self.addCell(c-2, r+1)
        self.addCell(c-2, r)
        self.addCell(c-2, r-1)
        self.addCell(c-1, r-1)
        self.addCell(c,   r-1)
        self.addCell(c+1, r-1)
        self.addCell(c+1, r-2)
        if dbg: self.printData(self.data, 'addShape2() c={} r={}'.format(c, r))
        if dbg: print('addShape2(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShape2A(self, c, r, dbg=1): #even even
        if dbg: print('addShape2A(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        self.addCell(c-2, r+1)
        self.addCell(c-2, r)
        self.addCell(c-2, r-1)
        self.addCell(c-1, r-1)
        self.addCell(c,   r-1)
        self.addCell(c+1, r-1)
        self.addCell(c+1, r-2)
        self.addCell(c+1, r)
        self.addCell(c+1, r+1)
        if dbg: self.printData(self.data, 'addShape2A() c={} r={}'.format(c, r))
        if dbg: print('addShape2A(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShape2B(self, c, r, dbg=1): #checkerboard
        if dbg: print('addShape2B(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[j])):
                if (i+j) % 2: self.cells[j][i].color = self.ALIVE
                else:         self.cells[j][i].color = self.ALIVE2
        if dbg: self.printData(self.data, 'addShape2B() c={} r={}'.format(c, r))
        if dbg: print('addShape2B(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShape3(self, c, r, dbg=1): #even odd
        if dbg: print('addShape3(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        self.addCell(c-2, r+1)
        self.addCell(c-2, r)
        self.addCell(c-1, r)
        self.addCell(c,   r)
        self.addCell(c+1, r)
        self.addCell(c+1, r-1)
        if dbg: self.printData(self.data, 'addShape3() c={} r={}'.format(c, r))
        if dbg: print('addShape3(END) c={} r={}'.format(c, r), file=DBG_FILE)

    def addShape4(self, c, r, dbg=1): #odd even
        if dbg: print('addShape4(BGN) c={} r={}'.format(c, r), file=DBG_FILE)
        self.addCell(c-1, r-2)
        self.addCell(c,   r-1)
        self.addCell(c-1, r)
        self.addCell(c+1, r)
        self.addCell(c+1, r+1)
        if dbg: self.printData(self.data, 'addShape4() c={} r={}'.format(c, r))
        if dbg: print('addShape4(END) c={} r={}'.format(c, r), file=DBG_FILE)

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

    def getNNCountHard(self, c, r):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                n += self.data[(r+j+self.nRows)%self.nRows][(c+i+self.nCols)%self.nCols]
        n -= self.data[r][c]
        return n

    def getNNCountWrap(self, c, r, dbg=0):
        n = 0
        for j in range(-1, 2):
            for i in range(-1, 2):
                if r+j >= 0 and c+i >= 0 and r+j < self.nRows and c+i < self.nCols:
                    n += self.data[r+j][c+i]
        n -= self.data[r][c]
        return n

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

    @staticmethod
    def printData(data, reason=''):
        rows, cols = len(data), len(data[0]); area = rows * cols
        print('\n:BGN: printData({}) data[{}x{}={:,}]'.format(reason, rows, cols, area), file=DBG_FILE)
        for r in range(rows-1, -1, -1):
            for c in range(cols):
                if data[r][c] == 0: print(' ', file=DBG_FILE, end='')
                else:               print('X', file=DBG_FILE, end='')
            print(file=DBG_FILE)
        print(':END: printData({}) data[{}x{}={:,}]\n'.format(reason, rows, cols, area), file=DBG_FILE)

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

@window.event
def on_draw():
    t.on_draw()

@window.event
def on_resize(width, height): t.on_resize(width, height)

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    t = TestGui(window)
    pyglet.app.run()

'''
import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key

batch = pyglet.graphics.Batch()
display = pyglet.canvas.get_display()
screens = display.get_screens()
windows = []
for screen in screens:
    windows.append(pyglet.window.Window(screen=screen))

class Test(object):
    def __init__(self):
        super(Test, self).__init__()
        self.ALIVE = (100, 192, 100)
        self.DEAD = (90, 16, 26)
        self.MAJ_GRID_LINE = (255, 0, 0)
        self.NOM_GRID_LINE = (127, 31, 31)
        self.MIN_GRID_LINE = (63, 15, 15)
        (self.data, self.cells, self.lines) = self.grid()

    def grid(self, c=100, r=70, w=10, h=10, p=0, q=0): #c=nCols r=nRows w=cellW h=cellH p=xOff q=yOff
        data, cells, lines = [], [], []
        for j in range(r):
            tmp1, tmp2 = [], []
            for i in range(c):
                tmp1.append(0)
                tmp2.append(shapes.Rectangle(i*w+p, j*h+q, w, h, color=self.DEAD, batch=batch))
            data.append(tmp1)
            cells.append(tmp2)
        for i in range(c+1):
            if   i%50 == 0: lines.append(shapes.Line(i*w+p, q, i*w+p, r*h+q, width=1, color=self.MAJ_GRID_LINE))
            elif i%10 == 0: lines.append(shapes.Line(i*w+p, q, i*w+p, r*h+q, width=1, color=self.NOM_GRID_LINE))
            else:           lines.append(shapes.Line(i*w+p, q, i*w+p, r*h+q, width=1, color=self.MIN_GRID_LINE))
        for j in range(r+1):
            if   j%50 == 0: lines.append(shapes.Line(p, j*h+q, c*w+p, j*h+q, width=1, color=self.MAJ_GRID_LINE))
            elif j%10 == 0: lines.append(shapes.Line(p, j*h+q, c*w+p, j*h+q, width=1, color=self.NOM_GRID_LINE))
            else:           lines.append(shapes.Line(p, j*h+q, c*w+p, j*h+q, width=1, color=self.MIN_GRID_LINE))
        return (data, cells, lines)

    def on_draw(self):
        self.clear()
        self.label.draw()

if __name__ == '__main__':
    window = Test()
    pyglet.app.run()

'''
'''
ALIVE = (100, 192, 100)
DEAD = (90, 16, 26)

def grid(n=100, m=70, w=10, h=10, p=0, q=0):
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

window = pyglet.window.Window(1024, 714)
batch = pyglet.graphics.Batch()
eventLogger = pyglet.window.event.WindowEventLogger()
window.push_handlers(eventLogger)
(cells, lines) = grid(10, 7, 20, 20, 10, 5)
addShape()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.Q and modifiers == key.MOD_CTRL: exit()
    if symbol < 256: print('on_key_press() symbol={}({}) modifiers={}'.format(symbol, chr(symbol), modifiers), flush=True)
    else: print('on_key_press() symbol={} modifiers={}'.format(symbol, modifiers), flush=True)

@window.event
def on_draw():
    window.clear()
    batch.draw()

if __name__ == "__main__":
    pyglet.app.run()
'''
