from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider
from Windows.PerfOptionsTemplate import Ui_Dialog


class PerfOptions(QWidget, Ui_Dialog):
    def __init__(self, loaded, layer_size=None):
        super(PerfOptions, self).__init__()
        self.setWindowTitle("Perfomance Options")
        self.setupUi(self)
        self.loaded = loaded
        self.layer_size = layer_size
        self.basicOptions()
        self.show()
        self.options = None

    def basicOptions(self):
        self.horizontalSlider.valueChanged.connect(self.averagingChange)
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)
        self.horizontalSlider_3.valueChanged.connect(self.sizeChange)

        self.horizontalSlider.setEnabled(True)
        self.horizontalSlider.setMaximum(5)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setValue(4)
        self.horizontalSlider.setSingleStep(1)

        self.horizontalSlider_3.setEnabled(True)
        self.horizontalSlider_3.setMaximum(5)
        self.horizontalSlider_3.setMinimum(1)
        self.horizontalSlider_3.setValue(1)
        self.horizontalSlider_3.setSingleStep(1)

        if not self.loaded:
            self.horizontalSlider_2.setEnabled(False)
        elif self.loaded:
            self.horizontalSlider_2.setEnabled(True)
            self.horizontalSlider_2.setMaximum(self.layer_size)
            self.horizontalSlider_2.setMinimum(0)
            self.horizontalSlider_2.setValue(3)
            self.horizontalSlider_2.setSingleStep(1)

    def layerChange(self):
        val = self.horizontalSlider_2.value()
        self.label_3.setText("LAYER: {}".format(val))

    def averagingChange(self):
        val = self.horizontalSlider.value()
        self.label.setText("Averaging: {}".format(val))

    def sizeChange(self):
        val = self.horizontalSlider_3.value()
        self.label_4.setText("Size: {}".format(val))

    def optionsVerifier(self):
        # order as follows: color scheme, averaging, layer
        if self.checkBox.isChecked():
                optionsList = [self.comboBox.currentText(),
                                self.horizontalSlider.value(),
                                'all',
                                self.horizontalSlider_3.value()]
        else:
            optionsList = [self.comboBox.currentText(),
                            self.horizontalSlider.value(),
                            self.horizontalSlider_2.value(),
                            self.horizontalSlider_3.value()]
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
