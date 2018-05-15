from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5 import QtCore


class PopUpWrapper(QWidget):
    def __init__(self, title, msg, more=None, yesMes=None, noMes=None,
                    actionWhenYes=None, actionWhenNo=None, parent=None):
        super().__init__()

        self.width = 320
        self.height = 200

        if parent == None:
            app = QtCore.QCoreApplication.instance()
            screen_resolution = app.desktop().screenGeometry()
            width, height = screen_resolution.width(), screen_resolution.height()
            self.setGeometry((width - self.width()) / 2, (height - self.height()) / 2, 300, 400)
        else:
            self.left = parent.width()/2 - self.width/2
            self.top = parent.height()/2 - self.height/2

        self.title = title
        self.msg = msg
        self.actionWhenYes = actionWhenYes
        self.actionWhenNo = actionWhenNo
        self.yesMes = yesMes
        self.noMes = noMes
        self.more = more
        self.loaded = False

        if self.more is not None and self.yesMes is None:
            self.infoWindow()
        else:
            self.questionWindow()

    def questionWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        buttonReply = QMessageBox.question(self, self.title, self.msg,
                                            self.yesMes | self.noMes, self.yesMes)
        if buttonReply == self.yesMes:
            if self.actionWhenYes is not None:
                self.actionWhenYes()
        else:
            if self.actionWhenNo is not None:
                self.actionWhenNo()
        self.show()

    def infoWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        infotext = QMessageBox.information(self, self.title, self.msg, QMessageBox.Ok)

        if infotext == QMessageBox.Ok:
            if self.loaded:
                self.close()
        else:
            self.infoWindow()
        self.show()
