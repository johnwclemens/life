'''
import pyglet

class HelloWorldWindow(pyglet.window.Window):
    def __init__(self):
        display      = pyglet.canvas.get_display()
        self.screens = display.get_screens()
        super().__init__(screen=self.screens[1], resizable=True, visible=False)
        self.batch = pyglet.graphics.Batch()
#        self.label = pyglet.text.Label('Hello, world', font_name='Times New Roman', font_size=36, x=self.width//2, y=self.height//2, anchor_x='center', anchor_y='center')
        self.label = pyglet.text.Label('ABC', font_name='Lucida Console', font_size=16, x=self.width//2, y=self.height//2, anchor_x='center', anchor_y='center', batch=self.batch)
        self.set_visible(True)

    def on_draw(self):
        self.clear()
        self.batch.draw()
#        self.label.draw()

if __name__ == '__main__':
    window = HelloWorldWindow()
    pyglet.app.run()
'''
import sys
import pyglet
#import pyglet.shapes# as pygshp
#import pyglet.text  # as pygtxt
#import pyglet.window# as pygwin

class TestGuiC(pyglet.window.Window):
    def __init__(self):
        self.ww, self.wh = 1000, 600
        super(TestGuiC, self).__init__(width=self.ww, height=self.wh, resizable=True, visible=False)
        self.batch = pyglet.graphics.Batch()
        self.nc, self.nr = 24, 12
        w, h = self.ww/self.nc, self.wh/self.nr
        self.useCells, self.useLabels, self.useSprites = False, False, True
        if self.useCells:  self._initCells()
        if self.useLabels: self._initLabels()
        if self.useSprites: self._initSprites()
        self._initCBS()
#        if self.useCells:  self.cells = [[pyglet.shapes.Rectangle(c*w, self.wh-h-r*h, w, h, color=COLORS[(c+r)%2], batch=self.batch) for c in range(self.nc)] for r in range(self.nr)]
#        if self.useLabels: self.labels = [[pyglet.text.Label('Ab', font_name='Lucida Console', font_size=16, x=c*w, y=self.wh-h-r*h, width=w, height=h, anchor_x='left', anchor_y='center', align='left', batch=self.batch) for c in range(self.nc)] for r in range(self.nr)]
        self.set_visible(True)

    def _initCells(self):
        w, h = self.ww/self.nc, self.wh/self.nr
        self.cells = []
        for r in range(self.nr):
            tmp = []
            for c in range(self.nc):
                x, y = (self.ww+c*w)/2, self.wh-h-r*h
                tmp.append(pyglet.shapes.Rectangle(x, y, w/2, h, color=COLORS[(c+r)%2], batch=self.batch))
            self.cells.append(tmp)

    def _initLabels(self):
        w, h = self.ww/self.nc, self.wh/self.nr
        self.labels, f, s, n, b = [], 'Lucida Console', 10, 12, self.batch
        for r in range(self.nr):
            tmp = []
            for c in range(self.nc):
                x, y, C = c*w/2, self.wh-h-r*h, (255, 255-20*r, 15+10*c, 255)
                if   c%n==0:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='left',   anchor_y='top',      align='left',   color=C, batch=b))
                elif c%n==1:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='center', anchor_y='top',      align='left',   color=C, batch=b))
                elif c%n==2:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='right',  anchor_y='top',      align='left',   color=C, batch=b))
                elif c%n==3:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='left',   anchor_y='center',   align='center', color=C, batch=b))
                elif c%n==4:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='center', anchor_y='center',   align='center', color=C, batch=b))
                elif c%n==5:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='right',  anchor_y='center',   align='center', color=C, batch=b))
                elif c%n==6:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='left',   anchor_y='bottom',   align='right',  color=C, batch=b))
                elif c%n==7:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='center', anchor_y='bottom',   align='right',  color=C, batch=b))
                elif c%n==8:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='right',  anchor_y='bottom',   align='right',  color=C, batch=b))
                elif c%n==9:  tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='left',   anchor_y='baseline', align='center', color=C, batch=b))
                elif c%n==10: tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='center', anchor_y='baseline', align='center', color=C, batch=b))
                elif c%n==11: tmp.append(pyglet.text.Label('Ab', font_name=f, font_size=s, x=x, y=y, width=w/2, height=h, anchor_x='right',  anchor_y='baseline', align='center', color=C, batch=b))
                else:         print('ERROR: c={} n={} c%%n={}'.format(c, n, c%n)); exit(1)
                print('[{}][{}]{:6.1f},{:6.1f} '.format(r, c, tmp[c].x, tmp[c].y), end='')
            print()
            self.labels.append(tmp)

    def _initSprites(self):
        self.sprites = []
        decoder = pyglet.image.codecs.png.PNGImageDecoder()
        for i, f in enumerate(['C:/Python36/my/tabs/pyglet.png', 'C:/Python36/my/tabs/apple_raw.png']):
            img = pyglet.image.load(f, decoder=decoder)
            sprite = pyglet.sprite.Sprite(img, x=(i+1)*200, y=50, batch=self.batch)
            w, h = sprite.width, sprite.height
            print('w={} h={}'.format(w, h))
            sprite.scale_x, sprite.scale_y = 100/w, 100/h
            self.sprites.append(sprite)

    def _initCBS(self):
        self.CBS = []
        cbp = pyglet.image.CheckerImagePattern((255, 127, 63, 255), (63, 127, 255, 255))
        cbi = cbp.create_image(width=200, height=200)
        cbs = pyglet.sprite.Sprite(img=cbi, x=200, y=150, batch=self.batch)
        self.CBS.append(cbs)
        print('_initCBS() cbs={}'.format(cbs))

    def on_resize(self, width, height):
        ww, wh = self.ww, self.wh
        super().on_resize(width, height)
        self.ww, self.wh = width, height
        w, h = self.ww/self.nc, self.wh/self.nr
        for r in range(self.nr):
            for c in range(self.nc):
                if self.useLabels:
                    self.labels[r][c].x,     self.labels[r][c].y      = c*w/2,           self.wh-h-r*h
                    self.labels[r][c].width, self.labels[r][c].height = w/2,             h
                if self.useCells:
                    self.cells[r][c].x,      self.cells[r][c].y       = (self.ww+c*w)/2, self.wh-h-r*h
                    self.cells[r][c].width,  self.cells[r][c].height  = w/2,             h
        for i in self.CBS:
            i.update(x=200*width/ww, y=200*height/wh, scale_x=width/ww, scale_y=height/wh)
#            i.anchor_x, i.anchor_y = 200, 200
#            i.scale_x, i.scale_y = width/ww, height/wh
#        if self.useImages:
#            for i in range(len(self.images)):
#                    self.images[i].update(scale_x=100/width, scale_y=h)

    def on_draw(self):
        self.clear()
        self.batch.draw()

if __name__ == '__main__':
    DBG_FILE = open(sys.argv[0] + ".log", 'w')
    COLORS = [(127, 127, 127), (66, 60, 144)]
    test = TestGuiC()
    pyglet.app.run()
