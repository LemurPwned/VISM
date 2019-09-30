import numpy as np
import os

from Windows.PlotSettings import PlotSettings
from state_machine.AbstractCanvas import AbstractCanvas
from pattern_types.Patterns import AbstractGLContextDecorators
from matplotlib.figure import Figure
from processing.multiprocessing_parse import getPlotData
from PyQt5.QtWidgets import (QApplication, QOpenGLWidget, QWidget)


class Canvas(AbstractCanvas, QWidget):
    def __init__(self, data_dict, parent=None):
        super().__init__(self)
        self.shareData(**data_dict)
        self.i = self.current_state
        self.triggered = True
        self.q = None
        self.worker = None
        plot_filename = None
        for filename in os.listdir(self.directory):
            if filename.endswith('.txt') or filename.endswith('.odt'):
                plot_filename = os.path.join(self.directory, filename)
                break
        if plot_filename is None:
            raise ValueError("Plot file .txt or .odt not found!")
        self.plot_data, stages = getPlotData(plot_filename)
        print("STARTING OFF WITH PLT")
        self.settings = PlotSettings(
            self.plot_data, eventHandler=self.createPlotCanvas)

    def construct_triggered_plot(self):
        if self.trigger is not None and self.options['one_one']:
            self.triggered = False
            # shorter list
            self.plot_data = self.plot_data.iloc[self.trigger]
            """
            this displays only datapoints that match exactly the 
            view on the 3D animation i.e. one-one plot
            """
            self.options['line_style'] = 'None'

    def createPlotCanvas(self, options):
        self.options = options
        self.title = self.options['column']
        self.xcol = self.options['xcolumn']
        self.construct_triggered_plot()
        self.graph_data = self.plot_data[self.title].tolist()
        self.internal_iterations = len(self.graph_data)
        self.synchronizedPlot = self.options['synchronizedPlot']
        self.one_onePlot = self.options['one_one']

        self.plot_axis = self.fig.add_subplot(111)
        self.null_data = self.plot_data[self.xcol].tolist()
        """
        Previous setup called for Time or iteration on the xaxis
        this is no longer a case
        xlabl = "Time"
        try:
            self.null_data = self.plot_data['TimeDriver::Simulation time'].tolist()
        except KeyError:
            self.null_data = [x for x in range(self.internal_iterations)]
            xlabl = "Iteration"
        """
        if self.synchronizedPlot == False and not self.one_onePlot:
            self.plot_axis.plot(self.null_data, self.graph_data,
                                color=self.options['color'],
                                linestyle=self.options['line_style'],
                                marker=self.options['marker'],
                                markerfacecolor=self.options['marker_color'],
                                markersize=self.options['marker_size'])
        else:
            self.plot_axis.hpl = self.plot_axis.plot(self.null_data,
                                                     self.graph_data[0:self.i] +
                                                     self.null_data[self.i:],
                                                     color=self.options['color'],
                                                     linestyle=self.options['line_style'],
                                                     marker=self.options['marker'],
                                                     markerfacecolor=self.options['marker_color'],
                                                     markersize=self.options['marker_size'])[0]
        self.plot_axis.axis([np.min(self.null_data), np.max(self.null_data),
                             np.min(self.graph_data), np.max(self.graph_data)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_xlabel(self.xcol)
        self.plot_axis.set_ylabel(self.title)
        self.plot_axis.set_title(
            '{}/{}'.format(self.i, self.internal_iterations))

    @AbstractGLContextDecorators.recording_decorator
    def replot(self):
        if self.synchronizedPlot == False and not self.one_onePlot:
            """
            instant plot cannot obstruct one-one plot
            """
            return
        self.i %= self.internal_iterations
        self.plot_axis.hpl.set_xdata(np.pad(self.null_data[:self.i],
                                            (0, self.internal_iterations - self.i),
                                            mode='constant', constant_values=(np.nan,)))
        self.plot_axis.hpl.set_ydata(np.pad(self.graph_data[:self.i],
                                            (0, self.internal_iterations - self.i),
                                            mode='constant', constant_values=(np.nan,)))
        self.plot_axis.set_title(
            '{}/{}'.format(self.i, self.internal_iterations))

    def set_i(self, value, trigger=False, record=False, reset=False):
        if trigger and self.triggered:
            self.i = self.trigger[value]
        else:
            self.i = value
        self.i %= self.internal_iterations
        self.replot()
        self.plot_axis.get_figure().canvas.draw()
        self.record = record
