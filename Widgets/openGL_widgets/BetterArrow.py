import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import OpenGL.GL as gl
import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt

from cython_modules.cython_parse import getLayerOutline, genCubes

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext
from pattern_types.Patterns import AbstractGLContextDecorators

from ColorPolicy import ColorPolicy
from multiprocessing import Pool
from ctypes import c_void_p

import math

class BetterArrow(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        super().shareData(**data_dict)
        self.sides = 32
        self.spacer = 5
        theta = 2*np.pi/self.sides
        c = np.cos(theta)
        s = np.sin(theta)
        # this is cylinder rotation matrix[a]
        self.zero_pad = [0 for x in range(396)]
        self.t_rotation = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        self.default_radius = 1
        self.co_rot =  np.array([self.default_radius, self.default_radius, 0])
        self.height = np.array([0, 0, 3])
        self.drawing_function = self.vbo_arrow_draw
        self.ff = 'slow2'
        self.prerendering_calculation()

    def prerendering_calculation(self):
        self.decimate = 3
        super().prerendering_calculation()
        if self.normalize:
            BetterArrow.normalize_specification(self.color_vectors, vbo=True)
        if self.ff == 'slow':
            self.drawing_function = self.slow_arrow_draw
            return
        self.structure_vbo, self.vertices = self.generate_structure(self.vectors_list,
                                                                    self.color)
        self.vertices = self.vertices
        self.color_vectors = ColorPolicy.apply_vbo_format(self.color_vectors, k=198*2)
        print(np.array(self.structure_vbo).shape, self.color_vectors.shape)
        print("ARROW SHAPES {}, {}".format(self.vertices, len(self.structure_vbo)))

        # self.vertices *= 4
        # self.vertices -= 1
        self.buffers = None
        # pad the color
        self.color_vertices = len(self.vectors_list)
        # self.vertices = self.structure_vbo/2
        self.color_buffer_len = len(self.color_vectors[0])

        self.__FLOAT_BYTE_SIZE__ = 8

    def paintGL(self):
        """
        Clears the buffer and redraws the scene
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Push Matrix onto stack
        gl.glPushMatrix()
        self.transformate()
        self.drawing_function()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def slow_arrow_draw(self):
        for vector, color in zip(self.vectors_list,
                                    self.color_vectors[self.i]):
            if not np.any(color):
                continue
            gl.glColor3f(*color)
            self.base_arrow(vector)

    def base_arrow(self, vector):
        ang = 30
        ct = np.cos(ang)
        st = np.sin(ang)
        rot_matrix = np.array([[ct, -st, 0],
                               [st, ct, 0],
                               [0, 0 , 1]])
        origin_circle = np.array([vector[0]+self.spacer+self.default_radius,
                                  vector[1]+self.default_radius+self.spacer,
                                  vector[2]+self.spacer])
        cone_base = np.array([vector[0]+self.default_radius*2+self.spacer,
                              vector[1]+self.default_radius*2+self.spacer,
                              vector[2]+self.spacer])
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        self.c_rot = self.co_rot
        for i in range(self.sides+1):
            # bottom triangle - cylinder
            gl.glVertex3f(*rot_matrix.dot(origin_circle+self.c_rot))
            # top triangle -cylinder
            gl.glVertex3f(*rot_matrix.dot(origin_circle+self.c_rot+self.height))
            self.c_rot = self.t_rotation.dot(self.c_rot)
        gl.glEnd()
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        self.c_rot = self.co_rot
        for i in range(self.sides+1):
            # bottom triangle - cone
            gl.glVertex3f(*rot_matrix.dot(cone_base+self.c_rot+self.height))

            # top triangle -cone
            gl.glVertex3f(*rot_matrix.dot(cone_base+self.height*1.5))
            self.c_rot = self.t_rotation.dot(self.c_rot)
        gl.glEnd()

    def create_vbo(self):
        buffers = gl.glGenBuffers(2)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.structure_vbo[self.i],
                        dtype='float32').flatten(),
                        gl.GL_DYNAMIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.color_vectors[self.i],
                        dtype='float32').flatten(),
                        gl.GL_DYNAMIC_DRAW)
        return buffers

    def vbo_arrow_draw(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.vertices*2,
                               np.array(self.structure_vbo[self.i],
                               dtype='float32').flatten())

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference changes
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.color_buffer_len,
                               np.array(self.color_vectors[self.i],
                               dtype='float32').flatten())
        self.draw_vbo()

    @AbstractGLContextDecorators.recording_decorator
    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        # bind color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        # bind vertex buffer - cylinder
        # stride is one  vertex
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT, 0,  None)
        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, int(self.vertices))
        # bind color buffer
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        # gl.glColorPointer(3, gl.GL_FLOAT, 0, None)
        #
        # # bind vertex buffer - cone
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        # gl.glVertexPointer(3, gl.GL_FLOAT, 3*self.__FLOAT_BYTE_SIZE__, c_void_p(4*3))
        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, int(self.vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def generate_arrow_object(self, origin, rot_matrix):
        # no faces for now
        vbo = []
        # ang = 30
        # ct = math.cos(ang)
        # st = math.sin(ang)
        # rot_matrix = np.array([[ct, -st, 0],
        #                        [st, ct, 0],
        #                        [0, 0 , 1]])

        rot_matrix = np.array([[1, 0, 0],
                               [0,1, 0],
                               [0, 0 , 1]])
        origin_circle = np.array([origin[0]+self.default_radius+self.spacer,
                                  origin[1]+self.default_radius+self.spacer,
                                  origin[2]+self.spacer])
        cone_base = np.array([origin[0]+self.default_radius*2+self.spacer,
                              origin[1]+self.default_radius*2+self.spacer,
                              origin[2]+self.spacer])
        c_rot = self.co_rot
        for i in range(self.sides+1):
            # top triangle -cylinder
            vbo.extend(rot_matrix.dot(origin_circle+c_rot+self.height))
            # top triangle -cone
            vbo.extend(rot_matrix.dot(origin_circle+self.height*1.5))
            # bottom triangle - cylinder
            vbo.extend(rot_matrix.dot(origin_circle+c_rot))
            # bottom triangle - cone
            vbo.extend(rot_matrix.dot(origin_circle+c_rot+self.height))

            c_rot = self.t_rotation.dot(c_rot)
        return vbo

    def construct_rotation_matrix(self, vector):
        # default_cone_orientation = [0,0,1]
        cos_x_rot = vector[2]/np.sqrt(vector[1]**2 + vector[2]**2)
        cos_y_rot = vector[2]/np.sqrt(vector[0]**2 + vector[2]**2)
        sin_x_rot = np.sin(np.arccos(cos_x_rot))
        sin_y_rot = np.sin(np.arccos(cos_y_rot))
        rot_matrix = [[cos_y_rot, 0, sin_y_rot],
                      [sin_y_rot*sin_x_rot, cos_x_rot, -sin_x_rot*cos_y_rot],
                      [-cos_x_rot*sin_y_rot, sin_x_rot, sin_x_rot*cos_y_rot]]
        return np.array(rot_matrix)

    def generate_structure(self, vectors_list, colors_list):
        global_vbo = []
        print(vectors_list.shape, colors_list.shape)
        for iteration in colors_list:
            local_vbo = []
            for vector, color in zip(vectors_list, iteration):
                if color.any():
                    rot_matrix = self.construct_rotation_matrix(color)
                    # rot_matrix = None
                    local_vbo.extend(self.generate_arrow_object(vector, rot_matrix))
                    # print(local_vbo)
                # quit()
                else:
                    # local_vbo.extend(self.zero_pad)
                    rot_matrix = None
                    local_vbo.extend(self.generate_arrow_object(vector, rot_matrix))
                # quit()
            global_vbo.append(local_vbo)
        return global_vbo, len(local_vbo)
