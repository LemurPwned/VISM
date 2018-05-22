from PyQt5 import QtCore
import time as tm
import threading


class DirectoryLoaderPoll(QtCore.QObject):
    def __init__(self, q, callback):
        super(self.__class__, self).__init__()
        self.q = q
        self.callback = callback

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
            tm.sleep(0.1)

        self.callback(status)

