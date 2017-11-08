import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.animation as animation
import numpy as np
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QSizePolicy, QPushButton
from matplotlib.figure import Figure

class Canvas3D(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def createPlotCanvas(self):
        print("PREPARING CANVAS")
        self.canvas_type = 'panel'
        x, y = self.reshape_data()
        self.fig.suptitle(self.title)
        self.ax_sc = self.fig.add_subplot(111)
        scat = self.ax_sc.scatter(x, y, c=tuple(self.layer[self.i]), cmap=cm.jet)
        self.ax_sc.hpl = scat
        self.fig.colorbar(self.ax_sc.hpl)
        self.ax_sc.axis('scaled')
        self.ax_sc.axis([0, len(x), 0, len(y)])
        self.ax_sc.set_autoscale_on(False)
        self.ax_sc.set_title('{}/{}'.format(self.i, self.iterations))
        plt.show()
    def increaseIterator(self):
        self.i += 1

    def refresh(self):
        self.ax_sc.get_figure().canvas.draw()

    def loop(self, scheduler=0.1):
        i = 0
        print("ITERATING")
        while(self.iterations):
            time.sleep(scheduler)
            i += 1
            self.increaseIterator()
            self.refresh()
            self.replot()
            if (i == self.iterations):
                i = 0

    def replot(self):
        self.scat.set_array(np.array(self.layer[i]), dtype=float)
        #change name if you wish
        self.ax_pl.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self):
        '''
        reshaping the data so that plotting might happen faster
        '''
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        self.mulitple_layers = np.array([x.reshape(zc,yc*xc,3)[self.current_layer]
                                        for x in self.multiple_data])
        self.layer = np.array([self.calculate_layer_colors(x)
                                for x in self.mulitple_layers])
        x = np.linspace(0, xc, xc)
        y = np.linspace(0, yc, yc)
        dx, dy = np.meshgrid(x,y)
        return dx, dy

    def parameter_check(self, **kwargs):
        minimum_parameter_list = ['xnodes', 'ynodes', 'znodes',
                                  'xbase', 'ybase', 'zbase']
        for parameter in minimum_parameter_list:
            if not parameter in kwargs.keys():
                print("No matching parameter has been found in the provided list")
                print("minimum_parameter_list is not provided")
                raise TypeError

    def calculate_layer_colors(self, x, relative_vector = [0,1,0], scale=1):
        #TODO: make relate object a variable
        norm = np.apply_along_axis(np.linalg.norm, 1, x)
        dot = np.divide(np.array([np.inner(i, relative_vector)
                                    for i in x]), norm)
        angle = np.arccos(dot)**scale
        angle[np.isnan(angle)] = -1 # get rid of NaN expressions
        return angle

    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main plot iterator
        """
        print("SHARING DATA")
        #TODO: define minimum_list in arguments and force SPECIFIC keys
        for k, v in kwargs.items():
            setattr(self, k, v)
        print("DATA SHARED successfully")
