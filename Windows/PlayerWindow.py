from PyQt5 import QtWidgets, QtCore
import time as tm
import sys #temp

class PlayerWindow(QtCore.QObject):

    signalStatus = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.gui = Window()
        self.parent = parent

        self.checkForErrors()

        # Setup the worker object and the worker_thread.
        self.worker = WorkerObject().getInstance()
        if WorkerObject().getNumbers() == 2:
            self.worker_thread = QtCore.QThread()
            self.worker.moveToThread(self.worker_thread)
            self.worker_thread.start()
        else:
            #worker already exists, load it's data
            if self.worker.running:
                self.gui.button_start.setText("Pause")

            self.gui.slider_speed.setValue(self.worker.getSpeed())
            self.gui.speedLabel.setText("Animation Speed: " + str(self.worker.getSpeed()/10))

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

    def setHandler(self, handler):
        self.handler = handler
        self.worker.handler = handler

        self._connectSignals()

    def setIterators(self, iterators):
        self.worker.widgetIterators = iterators

    def _connectSignals(self):
        self.gui.button_start.clicked.connect(self.PlayPauseClicked)
        self.gui.button_start.clicked.connect(self.worker.startWork)
        self.gui.button_stop.clicked.connect(self.forceWorkerReset)
        self.gui.button_nextFrame.clicked.connect(lambda: self.worker.moveFrame(1))
        self.gui.button_prevFrame.clicked.connect(lambda: self.worker.moveFrame(-1))
        self.gui.slider_speed.valueChanged.connect(self.speedChange)

        # self.parent().aboutToQuit.connect(self.forceWorkerQuit) #TODO search about this

    def PlayPauseClicked(self):
        self.worker.running = not self.worker.running
        if self.worker.running:
            self.gui.button_start.setText("Pause")
        else:
            self.gui.button_start.setText("Play")

    def forceWorkerReset(self):
        # if self.worker_thread.isRunning():
        self.worker.running = False
        self.gui.button_start.setText("Play")
        self.worker.resetIterator()

    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

    def speedChange(self):
        self.gui.speedLabel.setText("Animation Speed: " + \
                                    str(self.gui.slider_speed.value()/10))
        self.worker.setSpeed(self.gui.slider_speed.value())

    def closeMe(self):
        self.gui.close()

    def passTriggerList(self, trigger):
        self.worker.passTriggerList(trigger)

#SINGLETON

#reset while playing weird stuff
class WorkerObject:
    class __WorkerObject(QtCore.QObject):

        def __init__(self, parent=None):
            super(self.__class__, self).__init__(parent)
            self._iterator = 0
            self.running = False
            self._speed = 10
            self.handler = None
            self.widgetIterators = None
            self._TRIGGER_ = False
            self.trig_len = 0
            self.play = self.standard_play

        def passTriggerList(self, trigger):
            self.trigger = trigger
            self._TRIGGER_ = True
            self.trig_len = len(self.trigger)
            self.play = self.trigger_play

        def clearWidgetIterators(self):
            self.widgetIterators = None

        def getIterator(self):
            return self._iterator

        def setSpeed(self, speed):
            self._speed = speed

        def getSpeed(self):
            return self._speed

        def resetIterator(self):
            self._iterator = 0

        def startWork(self):
            self.play()

        def standard_play(self):
            while(True):
                if self.running:
                    self._iterator += 1
                    for i in self.widgetIterators:
                        i(self._iterator)
                if not self.running:
                    break
                tm.sleep(1/self._speed)

        def trigger_play(self):
            while(True):
                for k in self.trigger:
                    if self.running:
                        self._iterator += 1
                        c = 0
                        for i in self.widgetIterators:
                            print(c)
                            i(k, trigger=True)
                            c+=1
                    if not self.running:
                        break
                    tm.sleep(1/self._speed)


        def moveFrame(self, howMany):
            self._iterator += howMany
            if self._TRIGGER_:
                self._iterator %= self.trig_len
                for i in self.widgetIterators:
                    i(self.trigger[self._iterator], trigger=True)
            else:
                for i in self.widgetIterators:
                    i(self._iterator)

    numbers = 0  # fast_fix
    instance = None
    def __init__(self, parent=None):
        if not WorkerObject.instance:
            WorkerObject.instance = WorkerObject.__WorkerObject(parent)

        else:
            WorkerObject.instance.parent = parent
        WorkerObject.numbers += 1

    @staticmethod
    def getInstance():
        return WorkerObject.instance

    @staticmethod
    def getNumbers():
        return WorkerObject.numbers

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
        self.slider_speed.setMaximum(100)
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
