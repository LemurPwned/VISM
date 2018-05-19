from PyQt5 import QtCore
import time as tm
import threading


class DirectoryLoaderPoll(QtCore.QObject):
    def __init__(self, q, callback):
        super(self.__class__, self).__init__()
        self.q = q
        self.callback = callback

    def startWork(self):
        while(True):
            if not self.q.empty() and not self.q.get():
                break
            tm.sleep(0.1)

        self.callback()
