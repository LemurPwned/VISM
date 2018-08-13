from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.PerfOptionsTemplate import Ui_Dialog
from Windows.SimplePerfOptions import SimplePerfOptions
from PopUp import PopUpWrapper
import re
import numpy as np


class PerfOptions(QWidget, Ui_Dialog):
    def __init__(self, layer_size=None, object_type='None', parent=None):
        super(PerfOptions, self).__init__()
        self.setWindowTitle("Perfomance Options")
        self.setupUi(self)
        self.loaded = True
        self.layer_size = layer_size['znodes']
        if self.layer_size == 1:
            self.checkBox.setEnabled(False)
            self.checkBox.setChecked(True)

        self.subsampling = 0
        self.initial_options(object_type)

        self.basicOptions()
        self.show()
        self.options = None
        self.color_disable = False

    def initial_options(self, object_type):
        self.default_size = 1
        self.horizontalSlider_3.setEnabled(True)
        if object_type == 'CubicGLContext':
            self.default_size = 5
            # only one size is allowed
            self.horizontalSlider_3.setEnabled(True)

    def disableDot(self):
        self.lineEdit.setText('[1, 0, 0]')
        self.lineEdit_2.setText('[0, 1, 0]')
        self.lineEdit_3.setText('[0, 0, 1]')
        self.color_disable = not self.color_disable

    def basicOptions(self):
        self.label.setText("Subsampling: {}".format(self.subsampling*2))

        # disable coloring
        self.pushButton_4.clicked.connect(self.disableDot)
        self.horizontalSlider.valueChanged.connect(self.subsamplingChange)
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)
        self.horizontalSlider_3.valueChanged.connect(self.sizeChange)

        # subsampling
        self.horizontalSlider.setMaximum(4)
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setValue(self.subsampling)
        self.horizontalSlider.setSingleStep(1)

        # scale
        self.horizontalSlider_3.setMaximum(5)
        self.horizontalSlider_3.setMinimum(1)
        self.horizontalSlider_3.setValue(self.default_size)
        self.horizontalSlider_3.setSingleStep(1)

        # layer
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

    def subsamplingChange(self):
        self.subsampling = self.horizontalSlider.value()*2
        self.label.setText("Subsampling: {}".format(self.subsampling))

    def sizeChange(self):
        val = self.horizontalSlider_3.value()
        self.label_4.setText("Size: {}".format(val))

    def optionsVerifier(self):
        # order as follows: color scheme, subsampling, layer
        # checkBox_5 is normalize
        if self.checkBox.isChecked():
            optionsList = [ self.checkBox_5.isChecked(),
                            self.subsampling,
                            'all',
                            self.horizontalSlider_3.value(),
                            self.parseVectors(),
                            self.color_disable,
                            self.checkBox_6.isChecked()]
        else:
            optionsList = [ self.checkBox_5.isChecked(),
                            self.subsampling,
                            self.horizontalSlider_2.value(),
                            self.horizontalSlider_3.value(),
                            self.parseVectors(),
                            self.color_disable,
                            self.checkBox_6.isChecked()]
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
        except ValueError as e:
            x = PopUpWrapper(
                title='Invalid format',
                msg='Vectors must be in format [x,y,z] {}'.format(e),
                more='',
                yesMes=None, parent=self)
            self.show()

    def reject(self):
        self.options = None
        self.eventHandler(None)
        self.deleteLater()

    def getOptions(self):
        if self.options is not None:
            return self.options

    def closeEvent(self, event):
        self.options = None
        self.eventHandler(None)
        self.close()