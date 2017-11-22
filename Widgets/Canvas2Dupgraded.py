import numpy as np
from pyqtgraph import PlotWidget
from AnimatedWidget import AnimatedWidget #can inherit but \
# have to overwrite anyway

class Canvas2Dupgraded(PlotWidget, AnimatedWidget):
        def __init__(self, parent=None):
            super(Canvas2Dupgraded, self).__init__()
            self.plotWidget = PlotWidget(self)
            self._i = 0
            #self.testInitialConditions()
            #self.createPlotCanvas()

        def testInitialConditions(self):
            self.title = "Plot number 1"
            self.iterations = 544
            self.graph_data = np.random.random(self.iterations)

        def createPlotCanvas(self):
            print("working")
            self.plotWidget.setTitle(self.title)
            self.plotWidget.setGeometry(0, 0, 800, 600)
            self.plotWidget.setXRange(0, self.iterations)
            self.plotWidget.setYRange(np.min(self.graph_data), np.max(self.graph_data))
            self.plotWidget.enableAutoRange('xy', False)
            self.plotWidget.plot(self.graph_data[:self._i], pen="r", name="data1")

        def set_i(self, value):
            self._i = value;
            self.plotWidget.plot(self.graph_data[:self._i], pen="r", name="data1") #TODO


        def setPlotParameters(self, param_dict):
            if param_dict != {}:
                self.p_dict = param_dict
            else:
                # set default if not specified
                self.p_dict = {
                    'color': 'green',
                    'line_style': 'dashed',
                    'marker': '*',
                    'marker_color': 'blue',
                    'marker_size': 3
                }

