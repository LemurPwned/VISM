import traceback
import sys
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QRunnable, QThreadPool
from PopUp import PopUpWrapper


class ThreadingWrapper:
    def __init__(self, exceptionAction):
        self.threadPool = QThreadPool()
        self.exceptionAction = exceptionAction
    
    def collapse_threads(self, func, *args, **kwargs):
        worker = Worker(func, *args, **kwargs)
        worker.signals.exception.connect(self.exceptionAction)
        worker.signals.finished.connect(self.thread_complete)
        self.threadPool.start(worker)

    def thread_complete(self):
        print("Complete")


class ExceptionWorker(QObject):
    finished = pyqtSignal()
    exception = pyqtSignal(tuple)

class Worker(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = ExceptionWorker()

    @pyqtSlot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value  = sys.exc_info()[:2]
            self.signals.exception.emit((exctype, value, 
                                    traceback.format_exc()))
        else:
            self.signals.finished.emit()
