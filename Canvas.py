import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QSizePolicy, QPushButton
from matplotlib.figure import Figure

class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self._i = 0

    def createPlotCanvas(self):
        self.canvas_type = 'panel'
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        self._i = self.i
        self.null_data = [x for x in range(self.iterations)]
        a_handler = self.plot_axis.plot(self.null_data,
            self.graph_data[0:self._i] + self.null_data[self._i:], 'ro')[0]
        self.plot_axis.hpl = a_handler
        self.plot_axis.axis([0, self.iterations, np.min(self.graph_data),
                            np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
<<<<<<< HEAD
        self.plot_axis.set_title('{}/{}'.format(self._i, self.iterations))

    def replot(self):
        self.plot_axis.hpl.set_ydata(self.graph_data[0:self._i] + \
                                self.null_data[self._i:])
        self.plot_axis.set_title('{}/{}'.format(self._i, self.iterations))

    def set_i(self, value):
        self._i = value
        try:
            self.loop_guard()
            self.replot()
            self.refresh()
        except:
            pass

    def refresh(self):
        self.plot_axis.get_figure().canvas.draw()

    def loop_guard(self):
        if (self.i >= self.iterations):
            self.i = 0

    def loop(self, scheduler=0.1):
        while(self.iterations):
            time.sleep(scheduler)
            self.increaseIterator()
            self.loop_guard()
            self.refresh()
            self.replot()

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
                print("No matching parameter has been found in the provided list")
                print("minimum_parameter_list is not provided")
                raise TypeError

    def __str__(self):
        return str(self.__dict__)

    def check_instance(self):
        print(self.title)
