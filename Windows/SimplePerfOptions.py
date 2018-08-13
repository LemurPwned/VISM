from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.SimplePerfOptionsTemplate import Ui_Dialog
import re
import numpy as np
from PopUp import PopUpWrapper

class SimplePerfOptions(QWidget, Ui_Dialog):
    def __init__(self, layer_size=None, parent=None):
        super(SimplePerfOptions, self).__init__()
        self.setWindowTitle("Simple Perfomance Options")
        self.setupUi(self)
        self.loaded = True
        self.layer_size = layer_size['znodes']

        self.basicOptions()
        self.show()
        self.options = None

    def basicOptions(self):
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)

        if not self.loaded:
            self.horizontalSlider_2.setEnabled(False)
        elif self.loaded:
            self.horizontalSlider_2.setEnabled(True)
            self.horizontalSlider_2.setMaximum(self.layer_size-1)
            self.horizontalSlider_2.setMinimum(0)
            self.horizontalSlider_2.setValue(3)
            self.horizontalSlider_2.setSingleStep(1)

        # only a single layer is available
        if self.layer_size == 1:
            self.horizontalSlider_2.setEnabled(False)
            self.picked_layer = 0

    def layerChange(self):
        val = self.horizontalSlider_2.value()
        self.picked_layer = val
        self.label_3.setText("Layer: {}".format(val))

    def optionsVerifier(self):
        # order as follows: color scheme, averaging, layer
        # checkBox_5 is normalize
        optionsList = [ self.checkBox_5.isChecked(),
                        0,
                        self.picked_layer,
                        0,
                        self.parseVectors(),
                        0,
                        False]
        return optionsList

    def parseVectors(self):
        vector1 = self.lineEdit.text()
        p = self.isVectorEntryValid(vector1)
        if not p:
            raise ValueError("Invalid entry in vector specification")
        return p

    def isVectorEntryValid(self, entry):
        match_string = '^\[([0-1]),\s?([0-1]),\s?([0-1])\]'
        rg = re.compile(match_string)
        m = rg.search(entry)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            z = int(m.group(3))
            norm = np.sqrt(x**2 + y**2 + z**2)  
            return [x/norm, y/norm, z/norm]
        else:
            return False

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def accept(self):
        self.hide()
        try:
            self.options = self.optionsVerifier()
            if self.options is not None:
                self.eventHandler(self.options)
            self.close()
        except ValueError as ve:
            x = PopUpWrapper(
                title='Invalid format',
                msg='Vectors must be in format [x,y,z] {}'.format(ve),
                more='',
                yesMes=None, parent=self)
            self.show()
        
    def reject(self):
        self.eventHandler(None)
        self.deleteLater()

    def getOptions(self):
        if self.options is not None:
            return self.options

    def closeEvent(self, event):
        self.options = None
        self.eventHandler(None)
        self.close()