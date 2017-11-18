from AnimatedWidget import AnimatedWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy, QPushButton

class AbstractCanvas(AnimatedWidget, FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        #self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self._CANVAS_ALREADY_CREATED_ = False

    def createPlotCanvas(self):
        """
        creates Canvas to be passed to Qt widgets. Creates a general instance of
        matplotlib axis and a particular object of matplotlib canvas type
        """
        pass

    def replot(self):
        """
        replot an axis, change data attached to the plot,
        it specifies the type axis plot will be redrawn i.e. scatterplot, plot
        """
        pass

    def refresh(self):
        self.plot_axis.get_figure().canvas.draw()

    def set_i(self, value):
        self.i = value
        try:
            self.loop_guard()
            self.replot()
            self.refresh()
        except:
            pass
