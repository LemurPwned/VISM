from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QObject, pyqtSlot
import numpy as np
import OpenGL.GL as gl


class VirtualStateMachine(QObject):
    def handle_buffer_flush(func_clr):
        def buffer_flush(self, new_val):
            # nullify the buffers (single instance so it's ok)
            self.buffers = None
            func_clr(self, new_val)
        return buffer_flush

    def __init__(self):
        super(VirtualStateMachine, self).__init__()
        self.color_scheme = None
        self.object_type = None

    @pyqtSlot(int)
    @handle_buffer_flush
    def resolution_change(self, new_resolution_value):
        self.resolution = new_resolution_value
        self.buffers = None
        self.refresh()

    @pyqtSlot(int)
    @handle_buffer_flush
    def sampling_change(self, new_sampling_change):
        self.sampling = new_sampling_change
        self.refresh()

    @pyqtSlot(float)
    def ambient_change(self, new_ambient):
        self.ambient = float("%.2f" % new_ambient)
        self.update()

    @pyqtSlot(float)
    @handle_buffer_flush
    def height_change(self, new_height):
        self.height = new_height
        self.refresh()

    @pyqtSlot(float)
    @handle_buffer_flush
    def radius_change(self, new_radius):
        self.radius = new_radius
        self.refresh()

    @pyqtSlot(int)
    @handle_buffer_flush
    def start_layer_change(self, new_layer):
        self.start_layer = new_layer
        self.refresh()

    @pyqtSlot(int)
    @handle_buffer_flush
    def stop_layer_change(self, new_layer):
        self.stop_layer = new_layer
        self.refresh()
