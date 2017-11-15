import OpenGL.GL as gl
import OpenGL.GLU as glu
from Parser import Parser
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from PyQt5.Qt import QWheelEvent, Qt
import numpy as np
import time

class GLWidget(QOpenGLWidget):
    def __init__(self, ddict, null_object=True, parent=None):
        super(GLWidget, self).__init__(parent)
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.null_object = null_object
        self.initialRun = True
        self.spacer = 0.2
        self.lastPos = QPoint()
        self.DATA_FLAG = False
        self.steps = 1
        self.shareData(**ddict)
        self.initializeGL()

    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main plot iterator
        """
        #TODO: define minimum_list in arguments and force SPECIFIC keys
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.vectors = Parser.getLayerOutline(self.omf_header)

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

    def draw_vector(self, vec, color=[0, 0, 0], a=[1,1,0], b= [-1,-1,0]):
        gl.glLineWidth(3)
        gl.glColor3f(np.dot(a, color), np.dot(b, color), 0)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[3]+color[0], vec[4]+color[1], vec[5]+color[2])
        gl.glEnd()
        gl.glPointSize(5)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex3f(vec[3]+color[0], vec[4]+color[1], vec[5]+color[2])
        gl.glEnd()

    def initializeGL(self):
        gl.glClearColor(1.0, 1.0, 1.0, 1.0);
        #self.object = self.first_draw()
        self.object = self.null_object_painter()
        self.current_list = 1
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        print(self.getOpenglInfo())

    def draw_cordinate_system(self, size=5):
        self.draw_vector([0, 0, 0, size, 0, 0], [1, 0, 0]) #x
        self.draw_vector([0, 0, 0, 0, size, 0], [0, 1, 0]) #y
        self.draw_vector([0, 0, 0, 0, 0, size], [0, 0, 1]) #z

    def increaseIterator(self):
        self.i += 1

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -10.0)
        glu.gluPerspective(45.0*self.steps, \
                    float(self.width)/float(self.height), 0.1, 100.0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        if self.DATA_FLAG:
            self.spins()
        else:
            gl.glCallList(self.current_list)

    def resizeGL(self, width, height):
        side = min(width, height)
        self.width = width
        self.height = height
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        print("CHANGING")

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
        self.lastPos = event.pos()

    def wheelEvent(self, event):
        print("SCROLl")
        degs = event.angleDelta().y()/8
        self.steps += degs/15
        self.update()

    def null_object_painter(self):
        self.spin_struc = gl.glGenLists(1);
        gl.glNewList(self.spin_struc, gl.GL_COMPILE);
        gl.glBegin(gl.GL_QUADS)
        gl.glColor3f(1.0, 0.2, 0.1)
        self.draw_cube([0,0,0])
        gl.glEnd()
        gl.glEndList();

        gl.glShadeModel(gl.GL_FLAT);
        gl.glClearColor(0.0, 0.0, 0.0, 0.0);

    def first_draw(self):
        print("CALLED DRAW")
        self.spin_struc = gl.glGenLists(2);
        gl.glNewList(self.spin_struc, gl.GL_COMPILE);
        self.spins();
        gl.glEndList();

        gl.glShadeModel(gl.GL_FLAT);
        gl.glClearColor(0.0, 0.0, 0.0, 0.0);

        return self.spin_struc

    def spins(self):
        print("redrawn")
        gl.glBegin(gl.GL_QUADS)
        for vector, color in zip(self.vectors, self.colors[self.i]):
            gl.glColor3f(color[0], color[1], color[2])
            self.draw_cube(vector)
        gl.glEnd()

    def draw_cube(self, vec):
        #TOP FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        #BOTTOM FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #FRONT FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #BACK FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #RIGHT FACE
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #LEFT FACE
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
