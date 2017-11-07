class Animation:
    def __init__(self, odtData, canvas=None, external_iteration=None, update_function=None):
        self.odtData = odtData
        self.canvas = canvas
        self.external_iteration = external_iteration
        self.update_function = update_function
        self.reshape_data()
        self._z = 0
        self._iterator
        drawPlot()

    def drawPlot(self):
        pass

    @z.setter
    def z(self, value):
        self._z = z

    @z.getter
    def z(self):
        return self._z

    @iterator.setter
    def iterator(self, value):
        self._iterator = iterator

    @iterator.getter
    def iterator(self, value):
        return self._iterator

    def reshape_data(self):
        '''
        Z is number of z layer in structure.
        Function is reshaping the data so that plotting might happen faster - in omf files data are in odd order. First we increment x with y = const, z equals 0. If we reach end of x we increment y by one and again increment x with y = const. This function reshapes data structure to 2D (we only need x and y in 2D plot) so we take number of z layer and generate meshgrid to plot in 2D matplotlib
        '''
        xc = int(self.base_data['xnodes'])
        yc = int(self.base_data['ynodes'])
        zc = int(self.base_data['znodes'])
        layers_data = np.array([x.reshape(zc,yc*xc,3)[self._z] for x in self.odtData])
        current_single_layer = np.array([calculate_angles(x)
                                for x in layers_data])
        x = np.linspace(0, xc, xc)
        y = np.linspace(0, yc, yc)
        self.dx, self.dy = np.meshgrid(x,y)



if __name__ == "__main__":
    anim = Animation()
