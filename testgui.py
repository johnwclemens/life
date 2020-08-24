import pyglet
from pyglet import shapes
from pyglet.window import event
from pyglet.window import key

class HelloWorldWindow(pyglet.window.Window):
    def __init__(self):
        super(HelloWorldWindow, self).__init__()

        self.label = pyglet.text.Label('Hello, world!')

    def on_draw(self):
        self.clear()
        self.label.draw()

if __name__ == '__main__':
    window = HelloWorldWindow()
    pyglet.app.run()

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
