from matplotlib import cm
import numpy as np

from ColorPolicy import ColorPolicy
from Widgets.plot_widgets.AbstractCanvas import AbstractCanvas
from multiprocessing_parse import asynchronous_pool_order
from cython_modules.color_policy import multi_iteration_normalize, \
                                        multi_iteration_dot_product

class CanvasLayer(AbstractCanvas):
    def __init__(self, data_dict):
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
        self.xc = int(self.omf_header['xnodes'])
        self.yc = int(self.omf_header['ynodes'])
        self.zc = int(self.omf_header['znodes'])

        self.title = 'Displayed layer {}'.format(self.layer)
        self.i = self.current_state
        dx, dy = self.reshape_data()
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        color_array = self.color_vectors[self.i].astype(float)
        self.color_vectors = self.color_vectors.reshape(self.iterations,
                                                          self.xc*self.yc)

        scat = self.plot_axis.scatter(dx, dy, c=color_array, cmap=cm.jet)
        self.plot_axis.hpl = scat
        self.fig.colorbar(self.plot_axis.hpl)
        self.plot_axis.axis('scaled')
        self.plot_axis.axis([0, len(dx), 0, len(dy)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
        self._CANVAS_ALREADY_CREATED_ = True

    def replot(self):
        self.plot_axis.hpl.set_array(self.color_vectors[self.i])
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self):
        """
        reshaping the data so that plotting might happen faster
        """
        print("DATA!!!")
        print(self.iterations, self.xc, self.yc, self.zc)
        if self.normalize:
            multi_iteration_normalize(self.color_vectors)
        # dot product
        self.color_vectors = np.array(self.color_vectors)
        self.color_vectors = self.color_vectors.reshape(self.iterations,
                                                        self.zc, self.yc,
                                                        self.xc, 3)
        self.color_vectors = self.color_vectors[:, self.layer, :, :, :]
        print(self.iterations, self.xc, self.yc, self.zc)
        self.color_vectors = self.color_vectors.reshape(self.iterations,
                                                            self.xc*self.yc, 3)
        self.color_vectors = asynchronous_pool_order(CanvasLayer.calculate_layer_colors,
                                                        (self.vector_set,),
                                                        self.color_vectors)
        self.color_vectors = np.array(self.color_vectors, dtype=np.float)
        try:
            assert self.color_vectors.shape == (self.iterations, self.xc, self.yc)
        except AssertionError:
            self.color_vectors = self.color_vectors.reshape(self.iterations,
                                                              self.xc, self.yc)
        x = np.linspace(0, self.xc, self.xc)
        y = np.linspace(0, self.yc, self.yc)
        dx, dy = np.meshgrid(x, y)
        return dx, dy

    @staticmethod
    def calculate_layer_colors(x, relative_vector=[0, 1, 0], scale=1):
        dot = np.array([np.inner(i, relative_vector) for i in x])
        angle = np.arccos(dot) ** scale
        angle[np.isnan(angle)] = 0  # get rid of NaN expressions
        return angle
