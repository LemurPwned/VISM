
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)


import sys
from state_machine.state_main import StateMachine
from Windows.StateMenu import StateMenuController


class Window(QWidget):

    def __init__(self):
        super(Window, self).__init__()

        directory = 'examples/0200nm'
        # directory = 'test_folder'
        self.glWidget = StateMachine(directory)
        self.subwindow = StateMenuController(state_object=self.glWidget)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle("State Machine GL")
        self.subwindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())
