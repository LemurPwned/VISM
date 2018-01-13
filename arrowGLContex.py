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

        self.lastPos = QPoint()
        self.setFocusPolicy(Qt.Stron2dLayerArrowsgFocus)  # needed if keyboard to be active

        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [10, 10, -50]  # xyz initial

    def initial_transformation(self):
        """
        resets the view to the initial one
        :return:
        """
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [10, 10, -50]  # xyz initial

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.vectors_list = getLayerOutline(self.omf_header)
        custom_color_policy = ColorPolicy()
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])

        layer = 3
        # testing layer extraction
        self.color_list = [self.color_list[i].reshape(zc, xc*yc,3)[layer-1]
                                for i in range(self.iterations)]
        zc = 1
        pool = Pool()
        multiple_results = [pool.apply_async(
                            custom_color_policy.apply_normalization,
                            (self.color_list[i], xc, yc, zc))
                            for i in range(len(self.color_list))]
        self.color_list = [result.get(timeout=12) for result
                            in multiple_results]
        print("POLICY CALCULATED")
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
        # self.draw_vbo()
        self.slow_arrow_draw()
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

    def slow_arrow_draw(self):
        for vector, color in zip(self.vectors_list,
                                    self.color_list[self.i]):
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
