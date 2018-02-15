from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider
from Windows.PerfOptionsTemplate import Ui_Dialog
class PerfOptions(QWidget, Ui_Dialog):
    def __init__(self):
        super(PerfOptions, self).__init__()
        self.setupUi(self)
        self.show()
        self.options = None

    def basicOptions(self):
        pass

    def optionsVerifier(self):
        optionsList = [self.comboBox.currentText(),
                        self.horizontalSlider.value()]
        return optionsList

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def accept(self):
        self.options = self.optionsVerifier()
        self.close()

    def reject(self):
        self.close()

    def getOptions(self):
        if self.options is not None:
            return self.options
