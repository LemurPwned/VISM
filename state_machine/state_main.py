import numpy as np
import ctypes
import os

from CParseAdvanced.AdvParser import AdvParser
# from cython_modules.cython_parse import getLayerOutline, genCubes


from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

import OpenGL.GL as gl
import OpenGL.GLU as glu


class VirtualStateMachine:
    OBJ_HANDLER = None

    def __init__(self, *args, **kwargs):
        self.color_scheme = None
        self.object_type = None


class StateMachine(QOpenGLWidget, QWidget):
    def __init__(self, directory):
        super(StateMachine, self).__init__()

        self.parser = AdvParser()
        self.frame_file_list = list(map(lambda x: os.path.join(directory, x), sorted(filter(
            lambda x: x.endswith('.omf'), os.listdir(directory)))))
        self.header = None

        self.shape = None

        self.color_vector = [1.0, 1.0, 0.0]
        self.positive_color = [0.0, 1.0, 0.0]
        self.negative_color = [1.0, 0.0, 0.0]

        self.indices_no = 72
        self.vertex_no = int(self.indices_no/3)
        self.total_vertices = 104*104*32*24
        self.buffer_len = 0
        self.buffers = None

        self.steps = 1
        self.setFocusPolicy(Qt.StrongFocus)  # needed if keyboard to be active
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [0, 0, -50]  # xyz initial
        self.geom = (1200, 800)
        """ 
        left mouse must be separately registered
        because right clicks and left clicks with 
        large distance between current and last position
        can lead to rapid rotations 
        """
        self.registered_left_mouse = False
        self.registered_left_mouse_pos = None

    def display_current_frame(self, frame_num):
        self.current_frame = self.parser.getMifAsNdarrayWithColor(
            self.frame_file_list[frame_num],
            self.vertex_no,
            self.color_vector,
            self.positive_color,
            self.negative_color)

        print(f"Reading {frame_num}, {self.current_frame.shape}")

        if self.header is None:
            self.header = {'xnodes': self.parser.xnodes,
                           'ynodes': self.parser.ynodes,
                           'znodes': self.parser.znodes,
                           'xbase': self.parser.xbase,
                           'ybase': self.parser.ybase,
                           'zbase': self.parser.zbase,
                           'per_vertex': self.indices_no}
            print(self.header)

            self.shape = self.parser.getShapeOutline(self.parser.xnodes,
                                                     self.parser.ynodes,
                                                     self.parser.znodes,
                                                     self.parser.xbase*1e9,
                                                     self.parser.ybase*1e9,
                                                     self.parser.zbase*1e9,
                                                     self.indices_no)
            self.buffer_len = self.header['xnodes'] * \
                self.header['ynodes']*self.header['znodes']*self.vertex_no*3
            print(self.shape.shape)
            print(self.shape)
        self.update()

    def loop(self):
        length = len(self.frame_file_list)
        self.frame_iterator = 0
        # while True:
        #     self.frame_iterator += 1
        #     if (self.frame_iterator >= length):
        #         # reset
        #         self.frame_iterator = 0
        self.display_current_frame(self.frame_iterator)

    def create_vbo(self):
        buffers = gl.glGenBuffers(2)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.shape.astype(np.float32),
                        gl.GL_STATIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.current_frame.astype(np.float32),
                        gl.GL_DYNAMIC_DRAW)
        return buffers

    def update_context(self):
        if self.shape is None:
            print("NONE SHPAE")
            return
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference changes
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0,
                               self.buffer_len,
                               self.current_frame.astype(np.float32))
        self.draw_vbo()

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        # bind vertex buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, ctypes.c_void_p(0))

        # bind color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, ctypes.c_void_p(0))

        gl.glDrawArrays(gl.GL_QUADS, 0, int(self.total_vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def zoomOut(self):
        self.position[2] -= 16 / 8

    def wheelEvent(self, event):
        """
        Handles basic mouse scroll
        """
        degsx = event.angleDelta().x() / 8
        degsy = event.angleDelta().y() / 8
        if (abs(degsx) > abs(degsy)):
            self.position[0] += event.angleDelta().x() / 8 / 2
        else:
            self.position[2] += event.angleDelta().y() / 8 / 2
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
            if self.registered_left_mouse:
                dx = event.x() - self.registered_left_mouse_pos.x()
                dy = event.y() - self.registered_left_mouse_pos.y()
                rotation_speed = 0.5
                if abs(dx) > abs(dy):
                    ang = self.normalize_angle(dx * rotation_speed)
                    self.rotation[0] += ang
                else:
                    ang = self.normalize_angle(dy * rotation_speed)
                    self.rotation[1] += ang
            self.registered_left_mouse = True
            self.registered_left_mouse_pos = event.pos()
        elif event.buttons() & Qt.RightButton:
            self.position[0] += dx * 0.4
            self.position[1] -= dy * 0.4
        self.update()

    def mouseReleaseEvent(self, event):
        if self.registered_left_mouse:
            self.registered_left_mouse = False

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def initial_transformation(self):
        """
        resets the view to the initial one
        :return:
        """
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [0, 0, -150]  # xyz initial
        # reset translational view
        width = self.geom[0]
        height = self.geom[1]
        self.lastPos = QPoint(int(width/2), int(height/2))

    def transformate(self):
        """
        applies rotation and transformation
        """
        gl.glRotatef(self.rotation[1], 1, 0, 0)  # rotate around x axis
        gl.glRotatef(self.rotation[0], 0, 1, 0)  # rotate around y axis
        gl.glRotatef(self.rotation[2], 0, 0, 1)  # rotate around z axis

    def initializeGL(self):
        """
        Initializes openGL context and scenery
        """
        gl.glClearColor(*[0.0, 0.0, 0.0], 0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_POLYGON_SMOOTH)
        self.initial_transformation()
        self.loop()

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

    def paintGL(self):
        """
        Clears the buffer and redraws the scene
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Push Matrix onto stack
        gl.glPushMatrix()
        gl.glTranslatef(*self.position)
        self.transformate()
        self.update_context()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()
