from AnimatedWidget import AnimatedWidget
from PyQt5.QtWidgets import QOpenGLWidget

import OpenGL.GL as gl
import OpenGL.GLU as glu

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint

import math as mt
from PIL import Image
import os

import numpy as np

from cython_modules.color_policy import multi_iteration_normalize
from cython_modules.cython_parse import getLayerOutline, genCubes
from ColorPolicy import ColorPolicy

import time

class AbstractGLContext(QOpenGLWidget, AnimatedWidget):
    FRAME_BENCHMARK_FLAG = False
    FRAMES = 0
    FPS_UPDATE_INTERVAL = 0.5
    TIME_PASSED = 0.0

    def __init__(self, parent=None):
        super(AbstractGLContext, self).__init__(parent)

        self.lastPos = QPoint()
        self.setFocusPolicy(Qt.StrongFocus)  # needed if keyboard to be active

        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [0, 0, -50]  # xyz initial
        self.drawing_function = None
        self.function_select = 'fast'
        self.background = [0.5, 0.5, 0.5]
        self.record = False
        self.spacer = 0.2
        self.steps = 1

        self.frames = 0

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        super().handleOptionalData()
        self.receivedOptions()
        self.i = self.current_state
        print(self.iterations)

    @classmethod
    def normalize_specification(cls, color_vectors, vbo=False):
        """
        normalization procedure
        """
        multi_iteration_normalize(color_vectors)
        background = np.array([0.5, 0.5, 0.5])
        if cls.__name__ == 'CubicGLContext':
            # replace black with background colors
            # NOTE: This is dangerous since dot product can be zero
            color_vectors[~color_vectors.any(axis=2)] = background
        elif cls.__name__ == 'VectorGLContext':
            if vbo:
                # replace black with background colors
                # NOTE: This is dangerous since dot product can be zero
                color_vectors[~color_vectors.any(axis=2)] = background

    def prerendering_calculation(self):
        """
        Some calculations that take place before object gets rendered
        """
        # get vector outline
        self.vectors_list = getLayerOutline(self.file_header)
        self.auto_center()
        # adjust spacing
        self.spacer = self.spacer*self.scale

        xc = int(self.file_header['xnodes'])
        yc = int(self.file_header['ynodes'])
        zc = int(self.file_header['znodes'])
        # change drawing function
        self.color_vectors, self.vectors_list, decimate = \
                    ColorPolicy.standard_procedure(self.vectors_list,
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

    def handleOptionalData(self):
        # must handle iterations since these are optional
        try:
            getattr(self, 'iterations')
        except NameError:
            self.iterations = 1

    def auto_center(self):
        """
        auto centers the structure in widget screen
        """
        x_fix = (self.file_header['xnodes'] * self.file_header['xbase'] * 1e9) / 2
        y_fix = (self.file_header['ynodes'] * self.file_header['ybase'] * 1e9) / 2
        z_fix = (self.file_header['znodes'] * self.file_header['zbase'] * 1e9) / 2
        for vec in self.vectors_list:
            vec[0] -= x_fix
            vec[1] -= y_fix
            vec[2] -= z_fix

    def initial_transformation(self):
        """
        resets the view to the initial one
        :return:
        """
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [0, 0 , -50]  # xyz initial

    def transformate(self):
        """
        applies rotation and transformation
        """
        gl.glRotatef(self.rotation[0], 0, 1, 0)  # rotate around y axis
        gl.glRotatef(self.rotation[1], 1, 0, 0)  # rotate around x axis
        gl.glRotatef(self.rotation[2], 0, 0, 1)  # rotate around z axis
        gl.glTranslatef(self.position[0], self.position[1], self.position[2])

    def initializeGL(self):
        """
        Initializes openGL context and scenery
        """

        gl.glClearColor(*self.background, 1)
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
        self.frames +=1
        self.fps_counter()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Push Matrix onto stack
        gl.glPushMatrix()
        self.transformate()
        self.drawing_function()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    def set_i(self, value, trigger=False):
        if trigger:
            self.i += 1
        else:
            self.i = value
        self.i %= self.iterations

    def keyPressEvent(self, event):
        """
        Key mapping:
        R - reset central view
        I - zoom in
        O - zoom out
        Y - start/stop recording
        S - take a screenshot
        """
        key = event.key()
        if key == Qt.Key_R:
            self.initial_transformation()
            self.update()

        elif key == Qt.Key_I:
            self.zoomIn()

        elif key == Qt.Key_O:
            self.zoomOut()

        if key == Qt.Key_Y:
            self.record = not self.record

        if key == Qt.Key_S:
            self.screenshot_manager()

        if key == Qt.Key_B:
            self.fps_counter(initialize=True)
            AbstractGLContext.FRAME_BENCHMARK_FLAG = True

    def zoomIn(self):
        self.steps = 1
        # SMART SCROLL BETA
        self.position[0] -= mt.sin(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[1] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.sin(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[2] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps


    def zoomOut(self):
        self.steps = -1

        self.position[0] -= mt.sin(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[1] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.sin(self.rotation[1] * mt.pi / 180) * self.steps
        self.position[2] += mt.cos(self.rotation[0] * mt.pi / 180) * \
                            mt.cos(self.rotation[1] * mt.pi / 180) * self.steps

    def wheelEvent(self, event):
        """
        Handles basic mouse scroll
        """
        degs = event.angleDelta().y() / 8
        self.steps = degs / 15
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
            if abs(self.rotation[0])%360 < 90:
                self.position[0] += dx * 0.2
            else:
                self.position[0] -= dx * 0.2

            self.position[1] -= dy * 0.2
        self.update()

    def fps_counter(self, initialize=False):
        if initialize:
            AbstractGLContext.TIME_PASSED = time.time()
            self.frames = 0
        elif AbstractGLContext.FRAME_BENCHMARK_FLAG:
            ctime = time.time()
            if ((ctime - AbstractGLContext.TIME_PASSED) > \
                                    AbstractGLContext.FPS_UPDATE_INTERVAL):
                fps = self.frames/(ctime - AbstractGLContext.TIME_PASSED)
                AbstractGLContext.TIME_PASSED = ctime
                self.frames = 0

    @staticmethod
    def get_open_gl_info():
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
            """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))
        return info

    def screenshot_manager(self):
        """
        saves the screenshot to the folder specified in screenshot_dir
        """
        # fetch dimensions for highest resolution
        _, _, width, height = gl.glGetIntegerv(gl.GL_VIEWPORT)
        color = gl.glReadPixels(0, 0,
                               width, height,
                               gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        image = Image.frombytes(mode='RGB', size=(width, height),
                                                    data=color)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        try:
            image.save(os.path.join(self.screenshot_dir,
                                        str(self.i).zfill(4) + ".png"))
        except FileNotFoundError:
            # if basic dir not found, create it and save there
            os.mkdir(self.screenshot_dir)
            image.save(os.path.join(self.screenshot_dir,
                                        str(self.i).zfill(4) + ".png"))
