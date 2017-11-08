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
        self.verticalLayoutWidget = QtWidgets.QWidget(PlotSettings)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 381, 281))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

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

