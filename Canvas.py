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

        p_dict = {
                    'color': 'green',
                    'line_style': 'dashed',
                    'marker': '*',
                    'marker_color': 'blue',
                    'marker_size': 3
                    }
        self.canvas_type = 'panel'
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        print(len(self.graph_data))
        self.null_data = [x for x in range(self.iterations)]
        a_handler = self.plot_axis.plot(self.null_data,
            self.graph_data[0:self.i] + self.null_data[self.i:],
            color= p_dict['color'], linestyle=p_dict['line_style'],
            marker=p_dict['marker'], markerfacecolor=p_dict['marker_color'],
            markersize=p_dict['marker_size'])[0]
        self.plot_axis.hpl = a_handler
        self.plot_axis.axis([0, self.iterations, np.min(self.graph_data),
                            np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
        self._CANVAS_ALREADY_CREATED_ = True

    def replot(self):
        self.plot_axis.hpl.set_ydata(np.lib.pad(self.graph_data[:self.i],
                (0, self.iterations-self.i), mode='constant'))
        print(self.i)
        print(self.iterations-self.i)
        print(len(self.graph_data[:self.i]))
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
