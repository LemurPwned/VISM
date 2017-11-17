import pyglet
from pyglet import gl
from OpenGL.GLUT import *
import numpy as np
pyglet.options['debug_gl'] = False
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

from PyQt5.Qt import QWheelEvent, Qt
from PyQt5.QtCore import QPoint, QTimer
from Parser import Parser
import math as mt


class PygletContext(QOpenGLWidget):
    def __init__(self, data_dict, parent=None):
        super(PygletContext, self).__init__(parent)
        self.shareData(**data_dict)
        self.spacer = 0.2
        self.lastPos = QPoint()
        self.width = 800
        self.height = 480
        # init members
        #place QTimer here with 0

    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main plot iterator
        """
        #TODO: define minimum_list in arguments and force SPECIFIC keys
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.vectors_list = Parser.getLayerOutline(self.omf_header)

    def _update(self):
        """
        Calls on_update with the choosen dt
        """
        self.on_update(self._dt)

    def on_init(self):
        """
        Lets the user initialise himself
        """
        self.steps = 1
        gl.glEnable(gl.GL_DEPTH_TEST)
        self.initial_transformation()

    def initial_transformation(self):
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [-10, -10, -40]  # xyz initial

    def transformate(self):  # applies rotation and transformation
        gl.glRotatef(self.rotation[0], 0, 1, 0)  # weird
        gl.glRotatef(self.rotation[1], 1, 0, 0)  # weird
        gl.glRotatef(self.rotation[2], 0, 0, 1)
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])

    def on_draw(self):
        """
        Lets the user draw his scene
        """
        # Push Matrix onto stack
        gl.glPushMatrix()
        print("DRAWING")
        self.transformate()
        for vector, color in zip(self.vectors_list, \
                                                self.color_list[self.i]):
            gl.glColor3f(color[0], color[1], color[2])
            self.draw_cube(vector)
        # Pop Matrix off stack
        gl.glPopMatrix()

    def on_update(self, dt):
        """
        Lets the user draw his scene
        """
        self.on_resize(self.width, self.height)

    def on_resize(self, w, h):
        """
        Lets the user handle the widget resize event. By default, this method
        resizes the view to the widget size.
        """
        print("RESIZE")
        gl.glViewport(0, 0, w, h)
        # using Projection mode
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspectRatio = w / h
        gl.gluPerspective(85*self.steps, aspectRatio, 1, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def initializeGL(self):
        """
        Initialises open gl:
            - create a mock context to fool pyglet
            - setup various opengl rule (only the clear color atm)
        """
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.on_init()

    def resizeGL(self, w, h):
        """
        Resizes the gl camera to match the widget size.
        """
        self.on_resize(w, h)

    def paintGL(self):
        """
        Clears the back buffer than calls the on_draw method
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.on_draw()

    def draw_cube(self, vec):
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
        print("EVENT")
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
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        rotation_speed = 1
        if event.buttons() & Qt.LeftButton:
            print("EVENT_LMB")
            rotation_speed = 0.5
            self.rotation[0] += dx * rotation_speed
            xpos = self.position[0] * mt.cos(dx * rotation_speed * mt.pi / 180)\
                - self.position[2] * mt.sin(dx * rotation_speed * mt.pi / 180)
            zpos = self.position[0] * mt.sin(dx * rotation_speed * mt.pi / 180)\
                + self.position[2] * mt.cos(dx * rotation_speed * mt.pi / 180)

            self.position[0] = xpos
            self.position[2] = zpos

        elif event.buttons() & Qt.RightButton:
            print("EVENT_RMB")
            self.position[0] += dx * 0.1
            self.position[1] += dy * 0.1

        self.lastPos = event.pos()
        self.update()

    def set_i(self, value):
        self.i = value
        print("JAKUBS", self.i)
        self.update()
