import OpenGL.GLU as glu
import OpenGL.GL as gl
import numpy as np
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

from PyQt5.Qt import QWheelEvent, Qt
from PyQt5.QtCore import QPoint, QTimer
from Parser import Parser
import math as mt

from AbstractGLContext import AbstractGLContext
s=5.0
vertices=[
        -s, -s, -s,
         s, -s, -s,
         s,  s, -s,
        -s,  s, -s,
        -s, -s,  s,
         s, -s,  s,
         s,  s,  s,
        -s,  s,  s,
        ]

colors=[
        0, 0, 0,
        1, 0, 0,
        0, 1, 0,
        0, 0, 1,
        0, 1, 1,
        1, 0, 1,
        1, 1, 1,
        1, 1, 0,
        ]
indices=[
        0, 1, 2, 2, 3, 0,
        0, 4, 5, 5, 1, 0,
        1, 5, 6, 6, 2, 1,
        2, 6, 7, 7, 3, 2,
        3, 7, 4, 4, 0, 3,
        4, 7, 6, 6, 5, 4,
]

class OpenGLContext(AbstractGLContext):
    def __init__(self, data_dict):
        super().__init__()
        self.spacer = 10
        self.lastPos = QPoint()
        self.buffers = None
        if data_dict != {}:
            self.shareData(**data_dict)
        vec = [5, 5, 5]
        self.v1 =[
            vec[0]+self.spacer, vec[1], vec[2]+self.spacer,
            vec[0], vec[1], vec[2]+self.spacer,
            vec[0], vec[1]+self.spacer, vec[2]+self.spacer,
            vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer,
            #BOTTOM FACE
            vec[0]+self.spacer, vec[1], vec[2],
            vec[0], vec[1], vec[2],
            vec[0], vec[1]+self.spacer, vec[2],
            vec[0]+self.spacer, vec[1]+self.spacer, vec[2],
            #FRONT FACE
            vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer,
            vec[0], vec[1]+self.spacer, vec[2]+self.spacer,
            vec[0], vec[1]+self.spacer, vec[2],
            vec[0]+self.spacer, vec[1]+self.spacer, vec[2],
            #BACK FACE
            vec[0]+self.spacer, vec[1], vec[2]+self.spacer,
            vec[0], vec[1], vec[2]+self.spacer,
            vec[0], vec[1], vec[2],
            vec[0]+self.spacer, vec[1], vec[2],
            #RIGHT FACE
            vec[0]+self.spacer, vec[1], vec[2]+self.spacer,
            vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer,
            vec[0]+self.spacer, vec[1]+self.spacer, vec[2],
            vec[0]+self.spacer, vec[1], vec[2],
            #LEFT FACE
            vec[0], vec[1]+self.spacer, vec[2]+self.spacer,
            vec[0], vec[1], vec[2]+self.spacer,
            vec[0], vec[1], vec[2],
            vec[0], vec[1]+self.spacer, vec[2]]

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.vectors_list = Parser.getLayerOutline(self.omf_header)

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
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        vertices= np.array([
                    0.5, 0.5, -0.5, 0.5, -0.5,-0.5,0.5, -0.5], dtype='float32')
        gl.glBufferData(gl.GL_ARRAY_BUFFER,  vertices, gl.GL_STATIC_DRAW)

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
        # glMatrixMode(GL_MODELVIEW)
        # glLoadIdentity()
        # glTranslatef(0.0, 0.0, -2.0)
        self.transformate()
        # for vector, color in zip(self.vectors_list, \
        #                                         self.color_list[self.i]):
        #     gl.glColor3f(color[0], color[1], color[2])
        #     self.draw_cube(vector)
        gl.glColor3f(1.0, 0.0, 0.0)
        self.draw_cube2()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def create_vbo(self):
        buffers = gl.glGenBuffers(1)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers)
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                np.array(self.v1, dtype='float32'),
                gl.GL_STATIC_DRAW)
        # color buffer
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        # gl.glBufferData(gl.GL_ARRAY_BUFFER,
        #         np.array(colors, dtype='float32'),
        #         gl.GL_STATIC_DRAW)
        # indices buffer
        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, buffers[2])
        # gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
        #         np.array(indices, dtype='uint'),
        #         gl.GL_STATIC_DRAW)
        return buffers

    def draw_cube2(self):
        if self.buffers is None:
            self.buffers=self.create_vbo()
        self.draw_vbo()

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY);
        #gl.glEnableClientState(gl.GL_COLOR_ARRAY);
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers);
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None);
        #gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1]);
        #gl.glColorPointer(3, gl.GL_FLOAT, 0, None);
        #gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2]);
        # gl.glDrawElements(gl.GL_QUADS, len(indices), gl.GL_UNSIGNED_INT, None);
        # gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDrawArrays(gl.GL_QUADS, 0, 24)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY);

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
