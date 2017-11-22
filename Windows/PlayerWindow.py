from PyQt5 import QtWidgets, QtCore
import time as tm
import sys #temp

class PlayerWindow(QtCore.QObject):

    signalStatus = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)


        # Create a gui object.
        self.gui = Window()
        self.parent = parent

        self.checkForErrors()

        # Setup the worker object and the worker_thread.
        self.worker = WorkerObject()
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self._connectSignals()
        self.gui.show()


    def checkForErrors(self):
        if self.parent == None:
            msg = "PlayerWindow: no parent provided! Use: x = PlayerWindow(self) instead of x = PlayerWindow()"
            print(msg)
            exit()

        if self.parent._LOADED_FLAG_ == False:
            msg = "PlayerWindow: First load data! Go to: File > Load Directory and select proper directory!"
            print(msg)
            for element in self.gui.elements:
                element.setEnabled(False)

            return False

        if self.parent.panes[0].widget == None:
            msg = "PlayerWindow: No widget selected Click Add Widget button in main window!"
            print(msg)
            for element in self.gui.elements:
                element.setEnabled(False)

            return False

        return True


    def reloadGui(self):
        if self.checkForErrors():
            for element in self.gui.elements:
                element.setEnabled(True)


    def setIterators(self, iterators):
        self.worker.widgetIterators = iterators

    def _connectSignals(self):
        self.gui.button_start.clicked.connect(self.PlayPauseClicked)
        self.gui.button_start.clicked.connect(self.worker.startWork)
        self.gui.button_stop.clicked.connect(lambda: self.forceWorkerReset(True))
        #self.worker.signalStatus.connect(self.handler)
        self.gui.button_nextFrame.clicked.connect(lambda: self.worker.moveFrame(1))
        self.gui.button_prevFrame.clicked.connect(lambda: self.worker.moveFrame(-1))
        self.gui.slider_speed.valueChanged.connect(self.speedChange)

        #self.parent().aboutToQuit.connect(self.forceWorkerQuit) #TODO search about this

    def PlayPauseClicked(self):
        self.worker.running = not self.worker.running
        if self.worker.running:
            self.gui.button_start.setText("Pause")
        else:
            self.forceWorkerReset(False)
            self.gui.button_start.setText("Play")

    def forceWorkerReset(self, reset=True):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            if reset:
                self.worker.resetIterator()
            self.worker.running = False
            self.worker_thread.start()

    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

    def speedChange(self):
        self.gui.speedLabel.setText("Animation Speed: " + \
                                    str(self.gui.slider_speed.value()/10))
        self.worker.setSpeed(self.gui.slider_speed.value())

class WorkerObject(QtCore.QObject):
    signalStatus = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self._iterator = 0
        self.running = False
        self._speed = 10
        self.handler = None
        self.widgetIterators = None

    def setSpeed(self, speed):
        self._speed = speed

    def resetIterator(self):
        self._iterator = 0


    def startWork(self):
        #self.running = not self.running
        if self.running:
            self.play()

        #self.signalStatus.emit('Idle.')
    @QtCore.pyqtSlot()
    def play(self):
        while(True):
            if self.running:
                self._iterator = self._iterator + 1
                for i in self.widgetIterators:
                    i(self._iterator)
                #self.signalStatus.emit(self._iterator)

            if not self.running:
                pass

            tm.sleep(1/self._speed)

    @QtCore.pyqtSlot()
    def moveFrame(self, howMany):
        print(self._iterator, howMany)
        if ((self._iterator + howMany) >= 0):
            self._iterator = (self._iterator + howMany)
            self.signalStatus.emit(self._iterator)
        else:
            self._iterator = 0
            self.signalStatus.emit(self._iterator)


class Window(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.elements = []
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.button_start = QtWidgets.QPushButton('Play', self)
        self.button_stop = QtWidgets.QPushButton('Reset', self)
        self.button_nextFrame = QtWidgets.QPushButton('>', self)
        self.button_prevFrame = QtWidgets.QPushButton('<', self)
        self.slider_speed = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.speedLabel = QtWidgets.QLabel("Animtaion Speed: 1", self)
        self.slider_speed.setMaximum(50)
        self.slider_speed.setMinimum(1)
        self.slider_speed.setValue(10)
        self.slider_speed.setSingleStep(1)
        #self.label_status = QtWidgets.QLabel('test', self)

        self.elements.append(self.button_start)
        self.elements.append(self.button_stop)
        self.elements.append(self.button_nextFrame)
        self.elements.append(self.button_prevFrame)
        self.elements.append(self.slider_speed)
        self.elements.append(self.speedLabel)


        self.mainLayout = QtWidgets.QGridLayout(self)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.button_prevFrame,0,0)
        layout.addWidget(self.button_start,0,1)
        layout.addWidget(self.button_stop,0,2)
        layout.addWidget(self.button_nextFrame,0,3)
        #layout.addWidget(self.label_status)

        layout2 = QtWidgets.QVBoxLayout()
        layoutin2_1 = QtWidgets.QHBoxLayout()
        layoutin2_2 = QtWidgets.QHBoxLayout()
        layoutin2_1.addWidget(self.slider_speed)
        layoutin2_2.addWidget(self.speedLabel)

        layout2.addLayout(layoutin2_1)
        layout2.addLayout(layoutin2_2)
        self.mainLayout.addLayout(layout, 0,0)
        self.mainLayout.addLayout(layout2, 1,0)

        self.setFixedSize(400, 150)
