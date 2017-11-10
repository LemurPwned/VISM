import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
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
        dx, dy = self.reshape_data()
        self.fig.suptitle(self.title)
        self.ax_sc = self.fig.add_subplot(111)
        print(self.layer[self.i].shape)
        print(dx.shape)
        color_array = np.random.random((len(dx), len(dy)))
        color_array = self.layer[self.i].astype(float)
        print(color_array)
        # print(np.can_cast(color_array.dtype, float, "same_kind"), color_array.ndim)
        # print(type(self.layer[self.i]))
        # print(self.layer[self.i].dtype)
        # c = mpl.colors.to_rgba_array(color_array)
        # quit()
        scat = self.ax_sc.scatter(dx, dy, c=color_array, cmap=cm.jet)
        self.ax_sc.hpl = scat
        self.fig.colorbar(self.ax_sc.hpl)
        self.ax_sc.axis('scaled')
        self.ax_sc.axis([0, len(dx), 0, len(dy)])
        self.ax_sc.set_autoscale_on(False)
        self.ax_sc.set_title('{}/{}'.format(self.i, self.iterations))

    def increaseIterator(self):
        self.i += 1

    def refresh(self):
        print(self.ax_sc.get_array().shape)
        self.ax_sc.get_figure().canvas.draw()

    def loop(self, scheduler=0.1):
        i = 0
        print("ITERATING")
        while(self.iterations):
            time.sleep(scheduler)
            i += 1
            self.increaseIterator()
            self.replot()
            self.draw()
            if (i == self.iterations):
                i = 0

    def replot(self):
        color_array = self.layer[self.i][0].astype(float)
        self.ax_sc.hpl.set_array(np.array([color_array]))
        #change name if you wish
        self.ax_sc.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self):
        '''
        reshaping the data so that plotting might happen faster
        '''
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        print(self.multiple_data.shape)
        self.multiple_data = np.array([x.reshape(zc,yc*xc,3)[self.current_layer]
                                        for x in self.multiple_data])
        print(self.multiple_data.shape)
        self.layer = np.array([self.calculate_layer_colors(x)
                                for x in self.multiple_data])
        self.layer = np.array([x.reshape(yc, xc) for x in self.layer])
        print("COLOR LAYER SHAPE {}".format(self.layer.shape))
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
        angle[np.isnan(angle)] = 0.1 # get rid of NaN expressions
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
