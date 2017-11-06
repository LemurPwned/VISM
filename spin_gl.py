
import OpenGL.GL as gl
import OpenGL.GLU as glu
from Parser import Parser
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from PyQt5.QtGui import QColor
import numpy as np
class GLWidget(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.initialRun = True
        self.spacer = 0.2
        self.lastPos = QPoint()

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
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def draw_vector(self, vec, color=[0, 0, 0], a=[1,1,0], b= [-1,-1,0]):
        # [1,1,0] x, y ,z - red
        # [-1,-1,0] x, y, z - blue
        gl.glLineWidth(3)
        #glColor3f(color[0], color[1], color[2])
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
        #self.gl = self.context().versionFunctions()
        #self.gl.initializeOpenGLFunctions()
        gl.glClearColor(1.0, 1.0, 1.0, 1.0);
        self.object = self.first_draw()
        # gl.glShadeModel(gl.GL_FLAT)
        #gl.glEnable(gl.GL_DEPTH_TEST)
        #gl.glEnable(gl.GL_CULL_FACE)
        print(self.getOpenglInfo())

    def draw_cordinate_system(self, size=5):
        self.draw_vector([0, 0, 0, size, 0, 0], [1, 0, 0]) #x
        self.draw_vector([0, 0, 0, 0, size, 0], [0, 1, 0]) #y
        self.draw_vector([0, 0, 0, 0, 0, size], [0, 0, 1]) #z'''

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        self.draw_cordinate_system(5)
        #self.draw_cube()
        self.draw_vector([5,5,5,10,10,10])
        gl.glTranslated(0.0, 0.0, -10.0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gl.glCallList(self.object)
        gl.glFlush()



    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
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
            print("SMTH")
            gl.glScalef(self.xRot, self.yRot, 1.0)
        self.lastPos = event.pos()

    def makeObject(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        #gl.glColor4f(1.0, 1.0, 0.0, 1.0)
        #for x,y,z in zip(range(1), range(1), range(1)):
        gl.glColor3f(0.0,1.0,0.0)
        for vec in vectors:
            gl.glTranslate(vec[0], vec[1], vec[2])
            gl.glBegin(gl.GL_QUADS)
            self.draw_cube()
            gl.glEnd()
        gl.glEndList()

        return genList

    def first_draw(self):
        filename = "./data/firstData/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000800.omf"
        self.vec = Parser.getLayerOutlineFromFile(filename)

        self.spin_struc = gl.glGenLists (1);
        gl.glNewList(self.spin_struc, gl.GL_COMPILE);
        self.spins();
        gl.glEndList();

        gl.glShadeModel(gl.GL_FLAT);
        gl.glClearColor(0.0, 0.0, 0.0, 0.0);

        return self.spin_struc

    def spins(self):
        gl.glBegin(gl.GL_QUADS)
        for vector in self.vec:
            self.draw_cube(vector)
        gl.glEnd()

    def draw_cube(self, vec, color=[1,0,1], a=[1,1,0], b= [-1,-1,0]):
        #glBegin(GL_QUADS)
        #TOP FACE
        gl.glColor3f(color[0], color[1],color[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        #BOTTOM FACE
        gl.glColor3f(color[0], color[1],color[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #FRONT FACE
        gl.glColor3f(color[0], color[1],color[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #BACK FACE
        gl.glColor3f(color[0], color[1],color[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0], vec[1], vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #RIGHT FACE
        gl.glColor3f(color[0], color[1],color[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        gl.glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        gl.glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #LEFT FACE
        gl.glColor3f(color[0], color[1],color[2])
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

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())
