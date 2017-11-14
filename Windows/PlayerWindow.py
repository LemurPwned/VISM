from PyQt5 import QtWidgets, QtCore
import time as tm
import sys #temp

class PlayerWindow(QtCore.QObject):

    signalStatus = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        # Create a gui object.
        self.gui = Window()

        # Setup the worker object and the worker_thread.
        self.worker = WorkerObject()
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self.gui.show()

    def setHandler(self, handler):
        self.handler = handler

        # Make any cross object connections.
        self._connectSignals()

    def _connectSignals(self):
        self.gui.button_start.clicked.connect(self.worker.startWork)
        self.gui.button_pause.clicked.connect(self.forceWorkerReset)
        #self.signalStatus.connect(self.gui.updateStatus)
        self.worker.signalStatus.connect(self.handler)

        #self.parent().aboutToQuit.connect(self.forceWorkerQuit)

    def forceWorkerReset(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

            self.signalStatus.emit('Idle.')
            self.worker_thread.start()

    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()


class WorkerObject(QtCore.QObject):
    signalStatus = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self._iterator = 0

    @QtCore.pyqtSlot()
    def startWork(self):
        factors = self.play()
        self.signalStatus.emit('Idle.')

    def play(self):
        while(True):
            tm.sleep(0.1)
            self._iterator = self._iterator + 1
            self.signalStatus.emit(str(self._iterator))

class Window(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.button_start = QtWidgets.QPushButton('Start', self)
        self.button_pause = QtWidgets.QPushButton('Pause', self)
        self.label_status = QtWidgets.QLabel('', self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.button_start)
        layout.addWidget(self.button_pause)
        layout.addWidget(self.label_status)

        self.setFixedSize(400, 200)

    '''@QtCore.pyqtSlot(str)
    def updateStatus(self, status):
        #self.label_status.setText(status)
        print(status)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    example = PlayerWindow(app)
    sys.exit(app.exec_())'''
