from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QHBoxLayout, QApplication
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
        self.progressLabel.setFixedWidth(100)

        # Creating a progress bar and setting the value limits
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)

        # Creating a Horizontal Layout to add all the widgets
        self.hboxLayout = QHBoxLayout(self)

        # Adding the widgets
        self.hboxLayout.addWidget(self.progressLabel)
        self.hboxLayout.addWidget(self.progressBar)

        # Setting the hBoxLayout as the main layout
        self.setLayout(self.hboxLayout)
        self.setWindowTitle('Dialog with Progressbar')

        self.show()

    def changeProgress(self):
        if self.i in self.breakPoints.keys():
            # self.timer.stop()
            # time.sleep(self.breakPoints[self.i][1])
            if self.counter < self.breakPoints[self.i][1] / 50:
                print("here:", self.counter, self.breakPoints[self.i][1])
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
        self.timer.stop()

# class Worker(QtCore.QObject):
#     def __init__(self, parent=None):
#         super(self.__class__, self).__init__()
#         self.progress = 0
#         self.stillDumbing = True
#         self.parent = parent
#         print("init")
#
#     def work(self):
#         if self.parent == None:
#             raise EnvironmentError("No parent provided!")
#         while True:
#             for i in range(101): #to get too 100%
#                 if not self.stillDumbing:
#                     break
#                 self.parent.changeProgress(i)
#                 print("progress to: ", i)
#                 time.sleep(0.1)

if __name__=="__main__":
    app = QApplication(sys.argv)

    main_window = ProgressBar_Dialog()
    main_window.show()
    main_window.smartDumbProgress({25: ["test25", 1000],\
                                   50:["test50", 1000],\
                                   75:["test75", 1000]})
    # time.sleep(5)
    # main_window.close()
    # main_window.close()

    sys.exit(app.exec_())
