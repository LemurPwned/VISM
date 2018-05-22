from PyQt5 import QtCore
import time as tm

class DirectoryLoaderPoll(QtCore.QObject):
    signal = QtCore.pyqtSignal(int)
    def __init__(self, q, callback):
        super(self.__class__, self).__init__()
        self.q = q
        self.signal.connect(callback)

    def startWork(self):
        # q:
        # 0 - loading directory still running
        # 1 - loading finished without errors
        # 2 - ValueError during process
        # 3 - Exception during process

        status = 3
        while(True):

            if not self.q.empty():
                status = self.q.get()
                if status != 0:
                    break
            # to avoid too much overhead for cpu
            tm.sleep(0.1)

        self.signal.emit(status)
