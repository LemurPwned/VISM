from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
    QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from Windows.Templates.BackgroundTemplate import Ui_Dialog
from util_tools.PopUp import PopUpWrapper
import re
import numpy as np


class BackgroundSettings(QWidget, Ui_Dialog):
    def __init__(self, parent=None):
        super(BackgroundSettings, self).__init__()
        self.setWindowTitle("Background Options")
        self.setupUi(self)
        self.default_color = '[0.5, 0.5, 0.5]'
        self.toDelete = False
        self.lineEdit.setText(self.default_color)
        self.show()

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def reject(self):
        self.eventHandler(None)
        self.toDelete = True
        self.deleteLater()

    def isRGBValid(self, entry):
        match_string = '^\[(-?[0-1]\.?(?:[0-9]+)?),\s?(-?[0-1]\.?(?:[0-9]+)?),\s?(-?[0-1]\.?(?:[0-9]+)?)\]'
        rg = re.compile(match_string)
        m = rg.search(entry)
        if m is not None:
            x = float(m.group(1))
            y = float(m.group(2))
            z = float(m.group(3))
            if x > 1.0 or y > 1.0 or z > 1.0:
                return False
            norm = np.sqrt(x**2 + y**2 + z**2)
            if norm == 0:
                return [0.0, 0.0, 0.0]
            return [x, y, z]
        else:
            return False

    def accept(self):
        self.hide()
        try:
            self.new_back = self.isRGBValid(self.lineEdit.text())
            if (self.new_back is not None) and (self.new_back):
                self.eventHandler(self.new_back)
            else:
                raise IOError
            self.toDelete = True
            self.deleteLater()
        except IOError as e:
            x = PopUpWrapper(
                title='Invalid RGB format',
                msg='RGB must be in format [x,y,z] {}, each value between 0 and 1'.format(
                    e),
                more='',
                yesMes=None, parent=self)
            self.lineEdit.setText(self.default_color)
            self.show()

    def closeEvent(self, event):
        if self.toDelete:
            self.toDelete = False
            event.accept()
        else:
            self.eventHandler(None)
            event.accept()
