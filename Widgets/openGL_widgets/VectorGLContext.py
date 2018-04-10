from PyQt5.QtWidgets import QWidget

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext

from ColorPolicy import ColorPolicy

from ctypes import c_void_p
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QThread

from cython_modules.cython_parse import getLayerOutline
from cython_modules.color_policy import multi_iteration_normalize

import numpy as np
import OpenGL.GLU as glu
import OpenGL.GL as gl
import math as mt
from multiprocessing import Pool

class VectorGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        self.shareData(**data_dict)
        self.buffers = None
        self.vertices = 1
        self.steps = 1

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.spacer = 0.2

        self.drawing_function = self.slow_arrow_draw
        self.vectors_list = getLayerOutline(self.omf_header)

        # remap
        self.i = self.current_state

        custom_color_policy = ColorPolicy()
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        self.function_select = 'slow'
        self.color_vectors, self.vectors_list, decimate = \
                    custom_color_policy.standard_procedure(self.vectors_list,
                                                           self.color_vectors,
                                                           self.iterations,
                                                           self.averaging,
                                                           xc, yc, zc,
                                                           self.layer,
                                                           self.vector_set,
                                                           self.decimate,
                                                           self.disableDot)

        if self.normalize:
            multi_iteration_normalize(self.color_vectors)

        if decimate is not None:
            # this is arbitrary
            self.spacer *= decimate*3

        self.drawing_function = self.slow_arrow_draw

    def slow_arrow_draw(self):
        for vector, color in zip(self.vectors_list,
                                    self.color_vectors[self.i]):
            if not color.any():
                continue
            self.base_arrow(vector, color)

    def base_arrow(self, vector, color):
        gl.glColor3f(*color)
        gl.glLineWidth(2*self.scale)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(*vector)
        gl.glVertex3f(vector[0]+color[0], vector[1]+color[1],
                        vector[2]+color[2])
        gl.glEnd()
        gl.glPointSize(3*self.scale)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex3f(vector[0]+color[0], vector[1]+color[1],
                        vector[2]+color[2])
        gl.glEnd()

    def standard_vbo_draw(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        gl.glDrawArrays(gl.GL_LINES, 0, self.vertices)

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def vbo_arrow_draw(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.buffer_len,
                               np.array(self.vectors_list[self.i],
                               dtype='float32'))

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.buffer_len,
                               np.array(self.color_vectors[self.i],
                               dtype='float32'))

        self.standard_vbo_draw()

    def create_vbo(self):
        buffers = gl.glGenBuffers(2)
        gl.glLineWidth(3)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.vectors_list[self.i],
                        dtype='float32'),
                        gl.GL_DYNAMIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.color_vectors[self.i],
                        dtype='float32'),
                        gl.GL_DYNAMIC_DRAW)
        return buffers
