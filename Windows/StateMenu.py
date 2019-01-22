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
        self.spinBox_3.valueChanged.connect(self.start_layer_trigger)
        self.spinBox_4.valueChanged.connect(self.stop_layer_trigger)

        self.spinBox.setValue(self.state_controller.resolution)
        self.spinBox_2.setValue(self.state_controller.sampling)
        self.spinBox_3.setMaximum(self.state_controller.znodes-1)
        self.spinBox_3.setValue(self.state_controller.start_layer)
        self.spinBox_4.setMaximum(self.state_controller.znodes)
        self.spinBox_4.setValue(self.state_controller.stop_layer)

        self.doubleSpinBox.setValue(self.state_controller.ambient)
        self.doubleSpinBox_2.setValue(self.state_controller.height)
        self.doubleSpinBox_3.setValue(self.state_controller.radius)

        self.doubleSpinBox.valueChanged.connect(self.ambient_trigger)
        self.doubleSpinBox_2.valueChanged.connect(self.height_trigger)
        self.doubleSpinBox_3.valueChanged.connect(self.radius_trigger)

        self.show()

    def start_layer_trigger(self, val):
        self.state_controller.start_layer_change(val)

    def stop_layer_trigger(self, val):
        self.state_controller.stop_layer_change(val)

    def resolution_trigger(self, val):
        self.state_controller.resolution_change(val)

    def sampling_trigger(self, val):
        self.state_controller.sampling_change(val)

    def ambient_trigger(self, val):
        self.state_controller.ambient_change(val)

    def height_trigger(self, val):
        self.state_controller.height_change(val)

    def radius_trigger(self, val):
        self.state_controller.radius_change(val)

    def accept(self):
        pass

    def reject(self):
        pass

    def closeEvent(self, event):
        event.accept()
