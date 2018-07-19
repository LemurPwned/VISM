from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.SelectTemplate import Ui_Dialog
from PopUp import PopUpWrapper
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
        self.text = self.lineEdit.text()
        # enable recording
        self.eventHandler(self.text)
        self.close()

    def reject(self):
        if self.eventHandler is not None:
            self.eventHandler(None)
        self.close()

    def setEventHandler(self, handler):
        self.eventHandler = handler
