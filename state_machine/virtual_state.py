from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QObject, pyqtSlot
import numpy as np
import OpenGL.GL as gl


class VirtualStateMachine(QObject):
    def handle_buffer_flush(func_clr):
        def buffer_flush(self, new_val):
            # nullify the buffers (single instance so it's ok)
            self.buffers = None
            func_clr(self, new_val)
            self.refresh()
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

    @pyqtSlot(int)
    @handle_buffer_flush
    def sampling_change(self, new_sampling_change):
        self.sampling = new_sampling_change
        self.sampling_changed = True

    @pyqtSlot(float)
    def ambient_change(self, new_ambient):
        self.ambient = float("%.2f" % new_ambient)
        self.update()

    @pyqtSlot(float)
    @handle_buffer_flush
    def height_change(self, new_height):
        self.height = new_height

    @pyqtSlot(float)
    @handle_buffer_flush
    def radius_change(self, new_radius):
        self.radius = new_radius

    @pyqtSlot(int)
    @handle_buffer_flush
    def start_layer_change(self, new_layer):
        self.sampling_changed = True
        self.start_layer = new_layer

    @pyqtSlot(int)
    @handle_buffer_flush
    def stop_layer_change(self, new_layer):
        self.sampling_changed = True
        self.stop_layer = new_layer

    @pyqtSlot(str)
    @handle_buffer_flush
    def function_change(self, ftype):
        self.draw_function = ftype
        self.update_context = self.cube_update_context if ftype == 'cube' else self.arrow_update_context

    @pyqtSlot(int)
    def set_xLight(self, val):
        self.xLight = val
        self.update()

    @pyqtSlot(int)
    def set_yLight(self, val):
        self.yLight = val
        self.update()

    @pyqtSlot(int)
    def set_zLight(self, val):
        self.zLight = val
        self.update()

    @pyqtSlot(int)
    @handle_buffer_flush
    def set_xBase(self, val):
        self.xbase_scaler = val

    @pyqtSlot(int)
    @handle_buffer_flush
    def set_yBase(self, val):
        self.ybase_scaler = val

    @pyqtSlot(int)
    @handle_buffer_flush
    def set_zBase(self, val):
        self.zbase_scaler = val

    @handle_buffer_flush
    def set_color_vector(self, val):
        self.color_vector = val

    @handle_buffer_flush
    def set_negative_color(self, val):
        self.negative_color = val

    @handle_buffer_flush
    def set_positive_color(self, val):
        self.positive_color = val
