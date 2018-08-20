import sys
import math

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from Widgets.openGL_widgets.CubicGLContext import CubicGLContext
from Widgets.openGL_widgets.ArrowGLContext import ArrowGLContext
import OpenGL.GL as gl
import OpenGL.GLU as glu
import os 
from processing.multiprocessing_parse import MultiprocessingParse

class Window(QWidget):

    def __init__(self):
        super(Window, self).__init__()
        
        # directory = r"D:\Dokumenty\VISM\examples\730uA"
        directory = r"D:\Dokumenty\VISM\examples\0200nm"
        files = os.listdir(directory)
        i = 0
        filename = files[i]
        while(not (filename.endswith(".omf") or filename.endswith(".ovf"))):
            i += 1
            filename = files[i]
        # rawVectorData, header, _, stages, _ = \
        #                     MultiprocessingParse.readFolder(directory)
        rawVectorData, header = MultiprocessingParse.readFile(os.path.join(directory, filename))
        """
        new cross color
        user vector 1st
        positive vector 2nd
        negative vector 3rd
        """
        self.options = [True, 5, 'all', 2, 
        [[1.0, 0, 0], [1.0, 0, 0], [0, 0, 1.0]], 'Standard', False, 12]
        data_dict = {
                        "color_vectors" : rawVectorData,
                        "file_header": header,
                        "iterations": 1,
                        "averaging": 2,
                        "options": self.options,
                        "current_state": 0,
                        "geom": (800, 400),
        }
        self.glWidget = ArrowGLContext(data_dict, self)
        # self.glWidget = CubicGLContext(data_dict, self)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle("Hello GL")

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())

