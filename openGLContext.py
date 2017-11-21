import OpenGL.GLU as glu
import OpenGL.GL as gl
import numpy as np
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

from PyQt5.Qt import QWheelEvent, Qt
from PyQt5.QtCore import QPoint, QTimer
from Parser import Parser
import math as mt
from Parser import Parser
from AbstractGLContext import AbstractGLContext
from multiprocessing import Pool

class OpenGLContext(AbstractGLContext):
    def __init__(self, data_dict):
        super().__init__()
        self.spacer = 10
        self.lastPos = QPoint()
        self.buffers = None
        if data_dict != {}:
            self.shareData(**data_dict)
        filename = './test_folder/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000000.omf'
        self.v1, self.sp = Parser.generate_cubes(filename) #sp = vertices
        print(self.sp)

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.vectors_list = Parser.getLayerOutline(self.omf_header)
        self.colors = self.color_list
        # p1 = Pool()
        # res = [p1.apply_async(OpenGLContext.expand, (y,)) for y in self.color_list]
        # # self.colors = [np.array([[x for i in range(24)] for x in color_iteration]).flatten()
        # #     for color_iteration in self.color_list[0:10]]
        # # print(self.color_list[0].shape)
        # # print(self.colors[self.i].shape)
        # self.colors = []
        # for result in res:
        #     self.colors.append(result.get())

    @staticmethod
    def expand(y):
        return np.array([[x for i in range(24)] for x in y]).flatten()

    def initial_transformation(self):
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [-10, -10, -40]  # xyz initial

    def transformate(self):  # applies rotation and transformation
        gl.glRotatef(self.rotation[0], 0, 1, 0)
        gl.glRotatef(self.rotation[1], 1, 0, 0)
        gl.glRotatef(self.rotation[2], 0, 0, 1)
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])

    def initializeGL(self):
        """
        Initializes openGL context and scenery
        """
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.steps = 1
        gl.glEnable(gl.GL_DEPTH_TEST)
        self.initial_transformation()


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
        glu.gluPerspective(85*self.steps, aspectRatio, 1, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def paintGL(self):
        """
        Clears the buffer and redraws the scene
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Push Matrix onto stack
        gl.glPushMatrix()
        self.transformate()
        self.draw_cube2()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def create_vbo(self):
        buffers = gl.glGenBuffers(2)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                np.array(self.v1, dtype='float32'),
                gl.GL_STATIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                np.array(self.colors[self.i], dtype='float32').flatten(),
                gl.GL_DYNAMIC_DRAW)
        return buffers

    def draw_cube2(self):
        if self.buffers is None:
            self.buffers=self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            gl.glBufferData(gl.GL_ARRAY_BUFFER,
                    np.array(self.colors[self.i], dtype='float32').flatten(),
                    gl.GL_DYNAMIC_DRAW)
        self.draw_vbo()

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY);
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0]);
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1]);
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)
        gl.glDrawArrays(gl.GL_QUADS, 0, int(self.sp))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def draw_cube(self, vec):
        """
        draws basic cubes separated by spacer value
        @param vec (x,y,z) coordinate determining bottom left face
        """
        #TOP FACE
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        #BOTTOM FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #FRONT FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #BACK FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #RIGHT FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #LEFT FACE
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glEnd()

    def wheelEvent(self, event):
        """
        Handles basic mouse scroll
        """
        degs = event.angleDelta().y()/8
        self.steps += degs/15
        #SMART SCROLL BETA
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
        """
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & Qt.LeftButton:
            rotation_speed = 0.5
            self.rotation[0] += dx * rotation_speed
            xpos = self.position[0] * mt.cos(dx * rotation_speed * mt.pi / 180)\
                - self.position[2] * mt.sin(dx * rotation_speed * mt.pi / 180)
            zpos = self.position[0] * mt.sin(dx * rotation_speed * mt.pi / 180)\
                + self.position[2] * mt.cos(dx * rotation_speed * mt.pi / 180)

            self.position[0] = xpos
            self.position[2] = zpos

        elif event.buttons() & Qt.RightButton:
            self.position[0] += dx * 0.1
            self.position[1] += dy * 0.1

        self.lastPos = event.pos()
        self.update()

    def set_i(self, value):
        self.i = value
        self.update()
