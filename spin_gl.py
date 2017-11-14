from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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
        self.initial_transformation()
        self.spacer = 0.2
        self.DATA_FLAG = False
        self.initializeGL()
        s=0.5
        self.yaw = 0
        self.pitch = 0
        self.shader = None
        directory = './data/firstData'
        self.color_list, self.bd, self.odt, self.iterations = Parser.readFolder(directory)
        self.vectors_list = Parser.getLayerOutline(self.bd)
        self.i = 0
        self.av = 1

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
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)

    def draw_cordinate_system(self, size=5):
        self.draw_vector([0, 0, 0, size, 0, 0], [1, 0, 0]) #x
        self.draw_vector([0, 0, 0, 0, size, 0], [0, 1, 0]) #y
        self.draw_vector([0, 0, 0, 0, 0, size], [0, 0, 1]) #z

    def paintGL(self):
        glPushMatrix()
        for vector, color in zip(self.vectors_list[0::self.av], \
                                                self.colors[0::self.av]):
            self.draw_cube(vector, color=color)
        glPopMatrix()
        print(self.i)
        self.resizeGL(480, 800)

    def transformate(self):  # applies rotation and transformation
        glRotatef(self.rotation[0], 0, 1, 0)  # weird
        glRotatef(self.rotation[1], 1, 0, 0)  # weird
        glRotatef(self.rotation[2], 0, 0, 1)
        glTranslatef(self.position[0], self.position[1], self.position[2])

    def initial_transformation(self):
        self.rotation = [0, 0, 0]  # xyz degrees in xyz axis
        self.position = [-10, -10, -40]  # xyz initial
        # self.pointing = [0,0,0] #where camera points

    def draw_cubeX(self):
        global buffers
        if self.shader == None:
            self.shader = Shader()
            self.shader.initShader('''
            void main()
            {
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                gl_FrontColor = gl_Color;
            }
                    ''',
                    '''
            void main()
            {
                gl_FragColor = gl_Color;
            }
                    ''')
        buffers=self.create_vbo()

        self.shader.begin()
        self.draw_vbo()
        self.shader.end()

    def create_vbo(self):
        buffers = glGenBuffers(3)
        glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
        glBufferData(GL_ARRAY_BUFFER,
                len(self.vertices)*4,  # byte size
                (ctypes.c_float*len(self.vertices))(*self.vertices),
                GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
        glBufferData(GL_ARRAY_BUFFER,
                len(self.colors)*4, # byte size
                (ctypes.c_float*len(self.colors))(*self.colors),
                GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                len(self.indices)*4, # byte size
                (ctypes.c_uint*len(self.indices))(*self.indices),
                GL_STATIC_DRAW)
        return buffers

    def draw_vbo(self):
        glEnableClientState(GL_VERTEX_ARRAY);
        glEnableClientState(GL_COLOR_ARRAY);
        glBindBuffer(GL_ARRAY_BUFFER, buffers[0]);
        glVertexPointer(3, GL_FLOAT, 0, None);
        glBindBuffer(GL_ARRAY_BUFFER, buffers[1]);
        glColorPointer(3, GL_FLOAT, 0, None);
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2]);
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None);
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY);

    def resizeGL(self, width, height):
        # viewport
        glViewport(0, 0, width, height)
        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspectRatio = width / height
        gluPerspective(85, aspectRatio, 1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, 0)
        self.colors = self.color_list[self.i]
        self.i += 1
        print(self.i)
        self.paintGL()

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
            glScalef(self.xRot*dx, self.yRot*dy, 1.0)
        self.lastPos = event.pos()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def draw_cube(self, vec, color=[1,0,1], a=[1,1,0], b= [-1,-1,0]):
        glBegin(GL_QUADS)
        #TOP FACE
        #glColor3f(color[0], color[1],color[2])
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        #BOTTOM FACE
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        #glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #FRONT FACE
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        #glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        #BACK FACE
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        #glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #RIGHT FACE
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        #glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0]+self.spacer, vec[1]+self.spacer, vec[2])
        glVertex3f(vec[0]+self.spacer, vec[1], vec[2])
        #LEFT FACE
        glColor3f(np.dot(a, color), np.dot(b, color), 0)
        #glColor3f(color[0], color[1],color[2])
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2]+self.spacer)
        glVertex3f(vec[0], vec[1], vec[2])
        glVertex3f(vec[0], vec[1]+self.spacer, vec[2])
        glEnd()

def printOpenGLError():
    err = glGetError()
    if (err != GL_NO_ERROR):
        print('GLERROR: ', gluErrorString(err))
        #sys.exit()

class Shader(object):

    def initShader(self, vertex_shader_source, fragment_shader_source):
        # create program
        self.program=glCreateProgram()
        print('create program')
        printOpenGLError()

        # vertex shader
        print('compile vertex shader...')
        self.vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vs, [vertex_shader_source])
        glCompileShader(self.vs)
        glAttachShader(self.program, self.vs)
        printOpenGLError()

        # fragment shader
        print('compile fragment shader...')
        self.fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fs, [fragment_shader_source])
        glCompileShader(self.fs)
        glAttachShader(self.program, self.fs)
        printOpenGLError()

        print('link...')
        glLinkProgram(self.program)
        printOpenGLError()

    def begin(self):
        if glUseProgram(self.program):
            printOpenGLError()

    def end(self):
        glUseProgram(0)
