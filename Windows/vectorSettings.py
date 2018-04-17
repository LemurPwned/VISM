from PopUp import PopUpWrapper
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider
from Windows.vectorSettingsTemplate import Ui_Dialog
import re

class vectorSettings(QWidget, Ui_Dialog):
    def __init__(self):
        super(vectorSettings, self).__init__()
        self.setWindowTitle("Vector Selection")
        self.setupUi(self)
        self.show()

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

    def accept(self):
        try:
            self.options = self.parseVectors()
            print(self.options)
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
