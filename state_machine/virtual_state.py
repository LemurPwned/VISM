from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QObject, pyqtSlot
import numpy as np
import OpenGL.GL as gl


class VirtualStateMachine(QObject):
    OBJ_HANDLER = None

    def __init__(self):
        super(VirtualStateMachine, self).__init__()
        self.color_scheme = None
        self.object_type = None

    @pyqtSlot(int)
    def resolution_change(self, new_resolution_value):
        self.resolution = new_resolution_value
        # reset and compile to the new value
        self.xnodes = self.header['xnodes']
        self.ynodes = self.header['ynodes']
        self.xnodes /= self.sampling
        self.ynodes /= self.sampling
        # recalculate index values
        N = int(self.xnodes * self.ynodes * self.znodes)
        self.indices = self.parser.generateIndices(
            N, int(self.resolution*2)).astype(np.uint32)
        self.refresh()

    @pyqtSlot(int)
    def sampling_change(self, new_sampling_change):
        self.sampling = new_sampling_change
        # reset and compile to the new value
        self.xnodes = self.header['xnodes']
        self.ynodes = self.header['ynodes']
        self.xnodes /= self.sampling
        self.ynodes /= self.sampling
        # recalculate index values
        N = int(self.xnodes * self.ynodes * self.znodes)
        self.indices = self.parser.generateIndices(
            N, int(self.resolution*2)).astype(np.uint32)
        self.refresh()

    @pyqtSlot(float)
    def ambient_change(self, new_ambient):
        self.ambient = float("%.2f" % new_ambient)
        print(self.ambient)
        self.update()

    @pyqtSlot(float)
    def height_change(self, new_height):
        self.height = new_height
        self.refresh()

    @pyqtSlot(float)
    def radius_change(self, new_radius):
        self.radius = new_radius
        self.refresh()
