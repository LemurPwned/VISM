# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Windows/UI_files/SimplePerfOptions.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(307, 374)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-40, 320, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(30, 20, 251, 281))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(0, QtWidgets.QFormLayout.SpanningRole, spacerItem)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.label_2)
        self.checkBox_5 = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBox_5.setChecked(True)
        self.checkBox_5.setObjectName("checkBox_5")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.checkBox_5)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(3, QtWidgets.QFormLayout.SpanningRole, spacerItem1)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.formLayoutWidget)
        self.horizontalSlider_2.setEnabled(False)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.horizontalSlider_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(7, QtWidgets.QFormLayout.SpanningRole, spacerItem2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(8, QtWidgets.QFormLayout.SpanningRole, spacerItem3)
        self.lineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label_4 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.label_4)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_2.setText(_translate("Dialog", "Color Policy"))
        self.checkBox_5.setText(_translate("Dialog", "Normalize all vectors?"))
        self.label_3.setText(_translate("Dialog", "Layers"))
        self.lineEdit.setText(_translate("Dialog", "[1, 0, 0]"))
        self.label_4.setText(_translate("Dialog", "Relative vector (RGB) "))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
