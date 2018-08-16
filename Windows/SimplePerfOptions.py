from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.SimplePerfOptionsTemplate import Ui_Dialog
from Windows.GeneralPerf import GeneralPerf
import re
import numpy as np
from PopUp import PopUpWrapper

class SimplePerfOptions(QWidget, Ui_Dialog, GeneralPerf):
    def __init__(self, layer_size=None, parent=None):
        super(SimplePerfOptions, self).__init__()
        self.setWindowTitle("Simple Perfomance Options")
        self.setupUi(self)
        self.loaded = True
        self.layer_size = layer_size['znodes']

        self.toDelete = False
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
            self.horizontalSlider_2.setValue(0)

    def parseVectors(self):
        """
        override since there is just a single vector
        """
        vector1 = self.lineEdit.text()
        p = self.isVectorEntryValid(vector1)
        if not p:
            raise ValueError("Invalid entry in vector specification")
        return p

    def optionsVerifier(self):
        # order as follows: color scheme, averaging, layer
        # checkBox_5 is normalize
        optionsList = [ self.checkBox_5.isChecked(),
                        0,
                        self.horizontalSlider_2.value(),
                        0,
                        self.parseVectors(),
                        0,
                        False]
        return optionsList
