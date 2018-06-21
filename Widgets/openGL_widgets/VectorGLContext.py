from PyQt5.QtWidgets import QWidget

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext

from ColorPolicy import ColorPolicy

from ctypes import c_void_p
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QThread

from cython_modules.color_policy import multi_iteration_normalize
from pattern_types.Patterns import AbstractGLContextDecorators

import numpy as np
import OpenGL.GLU as glu
import OpenGL.GL as gl
import math as mt
from multiprocessing import Pool
from ColorPolicy import ColorPolicy
from workerthreads import *
import time as tm


class VectorGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict, parent=None):
        super().__init__()
        super().shareData(**data_dict)
        self.dummy_startup_function()
        self.drawing_function = self.vbo_arrow_draw

    def dummy_finish_function(self, empty_arg):
        self.post_processing()

    def dummy_startup_function(self):
        self.p = ThreadingWrapper(completeAction=self.dummy_finish_function,
                                  exceptionAction=None, 
                                  parent=self)

        self.p.collapse_threads(self.prerendering_calculation, False)

        self.pafsaf= False

    def post_processing(self):
        self.interleaved = ColorPolicy.apply_vbo_interleave_format(self.vectors_list,
                                                                   self.color_vectors)
        self.buffers = None
        ## pad the color
        self.color_vectors = ColorPolicy.apply_vbo_format(self.color_vectors, k=2)
        self.color_vertices = len(self.vectors_list)
        self.vertices = self.color_vertices*2
        self.color_buffer_len = len(self.color_vectors[0])*4
        self.inter_buffer_len = len(self.interleaved[0])*4

        self.__FLOAT_BYTE_SIZE__ = 8

    @AbstractGLContextDecorators.recording_decorator
    def slow_arrow_draw(self):
        gl.glLineWidth(2*self.scale)
        gl.glPointSize(3*self.scale)
        for vector, color in zip(self.vectors_list,
                                    self.color_vectors[self.i]):
            if not np.any(color):
                continue
            self.base_arrow(vector, color)

    def standard_vbo_draw(self):
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        # draw the lines
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(4, gl.GL_FLOAT, 0, None)
        gl.glDrawArrays(gl.GL_LINES, 0, int(self.vertices))

        # now the points
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 3*self.__FLOAT_BYTE_SIZE__, None)

        # stride is 3 bytes (3 floats) VVVCCCVVVCCC etc...
        # VVVACCCAVVVACCCA etc. in case of 4f
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        # offset is at 3 indices, so points at 4th vector 3(vertices)*4
        # offset is at 4 indices, so points at 4th vector 4(vertices)*4
        # we have alpha value therefore it is a little different
        gl.glVertexPointer(4, gl.GL_FLOAT, 4*self.__FLOAT_BYTE_SIZE__,
                                                                c_void_p(4*4))
        gl.glDrawArrays(gl.GL_POINTS, 0, int(self.color_vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)


    def vbo_arrow_draw(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.inter_buffer_len,
                               np.array(self.interleaved[self.i],
                               dtype='float32').flatten())

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.color_buffer_len,
                               np.array(self.color_vectors[self.i],
                               dtype='float32').flatten())

        self.standard_vbo_draw()

    def create_vbo(self):
        buffers = gl.glGenBuffers(2)
        gl.glLineWidth(2*self.scale)
        gl.glPointSize(3*self.scale)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.interleaved[self.i],
                        dtype='float32').flatten(),
                        gl.GL_DYNAMIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.color_vectors[self.i],
                        dtype='float32').flatten(),
                        gl.GL_DYNAMIC_DRAW)
        return buffers
