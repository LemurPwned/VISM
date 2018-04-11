import OpenGL.GLU as glu
import OpenGL.GL as gl
import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QThread


from cython_modules.cython_parse import getLayerOutline, genCubes
from cython_modules.color_policy import multi_iteration_normalize

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext

from ColorPolicy import ColorPolicy
from multiprocessing import Pool


class CubicGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        self.drawing_function = None
        self.steps = 1
        self.spacer = 0.2
        self.vectors_list = None
        self.vertices = 0

        self.buffers = None
        self.fbo = None
        self.buffer_len = 0

        self.shareData(**data_dict)


    def shareData(self, **kwargs):
        super().shareData(**kwargs)

        self.spacer = self.spacer*self.scale
        xc = int(self.omf_header['xnodes'])
        yc = int(self.omf_header['ynodes'])
        zc = int(self.omf_header['znodes'])

        # remap
        self.i = self.current_state

        custom_color_policy = ColorPolicy()
        self.vectors_list = getLayerOutline(self.omf_header)
        # change drawing function
        self.color_vectors, self.vectors_list, decimate = \
                    custom_color_policy.standard_procedure(self.vectors_list,
                                                           self.color_vectors,
                                                           self.iterations,
                                                           self.averaging,
                                                           xc, yc, zc,
                                                           self.layer,
                                                           self.vector_set,
                                                           self.decimate,
                                                           disableDot=self.disableDot)
        if decimate is not None:
            # this is arbitrary
            self.spacer *= decimate*3

        if self.normalize:
            multi_iteration_normalize(self.color_vectors)

        if self.function_select == 'fast':
            self.drawing_function = self.vbo_cubic_draw
            self.buffers = None
            # if vbo drawing is selected, do additional processing
            self.color_vectors = custom_color_policy.apply_vbo_format(self.color_vectors)
            self.vectors_list, self.vertices = genCubes(self.vectors_list,
                                                                    self.spacer)
            print(np.array(self.vectors_list).shape, self.vertices)
            print(np.array(self.color_vectors).shape)

            # TODO: temporary fix, dont know why x4, should not be multiplied
            # at all!
            self.buffer_len = len(self.color_vectors[0])*4
            print("BUFFER LEN" , self.buffer_len)

        elif self.function_select == 'slow':
            self.drawing_function = self.slower_cubic_draw

    def create_vbo(self):
        buffers = gl.glGenBuffers(2)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.vectors_list,
                        dtype='float32').flatten(),
                        gl.GL_STATIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.color_vectors[self.i],
                        dtype='float32').flatten(),
                        gl.GL_DYNAMIC_DRAW)
        return buffers

    def vbo_cubic_draw(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
            if self.fbo is None:
                fbo_handler = self.defaultFramebufferObject()
                # self.fbo = gl.glGenFramebuffers(1)
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo_handler)
                self.fbo = 1
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference changes
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.buffer_len,
                               np.array(self.color_vectors[self.i],
                               dtype='float32').flatten())

            if self.grabFramebuffer().save('./SCR/'+str(self.i), 'JPG'):
                print("successfull saving")
        self.draw_vbo()

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        # bind vertex buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None)
        # bind color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        gl.glDrawArrays(gl.GL_QUADS, 0, int(self.vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def slower_cubic_draw(self):
        for vector, color in zip(self.vectors_list, self.color_vectors[self.i]):
            gl.glColor3f(*color)
            self.draw_cube(vector)

    def draw_cube(self, vec):
        """
        draws basic cubes separated by spacer value
        :param vec (x,y,z) coordinate specifying bottom left face corner
        """
        # TOP FACE
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2] + self.spacer)
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2] + \
                    self.spacer)
        # BOTTOM FACE
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2])
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2])
        # FRONT FACE
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2] + \
                    self.spacer)
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2])
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2])
        # BACK FACE
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2])
        # RIGHT FACE
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2] + \
                    self.spacer)
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2])
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2])
        # LEFT FACE
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2])
        gl.glEnd()
