from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel, QHBoxLayout, QApplication
from PyQt5 import QtCore
import sys
import time

class ProgressBar_Dialog(QDialog, QtCore.QObject):
    def __init__(self):
        super(ProgressBar_Dialog, self).__init__()
        self.init_ui()
        self.i=0

    def init_ui(self):
        # Creating a label
        # self.progressLabel = QLabel('Initialization...', self)

        # Creating a progress bar and setting the value limits
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)

        # Creating a Horizontal Layout to add all the widgets
        self.hboxLayout = QHBoxLayout(self)

        # Adding the widgets
        # self.hboxLayout.addWidget(self.progressLabel)
        self.hboxLayout.addWidget(self.progressBar)

        # Setting the hBoxLayout as the main layout
        self.setLayout(self.hboxLayout)
        self.setWindowTitle('Dialog with Progressbar')

        self.show()

    def changeProgress(self):
        self.i += 1
        # print(self.i)
        self.progressBar.setValue(self.i%101)
        # self.progressLabel.setText(str(self.i%101))


    def dumbProgress(self):
        #this function shows progress which has no connection
        # with real progress all it does it ensures user,
        #that app is still working and haven't crashed during process.
        # self.worker = Worker(self)
        # self.worker_thread = QtCore.QThread()
        # self.worker.moveToThread(self.worker_thread)
        # self.worker_thread.start()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.changeProgress)
        self.timer.start(25)

        # self.close()

    def close(self):
        self.stillDumbing = False

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
    main_window.dumbProgress()
    time.sleep(5)
    # main_window.close()
    main_window.close()

    sys.exit(app.exec_())
