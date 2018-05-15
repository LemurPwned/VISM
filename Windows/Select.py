from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.SelectTemplate import Ui_Dialog
from PopUp import PopUpWrapper
from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext

class Select(QWidget, Ui_Dialog):
    def __init__(self):
        super(Select, self).__init__()
        self.setWindowTitle("Select text to display")
        self.setupUi(self)
        self.show()
        self.eventHandler = None
    def accept(self):
        if AbstractGLContext.ANY_GL_WIDGET_IN_VIEW:
            AbstractGLContext.TEXT = self.lineEdit.text()
            # enable recording
            AbstractGLContext.RECORD_REGION_SELECTION = True
            self.hide()
        else:
            x = PopUpWrapper(
                title='No OpenGL widget',
                msg='Please select OpenGL widget first',
                more='Not changed',
                yesMes=None)
            self.close()

    def reject(self):
        self.close()

    def setEventHandler(self, handler):
        self.eventHandler = handler
