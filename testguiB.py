import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key
import sys, os, copy
sys.path.insert(0, os.path.abspath('../lib'))
import cmdArgs

#display = pyglet.canvas.get_display()
#screens = display.get_screens()
#windows = []
#for screen in screens:
#    windows.append(pyglet.window.Window(screen=screen))

window = pyglet.window.Window(visible=False, resizable=True)
#image = pyglet.image.SolidColorImagePattern((255,255,255,255)).create_image(200, 150)

class TestGuiB(object):
    def __init__(self, window):
        self.ALIVE = (127, 255, 127)
        self.DEAD =  (31, 0, 127)
        self.DEAD2 = (15, 0, 63)
        self.MIN_GRID_LINE = (255, 127, 127)
        self.NOM_GRID_LINE = (127, 127, 255)
        self.MAJ_GRID_LINE = (127, 255, 127)
        self.argMap = {}
        self.argMap = cmdArgs.parseCmdLine(dbg=1)
        print('argMap={}'.format(self.argMap), file=DBG_FILE)
        if 's' in self.argMap and len(self.argMap['s'])  > 0: self.shape = int(self.argMap['s'][0])
#        self.bg = pyglet.sprite.Sprite(pyglet.image.load('bg.png'), batch=self.batch)
        self.window = window
        if self.shape == 1:
            self.addGrid(c=19, r=11)
            self.addShape1(int(self.c/2), int(self.r/2))
        elif self.shape == 2:
            self.addGrid2(c=20, r=12) #c=20, r=12
            self.addShape2(int(self.c/2), int(self.r/2))
        elif self.shape == 3:
            self.addGrid(c=20, r=11)
            self.addShape3(int(self.c/2), int(self.r/2))
        self.window.set_visible()
    '''
    def addGrid(self, c=100, r=75, ww=1900, wh=1150, dbg=1):
        self.batch = pyglet.graphics.Batch()
        self.c, self.r, p, q = c, r, 0, 0
        self.window.set_size(ww, wh)
        self.ww, self.wh = self.window.get_size()
        w = self.w = self.ww / self.c
        h = self.h = self.wh / self.r
        if c % 2 == 1: p = -w / 2
        if r % 2 == 1: q =  h / 2
        self.data, self.cells, self.lines = [], [], []
        if dbg: print('addGrid(BGN) c={} r={} ww={} wh={} w={} h={}'.format(c, r, ww, wh, w, h), file=DBG_FILE)
        for j in range(r):
            tmp1, tmp2 = [], []
            for i in range(c):
                tmp1.append(0)
                tmp2.append(shapes.Rectangle(int(i*w), int(j*h), int(w), int(h), color=self.DEAD, batch=self.batch))
            self.data.append(tmp1)
            self.cells.append(tmp2)
        for i in range(c+1):
            if   int(i*w+p)%25 == 0: self.lines.append(shapes.Line(int(i*w+p), int(q), int(i*w+p), int(r*h+q), width=1, color=self.MAJ_GRID_LINE, batch=self.batch))
            elif int(i*w+p)% 5 == 0: self.lines.append(shapes.Line(int(i*w+p), int(q), int(i*w+p), int(r*h+q), width=1, color=self.NOM_GRID_LINE, batch=self.batch))
            else:                    self.lines.append(shapes.Line(int(i*w+p), int(q), int(i*w+p), int(r*h+q), width=1, color=self.MIN_GRID_LINE, batch=self.batch))
        for j in range(r+1):
            if   int(j*h+q)%25 == 0: self.lines.append(shapes.Line(int(p), int(j*h+q), int(c*w+p), int(j*h+q), width=1, color=self.MAJ_GRID_LINE, batch=self.batch))
            elif int(j*h+q)% 5 == 0: self.lines.append(shapes.Line(int(p), int(j*h+q), int(c*w+p), int(j*h+q), width=1, color=self.NOM_GRID_LINE, batch=self.batch))
            else:                    self.lines.append(shapes.Line(int(p), int(j*h+q), int(c*w+p), int(j*h+q), width=1, color=self.MIN_GRID_LINE, batch=self.batch))
        if dbg: print('addGrid(END) c={} r={} ww={} wh={} w={} h={}'.format(self.c, self.r, self.ww, self.wh, self.w, self.h), file=DBG_FILE)
    '''
#        for i in range(-int(c/2), int(c/2+1)):
#        for j in range(-int(r/2), int(r/2+1)):
    def addGrid2(self, c=100, r=75, ww=1900, wh=1150, dbg=1):
        self.batch = pyglet.graphics.Batch()
        x = 0 #ww / 2
        y = 0 #wh / 2
        self.c, self.r, p, q = c, r, 0, 0
#        self.window.set_location(0, 0)
#        self.window.set_size(ww, wh)
#        ww -= 2; wh -= 2
#        self.ww, self.wh = ww, wh
        self.window.set_size(ww, wh)
        self.ww, self.wh = self.window.get_size()
        w = self.w = self.ww / self.c
        h = self.h = self.wh / self.r
#        if c % 2 == 1: p = -w / 2
#        if r % 2 == 1: q =  h / 2
        self.data, self.cells, self.clines, self.rlines = [], [], [], []
        if dbg: print('addGrid(BGN) w={:6.2f} h={:6.2f} c={} r={} ww={} wh={} x={:6.2f} y={:6.2f}'.format(w, h, c, r, ww, wh, x, y), file=DBG_FILE)
        for j in range(r):
            tmp1, tmp2 = [], []
            for i in range(c):
                tmp1.append(0)
                if (i+j) % 2: color = self.DEAD
                else:         color = self.DEAD2
                tmp2.append(shapes.Rectangle(int(i*w+x), int(j*h+y), int(w), int(h), color=color, batch=self.batch))
            self.data.append(tmp1)
            self.cells.append(tmp2)
        for i in range(c+1):
            print('i={:4} w={:6.2f} x={:6.2f} i*w={:7.2f} {:4} i*w+x={:7.2f} {:4}'.format(i, w, x, i*w, int(i*w), i*w+x, int(i*w+x)), file=DBG_FILE)
            if   (10+i) % 4 == 0: self.clines.append(shapes.Line(int(i*w+x), int(y), int(i*w+x), int(r*h+y), width=3, color=self.MAJ_GRID_LINE, batch=self.batch))
            elif (10+i) % 2 == 0: self.clines.append(shapes.Line(int(i*w+x), int(y), int(i*w+x), int(r*h+y), width=3, color=self.NOM_GRID_LINE, batch=self.batch))
            else:            self.clines.append(shapes.Line(int(i*w+x), int(y), int(i*w+x), int(r*h+y), width=3, color=self.MIN_GRID_LINE, batch=self.batch))
        print(file=DBG_FILE)
        for j in range(r+1):
            print('j={:4} h={:6.2f} y={:6.2f} j*h={:7.2f} {:4} j*h+y={:7.2f} {:4}'.format(j, h, y, j*h, int(j*h), j*h+y, int(j*h+y)), file=DBG_FILE)
            if   (10+j) % 4 == 0: self.rlines.append(shapes.Line(int(x), int(j*h+y), int(c*w+x), int(j*h+y), width=3, color=self.MAJ_GRID_LINE, batch=self.batch))
            elif (10+j) % 2 == 0: self.rlines.append(shapes.Line(int(x), int(j*h+y), int(c*w+x), int(j*h+y), width=3, color=self.NOM_GRID_LINE, batch=self.batch))
            else:            self.rlines.append(shapes.Line(int(x), int(j*h+y), int(c*w+x), int(j*h+y), width=3, color=self.MIN_GRID_LINE, batch=self.batch))
        if dbg: print('addGrid(END) w={:6.2f} h={:6.2f} c={} r={} ww={} wh={} x={:6.2f} y={:6.2f}'.format(self.w, self.h, self.c, self.r, self.ww, self.wh, x, y), file=DBG_FILE)

#        for i in range(int(len(self.clines)/2-1)):
#        for j in range(int(len(self.rlines)/2-1), len(self.rlines)-1):
    def on_resize(self, width, height, dbg=1):
        return
        if dbg: print('on_resize(BGN) width={} height={} ww={} wh={} w={} h={}'.format(width, height, self.ww, self.wh, self.w, self.h), file=DBG_FILE)
        c, r = self.c, self.r
        ww = self.ww = width
        wh = self.wh = height
        w = self.w = self.ww / self.c
        h = self.h = self.wh / self.r
        if dbg: print('on_resize() w={:6.2f} h={:6.2f} ww={} wh={} x={:6.2f} y={:6.2f}'.format(w, h, ww, wh, x, y), file=DBG_FILE)
        for j in range(len(self.cells)):
            for i in range(len(self.cells[j])):
                self.cells[j][i].position = (int(i*w+x), int(j*h+y))
                self.cells[j][i].width = int(w)
                self.cells[j][i].height = int(h)
        for i in range(len(self.clines)):
            self.clines[i].position = (int(i*w+x), int(y), int(i*w+x), int(r*h+y))
            if dbg: print('i={:4} i*w+x={:6.2f} y={} r*h+y={:7.2f}'.format(i, i*w+x, y, r*h+y), file=DBG_FILE)
        print(file=DBG_FILE)
        for j in range(len(self.rlines)):
            self.rlines[j].position = (int(x), int(j*h+y), int(c*w+x), int(j*h+y))
            if dbg: print('j={:4} j*h+y={:6.2f} x={} c*w+x={:7.2f}'.format(j, j*h+y, x, c*w+x), file=DBG_FILE)
        if dbg: print('on_resize(END) ww={} wh={} w={:6.2f} h={:6.2f}'.format(self.ww, self.wh, self.w, self.h), file=DBG_FILE)

    def addShape1(self, c, r, dbg=1):
        self.addCell(c,   r+1)
        self.addCell(c-1, r)
        self.addCell(c,   r)
        self.addCell(c+1, r)
        self.addCell(c+1, r-1)
        if dbg: self.printData(self.data, 'addShape1() c={} r={}'.format(c, r))

    def addShape2(self, c, r, dbg=1):
        self.addCell(c-2, r+1)
        self.addCell(c-2, r)
        self.addCell(c-2, r-1)
        self.addCell(c-1, r-1)
        self.addCell(c,   r-1)
        self.addCell(c+1, r-1)
        self.addCell(c+1, r-2)
        if dbg: self.printData(self.data, 'addShape2() c={} r={}'.format(c, r))

    def addShape3(self, c, r, dbg=1):
        self.addCell(c-2, r+1)
        self.addCell(c-2, r)
        self.addCell(c-1, r)
        self.addCell(c,   r)
        self.addCell(c+1, r)
        self.addCell(c+1, r-1)
        if dbg: self.printData(self.data, 'addShape3() c={} r={}'.format(c, r))

    def addCell(self, c, r, dbg=1):
        if dbg: print('\n:BGN: addCell() c={} r={}'.format(c, r), file=DBG_FILE)
#        if self.data[r][c] == 0: self.pop += 1
        self.data[r][c] = 1
        self.cells[r][c].color = self.ALIVE
        if dbg: print(':END: addCell() c={} r={} data[r][c]={}\n'.format(c, r, self.data[r][c]), file=DBG_FILE)

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
#        image.blit(0, 0)
        self.batch.draw()

@window.event
def on_draw():
    t.on_draw()

@window.event
def on_resize(width, height): t.on_resize(width, height)

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    t = TestGuiB(window)
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