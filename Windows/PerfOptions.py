from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider
from Windows.PerfOptionsTemplate import Ui_Dialog
import re

class PerfOptions(QWidget, Ui_Dialog):
    def __init__(self, layer_size=None):
        super(PerfOptions, self).__init__()
        self.setWindowTitle("Perfomance Options")
        self.setupUi(self)
        self.loaded = True
        self.layer_size = layer_size['znodes']
        if self.layer_size == 1:
            self.checkBox.setEnabled(False)
            self.checkBox.setChecked(True)

        self.decimate = 1
        self.averaging = 1

        self.basicOptions()
        self.show()
        self.options = None

        self.color_disable = False

    def disableDecimate(self):
        self.horizontalSlider_4.setEnabled(False)
        # enable averaging
        self.horizontalSlider.setEnabled(True)

        self.decimate = 1
        self.averaging = self.horizontalSlider.value()
        self.label.setText("Averaging: {}".format(self.averaging))
        self.label_8.setText("Decimate: {}".format(self.decimate))

    def disableAveraging(self):
        self.horizontalSlider.setEnabled(False)
        # enable decimate
        self.horizontalSlider_4.setEnabled(True)

        self.averaging = 1
        self.decimate = self.horizontalSlider_4.value()
        self.label_8.setText("Decimate: {}".format(self.decimate))
        self.label.setText("Averaging: {}".format(self.averaging))

    def disableDot(self):
        self.lineEdit.setEnabled(self.color_disable)
        self.lineEdit_2.setEnabled(self.color_disable)
        self.lineEdit_3.setEnabled(self.color_disable)
        self.color_disable = not self.color_disable

    def basicOptions(self):
        # disable coloring
        self.checkBox_4.stateChanged.connect(self.disableDot)
        # these are averagnin and decimate
        self.checkBox_3.stateChanged.connect(self.disableDecimate)
        self.checkBox_2.stateChanged.connect(self.disableAveraging)

        # check decimate: decimate is checkbox 2 and slider 4
        self.checkBox_2.setChecked(True)

        self.horizontalSlider.valueChanged.connect(self.averagingChange)
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)
        self.horizontalSlider_3.valueChanged.connect(self.sizeChange)
        self.horizontalSlider_4.valueChanged.connect(self.decimateChange)

        self.horizontalSlider.setMaximum(5)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setValue(1)
        self.horizontalSlider.setSingleStep(1)

        self.horizontalSlider_3.setEnabled(True)
        self.horizontalSlider_3.setMaximum(5)
        self.horizontalSlider_3.setMinimum(1)
        self.horizontalSlider_3.setValue(1)
        self.horizontalSlider_3.setSingleStep(1)

        self.horizontalSlider_4.setEnabled(True)
        self.horizontalSlider_4.setMaximum(5)
        self.horizontalSlider_4.setMinimum(1)
        self.horizontalSlider_4.setValue(1)
        self.horizontalSlider_4.setSingleStep(1)

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
        self.label_3.setText("Layer: {}".format(val))

    def averagingChange(self):
        self.averaging = self.horizontalSlider.value()
        self.label.setText("Averaging: {}".format(self.averaging))

    def decimateChange(self):
        self.decimate = self.horizontalSlider_4.value()
        self.label_8.setText("Decimate: {}".format(self.decimate))

    def sizeChange(self):
        val = self.horizontalSlider_3.value()
        self.label_4.setText("Size: {}".format(val))

    def optionsVerifier(self):
        # order as follows: color scheme, averaging, layer
        if self.checkBox.isChecked():
                optionsList = [self.comboBox.currentText(),
                                self.averaging,
                                'all',
                                self.horizontalSlider_3.value(),
                                self.parseVectors(),
                                self.decimate,
                                self.color_disable]
        else:
            optionsList = [self.comboBox.currentText(),
                            self.averaging,
                            self.horizontalSlider_2.value(),
                            self.horizontalSlider_3.value(),
                            self.parseVectors(),
                            self.decimate,
                            self.color_disable]
        return optionsList

    def parseVectors(self):
        vector1 = self.lineEdit.text()
        vector2 = self.lineEdit_2.text()
        vector3 = self.lineEdit_3.text()
        result_group = []
        for v in [vector1, vector2, vector3]:
            p = self.isVectorEntryValid(v)
            if not p:
                raise ValueError("Invalid entry in vector specification")
            result_group.append(p)
        return result_group

    def isVectorEntryValid(self, entry):
        match_string = '^\[([0-1]),\s([0-1]),\s([0-1])\]'
        rg = re.compile(match_string)
        m = rg.search(entry)
        if m is not None:
            return [int(m.group(1)), int(m.group(2)), int(m.group(3))]
        else:
            return False

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def accept(self):
        try:
            self.options = self.optionsVerifier()
            self.eventHandler(self.options)
            self.close()
        except ValueError as ve:
            PopUpWrapper("Invalid vector format", str(ve), None,
                            QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, None, quit)
    def reject(self):
        self.close()

    def getOptions(self):
        if self.options is not None:
            return self.options
