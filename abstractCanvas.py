from abc import abstractmethod, ABC
import time
from AnimatedWidget import AnimatedWidget

class AbstractCanvas(ABC, AnimatedWidget):
    @abstractmethod
    def createPlotCanvas(self):
        """
        creates Canvas to be passed to Qt widgets. Creates a general instance of
        matplotlib axis and a particular object of matplotlib canvas type
        """
        pass

    @abstractmethod
    def replot(self):
        """
        replot an axis, change data attached to the plot,
        it specifies the type axis plot will be redrawn i.e. scatterplot, plot
        """
        pass

    def refresh(self):
        self.plot_axis.get_figure().canvas.draw()
