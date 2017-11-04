# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_files/animationSettings.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AnimationSettings(object):
    def setupUi(self, AnimationSettings):
        AnimationSettings.setObjectName("AnimationSettings")
        AnimationSettings.resize(400, 300)
        AnimationSettings.setMouseTracking(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(AnimationSettings)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtWidgets.QWidget(AnimationSettings)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 9, 381, 231))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.doubleSpinBox.setMinimumSize(QtCore.QSize(68, 0))
        self.doubleSpinBox.setDecimals(1)
        self.doubleSpinBox.setMaximum(10.0)
        self.doubleSpinBox.setSingleStep(0.1)
        self.doubleSpinBox.setProperty("value", 1.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.colorringMode_comboBox = QtWidgets.QComboBox(self.formLayoutWidget)
        self.colorringMode_comboBox.setObjectName("colorringMode_comboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.colorringMode_comboBox)

        self.retranslateUi(AnimationSettings)
        self.buttonBox.accepted.connect(AnimationSettings.accept)
        self.buttonBox.rejected.connect(AnimationSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(AnimationSettings)

    def retranslateUi(self, AnimationSettings):
        _translate = QtCore.QCoreApplication.translate
        AnimationSettings.setWindowTitle(_translate("AnimationSettings", "Dialog"))
        self.label.setText(_translate("AnimationSettings", "Animation Speed:"))
        self.label_2.setText(_translate("AnimationSettings", "Coloring mode:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AnimationSettings = QtWidgets.QDialog()
    ui = Ui_AnimationSettings()
    ui.setupUi(AnimationSettings)
    AnimationSettings.show()
    sys.exit(app.exec_())

