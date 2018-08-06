import OpenGL.GL as gl
import numpy as np
from PyQt5.QtWidgets import QWidget

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext
from pattern_types.Patterns import AbstractGLContextDecorators

from ColorPolicy import ColorPolicy
from ctypes import c_void_p
from multiprocessing_parse import asynchronous_pool_order
from cython_modules.color_policy import process_vector_to_vbo, multi_iteration_normalize
import math

from PopUp import PopUpWrapper

class ArrowGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict, parent):
        self.cld = parent
        super().__init__()
        super().shareData(**data_dict)
        self.DEFAULT_RADIUS = 0.25*self.scale
        self.CYLINDER_CO_ROT = np.array([self.DEFAULT_RADIUS,
                                         self.DEFAULT_RADIUS, 0])
        self.CONE_CO_ROT = np.array([2*self.DEFAULT_RADIUS, 
                                     2*self.DEFAULT_RADIUS, 0])
        self.HEIGHT = np.array([0, 0, 3])
        self.ZERO_ROT = np.array([[1, 0, 0],
                                  [0, 1, 0],
                                  [0, 0, 1]])
        self.SIDES = self.resolution
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
        multi_iteration_normalize(self.colorX)
        self.structure_vbo = self.regenerate_structure(self.colorX)
        self.index_required = self.SIDES*2
        self.indices = self.generate_index()
        self.color_vectors = ColorPolicy.apply_vbo_format(self.color_vectors, 
                                                          k=(self.index_required))
        self.buffers = None
        # pad the color
        self.color_vertices = len(self.vectors_list)
        self.color_buffer_len = len(self.color_vectors[0])

        self.__FLOAT_BYTE_SIZE__ = 8

    def generate_index(self):
        indices = []
        for n in range(self.n):
            start_index = n*self.index_required+3
            for i in range(int(self.index_required)-2):
                l = [start_index+i-3, start_index+i-2, start_index+i-1]
                indices.extend(l)
        indices = np.array(indices, dtype='uint32')
        return indices

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
            try:
                gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, 
                                    len(self.structure_vbo[self.i])*12,
                                    np.array(self.structure_vbo[self.i],
                                    dtype='float32').flatten())
            except ValueError as e:
                print(e) # watch out for setting array element with a sequence erorr
                print(len(self.structure_vbo[self.i]), len(self.structure_vbo[self.i][0]))

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
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_DIFFUSE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
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

    def regenerate_structure(self, colors_list):
        col_len = len(colors_list)
        iterative_vbo = np.ndarray((col_len, 
                                    len(self.vectors_list)*self.SIDES*4,3), 
                                    dtype='float32')
        for i in range(0, self.iterations):
            iterative_vbo[i, :] = process_vector_to_vbo(colors_list[i],
                                                        self.vectors_list, 
                                                        self.CYLINDER_CO_ROT,
                                                        self.CONE_CO_ROT,
                                                        self.T_ROTATION,
                                                        self.HEIGHT,
                                                        self.SIDES)
        self.n = len(self.vectors_list)
        return iterative_vbo
