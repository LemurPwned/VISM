import OpenGL.GL as gl
import OpenGL.GLU as glu
from Parser import Parser
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from PyQt5.QtGui import QColor
import numpy as np
import time

class GLWidget(QOpenGLWidget):
    def __init__(self, null_object=True, parent=None):
        super(GLWidget, self).__init__(parent)
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.initialRun = True
        self.lastPos = QPoint()

        self.DATA_FLAG = False
        self.initializeGL()

    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )

        return info

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.update()

    def initializeGL(self):
        self._vertexBuffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vertexBuffer)
        filename = './data/firstData/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000100.omf'
        vertices = np.array([    -1.0,-1.0,-1.0, #// triangle 1 : begin
                                -1.0,-1.0, 1.0,
                                -1.0, 1.0, 1.0, #// triangle 1 : end
                                1.0, 1.0,-1.0, # triangle 2 : begin
                                -1.0,-1.0,-1.0,
                                -1.0, 1.0,-1.0,# triangle 2 : end
                                1.0,-1.0, 1.0,
                                -1.0,-1.0,-1.0,
                                1.0,-1.0,-1.0,
                                1.0, 1.0,-1.0,
                                1.0,-1.0,-1.0,
                                -1.0,-1.0,-1.0,
                                -1.0,-1.0,-1.0,
                                -1.0, 1.0, 1.0,
                                -1.0, 1.0,-1.0,
                                1.0,-1.0, 1.0,
                                -1.0,-1.0, 1.0,
                                -1.0,-1.0,-1.0,
                                -1.0, 1.0, 1.0,
                                -1.0,-1.0, 1.0,
                                1.0,-1.0, 1.0,
                                1.0, 1.0, 1.0,
                                1.0,-1.0,-1.0,
                                1.0, 1.0,-1.0,
                                1.0,-1.0,-1.0,
                                1.0, 1.0, 1.0,
                                1.0,-1.0, 1.0,
                                1.0, 1.0, 1.0,
                                1.0, 1.0,-1.0,
                                -1.0, 1.0,-1.0,
                                1.0, 1.0, 1.0,
                                -1.0, 1.0,-1.0,
                                -1.0, 1.0, 1.0,
                                1.0, 1.0, 1.0,
                                -1.0, 1.0, 1.0,
                                1.0,-1.0, 1.0
                                    ], dtype='float32')

        vertices = vertices/2
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_STATIC_DRAW)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        # gl.glShadeModel(gl.GL_FLAT)

    def draw_cordinate_system(self, size=5):
        self.draw_vector([0, 0, 0, size, 0, 0], [1, 0, 0]) #x
        self.draw_vector([0, 0, 0, 0, size, 0], [0, 1, 0]) #y
        self.draw_vector([0, 0, 0, 0, 0, size], [0, 0, 1]) #z

    def paintGL(self):
        gl.glViewport(0,0, self.width(), self.height())
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vertexBuffer)
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, None)
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 12*3)
        # for i in range(108):
        #     gl.glDrawArrays(gl.GL_TRIANGLES, 3*i, 3*(i+1))

        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        # gl.glDrawArrays(gl.GL_TRIANGLES, 3, 6)
        # gl.glDrawArrays(gl.GL_TRIANGLES, 6, 9)
        # for i in range(6125):
        #     gl.glDrawArrays(gl.GL_TRIANGLES, 3*i, 3*(i+1))
        #     gl.glColor3f(0.0, 0.5, 0.5)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        # glu.gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)
        elif event.buttons() & Qt.MidButton:
            print("MOUSE DRAG")
            print(dx, dy)
            gl.glScalef(self.xRot*dx, self.yRot*dy, 1.0)
        self.lastPos = event.pos()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
