import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
from AbstractCanvas import AbstractCanvas

class Canvas(AbstractCanvas):
    def __init__(self):
        super().__init__(self)
        self._MINIMUM_PARAMS_ = ['i', 'iterations', 'graph_data', 'title']

    def createPlotCanvas(self):
        if self.parameter_check():
            msg = "Cannot create canvas"
            raise ValueError(msg)

        self.canvas_type = 'panel'
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        self.null_data = [x for x in range(self.iterations)]
        a_handler = self.plot_axis.plot(self.null_data,
            self.graph_data[0:self.i] + self.null_data[self.i:], 'ro')[0]
        self.plot_axis.hpl = a_handler
        self.plot_axis.axis([0, self.iterations, np.min(self.graph_data),
                            np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
        self._CANVAS_ALREADY_CREATED_ = True

    def replot(self):
        self.plot_axis.hpl.set_ydata(self.graph_data[0:self.i] + \
                                self.null_data[self.i:])
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def loop(self, scheduler=0.1):
        while(self.iterations):
            time.sleep(scheduler)
            self.increaseIterator()
            self.loop_guard()
            self.refresh()
            self.replot()
