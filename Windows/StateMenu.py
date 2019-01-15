from Windows.Templates.StateMenuTemplate import Ui_Dialog
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
    QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore


class StateMenuController(QWidget, Ui_Dialog):
    def __init__(self, state_object):
        super(StateMenuController, self).__init__()
        self.setWindowTitle("State Machine Control Menu")
        self.setupUi(self)
        widow_flag = QtCore.Qt.WindowFlags() | QtCore.Qt.WindowStaysOnTopHint
        self.state_controller = state_object

        self.spinBox.valueChanged.connect(self.resolution_trigger)
        self.spinBox_2.valueChanged.connect(self.sampling_trigger)

        self.spinBox.setValue(16.0)

        self.doubleSpinBox.valueChanged.connect(self.ambient_trigger)
        self.doubleSpinBox_2.valueChanged.connect(self.height_trigger)
        self.doubleSpinBox_3.valueChanged.connect(self.radius_trigger)

        # self.pushButton.clicked.connect(self.global_trigger)
        self.show()

    def resolution_trigger(self, val):
        self.resolution = val
        self.state_controller.resolution_change(val)

    def sampling_trigger(self, val):
        self.sampling = val
        self.state_controller.sampling_change(val)

    def ambient_trigger(self, val):
        self.ambient = val
        self.state_controller.ambient_change(val)

    def height_trigger(self, val):
        self.height = val
        self.state_controller.height_change(val)

    def radius_trigger(self, val):
        self.radius = val
        self.state_controller.radius_change(val)

    def accept(self):
        pass

    def reject(self):
        pass

    def closeEvent(self, event):
        event.accept()
