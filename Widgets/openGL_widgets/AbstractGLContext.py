from AnimatedWidget import AnimatedWidget
from PyQt5.QtWidgets import QOpenGLWidget
import OpenGL.GL as gl
import OpenGL.GLU as glu

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QCoreApplication, QSize

import math as mt
from PIL import Image
import os

import numpy as np

from cython_modules.color_policy import multi_iteration_normalize
from cython_modules.cython_parse import getLayerOutline, genCubes
from ColorPolicy import ColorPolicy
from pattern_types.Patterns import AbstractGLContextDecorators

from buildVerifier import BuildVerifier

import time
import pygame

class AbstractGLContext(QOpenGLWidget, AnimatedWidget):
    PYGAME_INCLUDED = False
    RECORD_REGION_SELECTION = False
    SELECTED_POS = None
    TEXT = None

    ANY_GL_WIDGET_IN_VIEW = 0

    def __init__(self, parent=None):
        super(AbstractGLContext, self).__init__(parent)
        AbstractGLContext.ANY_GL_WIDGET_IN_VIEW += 1
        self.subdir = "GL" + str(AnimatedWidget.WIDGET_ID)
        AnimatedWidget.WIDGET_ID += 1
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

        self.display_frames = False
        self.frames = 0
        self.fps = 0
        self.FRAME_BENCHMARK_FLAG = False
        self.FPS_UPDATE_INTERVAL = 0.25
        self.TIME_PASSED = 0.0

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        super().handleOptionalData()
        self.receivedOptions()
        self.i = self.current_state

    @classmethod
    def normalize_specification(cls, color_vectors, vbo=False):
        """
        normalization procedure
        """
        multi_iteration_normalize(color_vectors)
        background = np.array([0.5, 0.5, 0.5])
        if cls.__name__ == 'CubicGLContext':
            # color_vectors = ColorPolicy.multi_padding(color_vectors)
            background = np.array([np.nan, np.nan, np.nan])
            # replace black with background colors
            # NOTE: This is dangerous since dot product can be zero
            # color_vectors[~color_vectors.any(axis=2)] = background
        elif cls.__name__ == 'VectorGLContext':
            background = np.array([0.0, 0.0, 0.0])
            if vbo:
                pass
                # not needed right now but leave for compatibility
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
        super().handleOptionalData()
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
        gl.glClearColor(*self.background, 0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_POLYGON_SMOOTH)

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
        self.text_functionalities()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    @AbstractGLContextDecorators.systemDisable
    def text_functionalities(self):
        self.frames +=1
        self.fps_counter()
        if self.display_frames:
            self.text_render(str(self.i))
        if AbstractGLContext.TEXT is not None \
            and AbstractGLContext.SELECTED_POS is not None:
            self.text_render(AbstractGLContext.TEXT,
                            AbstractGLContext.SELECTED_POS)

    def set_i(self, value, trigger=False, record=False):
        if trigger:
            self.i += 1
        else:
            self.i = value
        self.i %= self.iterations
        self.record = record

    def keyPressEvent(self, event):
        """
        Key mapping:
        R - reset central view
        I - zoom in
        O - zoom out
        Y - start/stop recording
        S - take a screenshot
        B - start benchmarking
        F - display current frame
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
            self.FRAME_BENCHMARK_FLAG = \
                                not self.FRAME_BENCHMARK_FLAG
        if key == Qt.Key_F:
            self.display_frames = True

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

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if AbstractGLContext.RECORD_REGION_SELECTION:
            y = self.geom[1] - y
            AbstractGLContext.SELECTED_POS = (x, y, 0)
            AbstractGLContext.RECORD_REGION_SELECTION = False

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
            if abs(dx) > abs(dy):
                self.rotation[0] += dx * rotation_speed
                xpos = self.position[0] * mt.cos(dx * rotation_speed * mt.pi / 180) \
                       - self.position[2] * mt.sin(dx * rotation_speed * mt.pi / 180)
                zpos = self.position[0] * mt.sin(dx * rotation_speed * mt.pi / 180) \
                       + self.position[2] * mt.cos(dx * rotation_speed * mt.pi / 180)

                self.position[0] = xpos
                self.position[2] = zpos
            else:
                self.rotation[1] += dy * rotation_speed
                ypos = self.position[1] * mt.cos(dy * rotation_speed * mt.pi / 180) \
                       + self.position[2] * mt.sin(dy * rotation_speed * mt.pi / 180)
                zpos = - self.position[1] * mt.sin(dy * rotation_speed * mt.pi / 180) \
                       + self.position[2] * mt.cos(dy * rotation_speed * mt.pi / 180)

                self.position[1] = ypos
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
            self.TIME_PASSED = time.time()
            self.frames = 0
        elif self.FRAME_BENCHMARK_FLAG:
            ctime = time.time()
            if ((ctime - self.TIME_PASSED) > \
                                    self.FPS_UPDATE_INTERVAL):
                self.fps = int(self.frames/(ctime - self.TIME_PASSED))
                _, _, width, height = gl.glGetIntegerv(gl.GL_VIEWPORT)
                self.TIME_PASSED = ctime
                self.frames = 0
            self.text_render(str(self.fps))

    def text_render(self, textString, position=(10, 10, 0)):
        if not AbstractGLContext.PYGAME_INCLUDED:
            pygame.init()
            AbstractGLContext.PYGAME_INCLUDED = True
        font = pygame.font.Font (None, 64)
        renderedFont = font.render(textString, False, (255,255,255,255))
        text = pygame.image.tostring(renderedFont, "RGBA", True)
        gl.glWindowPos3f(position[0], position[1] - renderedFont.get_height(),
                            position[2])
        gl.glDrawPixels(renderedFont.get_width(), renderedFont.get_height(),
                                     gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text)

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
        # print(width, height)
        if width == 0 or height == 0:
            width = self.geom[0]
            height = self.geom[1]
        color = gl.glReadPixels(0, 0,
                               width, height,
                               gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        image = Image.frombytes(mode='RGB', size=(width, height),
                                                    data=color)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        try:
            if os.path.basename(self.screenshot_dir) != self.subdir:
                self.screenshot_dir = os.path.join(self.screenshot_dir,
                                                                self.subdir)
            image.save(os.path.join(self.screenshot_dir,
                                        str(self.i).zfill(4) + ".png"))
        except FileNotFoundError:
            # if basic dir not found, create it and save there
            os.makedirs(self.screenshot_dir)
            image.save(os.path.join(self.screenshot_dir,
                                        str(self.i).zfill(4) + ".png"))
