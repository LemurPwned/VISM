import numpy as np
import ctypes
import os
import sys
import glfw

from CParseAdvanced.AdvParser import AdvParser

from state_machine.virtual_state import VirtualStateMachine
from state_machine.shaders.shaders import *
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (QApplication, QOpenGLWidget, QWidget)

import OpenGL.GL as gl
import OpenGL.GLU as glu
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader


class StateMachine(QOpenGLWidget, VirtualStateMachine):
    def __init__(self, directory):
        super(StateMachine, self).__init__()

        self.ambient = 0.7
        self.resolution = 16
        self.height = 2
        self.radius = 0.25
        self.frame_iterator = 0
        self.parser = AdvParser()
        self.frame_file_list = list(map(lambda x: os.path.join(directory, x),
                                        sorted(filter(lambda x: x.endswith('.ovf') or x.endswith('.omf'), os.listdir(directory)))))
        self.parser.getHeader(self.frame_file_list[0])
        self.header = {'xnodes': self.parser.xnodes,
                       'ynodes': self.parser.ynodes,
                       'znodes': self.parser.znodes,
                       'xbase': self.parser.xbase,
                       'ybase': self.parser.ybase,
                       'zbase': self.parser.zbase}
        print(self.header)
        self.outline = self.parser.getShapeAsNdarray(self.header['xnodes'],
                                                     self.header['ynodes'],
                                                     self.header['znodes'],
                                                     self.header['xbase']*1e9,
                                                     self.header['ybase']*1e9,
                                                     self.header['zbase']*10e9,
                                                     1)
        self.sampling = 1
        self.xnodes = self.header['xnodes']
        self.ynodes = self.header['ynodes']
        self.znodes = self.header['znodes']
        self.xnodes /= self.sampling
        self.ynodes /= self.sampling
        # self.header['znodes'] /= self.sampling
        N = int(self.xnodes * self.ynodes * self.znodes)
        self.indices = self.parser.generateIndices(
            N, int(self.resolution*2)).astype(np.uint32)

        print(len(self.indices), self.outline.shape)

        self.color_vector = [1.0, 1.0, 0.0]
        self.positive_color = [0.0, 1.0, 0.0]
        self.negative_color = [1.0, 0.0, 0.0]

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

        self.length = len(self.frame_file_list)
        self.__TRUE_FLOAT_BYTE_SIZE__ = 4

    def refresh(self):
        self.display_current_frame(self.frame_iterator)

    def display_current_frame(self, frame_num):
        # CUBES
        self.current_frame = self.parser.getMifAsNdarrayWithColor(
            self.frame_file_list[frame_num],
            self.resolution*2,
            self.color_vector,
            self.positive_color,
            self.negative_color,
            self.sampling)

        self.shape = self.parser.getArrows(self.outline,
                                           self.current_frame,
                                           self.resolution,
                                           self.sampling,
                                           self.height,
                                           self.radius)
        print(
            f"Reading {frame_num}, {self.current_frame.shape}, {self.shape.shape}, {self.indices.shape}")
        self.update()

    def create_vbo(self):
        buffers = gl.glGenBuffers(3)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.shape.astype(np.float32),
                        gl.GL_DYNAMIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.current_frame.astype(np.float32),
                        gl.GL_DYNAMIC_DRAW)

        # # index buffer
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, buffers[2])
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                        self.indices,
                        gl.GL_STATIC_DRAW)
        return buffers

    def update_context(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            try:
                gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0,
                                   self.shape.shape[0],
                                   self.shape.astype(np.float32))
            except ValueError as e:
                print(e)  # watch out for setting array element with a sequence erorr

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference changes
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0,
                               self.current_frame.shape[0],
                               self.current_frame.astype(np.float32))
        self.vbo_attrib()

    def vbo_attrib(self):
        """
        PATTERN:
        V1 V2 N1 N2 V1 V2 N1 N2 ...
        V1 - cyllinder
        V2 - cone
        N1 - cyllinder normal
        N2 - cone normal
        """
        stride = self.__TRUE_FLOAT_BYTE_SIZE__*4*3
        position = gl.glGetAttribLocation(self.shader, 'position')
        color = gl.glGetAttribLocation(self.shader, 'color')
        normal = gl.glGetAttribLocation(self.shader, 'normal')
        if position == -1 or color == -1 or normal == -1:
            raise ValueError("Attribute was not found")

        # gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_DIFFUSE)
        # gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glVertexAttribPointer(color, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_TRUE,
                                 0,
                                 None)
        gl.glEnableVertexAttribArray(color)
        # cyllinder part drawing
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexAttribPointer(position, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 stride,
                                 None)
        gl.glEnableVertexAttribArray(position)
        gl.glVertexAttribPointer(normal, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 stride,
                                 ctypes.c_void_p(2*3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glEnableVertexAttribArray(normal)
        gl.glDrawElements(gl.GL_TRIANGLES,
                          len(self.indices),
                          gl.GL_UNSIGNED_INT,
                          None)
        # now draw cones
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexAttribPointer(position, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 stride,
                                 ctypes.c_void_p(3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glEnableVertexAttribArray(position)
        gl.glVertexAttribPointer(normal, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 stride,
                                 ctypes.c_void_p(
                                     3*3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glEnableVertexAttribArray(normal)
        gl.glDrawElements(gl.GL_TRIANGLES,
                          len(self.indices),
                          gl.GL_UNSIGNED_INT,
                          None)
        gl.glDisableVertexAttribArray(position)
        gl.glDisableVertexAttribArray(color)
        gl.glDisableVertexAttribArray(normal)

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
        self.shader = compileProgram(
            compileShader(VERTEX_SHADER, gl.GL_VERTEX_SHADER),
            compileShader(FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER)
        )
        gl.glUseProgram(self.shader)

        n = gl.glGetUniformLocation(self.shader, 'lightPos')
        if n == -1:
            print("Not found lightPos attribute in shaders")
        gl.glUniform3f(n, 0.0, 0.0, 0.0)

        n = gl.glGetUniformLocation(self.shader, 'lightColor')
        if n == -1:
            print("Not found lightColor attribute in shaders")
        gl.glUniform3f(n, 0.5, 0.5, 1.0)

        n = gl.glGetUniformLocation(self.shader, 'ambientStrength')
        if n == -1:
            print("Not found ambientStrength attribute in shaders")
        gl.glUniform1fv(n, 1, self.ambient)

        print("COMPILED SHADERS SUCCESSFULLY")
        gl.glClearColor(*[0.0, 0.0, 0.0], 0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_POLYGON_SMOOTH)

        self.initial_transformation()
        self.display_current_frame(self.frame_iterator)

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
        n = gl.glGetUniformLocation(self.shader, 'ambientStrength')
        if n == -1:
            raise ValueError("Not found ambientStrength attribute in shaders")
        gl.glUniform1fv(n, 1, self.ambient)
        # Push Matrix onto stack
        gl.glPushMatrix()
        gl.glTranslatef(*self.position)
        self.transformate()
        self.update_context()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def keyPressEvent(self, event):
        """
        Key mapping:
        R - reset central view
        I - zoom in
        O - zoom out
        Y - start/stop recording
        S - take a screenshot
        B - start benchmarking
        F - display current frame
        """
        key = event.key()
        if key == Qt.Key_R:
            self.initial_transformation()
            self.update()

        elif key == Qt.Key_N:
            self.frame_iterator += 1
            self.frame_iterator %= self.length
            self.display_current_frame(self.frame_iterator)

        elif key == Qt.Key_P:
            self.frame_iterator -= 1
            self.frame_iterator %= self.length
            self.display_current_frame(self.frame_iterator)
