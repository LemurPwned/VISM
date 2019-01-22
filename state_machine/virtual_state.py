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
        self.buffers = None
        self.refresh()

    @pyqtSlot(int)
    def sampling_change(self, new_sampling_change):
        self.sampling = new_sampling_change
        self.buffers = None
        self.refresh()

    @pyqtSlot(float)
    def ambient_change(self, new_ambient):
        self.ambient = float("%.2f" % new_ambient)
        self.update()

    @pyqtSlot(float)
    def height_change(self, new_height):
        self.height = new_height
        self.buffers = None
        self.refresh()

    @pyqtSlot(float)
    def radius_change(self, new_radius):
        self.radius = new_radius
        self.buffers = None
        self.refresh()

    @pyqtSlot(int)
    def start_layer_change(self, new_layer):
        self.start_layer = new_layer
        self.buffers = None
        self.refresh()

    @pyqtSlot(int)
    def stop_layer_change(self, new_layer):
        self.stop_layer = new_layer
        self.buffers = None
        self.refresh()
