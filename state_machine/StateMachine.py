import numpy as np
import ctypes
import os
import sys

from CParseAdvanced.AdvParser import AdvParser
from Windows.StateMenu import StateMenuController
from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext
from Widgets.AnimatedWidget import AnimatedWidget

from state_machine.virtual_state import VirtualStateMachine
from state_machine.shaders.shaders import *
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (QApplication, QOpenGLWidget, QWidget)

from pattern_types.Patterns import AbstractGLContextDecorators

import OpenGL.GL as gl
import OpenGL.GLU as glu
from OpenGL.GL.shaders import compileProgram, compileShader
import gc

from mem_top import mem_top

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("__main__")


class StateMachine(AbstractGLContext, QWidget, VirtualStateMachine):
    def __init__(self, data_dict, parent):
        self.cld = parent
        super(StateMachine, self).__init__()
        super().shareData(**data_dict)
        self.i = self.current_state
        self.subdir = "GL_STM"
        self.frame_file_list = list(map(lambda x: os.path.join(self.directory, x),
                                        sorted(filter(lambda x:
                                                      x.endswith('.ovf') or x.endswith(
                                                          '.omf'),
                                                      os.listdir(self.directory)))))
        self.iterations = len(self.frame_file_list)
        self.sampling = 4
        self.ambient = 0.4
        self.resolution = 16
        self.height = 2
        self.radius = 0.25

        self.xLight = 0.0
        self.yLight = 0.0
        self.zLight = 0.0

        self.xbase_scaler = 1
        self.ybase_scaler = 1
        self.zbase_scaler = 5

        self.parser = AdvParser()

        self.parser.getHeader(self.frame_file_list[0])
        self.header = {'xnodes': self.parser.xnodes,
                       'ynodes': self.parser.ynodes,
                       'znodes': self.parser.znodes,
                       'xbase': self.parser.xbase,
                       'ybase': self.parser.ybase,
                       'zbase': self.parser.zbase}
        self.start_layer = 0
        self.stop_layer = self.parser.znodes

        self.xnodes = self.header['xnodes']
        self.ynodes = self.header['ynodes']
        self.znodes = self.header['znodes']

        print(self.header)
        self.color_vector = [1.0, 0.0, 0.0]
        self.positive_color = [0.0, 0.0, 1.0]
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

        self.draw_function = 'arrow'
        if self.draw_function == 'cube':
            self.update_context = self.cube_update_context
        elif self.draw_function == 'arrow':
            self.update_context = self.arrow_update_context
            # recalculate index values
            N = int(self.xnodes * self.ynodes * self.znodes)
            self.indices = self.parser.generateIndices(
                N, int(self.resolution*2)).astype(np.uint32)
        self.sampling_changed = True
        self.subwindow = StateMenuController(state_object=self)

    def calculate_geometry(self):
        self.geometry = self.parser.getCubeOutline(self.header['xnodes'],
                                                   self.header['ynodes'],
                                                   self.header['znodes'],
                                                   self.header['xbase']*1e9,
                                                   self.header['ybase']*1e9,
                                                   self.header['zbase']*5e9,
                                                   self.sampling,
                                                   self.start_layer,
                                                   self.stop_layer)

    def refresh(self):
        self.display_current_frame(self.i)

    def display_current_frame(self, frame_num):
        self.xnodes = self.header['xnodes']
        self.ynodes = self.header['ynodes']
        self.xnodes /= self.sampling
        self.ynodes /= self.sampling
        if self.draw_function == 'arrow':
            if self.sampling_changed:
                # recalculate index values
                N = int(self.xnodes * self.ynodes * self.znodes)
                self.indices = self.parser.generateIndices(
                    N, int(self.resolution*2)).astype(np.uint32)
            self.shape = self.parser.getMifVBO(
                self.frame_file_list[frame_num],
                self.resolution,
                self.color_vector,
                self.positive_color,
                self.negative_color,
                self.sampling,
                self.height,
                self.radius,
                int(self.start_layer),
                int(self.stop_layer),
                self.xbase_scaler,
                self.ybase_scaler,
                self.zbase_scaler,
                0  # binary
            )
        elif self.draw_function == 'cube':
            if self.sampling_changed:
                # recalculate the geometry
                self.calculate_geometry()
                self.sampling_changed = False
            self.color = self.parser.getMifAsNdarrayWithColor(
                self.frame_file_list[frame_num],
                self.color_vector,
                self.positive_color,
                self.negative_color,
                self.sampling,
                int(self.start_layer),
                int(self.stop_layer),
                0  # binary
            )

    def create_vbo(self):
        buffers = gl.glGenBuffers(3)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.shape.astype(np.float32),
                        gl.GL_DYNAMIC_DRAW)
        # index buffer
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, buffers[2])
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                        self.indices,
                        gl.GL_STATIC_DRAW)
        return buffers

    def arrow_update_context(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            try:
                gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0,
                                   self.shape.shape[0] *
                                   self.__TRUE_FLOAT_BYTE_SIZE__,
                                   self.shape.astype(np.float32))
            except ValueError as e:
                print(e)  # watch out for setting array element with a sequence erorr
        self.vbo_attrib()

    def cube_create_vbo(self):
        buffers = gl.glGenBuffers(2)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.color.astype(np.float32),
                        gl.GL_DYNAMIC_DRAW)
        # geometry buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.geometry.astype(np.float32),
                        gl.GL_STATIC_DRAW)
        return buffers

    def cube_update_context(self):
        if self.buffers is None:
            self.buffers = self.cube_create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            try:
                gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0,
                                   self.color.shape[0] *
                                   self.__TRUE_FLOAT_BYTE_SIZE__,
                                   self.color.astype(np.float32))
            except ValueError as e:
                print(e)  # watch out for setting array element with a sequence erorr
        self.cube_vbo_attrib()

    @AbstractGLContextDecorators.recording_decorator
    def cube_vbo_attrib(self):
        """
        PATTERN:
        2 VBOS
        """
        stride = self.__TRUE_FLOAT_BYTE_SIZE__*6
        position = gl.glGetAttribLocation(self.shader, 'position')
        color = gl.glGetAttribLocation(self.shader, 'color')
        normal = gl.glGetAttribLocation(self.shader, 'normal')
        if position == -1 or color == -1 or normal == -1:
            raise ValueError("Attribute was not found")

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexAttribPointer(color, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 0,
                                 ctypes.c_void_p(0))

        # vertex part drawing
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glVertexAttribPointer(position, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 stride,
                                 ctypes.c_void_p(0))
        gl.glVertexAttribPointer(normal, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 stride,
                                 ctypes.c_void_p(3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glEnableVertexAttribArray(normal)
        gl.glEnableVertexAttribArray(position)
        gl.glEnableVertexAttribArray(color)
        gl.glDrawArrays(gl.GL_QUADS, 0,
                        int(self.color.shape[0]))
        gl.glDisableVertexAttribArray(position)
        gl.glDisableVertexAttribArray(color)
        gl.glDisableVertexAttribArray(normal)

    @AbstractGLContextDecorators.recording_decorator
    def vbo_attrib(self):
        """
        PATTERN:
        C V1 V2 C N1 N2 C V1 V2 C N1 N2 C ...
        V1 - cyllinder
        V2 - cone
        N1 - cyllinder normal
        N2 - cone normal
        """
        stride = self.__TRUE_FLOAT_BYTE_SIZE__*3*4
        color_stride = self.__TRUE_FLOAT_BYTE_SIZE__*3*3
        vertex_stride = self.__TRUE_FLOAT_BYTE_SIZE__*3*6
        normal_stride = self.__TRUE_FLOAT_BYTE_SIZE__*3*6
        position = gl.glGetAttribLocation(self.shader, 'position')
        color = gl.glGetAttribLocation(self.shader, 'color')
        normal = gl.glGetAttribLocation(self.shader, 'normal')
        if position == -1 or color == -1 or normal == -1:
            raise ValueError("Attribute was not found")

        gl.glVertexAttribPointer(color, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 3*6*self.__TRUE_FLOAT_BYTE_SIZE__,
                                 ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(color)
        # cyllinder part drawing
        gl.glVertexAttribPointer(position, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 vertex_stride,
                                 ctypes.c_void_p(3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glVertexAttribPointer(normal, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_TRUE,
                                 normal_stride,
                                 ctypes.c_void_p(4*3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glEnableVertexAttribArray(normal)
        gl.glEnableVertexAttribArray(position)
        gl.glDrawElements(gl.GL_TRIANGLES,
                          len(self.indices),
                          gl.GL_UNSIGNED_INT,
                          None)
        # now draw cones
        gl.glVertexAttribPointer(position, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 vertex_stride,
                                 ctypes.c_void_p(2*3*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glVertexAttribPointer(normal, 3,
                                 gl.GL_FLOAT,
                                 gl.GL_FALSE,
                                 normal_stride,
                                 ctypes.c_void_p(
                                     3*5*self.__TRUE_FLOAT_BYTE_SIZE__))
        gl.glEnableVertexAttribArray(position)
        gl.glEnableVertexAttribArray(normal)
        gl.glDrawElements(gl.GL_TRIANGLES,
                          len(self.indices),
                          gl.GL_UNSIGNED_INT,
                          None)
        gl.glDisableVertexAttribArray(position)
        gl.glDisableVertexAttribArray(color)
        gl.glDisableVertexAttribArray(normal)

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
            print("Not found: lightPos attribute in shaders")
        gl.glUniform3f(n, self.xLight, self.yLight, self.zLight)

        n = gl.glGetUniformLocation(self.shader, 'lightColor')
        if n == -1:
            print("Not found: lightColor attribute in shaders")
        gl.glUniform3f(n, 1.0, 1.0, 1.0)

        n = gl.glGetUniformLocation(self.shader, 'ambientStrength')
        if n == -1:
            print("Not found: ambientStrength attribute in shaders")
        gl.glUniform1fv(n, 1, self.ambient)

        gl.glClearColor(*[0.5, 0.5, 0.5], 0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_POLYGON_SMOOTH)
        gl.glDisable(gl.GL_CULL_FACE)

        self.initial_transformation()
        self.display_current_frame(self.i)

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
            raise ValueError("Not found: ambientStrength attribute in shaders")
        gl.glUniform1fv(n, 1, self.ambient)

        n = gl.glGetUniformLocation(self.shader, 'lightPos')
        if n == -1:
            print("Not found: lightPos attribute in shaders")
        gl.glUniform3f(n, self.xLight, self.yLight, self.zLight)
        # Push Matrix onto stack
        gl.glPushMatrix()
        gl.glTranslatef(*self.position)
        self.transformate()
        self.update_context()
        self.text_functionalities()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def set_i(self, value, trigger=False, record=False, reset=1):
        super().set_i(value, trigger, record, reset)
        self.display_current_frame(self.i)
        # self.record = record
