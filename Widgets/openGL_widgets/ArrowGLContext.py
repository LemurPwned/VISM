import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import OpenGL.GL as gl
from OpenGL.arrays import vbo
from OpenGL.raw.GL.ARB.vertex_array_object import glGenVertexArrays, \
                                                  glBindVertexArray

import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt

from cython_modules.cython_parse import getLayerOutline, genCubes

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext
from pattern_types.Patterns import AbstractGLContextDecorators

from ColorPolicy import ColorPolicy
from multiprocessing import Pool
from ctypes import c_void_p

from multiprocessing_parse import asynchronous_pool_order

import math

class ArrowGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict, parent):
        self.cld = parent
        super().__init__()
        super().shareData(**data_dict)
        print(self.parent())
        self.DEFAULT_RADIUS = 0.25*self.scale
        self.CYLINDER_CO_ROT =  np.array([self.DEFAULT_RADIUS, 
                                          self.DEFAULT_RADIUS, 0])
        self.CONE_CO_ROT = np.array([2*self.DEFAULT_RADIUS, 
                                     2*self.DEFAULT_RADIUS, 0])
        self.HEIGHT = np.array([0, 0, 3])
        self.ZERO_ROT = np.array([[1, 0, 0],
                                  [0, 1, 0],
                                  [0, 0, 1]])
        self.SIDES = 32
        theta = 2*np.pi/self.SIDES
        c = np.cos(theta)
        s = np.sin(theta)
        self.T_ROTATION = np.array([[c, -s, 0], 
                                    [s, c, 0], 
                                    [0, 0, 1]])

        self.ZERO_PAD = [np.nan for x in range(self.SIDES*4*3)]
        self.drawing_function = self.vbo_arrow_draw
        self.buffers = None
        self.prerendering_calculation()

    def prerendering_calculation(self):
        super().prerendering_calculation()
        if self.normalize:
            ArrowGLContext.normalize_specification(self.color_vectors, vbo=True)
        self.structure_vbo = self.regenerate_structure(self.color_vectors)
        self.index_required = (self.SIDES)*2
        self.indices = self.generate_index()
        self.color_vectors = ColorPolicy.apply_vbo_format(self.color_vectors, 
                                                          k=(self.index_required))
        self.buffers = None
        # pad the color
        self.color_vertices = len(self.vectors_list)
        self.color_buffer_len = len(self.color_vectors[0])

        self.__FLOAT_BYTE_SIZE__ = 8


    def generate_index(self):
        # try:
        #     indices = np.loadtxt('savespace/index.obj', delimiter=';', dtype='uint32')
        #     return indices[:self.n]
        # except FileNotFoundError:
        indices = []
        for n in range(self.n):
            start_index = n*self.index_required+3
            for i in range(int(self.index_required)-2):
                l = [start_index+i-3, start_index+i-2, start_index+i-1]
                indices.extend(l)
        indices = np.array(indices, dtype='uint32')
        return indices

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

    def create_vbo(self):
        buffers = gl.glGenBuffers(3)
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

        # # index buffer
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, buffers[2])
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                        self.indices,
                        gl.GL_STATIC_DRAW)
        return buffers

    def vbo_arrow_draw(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, 
                               len(self.structure_vbo[self.i])*4,
                               np.array(self.structure_vbo[self.i],
                               dtype='float32').flatten())

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference changes
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, 
                               self.color_buffer_len*4,
                               np.array(self.color_vectors[self.i],
                               dtype='float32').flatten())
        self.draw_vbo()

    @AbstractGLContextDecorators.recording_decorator
    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        # bind color buffer
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        # bind vertex buffer - cylinder
        # stride is one  vertex
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT, 3*self.__FLOAT_BYTE_SIZE__, None)
        gl.glDrawElements(gl.GL_TRIANGLES,
                        len(self.indices),
                        gl.GL_UNSIGNED_INT, 
                        None)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT,
                            3*self.__FLOAT_BYTE_SIZE__, c_void_p(4*3))

        gl.glDrawElements(gl.GL_TRIANGLES,
                        len(self.indices),
                        gl.GL_UNSIGNED_INT, 
                        None)

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    @staticmethod
    def generate_arrow_object(origin_circle,
                               rot_matrix, 
                               cylinder_co_rot, 
                               cone_co_rot,
                               t_rotation,
                               height,
                               sides):
        # no faces for now
        vbo = []
        org_cyl_rot = cylinder_co_rot 
        org_cone_rot = cone_co_rot
        for i in range(sides-1):
            # bottom triangle - cylinder
            vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot))
            # bottom triangle - cone
            vbo.extend(origin_circle+rot_matrix.dot(cone_co_rot+height))
            # top triangle -cylinder
            vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot+height))
            # top triangle -cone
            vbo.extend(origin_circle+rot_matrix.dot(height*1.5))
            cylinder_co_rot = t_rotation.dot(cylinder_co_rot)        
            cone_co_rot = t_rotation.dot(cone_co_rot)     
               
        vbo.extend(origin_circle+rot_matrix.dot(org_cyl_rot))
        vbo.extend(origin_circle+rot_matrix.dot(org_cone_rot+height))
        vbo.extend(origin_circle+rot_matrix.dot(org_cyl_rot+height))
        vbo.extend(origin_circle+rot_matrix.dot(height*1.5))
        return vbo


    @staticmethod
    def construct_rotation_matrix(vector):
        cos_x_rot = vector[1]
        cos_y_rot = vector[0]/math.sqrt(1 - math.pow(vector[2],2))
        sin_x_rot = math.sin(math.acos(cos_x_rot)) # radian input
        sin_y_rot = math.sin(math.acos(cos_y_rot))
        return np.array([[cos_y_rot, 0, sin_y_rot],
                         [sin_y_rot*sin_x_rot, cos_x_rot, -sin_x_rot*cos_y_rot],
                         [-cos_x_rot*sin_y_rot, sin_x_rot, sin_x_rot*cos_y_rot]])

    @staticmethod
    def process_vector_to_vbo(iteration, 
                              vectors_list, 
                              cylinder_co_rot, 
                              cone_co_rot, 
                              t_rotation,
                              height,
                              zero_rot,
                              sides,
                              zero_pad):
        local_vbo = []
        for vector, color in zip(vectors_list, iteration):
            if color.any():
                try:
                    rot_matrix = ArrowGLContext.construct_rotation_matrix(color)
                    local_vbo.extend(ArrowGLContext.generate_arrow_object(np.array(vector[0:3]), 
                                                        rot_matrix,
                                                        cylinder_co_rot, 
                                                        cone_co_rot, 
                                                        t_rotation,
                                                        height,
                                                        sides))
                except:
                    local_vbo.extend(zero_pad)
            else:
                local_vbo.extend(zero_pad)

        return local_vbo

    def regenerate_structure(self, colors_list):
        iterative_vbo = asynchronous_pool_order(ArrowGLContext.process_vector_to_vbo, (
                                                self.vectors_list, self.CYLINDER_CO_ROT,
                                                                   self.CONE_CO_ROT,
                                                                   self.T_ROTATION,
                                                                   self.HEIGHT,
                                                                   self.ZERO_ROT,
                                                                   self.SIDES,
                                                                   self.ZERO_PAD), 
                                                colors_list)
        self.n = len(self.vectors_list)
        return np.array(iterative_vbo)