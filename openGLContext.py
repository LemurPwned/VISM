import OpenGL.GLU as glu
import OpenGL.GL as gl
import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt

from cython_modules.cython_parse import generate_cubes, getLayerOutline
from AbstractGLContext import AbstractGLContext
from ColorPolicy import ColorPolicy
from multiprocessing import Pool


class OpenGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        self.drawing_function = None
        self.steps = 1
        self.spacer = 0.2
        self.vectors_list = None
        self.vertices = 0

        self.modified_animation = True
        self.buffers = None
        self.buffer_len = 0
        self.shareData(**data_dict)

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        if self.omf_header['binary']:
            self.drawing_function = self.vbo_cubic_draw

            custom_color_policy = ColorPolicy()
            xc = int(self.omf_header['xnodes'])
            yc = int(self.omf_header['ynodes'])
            zc = int(self.omf_header['znodes'])
            layer = 3
            # testing layer extraction
            # extarction of layer means limiting vectors list
            self.color_list = np.array([self.color_list[i].reshape(zc, xc*yc,3)[layer-1]
                                    for i in range(self.iterations)])

            self.color_list = custom_color_policy.apply_normalization(self.color_list,
                                xc, yc, zc=1)

            self.color_list = \
                            custom_color_policy.averaging_policy(self.color_list,
                                                                None, 3)

            self.color_list = custom_color_policy.apply_vbo_format(self.color_list)

            self.buffer_len = len(self.color_list[0])
            self.vectors_list, self.vertices = generate_cubes(self.omf_header,
                                                    self.spacer, skip=3,
                                                    layer=1)
            # vertices = 3*vectors
        else:
            self.vectors_list = getLayerOutline(self.omf_header)
            self.drawing_function = self.slower_cubic_draw

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
        buffers = gl.glGenBuffers(2)
        # vertices buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[0])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.vectors_list, dtype='float32'),
                        gl.GL_STATIC_DRAW)
        # color buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffers[1])
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        np.array(self.color_list[self.i],
                        dtype='float32').flatten(),
                        gl.GL_DYNAMIC_DRAW)
        return buffers

    def vbo_cubic_draw(self):
        if self.buffers is None:
            self.buffers = self.create_vbo()
        else:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
            # later move to set_i function so that reference change
            # does not cause buffer rebinding
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.buffer_len,
                               np.array(self.color_list[self.i],
                               dtype='float32').flatten())
        self.draw_vbo()

    def draw_vbo(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[0])
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[1])
        gl.glColorPointer(3, gl.GL_FLOAT, 0, None)

        gl.glDrawArrays(gl.GL_QUADS, 0, int(self.vertices))

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    def slower_cubic_draw(self):
        for vector, color in zip(self.vectors_list, self.color_list[self.i]):
            gl.glColor3f(*color)
            self.draw_cube(vector)

    def draw_cube(self, vec):
        """
        draws basic cubes separated by spacer value
        @param vec (x,y,z) coordinate specifying bottom left face corner
        """
        # TOP FACE
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2] + self.spacer)
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2] + self.spacer)
        # BOTTOM FACE
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2])
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2])
        # FRONT FACE
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2] + self.spacer)
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
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2] + self.spacer)
        gl.glVertex3f(vec[0] + self.spacer, vec[1] + self.spacer, vec[2])
        gl.glVertex3f(vec[0] + self.spacer, vec[1], vec[2])
        # LEFT FACE
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2] + self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1] + self.spacer, vec[2])
        gl.glEnd()
