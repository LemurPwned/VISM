import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Canvas:
    def __init__(self):
        pass

    def createPlotCanvas(self):
        self.canvas_type = 'panel'
        self.fig = plt.figure()
        self.fig.suptitle(self.title)
        self.ax_pl = plt.subplot(111)
        self.i = self.i
        self.null_data = [x for x in range(self.iterations)]
        a_handler = self.ax_pl.plot(self.null_data,
            self.graph_data[0:self.i]+self.null_data[self.i:], 'ro')[0]
        self.ax_pl.hpl = a_handler
        self.ax_pl.axis([0, self.iterations, np.min(self.graph_data), np.max(self.graph_data)])
        self.ax_pl.set_autoscale_on(False)
        self.ax_pl.set_title('{}/{}'.format(self.i,self.iterations))

    def replot(self):
        self.ax_pl.hpl.set_ydata(self.graph_data[0:self.i]+self.null_data[self.i:])
        self.ax_pl.set_title('{}/{}'.format(self.i, self.iterations))
        self.ax_pl.get_figure().canvas.draw()

    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main plot iterator
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
