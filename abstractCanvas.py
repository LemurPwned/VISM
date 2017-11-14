from abc import abstractmethod, ABC
import time

class AbstractCanvas(ABC):
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

    def increaseIterator(self):
        self.i += 1

    def refresh(self):
        self.plot_axis.get_figure().canvas.draw()

    def loop_guard(self):
        if (self.i >= self.iterations):
            self.i = 0

    def loop(self, scheduler=0.1):
        while(self.iterations):
            time.sleep(scheduler)
            self.increaseIterator()
            self.loop_guard()
            self.refresh()
            self.replot()

    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main plot iterator
        """
        #TODO: define minimum_list in arguments and force SPECIFIC keys
        for k, v in kwargs.items():
            setattr(self, k, v)

    def parameter_check(self, **kwargs):
        minimum_parameter_list = ['xnodes', 'ynodes', 'znodes',
                                  'xbase', 'ybase', 'zbase']
        for parameter in minimum_parameter_list:
            if not parameter in kwargs.keys():
                print("No matching parameter has been found in the provided list")
                print("minimum_parameter_list is not provided")
                raise TypeError
