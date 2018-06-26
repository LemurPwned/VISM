from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.SelectTemplate import Ui_Dialog
from PopUp import PopUpWrapper
from widget_counter import WidgetCounter
from buildVerifier import BuildVerifier

class Select(QWidget, Ui_Dialog):
    def __init__(self, parent=None):
        super(Select, self).__init__()
        self.eventHandler = None
        self.text = None
        if BuildVerifier.OS_GLOB_SYS == 'Darwin':
            """
            temporary disable for Linux
            """
            return
        self.setWindowTitle("Select text to display")
        self.setupUi(self)
        self.show()

    def accept(self):
        if WidgetCounter.OPENGL_WIDGET:
            self.text = self.lineEdit.text()
            # enable recording
            self.hide()
            self.eventHandler(self.text)
        else:
            x = PopUpWrapper(
                title='No OpenGL widget',
                msg='Please select OpenGL widget first',
                more='Not changed',
                yesMes=None)
            self.close()

    def reject(self):
        if self.eventHandler is not None:
            self.eventHandler(None)
        self.close()

    def setEventHandler(self, handler):
        self.eventHandler = handler
