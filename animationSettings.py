from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from animationSettingsTemplate import Ui_AnimationSettings

class AnimationSettings(QWidget, Ui_AnimationSettings):
    animationSpeed = 1.0
    coloringMode = ""

    def __init__(self):
        super(AnimationSettings, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Animation Settings")
        self.setPossibleColoringAlgorithms()
        self.show()

    def setPossibleColoringAlgorithms(self, listOfItems=['Default']):
        self.colorringMode_comboBox.clear()
        self.colorringMode_comboBox.addItems(listOfItems)

    def accept(self):
        AnimationSettings.animationSpeed = (self.doubleSpinBox.value())
        AnimationSettings.coloringMode = self.colorringMode_comboBox.currentText()
        self.close()

    def reject(self):
        self.close()
