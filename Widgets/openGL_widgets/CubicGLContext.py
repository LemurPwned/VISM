import OpenGL.GL as gl
import numpy as np

from PyQt5.QtWidgets import QWidget

from cython_modules.cython_parse import getLayerOutline, genCubes

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext
from pattern_types.Patterns import AbstractGLContextDecorators

from ColorPolicy import ColorPolicy


class CubicGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict, parent):
        self.cld = parent
        super().__init__()
        super().shareData(**data_dict)
        self.vertices = 0
        self.buffers = None
        self.buffer_len = 0
        self.scale = 5

        self.prerendering_calculation()
        self.drawing_function = self.vbo_cubic_draw

    def prerendering_calculation(self):
        super().prerendering_calculation()
        if self.normalize:
            CubicGLContext.normalize_specification(self.color_vectors, vbo=True)

        if self.function_select == 'fast':
            self.drawing_function = self.vbo_cubic_draw
            self.buffers = None
            # if vbo drawing is selected, do additional processing

            xc = int(self.file_header['xnodes'])
            yc = int(self.file_header['ynodes'])
            zc = int(self.file_header['znodes'])
            self.vectors_list, self.vertices = genCubes(self.vectors_list,
                                                                    self.spacer)
            self.color_vectors = ColorPolicy.apply_vbo_format(self.color_vectors)

            print(np.array(self.vectors_list).shape, self.vertices)
            print(np.array(self.color_vectors).shape)

            # TODO: temporary fix, dont know why x4, should not be multiplied
            # at all!
            self.buffer_len = len(self.color_vectors[0])*4
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
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference changes
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.buffer_len,
                               np.array(self.color_vectors[self.i],
                               dtype='float32').flatten())
        self.draw_vbo()

    @AbstractGLContextDecorators.recording_decorator
    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        # bind vertex buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(4, gl.GL_FLOAT, 0, None)
        # bind color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        gl.glDrawArrays(gl.GL_QUADS, 0, int(self.vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    @AbstractGLContextDecorators.recording_decorator
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
