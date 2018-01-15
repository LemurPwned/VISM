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
        self.steps = 1
        self.vertices = 0

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.vectors_list = getLayerOutline(self.omf_header)
        
        custom_color_policy = ColorPolicy()
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        layer = 3
        # testing layer extraction
        # extarction of layer means limiting vectors list
        self.vectors_list = self.vectors_list[:xc*yc]
        self.color_list = np.array([self.color_list[i].reshape(zc, xc*yc,3)[layer-1]
                                for i in range(self.iterations)])

        self.color_list = custom_color_policy.apply_normalization(self.color_list,
                            xc, yc, zc=1)

        self.color_list, self.vectors_list = \
                        custom_color_policy.averaging_policy(self.color_list,
                                                            self.vectors_list, 3)

    def paintGL(self):
        """
        Clears the buffer and redraws the scene
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Push Matrix onto stack
        gl.glPushMatrix()
        self.transformate()
        # self.draw_vbo()
        self.slow_arrow_draw()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def slow_arrow_draw(self):
        for vector, color in zip(self.vectors_list,
                                    self.color_list[self.i]):
            if not color.any():
                continue
            gl.glColor3f(*color)
            gl.glLineWidth(2)
            gl.glBegin(gl.GL_LINES)
            gl.glVertex3f(*vector)
            gl.glVertex3f(vector[0]+color[0], vector[1]+color[1],
                            vector[2]+color[2])
            gl.glEnd()
            gl.glPointSize(3)
            gl.glBegin(gl.GL_POINTS)
            gl.glVertex3f(vector[0]+color[0], vector[1]+color[1],
                            vector[2]+color[2])
            gl.glEnd()

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer)

        # float32 is 4 bytes so 4*(3 for color + 3 for vertex) = 4*6 =24
        g = np.array(self.color_matrix[self.i], dtype='float32')
        gl.glInterleavedArrays(gl.GL_C3F_V3F, 4*(3+3), g)
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, int(self.vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
