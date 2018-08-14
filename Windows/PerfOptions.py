from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.PerfOptionsTemplate import Ui_Dialog
from Windows.SimplePerfOptions import SimplePerfOptions
from PopUp import PopUpWrapper
import re
import numpy as np
from Windows.GeneralPerf import GeneralPerf


class PerfOptions(QWidget, Ui_Dialog, GeneralPerf):
    def __init__(self, layer_size=None, object_type='None', parent=None):
        super(PerfOptions, self).__init__()
        self.setWindowTitle("Perfomance Options")
        self.setupUi(self)
        self.loaded = True
        self.layer_size = layer_size['znodes'] 
        if self.layer_size == 1:
            self.checkBox.setEnabled(False)
            self.checkBox.setChecked(True)

        self.general_initialization()
        self.initial_options(object_type)

        self.basicOptions()
        self.show()


    def initial_options(self, object_type):
        self.default_size = 1
        self.horizontalSlider_3.setEnabled(True)
        if object_type == 'CubicGLContext':
            self.default_size = 5
            # only one size is allowed
            self.horizontalSlider_3.setEnabled(True)

    def basicOptions(self):
        self.label.setText("Subsampling: {}".format(self.subsampling))

        # disable coloring
        self.pushButton_4.clicked.connect(self.reset)
        self.horizontalSlider.valueChanged.connect(self.subsamplingChange)
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)
        self.horizontalSlider_3.valueChanged.connect(self.sizeChange)

        # subsampling
        self.horizontalSlider.setMaximum(8)
        self.horizontalSlider.setMinimum(1)
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
            self.horizontalSlider_2.setMaximum(self.layer_size-1)
            self.horizontalSlider_2.setMinimum(0)
            self.horizontalSlider_2.setValue(3)
            self.horizontalSlider_2.setSingleStep(1)

    def optionsVerifier(self):
        # order as follows: color scheme, subsampling, layer
        # checkBox_5 is normalize
        if self.checkBox.isChecked():
            optionsList = [ self.checkBox_5.isChecked(),
                            self.subsampling,
                            'all',
                            self.horizontalSlider_3.value(),
                            self.parseVectors(),
                            self.color_selection,
                            self.checkBox_6.isChecked()]
        else:
            optionsList = [ self.checkBox_5.isChecked(),
                            self.subsampling,
                            self.horizontalSlider_2.value(),
                            self.horizontalSlider_3.value(),
                            self.parseVectors(),
                            self.color_selection,
                            self.checkBox_6.isChecked()]
        return optionsList

