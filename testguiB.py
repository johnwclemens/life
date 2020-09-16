import sys, os
sys.path.insert(0, os.path.abspath('C:/Python36/my/lib/pyglet'))
import pyglet

class TestGuiB(pyglet.window.Window):
    def __init__(self):
        display = pyglet.canvas.get_display()
        self.screens = display.get_screens()
#        self.auxwin = pyglet.window.Window(width=900, height=500, resizable=True, screen=self.screens[0], visible=False)
#        self.auxwin.set_visible()
#        super(TestGuiB, self).__init__(screen=self.screens[1], resizable=True, visible=False)
        ww, wh = 1000, 600
        super(TestGuiB, self).__init__(ww, wh, resizable=True, visible=False)
        self.COLORS  = [(0, 0, 0), (127, 255, 127)]
        self.batch = pyglet.graphics.Batch()
        self.cells = []
        self.c, self.r = 20, 10
        self.addCells(ww, wh)
        self.set_visible()

    def addCells(self, ww, wh):
        w = ww / (self.c * 2)
        h = wh / (self.r * 2)
        for j in range(self.r):
            tmp = []
            for i in range(self.c):
#                tmp.append(pyglet.shapes.Rectangle(i*w, j*h, w, h, color=self.COLORS[(i+j) % 2], batch=self.batch))
#                tmp.append(pyglet.shapes.Rectangle(i*w, wh-((j+1)*h), w, h, color=self.COLORS[(i+j) % 2], batch=self.batch))
                tmp.append(pyglet.shapes.Rectangle(i*w, wh-h-j*h, w, h, color=self.COLORS[(i+j) % 2], batch=self.batch))
            self.cells.append(tmp)
        self.cells[0][0].color = (127, 127, 255)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        return
        w = width  / (self.c * 2)
        h = height / (self.r * 2)
        for j in range(self.r):
            for i in range(self.c):
                self.cells[j][i].position = (i*w, j*h)
                self.cells[j][i].width    = w
                self.cells[j][i].height   = h

    def on_draw(self):
        self.clear()
        self.batch.draw()

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    life = TestGuiB()
    pyglet.app.run()
