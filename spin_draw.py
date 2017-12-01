import sys

from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QWidget)
from openGLContext import OpenGLContext


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = OpenGLContext({})

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)

        self.setWindowTitle("Early Spin Struct")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
