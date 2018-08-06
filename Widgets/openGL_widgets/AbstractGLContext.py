from AnimatedWidget import AnimatedWidget
from PyQt5.QtWidgets import QOpenGLWidget
import OpenGL.GL as gl
import OpenGL.GLU as glu

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QCoreApplication, QSize, QMutex

import math as mt
from PIL import Image
import os

import numpy as np

from cython_modules.color_policy import multi_iteration_normalize
from cython_modules.cython_parse import getLayerOutline, genCubes
from ColorPolicy import ColorPolicy
from pattern_types.Patterns import AbstractGLContextDecorators

from buildVerifier import BuildVerifier
from Windows.Select import Select

import time
import pygame

class AbstractGLContext(QOpenGLWidget, AnimatedWidget):
    PYGAME_INCLUDED = False
    ANY_GL_WIDGET_IN_VIEW = 0

    def __init__(self, parent=None):
        super(AbstractGLContext, self).__init__(parent)
        AbstractGLContext.ANY_GL_WIDGET_IN_VIEW += 1
        self.subdir = "GL" + str(AnimatedWidget.WIDGET_ID)
        AnimatedWidget.WIDGET_ID += 1
        self.setFocusPolicy(Qt.StrongFocus)  # needed if keyboard to be active

        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [0, 0, -50]  # xyz initial
        self.drawing_function = None
        self.function_select = 'fast'
        self.background = [0.5, 0.5, 0.5]
        self.record = False
        self.steps = 1

        self.display_frames = False
        self.frames = 0
        self.fps = 0
        self.FRAME_BENCHMARK_FLAG = False
        self.FPS_UPDATE_INTERVAL = 0.25
        self.TIME_PASSED = 0.0

        self.TEXT = None
        self.RECORD_REGION_SELECTION = False
        self.SELECTED_POS = None
        
        """ 
        left mouse must be separately registered
        because right clicks and left clicks with 
        large distance between current and last position
        can lead to rapid rotations 
        """
        self.registered_left_mouse = False
        self.registered_left_mouse_pos = None

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        self.handleOptionalData()
        self.receivedOptions()
        self.i = self.current_state

    def prerendering_calculation(self, empty=False):
        """
        Some calculations that take place before object gets rendered
        """
        # get vector outline
        self.vectors_list = getLayerOutline(self.file_header)
        self.auto_center()
        # adjust spacing

        xc = int(self.file_header['xnodes'])
        yc = int(self.file_header['ynodes'])
        zc = int(self.file_header['znodes'])
        # change drawing function
        self.color_vectors, self.vectors_list, self.colorX = \
                    ColorPolicy.standard_procedure(self.vectors_list,
                                                   self.color_vectors,
                                                   self.iterations,
                                                   self.averaging,
                                                   xc, yc, zc,
                                                   self.layer,
                                                   self.vector_set,
                                                   self.decimate,
                                                   disableDot=self.disableDot,
                                                   hyperContrast=self.hyperContrast)
        if self.normalize:
            multi_iteration_normalize(self.color_vectors)
        
    def handleOptionalData(self):
        super().handleOptionalData()
        # must handle iterations since these are optional
        try:
            value = getattr(self, 'iterations')
            if value is None:
                setattr(self, 'iterations', 1)
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
        self.position = [0, 0 , -150]  # xyz initial
        # reset translational view
        width = self.geom[0]
        height = self.geom[1]
        self.lastPos = QPoint(int(width/2), int(height/2))

    def transformate(self):
        """
        applies rotation and transformation
        """
        gl.glRotatef(self.rotation[1], 1, 0, 0)  # rotate around x axis
        gl.glRotatef(self.rotation[0], 0, 1, 0)  # rotate around y axis
        gl.glRotatef(self.rotation[2], 0, 0, 1)  # rotate around z axis

    def initializeGL(self):
        """
        Initializes openGL context and scenery
        """
        gl.glClearColor(*self.background, 0)
        
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_POLYGON_SMOOTH)
        self.initial_transformation()

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
        gl.glTranslatef(*self.position)
        self.transformate()
        self.drawing_function()
        self.text_functionalities()
        # Pop Matrix off stack
        gl.glPopMatrix()
        self.update()

    @AbstractGLContextDecorators.systemDisable
    def text_functionalities(self):
        """
        handles text display across OpenGl contexts
        """
        self.frames +=1
        self.fps_counter()
        if self.display_frames:
            self.text_render(str(self.i))
        if self.TEXT is not None \
            and self.SELECTED_POS is not None:
            self.text_render(self.TEXT,
                             self.SELECTED_POS)

    def set_i(self, value, trigger=False, record=False):
        # saving the previous configuration for the sake 
        # of documentation. Idk where bug occurred, 
        # that was working fine previously
        if trigger:
            if value == 1:
                self.i = 0
            else:
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
        self.position[2] += 16 / 8

    def zoomOut(self):
        self.position[2] -= 16 / 8

    def wheelEvent(self, event):
        """
        Handles basic mouse scroll
        """
        degsx = event.angleDelta().x() / 8
        degsy = event.angleDelta().y() / 8
        if (abs(degsx) > abs(degsy)):
            self.position[0] += event.angleDelta().x() / 8 / 2
        else:
            self.position[2] += event.angleDelta().y() / 8 / 2
        self.update()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if self.RECORD_REGION_SELECTION:
            y = self.geom[1] - y
            self.SELECTED_POS = (x, y, 0)
            self.RECORD_REGION_SELECTION = False
            print(self.SELECTED_POS)

    def mouseMoveEvent(self, event):
        """
        Handles basic mouse press
        SHOULD BE MOUSE DRAG RATHER A MOUSE EVENT
        """
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        self.lastPos = event.pos()
        if event.buttons() & Qt.LeftButton:
            if self.registered_left_mouse:
                dx = event.x() - self.registered_left_mouse_pos.x()
                dy = event.y() - self.registered_left_mouse_pos.y()
                rotation_speed = 0.5
                if abs(dx) > abs(dy):
                    ang = self.normalize_angle(dx * rotation_speed)
                    self.rotation[0] += ang
                else:
                    ang = self.normalize_angle(dy * rotation_speed)
                    self.rotation[1] += ang
            self.registered_left_mouse = True
            self.registered_left_mouse_pos = event.pos()
        elif event.buttons() & Qt.RightButton:
            self.position[0] += dx * 0.4 
            self.position[1] -= dy * 0.4 
        self.update()
    
    def mouseReleaseEvent(self, event):
        if self.registered_left_mouse:
            self.registered_left_mouse = False

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

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

    def text_render(self, textString, position=(100, 100, 0)):
        """
        renders a textstring into an OpenGl scene
        """
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

    def popup_text_selector(self):
        self.selectionWindow = Select(self)
        self.selectionWindow.setEventHandler(self.set_text)

    def set_text(self, text):
        self.TEXT = text
        if self.TEXT is not None:
            self.RECORD_REGION_SELECTION = True

    def screenshot_manager(self):
        """
        saves the screenshot to the folder specified in screenshot_dir
        """
        # fetch dimensions for highest resolution
        _, _, width, height = gl.glGetIntegerv(gl.GL_VIEWPORT)
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
