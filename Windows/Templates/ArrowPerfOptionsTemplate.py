# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Windows/UI_files/ArrowPerfOptions.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(342, 714)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(0, QtWidgets.QFormLayout.SpanningRole, spacerItem)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.horizontalSlider = QtWidgets.QSlider(Dialog)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(4)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setPageStep(1)
        self.horizontalSlider.setProperty("value", 1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(2)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.horizontalSlider)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(3, QtWidgets.QFormLayout.SpanningRole, spacerItem1)
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.horizontalSlider_4 = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_4.setMinimum(1)
        self.horizontalSlider_4.setMaximum(32)
        self.horizontalSlider_4.setSingleStep(4)
        self.horizontalSlider_4.setPageStep(1)
        self.horizontalSlider_4.setProperty("value", 16)
        self.horizontalSlider_4.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_4.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider_4.setTickInterval(2)
        self.horizontalSlider_4.setObjectName("horizontalSlider_4")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.horizontalSlider_4)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(6, QtWidgets.QFormLayout.SpanningRole, spacerItem2)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.label_2)
        self.checkBox_5 = QtWidgets.QCheckBox(Dialog)
        self.checkBox_5.setChecked(True)
        self.checkBox_5.setObjectName("checkBox_5")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.SpanningRole, self.checkBox_5)
        self.checkBox_6 = QtWidgets.QCheckBox(Dialog)
        self.checkBox_6.setEnabled(True)
        self.checkBox_6.setChecked(False)
        self.checkBox_6.setObjectName("checkBox_6")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.checkBox_6)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(10, QtWidgets.QFormLayout.SpanningRole, spacerItem3)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.checkBox = QtWidgets.QCheckBox(Dialog)
        self.checkBox.setObjectName("checkBox")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.checkBox)
        self.horizontalSlider_2 = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_2.setEnabled(False)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.SpanningRole, self.horizontalSlider_2)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(14, QtWidgets.QFormLayout.SpanningRole, spacerItem4)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(15, QtWidgets.QFormLayout.SpanningRole, self.label_4)
        self.horizontalSlider_3 = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.formLayout.setWidget(16, QtWidgets.QFormLayout.SpanningRole, self.horizontalSlider_3)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(17, QtWidgets.QFormLayout.SpanningRole, spacerItem5)
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(18, QtWidgets.QFormLayout.SpanningRole, self.label_9)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(20, QtWidgets.QFormLayout.SpanningRole, spacerItem6)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.lineEdit_3 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_3)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setObjectName("label_7")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.formLayout.setLayout(21, QtWidgets.QFormLayout.LabelRole, self.formLayout_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_4.addWidget(self.pushButton_4)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_4.addItem(spacerItem7)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.verticalLayout_4.addWidget(self.comboBox)
        self.formLayout.setLayout(21, QtWidgets.QFormLayout.FieldRole, self.verticalLayout_4)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(22, QtWidgets.QFormLayout.SpanningRole, spacerItem8)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(23, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.horizontalSlider_5 = QtWidgets.QSlider(Dialog)
        self.horizontalSlider_5.setMinimum(1)
        self.horizontalSlider_5.setMaximum(6)
        self.horizontalSlider_5.setPageStep(6)
        self.horizontalSlider_5.setProperty("value", 3)
        self.horizontalSlider_5.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_5.setObjectName("horizontalSlider_5")
        self.formLayout.setWidget(19, QtWidgets.QFormLayout.SpanningRole, self.horizontalSlider_5)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Arrow Performance Options"))
        self.label.setText(_translate("Dialog", "Subsampling"))
        self.label_8.setText(_translate("Dialog", "Resolution"))
        self.label_2.setText(_translate("Dialog", "Color Policy"))
        self.checkBox_5.setText(_translate("Dialog", "Normalize all vectors?"))
        self.checkBox_6.setText(_translate("Dialog", "Hyper Contrast?"))
        self.label_3.setText(_translate("Dialog", "Layers"))
        self.checkBox.setText(_translate("Dialog", "All"))
        self.label_4.setText(_translate("Dialog", "Size"))
        self.label_9.setText(_translate("Dialog", "Height"))
        self.label_5.setText(_translate("Dialog", "R"))
        self.lineEdit.setText(_translate("Dialog", "[1, 0, 0]"))
        self.lineEdit_2.setText(_translate("Dialog", "[0, 1, 0]"))
        self.label_6.setText(_translate("Dialog", "G"))
        self.lineEdit_3.setText(_translate("Dialog", "[0, 0, 1]"))
        self.label_7.setText(_translate("Dialog", "B"))
        self.pushButton_4.setText(_translate("Dialog", "Reset"))
        self.comboBox.setItemText(0, _translate("Dialog", "Standard"))
        self.comboBox.setItemText(1, _translate("Dialog", "RGB policy"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
