import matplotlib.pytplot as plt
import matplotlib.animation as animation

class Canvas:
    def __init__(self):
        pass

    def createPlotCanvas(self):
        fig = plt.figure()
        fig.suptitle(title)
        self.ax_pl = plt.subplot(111)
        null_data = [x for x in range(iterations)]
        a_handler = self.ax_pl.plot(null_data,
            graph_data[0:i]+null_data[i:], 'ro')[0]
        self.ax_pl.hpl = a_handler
        self.ax_pl.axis([0, iterations, np.min(graph_data), np.max(graph_data)])
        self.ax_pl.set_autoscale_on(False)
        self.ax_pl.set_title('{}/{}'.format(i, iterations))
