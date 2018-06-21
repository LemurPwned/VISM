from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.PerfOptionsTemplate import Ui_Dialog
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

        self.decimate = 1
        self.averaging = 1
        self.initial_options(object_type)

        self.basicOptions()
        self.show()
        self.options = None
        self.color_disable = False

    def initial_options(self, object_type):
        self.default_size = 1
        self.default_averaging = 1
        self.horizontalSlider_3.setEnabled(True)
        if object_type == 'ArrowGLContext':
            # defaults
            self.default_averaging = 4
            self.decimate = 1
            self.default_size = 2
        elif object_type == 'CubicGLContext':
            self.default_size = 5
            # only one size is allowed
            self.horizontalSlider_3.setEnabled(False)
        
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
        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(True)

        self.horizontalSlider.valueChanged.connect(self.averagingChange)
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)
        self.horizontalSlider_3.valueChanged.connect(self.sizeChange)
        self.horizontalSlider_4.valueChanged.connect(self.decimateChange)

        # averaging
        self.horizontalSlider.setMaximum(5)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setValue(self.default_averaging)
        self.horizontalSlider.setSingleStep(1)

        # scale
        self.horizontalSlider_3.setMaximum(5)
        self.horizontalSlider_3.setMinimum(1)
        self.horizontalSlider_3.setValue(self.default_size)
        self.horizontalSlider_3.setSingleStep(1)

        # decimate
        self.horizontalSlider_4.setEnabled(True)
        self.horizontalSlider_4.setMaximum(5)
        self.horizontalSlider_4.setMinimum(1)
        self.horizontalSlider_4.setValue(1)
        self.horizontalSlider_4.setSingleStep(1)

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
        # checkBox_5 is normalize
        if self.checkBox.isChecked():
                optionsList = [ self.checkBox_5.isChecked(),
                                self.averaging,
                                'all',
                                self.horizontalSlider_3.value(),
                                self.parseVectors(),
                                self.decimate,
                                self.color_disable,
                                self.checkBox_6.isChecked()]
        else:
            optionsList = [ self.checkBox_5.isChecked(),
                            self.averaging,
                            self.horizontalSlider_2.value(),
                            self.horizontalSlider_3.value(),
                            self.parseVectors(),
                            self.decimate,
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
        self.eventHandler(None)
        self.close()

    def getOptions(self):
        if self.options is not None:
            return self.options
