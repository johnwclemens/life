import pyglet
from pyglet import shapes
from pyglet.window import event

ALIVE = (128, 255, 133)
DEAD = (90, 16, 26)

def grid(nx=100, ny=70, w=10, h=10):
    cells = []
    for i in range(nx):
        tmp = []
        for j in range(ny):
            tmp.append(shapes.Rectangle(i*w, j*h, w, h, color=DEAD, batch=batch))
        cells.append(tmp)
    cells[5][8].color = ALIVE
    cells[6][8].color = ALIVE
    cells[7][8].color = ALIVE
    cells[6][9].color = ALIVE
    return cells

window = pyglet.window.Window(1024, 714)
batch = pyglet.graphics.Batch()
eventLogger = pyglet.window.event.WindowEventLogger()
window.push_handlers(eventLogger)
cells = grid(100, 70, 10, 10)

@window.event
def on_key_press(symbol, modifiers):
    if symbol < 256: print('on_key_press() symbol={}({}) modifiers={}'.format(symbol, chr(symbol), modifiers), flush=True)
    else: print('on_key_press() symbol={} modifiers={}'.format(symbol, modifiers), flush=True)

@window.event
def on_draw():
    window.clear()
    batch.draw()

if __name__ == "__main__":
    pyglet.app.run()
