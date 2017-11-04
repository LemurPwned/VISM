# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_files/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(863, 690)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 851, 651))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.verticalLayoutWidget)
        self.openGLWidget.setObjectName("openGLWidget")
        self.verticalLayout.addWidget(self.openGLWidget)
        self.statusBar_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.statusBar_label.setMaximumSize(QtCore.QSize(16777215, 10))
        self.statusBar_label.setText("")
        self.statusBar_label.setAlignment(QtCore.Qt.AlignCenter)
        self.statusBar_label.setObjectName("statusBar_label")
        self.verticalLayout.addWidget(self.statusBar_label)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setMaximumSize(QtCore.QSize(16777215, 10))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 863, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_File = QtWidgets.QAction(MainWindow)
        self.actionLoad_File.setObjectName("actionLoad_File")
        self.actionLoad_Directory = QtWidgets.QAction(MainWindow)
        self.actionLoad_Directory.setObjectName("actionLoad_Directory")
        self.action1_Window_Grid = QtWidgets.QAction(MainWindow)
        self.action1_Window_Grid.setObjectName("action1_Window_Grid")
        self.action2_Windows_Grid = QtWidgets.QAction(MainWindow)
        self.action2_Windows_Grid.setObjectName("action2_Windows_Grid")
        self.actionPlot = QtWidgets.QAction(MainWindow)
        self.actionPlot.setObjectName("actionPlot")
        self.actionAnimation = QtWidgets.QAction(MainWindow)
        self.actionAnimation.setObjectName("actionAnimation")
        self.action4_Windows_Grid = QtWidgets.QAction(MainWindow)
        self.action4_Windows_Grid.setObjectName("action4_Windows_Grid")
        self.menuFile.addAction(self.actionLoad_File)
        self.menuFile.addAction(self.actionLoad_Directory)
        self.menuEdit.addAction(self.actionPlot)
        self.menuEdit.addAction(self.actionAnimation)
        self.menuView.addAction(self.action1_Window_Grid)
        self.menuView.addAction(self.action2_Windows_Grid)
        self.menuView.addAction(self.action4_Windows_Grid)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionLoad_File.setText(_translate("MainWindow", "Load File"))
        self.actionLoad_Directory.setText(_translate("MainWindow", "Load Directory"))
        self.action1_Window_Grid.setText(_translate("MainWindow", "Window Grid"))
        self.action2_Windows_Grid.setText(_translate("MainWindow", "2 Windows Grid"))
        self.actionPlot.setText(_translate("MainWindow", "Plot"))
        self.actionAnimation.setText(_translate("MainWindow", "Animation"))
        self.action4_Windows_Grid.setText(_translate("MainWindow", "4 Windows Grid"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

