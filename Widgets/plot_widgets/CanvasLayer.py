from matplotlib import cm
import numpy as np

from Widgets.plot_widgets.AbstractCanvas import AbstractCanvas
from multiprocessing_parse import asynchronous_pool_order
from cython_modules.color_policy import multi_iteration_normalize, \
                                        multi_iteration_dot_product, \
                                        calculate_layer_colors
from copy import deepcopy

class CanvasLayer(AbstractCanvas):
    def __init__(self, data_dict, parent=None):
        super().__init__(self)
        super().shareData(**data_dict)
        super().receivedOptions()
        self.handleOptionalData()
        self.createPlotCanvas()

    def handleOptionalData(self):
        # must handle iterations since these are optional
        try:
            getattr(self, 'iterations')
        except NameError:
            self.iterations = 1
        finally:
            if self.iterations is None:
                self.iterations = 1

    def createPlotCanvas(self):
        self.xc = int(self.file_header['xnodes'])
        self.yc = int(self.file_header['ynodes'])
        self.zc = int(self.file_header['znodes'])

        self.title = 'Displayed layer {}'.format(self.layer)
        self.i = self.current_state

        copy_color_vectors = deepcopy(self.color_vectors)
        self.colors, dx, dy = self.reshape_data(copy_color_vectors)

        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)

        color_array = self.colors[self.i].astype(float)
        self.colors = self.colors.reshape(self.iterations,
                                          self.xc*self.yc)

        scat = self.plot_axis.scatter(dx, dy, c=color_array, cmap=cm.jet)
        self.plot_axis.hpl = scat
        self.fig.colorbar(self.plot_axis.hpl)
        self.plot_axis.axis('scaled')
        self.plot_axis.axis([0, len(dx), 0, len(dy)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def replot(self):
        self.plot_axis.hpl.set_array(self.colors[self.i])
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self, copy_color_vectors):
        """
        reshaping the data so that plotting might happen faster
        """
        if self.normalize:
            multi_iteration_normalize(copy_color_vectors)
        # dot product
        copy_color_vectors = np.array(copy_color_vectors)
        copy_color_vectors = copy_color_vectors.reshape(self.iterations,
                                                        self.zc, self.yc,
                                                        self.xc, 3)
        copy_color_vectors = copy_color_vectors[:, self.layer, :, :, :]
        copy_color_vectors = copy_color_vectors.reshape(self.iterations,
                                                            self.xc*self.yc, 3)
        copy_color_vectors = asynchronous_pool_order(calculate_layer_colors,
                                                     (self.vector_set,),
                                                     copy_color_vectors)
        copy_color_vectors = np.array(copy_color_vectors, dtype=np.float)
        try:
            assert copy_color_vectors.shape == (self.iterations, self.xc, self.yc)
        except AssertionError:
            copy_color_vectors = copy_color_vectors.reshape(self.iterations,
                                                              self.xc, self.yc)
        x = np.linspace(0, self.xc, self.xc)
        y = np.linspace(0, self.yc, self.yc)
        dx, dy = np.meshgrid(x, y)
        return copy_color_vectors, dx, dy

    def set_i(self, value, trigger=False, record=False):
        if trigger:
            self.i += 1
        else:
            self.i = value
        self.i %= self.iterations
        self.replot()
        self.plot_axis.get_figure().canvas.draw()
