import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class PopUpWrapper(QWidget):
    def __init__(self, title, msg, yesMes, noMes, actionWhenYes, actionWhenNo):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200

        self.title = title
        self.msg = msg
        self.actionWhenYes = actionWhenYes
        self.actionWhenNo = actionWhenNo
        self.yesMes = yesMes
        self.noMes = noMes
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        buttonReply = QMessageBox.question(self, self.title,
        self.msg, self.yesMes | self.noMes, self.yesMes)
        if buttonReply == self.yesMes:
            if self.actionWhenYes is not None:
                self.actionWhenYes()
        else:
            if self.actionWhenNo is not None:
                self.actionWhenNo()
        self.show()
