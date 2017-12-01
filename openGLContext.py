import OpenGL.GLU as glu
import OpenGL.GL as gl
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint
import math as mt
from cython_modules.cython_parse import generate_cubes, getLayerOutline
from AbstractGLContext import AbstractGLContext


class OpenGLContext(AbstractGLContext, QWidget):
    def __init__(self, data_dict):
        super().__init__()
        self.drawing_function = None
        self.steps = 1
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [10, 10, -50]  # xyz initial
        self.spacer = 0.2
        self.vectors_list = None
        self.vertices = 0

        self.setFocusPolicy(Qt.StrongFocus)  # needed if keyboard to be active
        self.modified_animation = True
        self.lastPos = QPoint()
        self.buffers = None
        self.buffer_len = 0
        self.shareData(**data_dict)

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        if self.omf_header['binary']:
            self.drawing_function = self.vbo_cubic_draw
            self.buffer_len = len(self.color_list[0])
            self.vectors_list, self.vertices = generate_cubes(self.omf_header,
                                                    self.spacer)
            print(len(self.vectors_list))
            print(self.vertices)
            print(len(self.color_list[0]))
            # vertices = 3*vectors
        else:
            self.vectors_list = getLayerOutline(self.omf_header)
            self.drawing_function = self.slower_cubic_draw

    def initial_transformation(self):
        """
        resets the view to the initial one
        :return: 
        """
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [10, 10, -50]  # xyz initial

    def transformate(self):  # applies rotation and transformation
        gl.glRotatef(self.rotation[0], 0, 1, 0)  # rotate around y axis
        gl.glRotatef(self.rotation[1], 1, 0, 0)  # rotate around x axis
        gl.glRotatef(self.rotation[2], 0, 0, 1)  # rotate around z axis
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])

    def initializeGL(self):
        """
        Initializes openGL context and scenery
        """
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

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
                        np.array(self.color_list[self.i], dtype='float32').flatten(),
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
                               np.array(self.color_list[self.i], dtype='float32').flatten())
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
        @param vec (x,y,z) coordinate determining bottom left face
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

    def wheelEvent(self, event):
        """
        Handles basic mouse scroll
        """
        degs = event.angleDelta().y() / 8
        self.steps += degs / 15
        # SMART SCROLL BETA
        self.position[0] -= mt.sin(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[1] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.sin(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[2] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps
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
            rotation_speed = 0.5
            self.rotation[0] += dx * rotation_speed
            xpos = self.position[0] * mt.cos(dx * rotation_speed * mt.pi / 180) \
                   - self.position[2] * mt.sin(dx * rotation_speed * mt.pi / 180)
            zpos = self.position[0] * mt.sin(dx * rotation_speed * mt.pi / 180) \
                   + self.position[2] * mt.cos(dx * rotation_speed * mt.pi / 180)

            self.position[0] = xpos
            self.position[2] = zpos
        elif event.buttons() & Qt.RightButton:
            self.position[0] += dx * 0.2
            self.position[1] += dy * 0.2

        self.update()

    def keyPressEvent(self, event):
        """
        if r is pressed on the keyboard, then reset view
        """
        key = event.key()
        if key == Qt.Key_R:
            self.initial_transformation()
            self.update()

    def set_i(self, value):
        self.i = value
        self.i %= self.iterations
        self.update()
