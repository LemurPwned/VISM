# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_files/PlotSettings.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PlotSettings(object):
    def setupUi(self, PlotSettings):
        PlotSettings.setObjectName("PlotSettings")
        PlotSettings.resize(400, 300)
        self.gridLayoutWidget = QtWidgets.QWidget(PlotSettings)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(9, 9, 381, 281))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 0, 0, 10, 10)

        self.retranslateUi(PlotSettings)
        QtCore.QMetaObject.connectSlotsByName(PlotSettings)

    def retranslateUi(self, PlotSettings):
        _translate = QtCore.QCoreApplication.translate
        PlotSettings.setWindowTitle(_translate("PlotSettings", "Dialog"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PlotSettings = QtWidgets.QDialog()
    ui = Ui_PlotSettings()
    ui.setupUi(PlotSettings)
    PlotSettings.show()
    sys.exit(app.exec_())

