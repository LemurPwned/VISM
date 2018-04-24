import numpy as np
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from AnimatedWidget import AnimatedWidget

class Canvas2Dupgraded(PlotWidget, AnimatedWidget):
    def __init__(self, parent=None, data_dict=None):
        super(Canvas2Dupgraded, self).__init__()
        self.shareData(**data_dict)
        self.plotWidget = PlotWidget(self)
        self._i = self.current_state
        self.title = self.options['column']
        self.graph_data = self.odt_data[self.title].tolist()
        self.internal_iterations = len(self.graph_data)
        self.createPlotCanvas()

    def createPlotCanvas(self):
        self.null_data = np.array([i for i in range(self.internal_iterations)])
        self.plotWidget.setTitle(self.title)
        self.plotWidget.setGeometry(0, 0, self.geom[0]-60, self.geom[1]-60)
        self.plotWidget.setXRange(0, self.internal_iterations)
        self.plotWidget.setYRange(np.min(self.graph_data), np.max(self.graph_data),
                                  padding=0.1)
        self.plotWidget.enableAutoRange('xy', False)
        self.plotData = self.plotWidget.plot(self.graph_data[:self._i],
                             pen=pg.mkPen(color=self.options['color'][0],
                                      width=self.options['marker_size']),
                                      name="data1", clear=True)

    def on_resize_geometry_reset(self, geom):
        """
        when another widget is promoted, this window must resize too
        this means resetting the graph unfortunately
        """
        self.plotWidget.setGeometry(0, 0, geom[0]-60, geom[1]-60)

    def set_i(self, value, trigger=False):
        self._i = value
        self._i %= self.internal_iterations
        self.plotData.setData(self.null_data[:self._i], self.graph_data[:self._i])
        pg.QtGui.QApplication.processEvents()
