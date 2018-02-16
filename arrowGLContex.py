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

        self.vectors_list = getLayerOutline(self.omf_header)

        custom_color_policy = ColorPolicy()
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])
        # testing layer extraction
        # extarction of layer means limiting vectors list
        if self.omf_header['binary']:
            if self.layer != 'all':
                self.specificLayerDisplay(self.layer, xc, yc, zc, custom_color_policy)
            else:
                self.color_list = custom_color_policy.apply_normalization(self.color_list,
                                    xc, yc, zc)
            self.color_list, self.vectors_list = \
                            custom_color_policy.averaging_policy(self.color_list,
                                                                 self.vectors_list,
                                                                 self.averaging)
            self.color_list = custom_color_policy.apply_dot_product(self.color_list)
        else:
            # code for non-binary formats
            if self.layer != 'all':
                # take only one layer
                layer_size = xc*yc
                sl = self.layer*layer_size # slice
                self.color_list = [c[sl:sl+layer_size] for c in self.color_list]
                self.color_list = custom_color_policy.apply_normalization(self.color_list,
                                                                        xc, yc, zc=1)
            else:
                self.color_list = custom_color_policy.apply_normalization(self.color_list,
                                                                          xc, yc, zc)
            self.color_list = np.array([c[::self.averaging] for c in self.color_list])
            self.vectors_list = getLayerOutline(self.omf_header)[::self.averaging]

    def specificLayerDisplay(self, layer, xc, yc, zc, custom_color_policy):
        # take only one layer so
        layer_size = xc*yc
        self.vectors_list = self.vectors_list[:layer_size]
        # reshape to extract a single layer
        self.color_list = np.array([self.color_list[i].reshape(zc, xc*yc, 3)[layer-1]
                                for i in range(self.iterations)])

        self.color_list = custom_color_policy.apply_normalization(self.color_list,
                            xc, yc, zc=1)

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
