import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.animation as animation

from PyQt5.QtWidgets import QSizePolicy, QPushButton
from matplotlib.figure import Figure
from Canvas import Canvas

class CanvasLayer(Canvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        Canvas.__init__(self, parent, width, height, dpi)

    def createPlotCanvas(self):
        self.canvas_type = 'panel'
        dx, dy = self.reshape_data()
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        color_array = self.layer[self.i].astype(float)

        scat = self.plot_axis.scatter(dx, dy, c=color_array, cmap=cm.jet)
        self.plot_axis.hpl = scat
        self.fig.colorbar(self.plot_axis.hpl)
        self.plot_axis.axis('scaled')
        self.plot_axis.axis([0, len(dx), 0, len(dy)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def replot(self):
        color_array = self.layer[self.i].reshape(35*35)
        self.plot_axis.hpl.set_array(color_array)
        #change name if you wish
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self):
        '''
        reshaping the data so that plotting might happen faster
        '''
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        self.multiple_data = np.array([x.reshape(zc,yc*xc,3)[self.current_layer]
                                        for x in self.multiple_data])
        self.layer = np.array([self.calculate_layer_colors(x)
                                for x in self.multiple_data])
        self.layer = np.array([x.reshape(yc, xc) for x in self.layer])
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
        angle[np.isnan(angle)] = 0 # get rid of NaN expressions
        return angle
