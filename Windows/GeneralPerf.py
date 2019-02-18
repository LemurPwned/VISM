import re
import numpy as np
from util_tools.PopUp import PopUpWrapper


def validate_entry(entry):
    match_string = '^\[(-?[0-9]+\.?[0-9]*),\s?(-?[0-9]+\.?[0-9]*),\s?(-?[0-9]+\.?[0-9]*)]'
    rg = re.compile(match_string)
    m = rg.search(entry)
    if m is not None:
        x = float(m.group(1))
        y = float(m.group(2))
        z = float(m.group(3))
        norm = np.sqrt(x**2 + y**2 + z**2)
        if norm == 0.0:
            return False
        return [x/norm, y/norm, z/norm]
    else:
        return False


def validate_entry_no_norm(entry):
    match_string = '^\[(-?[0-9]+\.?[0-9]*),\s?(-?[0-9]+\.?[0-9]*),\s?(-?[0-9]+\.?[0-9]*)]'
    rg = re.compile(match_string)
    m = rg.search(entry)
    if m is not None:
        x = float(m.group(1))
        y = float(m.group(2))
        z = float(m.group(3))
        return [x, y, z]
    else:
        return False


class GeneralPerf:
    def general_initialization(self):
        self.toDelete = False
        self.subsampling = 1
        self.options = None
        self.color_selection = 'Standard'
        self.comboBox.activated[str].connect(self.changeColorPolicy)
        self.changeColorPolicy(self.color_selection)

    def layerChange(self):
        val = self.horizontalSlider_2.value()
        self.label_3.setText("Layer: {}".format(val))

    def subsamplingChange(self):
        self.subsampling = self.horizontalSlider.value()
        self.label.setText("Subsampling: {}".format(self.subsampling))

    def sizeChange(self):
        val = self.horizontalSlider_3.value()
        self.label_4.setText("Size: {}".format(val))

    def parseVectors(self):
        vector1 = self.lineEdit.text()
        vector2 = self.lineEdit_2.text()
        vector3 = self.lineEdit_3.text()
        result_group = []
        for v in [vector1, vector2, vector3]:
            p = self.isVectorEntryValid(v)
            if not p:
                raise IOError("Invalid entry in vector specification")
            result_group.append(p)
        return result_group

    def isVectorEntryValid(self, entry):
        return validate_entry(entry)

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def accept(self):
        self.hide()
        try:
            self.options = self.optionsVerifier()
            if self.options is not None:
                self.eventHandler(self.options)
            self.toDelete = True
            self.deleteLater()
        except IOError as e:
            x = PopUpWrapper(
                title='Invalid format',
                msg='Vectors must be in format [x,y,z] {}'.format(e),
                more='',
                yesMes=None, parent=self)
            self.show()

    def reject(self):
        self.options = None
        self.eventHandler(None)
        self.toDelete = True
        self.deleteLater()

    def getOptions(self):
        if self.options is not None:
            return self.options

    def reset(self):
        if self.color_selection == 'RGB policy':
            self.lineEdit.setText('[1, 0, 0]')
            self.lineEdit_2.setText('[0, 1, 0]')
            self.lineEdit_3.setText('[0, 0, 1]')
        elif self.color_selection == 'Standard':
            self.lineEdit.setText('[1, 0, 0]')
            self.lineEdit_2.setText('[1, 0, 0]')
            self.lineEdit_3.setText('[0, 0, 1]')

    def changeColorPolicy(self, text):
        if text == 'Standard':
            self.color_selection = 'Standard'
            self.label_5.setText('D')
            self.label_6.setText('C+')
            self.label_7.setText('C-')
        else:
            self.color_selection = 'RGB policy'
            self.label_5.setText('R')
            self.label_6.setText('G')
            self.label_7.setText('B')
        self.reset()

    def closeEvent(self, event):
        if self.toDelete:
            self.toDelete = False
            event.accept()
        else:
            self.eventHandler(None)
            event.accept()
