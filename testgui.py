import sys, os
sys.path.insert(0, os.path.abspath('C:/Python36/my/lib/pyglet'))
import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key

#window = pyglet.window.Window(width=700, height=400, resizable=True)
display = pyglet.canvas.get_display()
screens = display.get_screens()
windows = []
for screen in screens:
    windows.append(pyglet.window.Window(width=700, height=400, resizable=True, screen=screen, visible=False))

class TestGui(object):
    def __init__(self, window):
        self.ALIVE  = (127, 255, 127)
        self.batch = pyglet.graphics.Batch()
        self.r = shapes.Rectangle(window.width/4, window.height/4, window.width/2, window.height/2, color=self.ALIVE, batch=self.batch)
        self.window = window
        self.window.set_visible()

    def on_resize(self, width, height):
        self.r.position = (width/4, height/4)
        self.r.width    = width/2
        self.r.height   = height/2

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

@pyglet.window.Window.event
def on_resize(width, height):
    life.on_resize(width, height)

@pyglet.window.Window.event
def on_draw():
    life.on_draw()

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    life = TestGui(windows[0])
    pyglet.app.run()
    