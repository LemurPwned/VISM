from PyQt5.QtWidgets import QWidget
from AbstractGLContext import AbstractGLContext
from ColorPolicy import ColorPolicy
from ctypes import c_void_p
from PyQt5.Qt import Qt

import numpy as np
import OpenGL.GLU as glu
import OpenGL.GL as gl
import math as mt


class ArrowGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        self.shareData(**data_dict)
        self.buffer = None
        self.steps = 1
        self.vertices = 0

        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [10, 10, -50]  # xyz initial

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        custom_color_policy = ColorPolicy()
        self.color_matrix = custom_color_policy.apply_dot_product(self.color_list,
                                                                  self.omf_header)
        print(self.color_matrix[self.i])
        print(len(self.color_matrix))
        self.vertices = len(self.color_matrix[0])
        print("DONE")

    def initializeGL(self):
        """
        Initializes openGL context
        :return:
        """
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)  # enables depth testing

    def paintGL(self):
        """
        Clears the buffer and redraws the scene
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Push Matrix onto stack
        gl.glPushMatrix()
        self.transformate()
        self.draw_vbo()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def resizeGL(self, w, h):
        """
        Resize function, applied when windows change size
        @param w width - use self.width() function
        @param h height - use self.height() function
        """
        gl.glViewport(0, 0, w, h)
        # using Projection mode
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspectRatio = w / h
        glu.gluPerspective(85 * self.steps, aspectRatio, 1, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def transformate(self):  # applies rotation and transformation
        gl.glRotatef(self.rotation[0], 0, 1, 0)  # rotate around y axis
        gl.glRotatef(self.rotation[1], 1, 0, 0)  # rotate around x axis
        gl.glRotatef(self.rotation[2], 0, 0, 1)  # rotate around z axis
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])
    #
    # def create_vbo_buffer(self):
    #     self.buffer = gl.glGenBuffers(1)
    #     # interleaved buffer
    #     gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer)
    #     gl.glBufferData(gl.GL_ARRAY_BUFFER,
    #                     np.array(self.color_matrix[self.i], dtype='float32'),
    #                     gl.GL_DYNAMIC_DRAW)
    #
    # def update_buffer(self):
    #     gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer)
    #     gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.buffer_len,
    #                        np.array(self.color_matrix[self.i], dtype='float32'))
    #     self.draw_vbo()

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

    def wheelEvent(self, event):
        """
        Handles basic mouse scroll
        """
        degs = event.angleDelta().y() / 8
        self.steps += degs / 15
        # SMART SCROLL BETA
        self.position[0] -= mt.sin(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[1] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.sin(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[2] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps
        self.update()

    def mouseMoveEvent(self, event):
        """
        Handles basic mouse press
        SHOULD BE MOUSE DRAG RATHER A MOUSE EVENT
        """
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        self.lastPos = event.pos()
        if event.buttons() & Qt.LeftButton:
            rotation_speed = 0.5
            self.rotation[0] += dx * rotation_speed
            xpos = self.position[0] * mt.cos(dx * rotation_speed * mt.pi / 180) \
                   - self.position[2] * mt.sin(dx * rotation_speed * mt.pi / 180)
            zpos = self.position[0] * mt.sin(dx * rotation_speed * mt.pi / 180) \
                   + self.position[2] * mt.cos(dx * rotation_speed * mt.pi / 180)

            self.position[0] = xpos
            self.position[2] = zpos
        elif event.buttons() & Qt.RightButton:
            self.position[0] += dx * 0.2
            self.position[1] += dy * 0.2

        self.update()

    def keyPressEvent(self, event):
        """
        if r is pressed on the keyboard, then reset view
        """
        key = event.key()
        if key == Qt.Key_R:
            self.initial_transformation()
            self.update()

    def set_i(self, value):
        self.i = value
        self.i %= self.iterations
        self.update()
