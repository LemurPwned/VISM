from matplotlib import cm
import numpy as np

from ColorPolicy import ColorPolicy

from Widgets.plot_widgets.AbstractCanvas import AbstractCanvas
from multiprocessing_parse import asynchronous_pool_order
from cython_modules.color_policy import multi_iteration_normalize

class CanvasLayer(AbstractCanvas):
    def __init__(self, data_dict):
        super().__init__(self)
        super().shareData(**data_dict)
        super().receivedOptions()
        self.createPlotCanvas()
        self._MINIMUM_PARAMS_ = ['i', 'iterations', 'multiple_data', 'title',
                                 'omf_header', 'current_layer']

    def createPlotCanvas(self):
        self.xc = int(self.omf_header['xnodes'])
        self.yc = int(self.omf_header['ynodes'])
        self.zc = int(self.omf_header['znodes'])

        self.title = 'Single layer'
        self.i = self.current_state
        dx, dy = self.reshape_data()
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        color_array = self.selected_layer[self.i].astype(float)

        scat = self.plot_axis.scatter(dx, dy, c=color_array, cmap=cm.jet)
        self.plot_axis.hpl = scat
        self.fig.colorbar(self.plot_axis.hpl)
        self.plot_axis.axis('scaled')
        self.plot_axis.axis([0, len(dx), 0, len(dy)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
        self._CANVAS_ALREADY_CREATED_ = True
        print("CREATED CANVAS")

    def replot(self):
        color_array = self.selected_layer[self.i].reshape(self.xc * self.yc)
        self.plot_axis.hpl.set_array(color_array)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self):
        """
        reshaping the data so that plotting might happen faster
        """


        if self.normalize:
            multi_iteration_normalize(self.color_vectors)

        self.color_vectors = np.array([x.reshape(self.zc, self.yc * self.xc, 3)[self.layer]
                                       for x in self.color_vectors])

        self.selected_layer = np.array([self.calculate_layer_colors(x)
                               for x in self.color_vectors])
        self.selected_layer = np.array([x.reshape(self.yc, self.xc)
                                for x in self.selected_layer])
        x = np.linspace(0, self.xc, self.xc)
        y = np.linspace(0, self.yc, self.yc)
        dx, dy = np.meshgrid(x, y)
        return dx, dy

    def atomic_reshape(self, x, layer):
        return x.reshape(zc, yc * xc, 3)[layer]

    def calculate_layer_colors(self, x, relative_vector=[0, 1, 0], scale=1):
        norm = np.apply_along_axis(np.linalg.norm, 1, x)
        dot = np.divide(np.array([np.inner(i, relative_vector)
                                  for i in x]), norm)
        angle = np.arccos(dot) ** scale
        angle[np.isnan(angle)] = 0  # get rid of NaN expressions
        return angle

    def setPlotParameters(self, **kwargs):
        pass
