from AnimatedWidget import AnimatedWidget
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

class AbstractGLContext(QOpenGLWidget, AnimatedWidget):
    def __init__(self, parent=None):
        super(AbstractGLContext, self).__init__(parent)
        self._MINIMUM_PARAMS_ = ['i', 'iterations', 'v1',
                                    'color_list', 'omf_header']

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
