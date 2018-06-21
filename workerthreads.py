import traceback
import sys
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QRunnable, QThreadPool, QByteArray, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel, QSizePolicy

from PopUp import PopUpWrapper


class ThreadingWrapper:
    def __init__(self, completeAction=None, exceptionAction=None, parent=None):
        """
        Creates a wrapper around GUI Thread management that displays 
        loading spinner
        """
        self.threadPool = QThreadPool()
        self.exceptionAction = exceptionAction
        self.completeAction = completeAction
        """
        part below sets up loading bar
        """
        self.movie = QMovie('red_big.gif')
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)

        self.movie_screen = QLabel(parent=parent)

        width = 320
        height = 200
        left = parent.width()/2 - width/2
        top = parent.height()/2 - height/2

        self.movie_screen.setGeometry(left, top, width, height)
        self.movie_screen.setAlignment(Qt.AlignCenter)
        self.movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.movie_screen.setAttribute(Qt.WA_TranslucentBackground, True)
        self.movie_screen.setStyleSheet("QLabel::item { border: 0px solid black };");

        self.movie_screen.setMovie(self.movie)
    
    def collapse_threads(self, func, *args, **kwargs):
        """
        this function runs the proper QThreadPool
        if exception is caught, then exceptionAction is excecuted and 
        a PopUp displays
        """
        worker = Worker(func, *args, **kwargs)
        worker.signals.exception.connect(self.thread_exception)
        worker.signals.finished.connect(self.thread_complete)
        self.threadPool.start(worker)
        self.movie_screen.show()
        self.movie.start()

    def thread_exception(self, exceptionE):
        if self.exceptionAction:
            self.exceptionAction()
        x = PopUpWrapper("Error", 
                            msg="Error {}\n{}".format(exceptionE[0], 
                                                        exceptionE[1]), 
                            more="Error window")
        self.movie.stop()
        self.movie_screen.close()

    def thread_complete(self):
        if self.completeAction:
            self.completeAction()
        self.movie.stop()
        self.movie_screen.close()

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
        # try:
        print("ENTERING")
        print(self.func.__name__)
        result = self.func(*self.args, **self.kwargs)
        print("DONE??")
        # except:
        #     print("EXCEPTION")
        #     traceback.print_exc()
        #     exctype, value  = sys.exc_info()[:2]
        #     self.signals.exception.emit((exctype, value, 
        #                             traceback.format_exc()))
        # finally:
        print("FINISHING")
        self.signals.finished.emit()
        print("QUIT")