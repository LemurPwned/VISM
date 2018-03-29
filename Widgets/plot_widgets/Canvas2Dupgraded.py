import numpy as np
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from AnimatedWidget import AnimatedWidget #can inherit but \
# have to overwrite anyway

class Canvas2Dupgraded(PlotWidget, AnimatedWidget):
        def __init__(self, parent=None, data_dict=None):
            super(Canvas2Dupgraded, self).__init__()
            self.shareData(**data_dict)
            self.plotWidget = PlotWidget(self)
            self._i = self.current_state
            self.title = self.options['column']
            self.graph_data = self.odt_data[self.title].tolist()
            self.createPlotCanvas()

        def testInitialConditions(self):
            self.title = "Plot number 1"
            self.iterations = 544
            self.graph_data = np.random.random(self.iterations)

        def createPlotCanvas(self):
            self.plotWidget.setTitle(self.title)
            self.plotWidget.setGeometry(0, 0, 1000, 800)
            self.plotWidget.setXRange(0, self.iterations)
            self.plotWidget.setYRange(np.min(self.graph_data), np.max(self.graph_data))
            self.plotWidget.enableAutoRange('xy', False)
            self.plotWidget.plot(self.graph_data[:self._i],
                                 pen=pg.mkPen(color=self.options['color'][0],
                                          width=self.options['marker_size']),
                                          name="data1")

        def set_i(self, value):
            self._i = value
            if self._i == 0:
                self.plotWidget.clear()
            else:
                self.plotWidget.plot(self.graph_data[:self._i],
                                     pen=pg.mkPen(color=self.options['color'][0],
                                              width=self.options['marker_size']),
                                              name="data1")
