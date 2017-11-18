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

class OpenGLContext(AbstractGLContext):
    def __init__(self, data_dict):
        super().__init__()
        self.spacer = 0.2
        self.lastPos = QPoint()
        self.width = 800
        self.height = 480
        self.shareData(**data_dict)

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

    def resizeGL(self, w, h):
        """
        Resize function, applied when windows change size
        @param w width
        @param h height
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
        for vector, color in zip(self.vectors_list, \
                                                self.color_list[self.i]):
            gl.glColor3f(color[0], color[1], color[2])
            self.draw_cube(vector)
        # Pop Matrix off stack
        gl.glPopMatrix()

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
        scroll_y = self.steps
        #SMART SCROLL BETA
        self.position[0] -= mt.sin(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * scroll_y
        self.position[1] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.sin(self.rotation[1] * mt.pi / 180) * scroll_y
        self.position[2] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * scroll_y
        self.update()

    def mouseMoveEvent(self, event):
        """
        Handles basic mouse press
        """
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        rotation_speed = 1
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
        self.i %= self.iterations
        self.update()
