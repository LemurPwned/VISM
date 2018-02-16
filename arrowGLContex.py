from PyQt5.QtWidgets import QWidget
from AbstractGLContext import AbstractGLContext
from ColorPolicy import ColorPolicy
from ctypes import c_void_p
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint

from cython_modules.cython_parse import generate_cubes, getLayerOutline

import numpy as np
import OpenGL.GLU as glu
import OpenGL.GL as gl
import math as mt
from multiprocessing import Pool


class ArrowGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        self.shareData(**data_dict)
        self.buffer = None
        self.vertices = 0
        self.steps = 1

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.receivedOptions()

        self.drawing_function = self.slow_arrow_draw
        self.vectors_list = getLayerOutline(self.omf_header)

        custom_color_policy = ColorPolicy()
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        # testing layer extraction
        # extarction of layer means limiting vectors list
        self.color_list, self.vectors_list = \
                            custom_color_policy.standard_procedure(self.vectors_list,
                                                                   self.color_list,
                                                                   self.iterations,
                                                                   self.averaging,
                                                                   xc, yc, zc, 3)

    def slow_arrow_draw(self):
        for vector, color in zip(self.vectors_list,
                                    self.color_list[self.i]):
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

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        # float32 is 4 bytes so 4*(3 for color + 3 for vertex) = 4*6 =24
        g = np.array(self.color_matrix[self.i], dtype='float32')
        gl.glInterleavedArrays(gl.GL_C3F_V3F, 4*(3+3), g)
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, int(self.vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
