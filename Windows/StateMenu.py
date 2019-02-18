from Windows.Templates.StateMenuTemplate import Ui_Dialog
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
    QVBoxLayout, QRadioButton, QLabel, QSlider, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
from Windows.GeneralPerf import validate_entry_no_norm


class StateMenuController(QWidget, Ui_Dialog):
    def __init__(self, state_object):
        super(StateMenuController, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("State Machine Control Menu")
        self.setWindowFlags(QtCore.Qt.WindowFlags() |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.state_controller = state_object

        self.spinBox.valueChanged.connect(self.resolution_trigger)
        self.spinBox_2.valueChanged.connect(self.sampling_trigger)
        self.spinBox_2.setMaximum(12)
        self.spinBox_3.valueChanged.connect(self.start_layer_trigger)
        self.spinBox_4.valueChanged.connect(self.stop_layer_trigger)

        self.spinBox.setValue(self.state_controller.resolution)
        self.spinBox_2.setValue(self.state_controller.sampling)
        self.spinBox_3.setMaximum(self.state_controller.znodes-1)
        self.spinBox_3.setValue(self.state_controller.start_layer)
        self.spinBox_4.setMaximum(self.state_controller.znodes)
        self.spinBox_4.setValue(self.state_controller.stop_layer)

        self.spinBox_5.valueChanged.connect(self.xLightPos)
        self.spinBox_6.valueChanged.connect(self.yLightPos)
        self.spinBox_7.valueChanged.connect(self.zLightPos)

        self.spinBox_8.valueChanged.connect(self.xBase)
        self.spinBox_9.valueChanged.connect(self.yBase)
        self.spinBox_10.valueChanged.connect(self.zBase)
        self.spinBox_10.setValue(self.state_controller.zbase_scaler)

        for spin_box in [self.spinBox_5,
                         self.spinBox_6,
                         self.spinBox_7]:
            spin_box.setMaximum(100)
            spin_box.setMinimum(-100)

        for spin_box in [self.spinBox_8,
                         self.spinBox_9,
                         self.spinBox_10]:
            spin_box.setMaximum(10)
            spin_box.setMinimum(1)

        self.doubleSpinBox.setValue(self.state_controller.ambient)
        self.doubleSpinBox_2.setValue(self.state_controller.height)
        self.doubleSpinBox_3.setValue(self.state_controller.radius)

        self.doubleSpinBox.valueChanged.connect(self.ambient_trigger)
        self.doubleSpinBox_2.valueChanged.connect(self.height_trigger)
        self.doubleSpinBox_3.valueChanged.connect(self.radius_trigger)

        self.comboBox.currentIndexChanged[str].connect(self.dropdown_trigger)
        self.comboBox.setCurrentIndex(1)

        self.lineEdit.textChanged.connect(self.positive_color_trigger)
        self.lineEdit.setText(str(self.state_controller.positive_color))
        self.lineEdit_2.textChanged.connect(self.negative_color_trigger)
        self.lineEdit_2.setText(str(self.state_controller.negative_color))
        self.lineEdit_3.textChanged.connect(self.color_direction_trigger)
        self.lineEdit_3.setText(str(self.state_controller.color_vector))
        self.show()

    def positive_color_trigger(self, val):
        nval = validate_entry_no_norm(val)
        if nval:
            self.state_controller.set_positive_color(nval)
        else:
            # reset
            self.lineEdit.setText(str(self.state_controller.positive_color))

    def negative_color_trigger(self, val):
        nval = validate_entry_no_norm(val)
        if nval:
            self.state_controller.set_negative_color(nval)
        else:
            # reset
            self.lineEdit_2.setText(str(self.state_controller.negative_color))

    def color_direction_trigger(self, val):
        nval = validate_entry_no_norm(val)
        if nval:
            self.state_controller.set_color_vector(nval)
        else:
            # reset
            self.lineEdit_3.setText(str(self.state_controller.color_vector))

    def xBase(self, val):
        self.state_controller.set_xBase(val)

    def yBase(self, val):
        self.state_controller.set_yBase(val)

    def zBase(self, val):
        self.state_controller.set_zBase(val)

    def xLightPos(self, val):
        self.state_controller.set_xLight(val)

    def yLightPos(self, val):
        self.state_controller.set_yLight(val)

    def zLightPos(self, val):
        self.state_controller.set_zLight(val)

    def dropdown_trigger(self, val):
        self.state_controller.function_change(val)

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
