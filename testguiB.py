import sys, os
sys.path.insert(0, os.path.abspath('C:/Python36/my/lib/pyglet'))
import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key

class TestGuiB(pyglet.window.Window):
    def __init__(self):
        super(TestGuiB, self).__init__(width=700, height=400, resizable=True)
        self.ALIVE  = (127, 255, 127)
        self.batch = pyglet.graphics.Batch()
        self.r = shapes.Rectangle(self.width/4, self.height/4, self.width/2, self.height/2, color=self.ALIVE, batch=self.batch)
        self.set_visible()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.r.position = (width/4, height/4)
        self.r.width    = width/2
        self.r.height   = height/2

    def on_draw(self):
        self.clear()
        self.batch.draw()

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    life = TestGuiB()
    pyglet.app.run()
    