from AnimatedWidget import AnimatedWidget
from PyQt5.QtWidgets import QOpenGLWidget

import OpenGL.GL as gl
import OpenGL.GLU as glu

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint

import math as mt
from PIL import Image
import os


class AbstractGLContext(QOpenGLWidget, AnimatedWidget):
    def __init__(self, parent=None):
        super(AbstractGLContext, self).__init__(parent)
        self._MINIMUM_PARAMS_ = ['i', 'iterations', 'color_list',
                                'omf_header']

        self.lastPos = QPoint()
        self.setFocusPolicy(Qt.StrongFocus)  # needed if keyboard to be active

        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [0, 0, -50]  # xyz initial
        self.drawing_function = None
        self.function_select = 'fast'
        self.background = [0.5, 0.5, 0.5]
        self.record = False

    def shareData(self, **kwargs):
        super().shareData(**kwargs)
        super().handleOptionalData()
        self.receivedOptions()

    def handleOptionalData(self):
        # must handle iterations since these are optional
        try:
            getattr(self, 'iterations')
        except NameError:
            self.iterations = 1

    def auto_center(self):
        x_fix = (self.omf_header['xnodes'] * self.omf_header['xbase'] * 1e9) / 2
        y_fix = (self.omf_header['ynodes'] * self.omf_header['ybase'] * 1e9) / 2
        z_fix = (self.omf_header['znodes'] * self.omf_header['zbase'] * 1e9) / 2
        for vec in self.vectors_list:
            vec[0] -= x_fix
            vec[1] -= y_fix
            vec[2] -= z_fix

    def screenshot_manager(self):
        """
        saves the screenshot to the folder specified in screenshot_dir
        """
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
