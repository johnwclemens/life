import sys, os, math
sys.path.insert(0, os.path.abspath('C:/Python36/my/lib/pyglet'))
import pyglet

def fri(f): return int(math.floor(f+0.5))

class TestGuiB(pyglet.window.Window):
    def __init__(self):
        display = pyglet.canvas.get_display()
        self.screens = display.get_screens()
        ww, wh = 1000, 600
        super(TestGuiB, self).__init__(ww, wh, resizable=True, visible=False)
        self.DATA_SET   = set('.*')
        self.XLATE      = str.maketrans('.*', '01')
        self.COLORS     = [(0, 0, 0), (63, 63, 127), (63, 255, 63)]
        self.batch      = pyglet.graphics.Batch()
        self.shapeKey   = 'MyShape_1'  # 'MyShape_1'  # 'Gosper glider gun'
        self.inName     = 'lexicon-no-wrap.txt'
        self.cells, self.shapes = [], {}
        self.c,     self.r      = 21, 11
        self.parse()
        self.addGrid(ww, wh)
        self.addShape(self.c/2, self.r/2, self.shapeKey)
        self.set_visible()

    def addGrid(self, ww, wh):
        w = ww / (self.c * 2)
        h = wh / (self.r * 2)
#        self.cells = [[pyglet.shapes.Rectangle(i*w, wh-h-j*h, w, h, color=self.COLORS[(i+j) % 2], batch=self.batch) for i in range(self.c)] for j in range(self.r)]
        self.cells = [[pyglet.shapes.Rectangle(i*w, j*h, w, h, color=self.COLORS[(i+j) % 2], batch=self.batch) for i in range(self.c)] for j in range(self.r)]
        for j in range(len(self.cells)):
            for i in range(len(self.cells[0])):
                print('addGrid() cells[{}][{}].color={}'.format(j, i, self.cells[j][i].color))

    def addShape(self, p, q, key='MyShape_1'):
        v = self.shapes[key]
        data = v[0]
        w, h = len(data[0]), len(data)
        c = fri(p-w/2)
        r = fri(q-h/2)
        a = w * h
        txt = 'wc={} wr={} p={} q={} c={} r={} [{}x{}={}]'.format(self.c, self.r, p, q, c, r, w, h, a)
        print('addShape(BGN) {}'.format(txt))
        print('info1={}'.format(v[1]))
        if v[2]: print('info2={}'.format(v[2]))
        if v[3]: print('info3={}'.format(v[3]))
        if data is None: print('addShape data={} is None Nothing to Add'.format(data)); return
        for j in range(h):
            for i in range(w):
                print('{}'.format(data[j][i]), end='')
                if data[j][i] == 1:
                    self.cells[j+r][i+c].color = self.COLORS[2]
#                    print('cells[{}][{}].color={}'.format(j+r, i+c, self.cells[j+r][i+c].color))
            print()
        self.printCells(self.cells, 'addShape()')
        print('addShape(END) {}'.format(txt))

    def printCells(self, cells, reason=''):
        rows, cols = len(cells), len(cells[0]); area = rows * cols
        print('printCells(BGN) {} cells[{}x{}={:,}] COLORS={}'.format(reason, rows, cols, area, self.COLORS))
        for r in range(rows):
            for c in range(cols):
                if   cells[r][c].color == self.COLORS[2]:
                    print('X', end='')
                elif cells[r][c].color == self.COLORS[0] or cells[r][c].color == self.COLORS[1]:
                    print(' ', end='')
                else:
                    print('?', end='')
#                print('printCells() cells[{}][{}].color={}'.format(r, c, cells[r][c].color))
            print()
        print('printCells(END) {} data[{}x{}={:,}] COLORS={}'.format(reason, rows, cols, area, self.COLORS))

    def on_resize(self, width, height):
        super().on_resize(width, height)
        w = width  / (self.c * 2)
        h = height / (self.r * 2)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[0])):
                self.cells[j][i].position = (i*w, j*h)
                self.cells[j][i].width    = w
                self.cells[j][i].height   = h

    def parse(self, dbg=0):
        print('parse(BGN)')
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
                                    print('key=[{}] size=[{} x {}={}]]'.format(key, len(data), len(data[0]), len(data)*len(data[0])))
                                    print('info1=[{}]\ninfo2=[{}]\ninfo3=[{}]'.format(info1, info2, info3))
                                info2 = info3 = ''
                            data = []
                            key = line[1:p]
                            info1 = line[p+1:].strip()
                            v = [None, info1, None, None]
                            self.shapes[key] = v
                            state = 1
                            if dbg: print('[{:.^50}] state={} v0={} v3={} v2={} v1={}'.format(key, state, v[0], v[3], v[2], v[1]))
                    elif dataSet >  self.DATA_SET:
                        info2 += line
                        if dbg: print('info2={}'.format(info2))
                    elif dataSet <= self.DATA_SET:
                        line = line.translate(self.XLATE)
#                        tmp = []
#                        for c in line:
#                            tmp.append(int(c))
#                        data.insert(0, tmp)
                        data.insert(0, [int(c) for c in line])
                        state = 2
                        if dbg: print('    {}'.format(line))
                    elif state == 2:
                        info3 += line
                        self.shapes[key][0] = data
                        state = 0
                        if dbg:
                            print('key=[{}] size=[{} x {}={}]]'.format(key, len(data), len(data[0]), len(data)*len(data[0])))
                            print('info1=[{}]\ninfo2=[{}]\ninfo3=[{}]'.format(info1, info2, info3))
                        data = []
        print('parse(END) len(shapes)={}'.format(len(self.shapes)))
        if dbg: self.printShapes()

    def on_draw(self):
        self.clear()
        self.batch.draw()

#    def addCell(self, c, r, dbg=1):
#        self.cells[r][c].color = self.COLORS[2]
#        if dbg: print('\naddCell() cells[{}][{}].color={}'.format(r, c, self.cells[r][c].color))

if __name__ == '__main__':
    life = TestGuiB()
    pyglet.app.run()
