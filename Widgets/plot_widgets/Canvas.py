import numpy as np
from Widgets.plot_widgets.AbstractCanvas import AbstractCanvas
from pattern_types.Patterns import AbstractGLContextDecorators
from matplotlib.figure import Figure

class Canvas(AbstractCanvas):
    def __init__(self, data_dict, parent=None):
        super().__init__(self)
        self.shareData(**data_dict)
        self.i = self.current_state
        self.triggered = False
        self.createPlotCanvas()

    def construct_triggered_plot(self):
        if self.trigger is not None and self.options['one_one']:
            self.triggered = True
            # shorter list
            self.plot_data = self.plot_data.iloc[self.trigger]
            self.options['line_style'] = 'None'

    def createPlotCanvas(self):
        self.title = self.options['column']
        self.construct_triggered_plot()

        self.graph_data = self.plot_data[self.title].tolist()
        self.internal_iterations = len(self.graph_data)
        self.synchronizedPlot = self.options['synchronizedPlot']

        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        xlabl = "Time"
        try:
            self.null_data = self.plot_data['TimeDriver::Simulation time'].tolist()
        except KeyError:
            self.null_data = [x for x in range(self.internal_iterations)]
            xlabl = "Iteration"

        self.plot_axis.hpl = self.plot_axis.plot(self.null_data,
                                        self.graph_data[0:self.i] + \
                                        self.null_data[self.i:],
                                        color=self.options['color'],
                                        linestyle=self.options['line_style'],
                                        marker=self.options['marker'],
                                        markerfacecolor=self.options['marker_color'],
                                        markersize=self.options['marker_size'])[0]
        self.plot_axis.axis([0, np.max(self.null_data), np.min(self.graph_data),
                             np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_xlabel(xlabl)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.internal_iterations))
        if self.synchronizedPlot == False:
            self.plot_axis.plot(self.graph_data)

    @AbstractGLContextDecorators.recording_decorator
    def replot(self):
        if self.synchronizedPlot == False:
            return
        
        self.i %= self.internal_iterations
        self.plot_axis.hpl.set_ydata(np.pad(self.graph_data[:self.i],
                                        (0, self.internal_iterations - self.i),
                                    mode='constant', constant_values=(np.nan,)))
        self.plot_axis.set_title('{}/{}'.format(self.i, self.internal_iterations))

    def set_i(self, value, trigger=False, record=False, reset=False):
        if self.triggered:
            self.i += 1
        else:
            self.i = value
        self.i %= self.internal_iterations
        self.replot()
        self.plot_axis.get_figure().canvas.draw()
        self.record = record
