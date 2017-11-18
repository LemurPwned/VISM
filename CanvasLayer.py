import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
import numpy as np
import matplotlib.animation as animation

from AbstractCanvas import AbstractCanvas

class CanvasLayer(AbstractCanvas):
    def __init__(self):
        super().__init__(self)
        self._MINIMUM_PARAMS_ = ['i', 'iterations', 'multiple_data', 'title',
                                    'omf_header', 'current_layer']

    def createPlotCanvas(self):
        if self.parameter_check():
            msg = "Cannot create layer canvas"
            raise ValueError(msg)

        self.canvas_type = 'panel'
        dx, dy = self.reshape_data()
        self.fig.suptitle(self.title)
        self.plot_axis = self.fig.add_subplot(111)
        color_array = self.layer[self.i].astype(float)

        scat = self.plot_axis.scatter(dx, dy, c=color_array, cmap=cm.jet)
        self.plot_axis.hpl = scat
        self.fig.colorbar(self.plot_axis.hpl)
        self.plot_axis.axis('scaled')
        self.plot_axis.axis([0, len(dx), 0, len(dy)])
        self.plot_axis.set_autoscale_on(False)
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))
        self._CANVAS_ALREADY_CREATED_ = True

    def replot(self):
        color_array = self.layer[self.i].reshape(35*35)
        self.plot_axis.hpl.set_array(color_array)
        #change name if you wish
        self.plot_axis.set_title('{}/{}'.format(self.i, self.iterations))

    def reshape_data(self):
        '''
        reshaping the data so that plotting might happen faster
        '''
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        self.multiple_data = np.array([x.reshape(zc,yc*xc,3)[self.current_layer]
                                        for x in self.multiple_data])
        self.layer = np.array([self.calculate_layer_colors(x)
                                for x in self.multiple_data])
        self.layer = np.array([x.reshape(yc, xc) for x in self.layer])
        x = np.linspace(0, xc, xc)
        y = np.linspace(0, yc, yc)
        dx, dy = np.meshgrid(x,y)
        return dx, dy

    def calculate_layer_colors(self, x, relative_vector = [0,1,0], scale=1):
        #TODO: make relate object a variable
        norm = np.apply_along_axis(np.linalg.norm, 1, x)
        dot = np.divide(np.array([np.inner(i, relative_vector)
                                    for i in x]), norm)
        angle = np.arccos(dot)**scale
        angle[np.isnan(angle)] = 0 # get rid of NaN expressions
        return angle
