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

class BetterArrow(AbstractGLContext, QWidget):
    DEFAULT_RADIUS = 0.25
    CYLINDER_CO_ROT =  np.array([DEFAULT_RADIUS, DEFAULT_RADIUS, 0])
    CONE_CO_ROT = np.array([2*DEFAULT_RADIUS, 2*DEFAULT_RADIUS, 0])
    HEIGHT = np.array([0, 0, 3])
    ZERO_ROT = np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]])
    SIDES = 32
    theta = 2*np.pi/SIDES
    c = np.cos(theta)
    s = np.sin(theta)
    T_ROTATION = np.array([[c, -s, 0], 
                           [s, c, 0], 
                           [0, 0, 1]])

    def __init__(self, data_dict):
        super().__init__()
        super().shareData(**data_dict)
        self.sides = 32
        self.spacer = 0
        theta = 2*np.pi/self.sides
        c = np.cos(theta)
        s = np.sin(theta)
        # this is cylinder rotation matrix[a]
        self.zero_rot = np.array([[1, 0, 0],[0, 1, 0],[0, 0, 1]])
        self.t_rotation = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        self.default_radius = 0.25
        self.cylinder_co_rot =  np.array([self.default_radius, self.default_radius, 0])
        self.cone_c_rot = np.array([2*self.default_radius, 2*self.default_radius, 0])
        self.height = np.array([0, 0, 3])
        self.drawing_function = self.vbo_arrow_draw
        self.buffers = None
        self.n = 20000
        self.prerendering_calculation()

    def prerendering_calculation(self):
        super().prerendering_calculation()
        if self.normalize:
            BetterArrow.normalize_specification(self.color_vectors, vbo=True)
        # self.structure_vbo = self.generate_structure(self.vectors_list,
                                                                    # self.color_vectors)
        self.structure_vbo = self.regenerate_structure(self.color_vectors)
        self.index_required = (self.sides)*2
        print("INDEX REQUIRED {}".format(self.index_required))
        self.indices = []
        self.generate_index()
        print("INDICES :{}".format(self.indices.shape))
        self.color_vectors = ColorPolicy.apply_vbo_format(self.color_vectors, 
                                                            k=(self.index_required))
        print(np.array(self.structure_vbo).shape, self.color_vectors.shape)

        self.buffers = None
        # pad the color
        self.color_vertices = len(self.vectors_list)
        self.color_buffer_len = len(self.color_vectors[0])

        self.__FLOAT_BYTE_SIZE__ = 8


    def generate_index(self):
        for n in range(self.n):
            start_index = n*self.index_required+3
            for i in range(int(self.index_required)-2):
                l = [start_index+i-3, start_index+i-2, start_index+i-1]
                self.indices.extend(l)
        self.indices = np.array(self.indices, dtype='uint32')

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
    def generate_arrow_object2(origin, rot_matrix):
        # no faces for now
        vbo = []
        origin_circle = np.array([origin[0],
                                  origin[1],
                                  origin[2]])

        cylinder_co_rot = BetterArrow.CYLINDER_CO_ROT
        cone_co_rot = BetterArrow.CONE_CO_ROT
        for i in range(BetterArrow.SIDES-1):
            # bottom triangle - cylinder
            vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot))
            # bottom triangle - cone
            vbo.extend(origin_circle+rot_matrix.dot(cone_co_rot+BetterArrow.HEIGHT))
            # top triangle -cylinder
            vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot+BetterArrow.HEIGHT))
            # top triangle -cone
            vbo.extend(origin_circle+rot_matrix.dot(BetterArrow.HEIGHT*1.5))
            cylinder_co_rot = BetterArrow.T_ROTATION.dot(cylinder_co_rot)        
            cone_co_rot = BetterArrow.T_ROTATION.dot(cone_co_rot)     
               
        vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot))
        vbo.extend(origin_circle+rot_matrix.dot(cone_co_rot+BetterArrow.HEIGHT))
        vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot+BetterArrow.HEIGHT))
        vbo.extend(origin_circle+rot_matrix.dot(BetterArrow.HEIGHT*1.5))
        return vbo

    def generate_arrow_object(self, origin, rot_matrix):
        # no faces for now
        vbo = []
        origin_circle = np.array([origin[0],
                                  origin[1],
                                  origin[2]])

        cylinder_co_rot = self.cylinder_co_rot
        cone_co_rot = self.cone_c_rot
        for i in range(self.sides-1):
            # bottom triangle - cylinder
            vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot))
            # bottom triangle - cone
            vbo.extend(origin_circle+rot_matrix.dot(cone_co_rot+self.height))
            # top triangle -cylinder
            vbo.extend(origin_circle+rot_matrix.dot(cylinder_co_rot+self.height))
            # top triangle -cone
            vbo.extend(origin_circle+rot_matrix.dot(self.height*1.5))
            cylinder_co_rot = self.t_rotation.dot(cylinder_co_rot)        
            cone_co_rot = self.t_rotation.dot(cone_co_rot)     
               
        vbo.extend(origin_circle+rot_matrix.dot(self.cylinder_co_rot))
        vbo.extend(origin_circle+rot_matrix.dot(self.cone_c_rot+self.height))
        vbo.extend(origin_circle+rot_matrix.dot(self.cylinder_co_rot+self.height))
        vbo.extend(origin_circle+rot_matrix.dot(self.height*1.5))
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
    def process_vector_to_vbo(iteration, vectors_list):
        local_vbo = []
        for vector, color in zip(vectors_list, iteration):
            if color.any():
                try:
                    rot_matrix = BetterArrow.construct_rotation_matrix(color)
                except:
                    rot_matrix = BetterArrow.ZERO_ROT
                local_vbo.extend(BetterArrow.generate_arrow_object2(vector, rot_matrix))
            else:                    
                local_vbo.extend(BetterArrow.generate_arrow_object2(vector, BetterArrow.ZERO_ROT))
        return local_vbo

    def regenerate_structure(self, colors_list):
        iterative_vbo = asynchronous_pool_order(BetterArrow.process_vector_to_vbo, (self.vectors_list,), 
                                                colors_list)
        self.n = len(self.vectors_list)
        return np.array(iterative_vbo)

    def generate_structure(self, vectors_list, colors_list):
        iterative_vbo = []
        print(vectors_list.shape, colors_list.shape)
        for iteration in colors_list:
            local_vbo = []
            for vector, color in zip(vectors_list, iteration):
                if color.any():
                    try:
                        rot_matrix = self.construct_rotation_matrix(color)
                    except:
                        rot_matrix = self.zero_rot
                    local_vbo.extend(self.generate_arrow_object(vector, rot_matrix))
                else:                    
                    local_vbo.extend(self.generate_arrow_object(vector, self.zero_rot))
            iterative_vbo.append(local_vbo)
        self.n = len(self.vectors_list)
        return iterative_vbo
