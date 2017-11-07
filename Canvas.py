import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QSizePolicy, QPushButton
from matplotlib.figure import Figure

class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=800, height=600, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        #self.title = "default"
        #self.i = 0

    def createPlotCanvas(self):
        #self.fig = plt.figure()
        self.canvas_type = 'panel'
        self.fig.suptitle(self.title)

        self.ax_pl = self.fig.add_subplot(111)
        print("test")
        self.i = self.i
        self.null_data = [x for x in range(self.iterations)]
        a_handler = self.ax_pl.plot(self.null_data,
            self.graph_data[0:self.i] + self.null_data[self.i:], 'ro')[0]
        self.ax_pl.hpl = a_handler
        self.ax_pl.axis([0, self.iterations, np.min(self.graph_data), np.max(self.graph_data)])
        self.ax_pl.set_autoscale_on(False)
        self.ax_pl.set_title('{}/{}'.format(self.i, self.iterations))

    def replot(self):
        self.ax_pl.hpl.set_ydata(self.graph_data[0:self.i]+self.null_data[self.i:])
        self.ax_pl.set_title('{}/{}'.format(self.i, self.iterations))
        self.ax_pl.get_figure().canvas.draw()

    def increaseIterator(self):
        self.i += 1

    def runCanvas(self):
        plt.show()

    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main plot iterator
        """
        #TODO: define minimum_list in arguments and force SPECIFIC keys
        for k, v in kwargs.items():
            setattr(self, k, v)

    def parameter_check(self, **kwargs):
        minimum_parameter_list = ['xnodes', 'ynodes', 'znodes',
                                  'xbase', 'ybase', 'zbase']
        for parameter in minimum_parameter_list:
            if not parameter in kwargs.keys():
                print("No matching parameter has been found in provided list")
                print("minimum_parameter_list is not provided")
                raise TypeError

    def __str__(self):
        return str(self.__dict__)

    def check_instance(self):
        print(self.title)
