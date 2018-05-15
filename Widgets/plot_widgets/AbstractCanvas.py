from AnimatedWidget import AnimatedWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy, QPushButton
import time
import os

class AbstractCanvas(AnimatedWidget, FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self._CANVAS_ALREADY_CREATED_ = False
        self.subdir = "Canvas" + str(AnimatedWidget.WIDGET_ID)
        AnimatedWidget.WIDGET_ID += 1


    def handleOptionalData(self):
        super().handleOptionalData()
        # must handle iterations since these are optional
        try:
            getattr(self, 'trigger')
        except NameError:
            self.trigger = None

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

    def loop_guard(self):
        self.i %= self.internal_iterations

    def screenshot_manager(self):
        """
        saves the screenshot to the folder specified in screenshot_dir
        """
        # fetch dimensions for highest resolution
        try:
            if os.path.basename(self.screenshot_dir) != self.subdir:
                self.screenshot_dir = os.path.join(self.screenshot_dir,
                                                                self.subdir)
            self.fig.savefig(os.path.join(self.screenshot_dir,
                                        str(self.i).zfill(4) + ".png"))
        except FileNotFoundError:
            # if basic dir not found, create it and save there
            os.makedirs(self.screenshot_dir)
            self.fig.savefig(os.path.join(self.screenshot_dir,
                                        str(self.i).zfill(4) + ".png"))


    def set_i(self, value, trigger=False, record=False):
        self.i = value
        self.loop_guard()
        self.replot()
        self.plot_axis.get_figure().canvas.draw()
        if record:
            self.screenshot_manager()

    def loop(self, scheduler=0.1):
        while (self.iterations):
            time.sleep(scheduler)
            self.increaseIterator()
            self.loop_guard()
            self.refresh()
            self.replot()
