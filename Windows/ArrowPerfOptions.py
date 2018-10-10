from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
    QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.ArrowPerfOptionsTemplate import Ui_Dialog
from Windows.GeneralPerf import GeneralPerf
from util_tools.PopUp import PopUpWrapper
import re
import numpy as np
import traceback


class ArrowPerfOptions(QWidget, Ui_Dialog, GeneralPerf):
    def __init__(self, layer_size=None, object_type='None', parent=None):
        super(ArrowPerfOptions, self).__init__()
        self.setWindowTitle("Arrow Perfomance Options")
        self.setupUi(self)
        self.loaded = True
        self.layer_size = layer_size['znodes']
        if self.layer_size == 1:
            self.checkBox.setEnabled(False)
            self.checkBox.setChecked(True)

        self.resolution = 16
        self.subsampling = 1
        self.height = 3
        self.general_initialization()
        self.basicOptions()
        self.show()

    def basicOptions(self):
        # defaults
        self.default_size = 2
        # no decimation but subsampling
        # no subsampling but resolution
        self.arrow_label = True
        self.label_9.setText("Height {}".format(self.height))
        self.label_8.setText("Resolution {}".format(self.resolution))
        self.label.setText("Subsampling {}".format(self.subsampling))

        # disable coloring
        self.pushButton_4.clicked.connect(self.reset)

        # subsampling
        self.horizontalSlider.setEnabled(True)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setMaximum(16)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setValue(self.subsampling)

        # size
        self.horizontalSlider_3.setMaximum(8)
        self.horizontalSlider_3.setMinimum(1)
        self.horizontalSlider_3.setValue(self.default_size)
        self.horizontalSlider_3.setSingleStep(1)

        # resolution
        self.horizontalSlider_4.setEnabled(True)
        self.horizontalSlider_4.setSingleStep(4)
        self.horizontalSlider_4.setMaximum(32)
        self.horizontalSlider_4.setMinimum(4)
        self.horizontalSlider_4.setValue(self.resolution)

        # height
        self.horizontalSlider_5.setEnabled(True)
        self.horizontalSlider_5.setSingleStep(1)
        self.horizontalSlider_5.setMaximum(6)
        self.horizontalSlider_5.setMinimum(1)
        self.horizontalSlider_5.setValue(self.height)

        # layer
        if not self.loaded:
            self.horizontalSlider_2.setEnabled(False)
        elif self.loaded:
            self.horizontalSlider_2.setEnabled(True)
            self.horizontalSlider_2.setMaximum(self.layer_size-1)
            self.horizontalSlider_2.setMinimum(0)
            self.horizontalSlider_2.setValue(3)
            self.horizontalSlider_2.setSingleStep(1)

        self.horizontalSlider.valueChanged.connect(self.subsamplingChange)
        self.horizontalSlider_2.valueChanged.connect(self.layerChange)
        self.horizontalSlider_3.valueChanged.connect(self.sizeChange)
        self.horizontalSlider_4.valueChanged.connect(self.resolutionChange)
        self.horizontalSlider_5.valueChanged.connect(self.heightChange)

    def heightChange(self):
        self.height = self.horizontalSlider_5.value()
        self.label_9.setText("Height {}".format(self.height))

    def resolutionChange(self):
        self.resolution = self.horizontalSlider_4.value()
        self.label_8.setText("Resolution {}".format(self.resolution))

    def optionsVerifier(self):
        # order as follows: color scheme, subsampling, layer
        # checkBox_5 is normalize
        if self.checkBox.isChecked():
            optionsList = [self.checkBox_5.isChecked(),
                           self.subsampling,
                           'all',
                           self.horizontalSlider_3.value(),
                           self.parseVectors(),
                           self.color_selection,
                           self.checkBox_6.isChecked(),
                           self.resolution,
                           self.height]
        else:
            optionsList = [self.checkBox_5.isChecked(),
                           self.subsampling,
                           self.horizontalSlider_2.value(),
                           self.horizontalSlider_3.value(),
                           self.parseVectors(),
                           self.color_selection,
                           self.checkBox_6.isChecked(),
                           self.resolution,
                           self.height]
        return optionsList
