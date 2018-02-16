from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider
from Windows.PerfOptionsTemplate import Ui_Dialog


class PerfOptions(QWidget, Ui_Dialog):
    def __init__(self, loaded, layer_size=None):
        super(PerfOptions, self).__init__()
        self.setupUi(self)
        self.loaded = loaded
        self.layer_size = layer_size
        self.basicOptions()
        self.show()
        self.options = None

    def basicOptions(self):
        self.horizontalSlider.setEnabled(True)
        self.horizontalSlider.setEnabled(True)
        self.horizontalSlider.setMaximum(5)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setValue(3)
        self.horizontalSlider.setSingleStep(1)

        if not self.loaded:
            self.horizontalSlider_2.setEnabled(False)
        elif self.loaded:
            self.horizontalSlider_2.setEnabled(True)
            self.horizontalSlider_2.setMaximum(self.layer_size)
            self.horizontalSlider_2.setMinimum(0)
            self.horizontalSlider_2.setValue(3)
            self.horizontalSlider_2.setSingleStep(1)

    def optionsVerifier(self):
        # order as follows: color scheme, averaging, layer
        if self.checkBox.isChecked():
                optionsList = [self.comboBox.currentText(),
                                self.horizontalSlider.value(),
                                'all']
        else:
            optionsList = [self.comboBox.currentText(),
                            self.horizontalSlider.value(),
                            self.horizontalSlider_2.value()]
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
