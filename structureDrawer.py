from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from Parser import Parser

from PyQt5.QtCore import QTimer, QPoint, pyqtSignal, Qt

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
class DrawData(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super(DrawData, self).__init__(parent)

        self.lastPos = QPoint()
        print(self.lastPos.x(), self.lastPos.y())
        self.rotation = [0,0,0]
        self.position = [0,-1,-10]
        self.initialRun = True
        self.spacer = 0.2


    def draw_cube(self, vec, color=[1,0,1], a=[1,1,0], b= [-1,-1,0]):
        #glBegin(GL_QUADS)
        #TOP FACE
        glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        #BOTTOM FACE
        glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #FRONT FACE
        glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #BACK FACE
        glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #RIGHT FACE
        glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #LEFT FACE
        glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        #glEnd()

    def draw_vector(self, vec, color=[0, 0, 0], a=[1,1,0], b= [-1,-1,0]):
        # [1,1,0] x, y ,z - red
        # [-1,-1,0] x, y, z - blue
        glLineWidth(3)
        #glColor3f(color[0], color[1], color[2])
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        glBegin(GL_LINES)
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[3]+color[0], vec[4]+color[1], vec[5]+color[2])
        glEnd()
        glPointSize(5)
        glBegin(GL_POINTS)
        glVertex3f(vec[3]+color[0], vec[4]+color[1], vec[5]+color[2])

        glEnd()

    def draw_cordinate_system(self, size=5):
        self.draw_vector([0, 0, 0, size, 0, 0], [1, 0, 0]) #x
        self.draw_vector([0, 0, 0, 0, size, 0], [0, 1, 0]) #y
        self.draw_vector([0, 0, 0, 0, 0, size], [0, 0, 1]) #z'''

    def cameraLeft(self):
        self.rotation[0] += 5

    def cameraRight(self):
        self.rotation[0] -= 5

    def initialSettings(self):
        self.position = [0, -1, -10]

    def first_draw(self):
        filename = "./data/firstData/voltage-spin-diode-Oxs_TimeDriver-Magnetization-00-0000800.omf"
        self.vec = Parser.getLayerOutlineFromFile(filename)

        self.spin_struc = glGenLists (1);
        glNewList(self.spin_struc, GL_COMPILE);
        self.spins();
        glEndList();

        glShadeModel(GL_FLAT);
        glClearColor(0.0, 0.0, 0.0, 0.0);

    def spins(self):
        glBegin(GL_QUADS)
        for vector in self.vec:
            self.draw_cube(vector)
        glEnd()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        print("EVENT POST ", event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        print("CHANGE IN MOV", dx, dy)

        self.lastPos = event.pos()

    def paintGL(self):
        '''testing purposes'''
        glClear(GL_COLOR_BUFFER_BIT)
        #print(glGetString(GL_VERSION))
        self.draw_cordinate_system(5)
        #self.draw_cube()
        self.draw_vector([5,5,5,10,10,10])

        #'self.draw_cube([1,1,1, 1,1,1], color=[1, 0, 1])
        if self.initialRun:
            self.initialSettings()
            gluPerspective(90, 651/551, 0.1, 50.0)
            self.first_draw()
            self.initialRun = False
        glColor3f (1.0, 1.0, 1.0)
        glCallList(self.spin_struc)
        glFlush()

        glTranslate(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[0], 0, 1, 0)  # weird
        glRotatef(self.rotation[1], 1, 0, 0)  # weird
        glRotatef(self.rotation[2], 0, 0, 1)
        self.position = [0,0,0]
        self.rotation = [0,0,0]
        #self.cameraLeft()

        #glTranslatef(0, -1, -10)
