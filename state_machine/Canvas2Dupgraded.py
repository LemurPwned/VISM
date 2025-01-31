import numpy as np
import os

from pyqtgraph import PlotWidget
import pyqtgraph as pg
from state_machine.AbstractCanvas import AbstractCanvas
from Widgets.plot_widgets.AbstractCanvas import AbstractCanvas
from Windows.PlotSettings import PlotSettings
from processing.multiprocessing_parse import determine_if_plot_triggered


class Canvas2Dupgraded(AbstractCanvas):
    def __init__(self, data_dict=None, parent=None):
        super().__init__(self)
        self.shareData(**data_dict)

        self._i = self.current_state
        self.triggered = True

        # Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plotWidget = PlotWidget(self)

        plot_filename = None
        for filename in os.listdir(self.directory):
            if filename.endswith('.txt') or filename.endswith('.odt'):
                plot_filename = os.path.join(self.directory, filename)
                break
        if plot_filename is None:
            raise ValueError("Plot file .txt or .odt not found!")
        self.plot_data, self.trigger = determine_if_plot_triggered(
            plot_filename)

        self.settings = PlotSettings(
            self.plot_data, eventHandler=self.createPlotCanvas)

    def createPlotCanvas(self, options):
        self.options = options

        self.title = self.options['column']
        self.synchronizedPlot = self.options['synchronizedPlot']
        self.one_onePlot = self.options['one_one']
        self.null_data = self.plot_data[self.options['xcolumn']].tolist()

        self.graph_data = self.plot_data[self.title].tolist()
        self.internal_iterations = len(self.graph_data)

        self.plotWidget.setTitle(self.title)
        self.plotWidget.setLabel('bottom', self.options['xcolumn'])
        self.plotWidget.setGeometry(0, 0, self.geom[0]-60, self.geom[1]-60)
        self.plotWidget.setXRange(0, self.internal_iterations)
        self.plotWidget.setYRange(np.min(self.graph_data), np.max(self.graph_data),
                                  padding=0.1)
        self.plotWidget.enableAutoRange('xy', True)
        if self.synchronizedPlot == False and not self.one_onePlot:
            self.plotData = self.plotWidget.plot(self.null_data, self.graph_data,
                                                 pen=pg.mkPen(color=self.options['color'][0],
                                                              width=self.options['marker_size']),
                                                 name="data1", clear=True)
        else:
            self.plotData = self.plotWidget.plot(self.graph_data[:self._i],
                                                 pen=pg.mkPen(color=self.options['color'][0],
                                                              width=self.options['marker_size']),
                                                 name="data1", clear=True)
        pg.QtGui.QApplication.processEvents()

    def on_resize_geometry_reset(self, geom):
        """
        when another widget is promoted, this window must resize too
        this means resetting the graph unfortunately
        """
        self.geom = geom
        self.plotWidget.setGeometry(0, 0, self.geom[0]-60, self.geom[1]-60)

    def set_i(self, value, trigger=False, record=False, reset=False):
        if self.synchronizedPlot == False and not self.one_onePlot:
            """
            instant plot cannot obstruct one-one plot
            """
            return
        if trigger and self.triggered:
            self._i = self.trigger[value % self.trigger_len]
        else:
            self._i = value
        self._i %= self.internal_iterations
        self.plotData.setData(
            self.null_data[:self._i], self.graph_data[:self._i])
        pg.QtGui.QApplication.processEvents()
        self.plotWidget.setGeometry(0, 0, self.geom[0]-60, self.geom[1]-60)
