import numpy as np
from Widgets.plot_widgets.AbstractCanvas import AbstractCanvas


class Canvas(AbstractCanvas):
    def __init__(self, data_dict):
        super().__init__(self)
        self.shareData(**data_dict)
        self.i = self.current_state
        self.title = self.options['column']
        self.graph_data = self.plot_data[self.title].tolist()
        # override
        self.internal_iterations = len(self.graph_data)
        self.createPlotCanvas()

    def createPlotCanvas(self):
        self.canvas_type = 'panel'
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        try:
            self.null_data = self.plot_data['Oxs_TimeDriver::Simulation time'].tolist()
        except KeyError:
            self.null_data = [x for x in range(self.internal_iterations)]
        a_handler = self.plot_axis.plot(self.null_data,
                                        self.graph_data[0:self.i] + \
                                        self.null_data[self.i:],
                                        color=self.options['color'],
                                        linestyle=self.options['line_style'],
                                        marker=self.options['marker'],
                                        markerfacecolor=self.options['marker_color'],
                                        markersize=self.options['marker_size'])[0]
        self.plot_axis.hpl = a_handler
        self.plot_axis.axis([0, self.internal_iterations, np.min(self.graph_data),
                             np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.internal_iterations))

    def replot(self):
        self.i %= self.internal_iterations
        self.plot_axis.hpl.set_ydata(np.pad(self.graph_data[:self.i],
                                        (0, self.internal_iterations - self.i),
                                    mode='constant', constant_values=(np.nan,)))
        self.plot_axis.set_title('{}/{}'.format(self.i, self.internal_iterations))
