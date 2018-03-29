import numpy as np
import pyqtgraph.opengl as gl
from AnimatedWidget import AnimatedWidget

class Structure3DScatterWidget(gl.GLViewWidget, AnimatedWidget):
    def __init__(self):
        super(Structure3DScatterWidget, self).__init__()
        self.glViewWidget = gl.GLViewWidget(self)
        self.glViewWidget.opts['distance'] = 30
        self.glViewWidget.show()
        g = gl.GLGridItem() #grid layer
        self.glViewWidget.addItem(g)

    def testInitialConditions(self):
        self.glViewWidget.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
        

w = gl.GLViewWidget()
w.opts['distance'] = 30
w.show()
#w.setGeometry(0,0,800,600)


g = gl.GLGridItem()
w.addItem(g)
pos = np.random.random(size=(1000,3))
pos *= [10,10,10]
pos -= [5,5,0]
#pos[0] = (0,0,0)
color = np.zeros((pos.shape[0], 4))
for i in range(len(color)):
    color[i][0] = 1
    color[i][3] = 0.5
d2 = (pos**2).sum(axis=1)**0.5
size = np.random.random(size=pos.shape[0])*10
sp2 = gl.GLScatterPlotItem(pos=pos, color=color, size=size)
w.addItem(sp2)