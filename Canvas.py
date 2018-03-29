import numpy as np
from AbstractCanvas import AbstractCanvas


class Canvas(AbstractCanvas):
    def __init__(self, data_dict):
        super().__init__(self)
        self.shareData(**data_dict)
        self._MINIMUM_PARAMS_ = ['i', 'iterations', 'graph_data', 'title']
        self.i = self.current_state
        self.title = self.options['column']
        self.graph_data = self.odt_data[self.title].tolist()
        self.createPlotCanvas()

    def createPlotCanvas(self):
        self.canvas_type = 'panel'
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        self.null_data = [x for x in range(self.iterations)]
        a_handler = self.plot_axis.plot(self.null_data,
                                        self.graph_data[0:self.i] + \
                                        self.null_data[self.i:],
                                        color=self.options['color'],
                                        linestyle=self.options['line_style'],
                                        marker=self.options['marker'],
                                        markerfacecolor=self.options['marker_color'],
                                        markersize=self.options['marker_size'])[0]
        self.plot_axis.hpl = a_handler
        self.plot_axis.axis([0, self.iterations, np.min(self.graph_data),
                             np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
        self._CANVAS_ALREADY_CREATED_ = True

    def replot(self):
        self.loop_guard()
        self.plot_axis.hpl.set_ydata(np.lib.pad(self.graph_data[:self.i],
                                                (0, self.iterations - self.i),
                                                mode='constant'))
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
