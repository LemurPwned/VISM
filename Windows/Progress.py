from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QVBoxLayout, QApplication
from PyQt5 import QtCore
import sys
import time

class ProgressBar_Dialog(QDialog, QtCore.QObject):
    def __init__(self):
        super(ProgressBar_Dialog, self).__init__()
        self.init_ui()
        self.i = 0
        self.counter = 0

    def init_ui(self):
        # Creating a label
        self.progressLabel = QLabel('Initialization...', self)

        # Creating a progress bar and setting the value limits
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)

        # Creating a Horizontal Layout to add all the widgets
        self.vboxLayout = QVBoxLayout(self)

        # Adding the widgets
        self.vboxLayout.addWidget(self.progressBar)
        self.vboxLayout.addWidget(self.progressLabel)


        # Setting the hBoxLayout as the main layout
        self.setLayout(self.vboxLayout)
        self.setWindowTitle('Action Progress...')

        self.show()

    def changeProgress(self):
        if self.i in self.breakPoints.keys():
            if self.counter < self.breakPoints[self.i][1] / 50:
                self.i -= 1
                self.counter += 1
                return

            self.counter = 0
            self.progressLabel.setText(self.breakPoints[self.i][0])

        if self.mode == "smart" and self.i > 98:
            self.timer.stop()
        self.progressBar.setValue(self.i%101)
        self.i += 1


    def dumbProgress(self):
        #this function shows progress which has no connection
        # with real progress all it does it ensures user,
        #that app is still working and haven't crashed during process.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.changeProgress)
        self.timer.start(25)
        self.mode = "dumb"

        # self.close()

    def smartDumbProgress(self, breakPoints={}):
        #breakPoints={25: ["Getting something ready", 200]}
        #so in 25% we put information "Getting something ready"\
        #and it lasts for 200ms.

        self.breakPoints = breakPoints
        self.breakPoints[99] = ["Finishing process...", 1000]

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.changeProgress)
        self.timer.start(50)
        self.mode = "smart"


    def close(self):
        self.counter = 1000
        self.i = 99
        self.timer.stop()

if __name__=="__main__":
    app = QApplication(sys.argv)

    main_window = ProgressBar_Dialog()
    main_window.show()
    main_window.smartDumbProgress({25: ["task25...", 1000],\
                                   50:["task50...", 1000],\
                                   75:["task75...", 1000]})
    sys.exit(app.exec_())
