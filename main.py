import sys

from PyQt5.QtCore import QTimer, QPoint, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QGroupBox, QGridLayout
from PyQt5.QtWidgets import (QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from Windows.MainWindowTemplate import Ui_MainWindow

from Canvas import Canvas
from Canvas3D import Canvas3D

from Parser import Parser

from Windows.animationSettings import AnimationSettings
from spin_gl import GLWidget
from Windows.PlotSettings import PlotSettings
import threading

class MainWindow(QMainWindow, Ui_MainWindow, QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.odt_data = ""
        #self.openGLWidget = GLWidget()
        '''IT IS CRUCIAL TO COMMENT OUT IN MainWindowTemplate.py THIS LINE:
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.verticalLayoutWidget)
        IT IS AUTOGENERATED
         AND IT WON'T WORK WITHOUT DELETING IT! I WILL DELETE THIS COMMENT
         AS SOON AS I WILL BE ABLE TO FIX THAT IN GUI GENERATOR.
         FOR NOW EVERY TIME YOU RECOMPILE GUI IT HAS TO BE COMMENTED.'''

        self.setupUi(self) #setting up UI from MainWindowTemplate.py File
        #(generated by gui generator)

        self.setWindowTitle("ESE - Early Spins Enviroment")
        self.setGeometry(10,10,1280, 768) #size of window
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())
        self.groupBox = []
        self.layout = []
        self.button = []

        self.makeGrid()
        self.make1WindowGrid()
        self.events()

    def events(self):
        '''creates listeners for all menu buttons'''
        #FILE SUBMENU
        self.actionLoad_Directory.triggered.connect(self.loadDirectory)

        #EDIT SUBMENU
        self.actionPlot.triggered.connect(self.showPlotSettings)
        self.actionAnimation.triggered.connect(self.showAnimationSettings)

        #VIEW SUBMENU
        self.action1_Window_Grid.triggered.connect(self.make1WindowGrid)
        self.action2_Windows_Grid.triggered.connect(self.make2WindowsGrid)
        self.action4_Windows_Grid.triggered.connect(self.make4WindowsGrid)

    def resizeEvent(self, event):
        '''What happens when window is resized'''
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height()-5)
        #self.verticalLayoutWidget.setGeometry(0,0,self.width(), self.height())

    def loadDirectory(self):
        '''Loads whole directory based on Parse class as simple as BHP'''
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if directory == None or directory == "":
            return 0

        self.rawVectorData, self.omf_header, self.odt_data, self.stages =  Parser.readFolder(directory)




    def showAnimationSettings(self):
        '''Shows window to change animations settings'''
        self.animationSettingsWindow = AnimationSettings()

    def showPlotSettings(self):

        self.plotSettingsWindow = PlotSettings(list(self.odt_data), self.gridSize)
        self.plotSettingsWindow.setEventHandler(self.plotSettingsReceiver)
        #plotSettingsWindow.show()

    def plotSettingsReceiver(self, value):
        picked_column = value[0][0]

        if self.gridSize > 1:
            data_dict = {
                        'i': 0,
                        'iterations': self.stages,
                        'graph_data': self.odt_data[picked_column].tolist(),
                        'title' : picked_column
                        }
            self.canvasPlot1.shareData(**data_dict)
            self.canvasPlot1.createPlotCanvas()
            #TODO: FIND A WAY TO KILL THIS THREAD EXTERNALLY
            try:
                threading.Thread(target=self.canvasPlot1.loop).start()
            except RuntimeError:
                print("THREADS CLOSED")


    def createNewSubWindow(self):
        '''Creating new subwindow'''
        self.button.append(QPushButton("Add Widget", self))
        self.button[-1].setFixedSize(150, 50)

        self.groupBox.append(QGroupBox("Window " + str(len(self.groupBox)), self))
        #groupBox2 = QGroupBox("Second Window", self)

        self.layout.append(QGridLayout())
        self.groupBox[-1].setLayout(self.layout[-1])
        self.layout[-1].addWidget(self.button[-1])
        #del (self.groupBox[-1])

    def makeGrid(self):
        '''Initialize all subwindows'''
        self.createNewSubWindow()
        self.gridLayout.addWidget(self.groupBox[-1], 0, 0)
        self.createNewSubWindow()
        self.gridLayout.addWidget(self.groupBox[-1], 0, 1)
        self.createNewSubWindow()
        self.gridLayout.addWidget(self.groupBox[-1], 1, 0)
        self.createNewSubWindow()
        self.gridLayout.addWidget(self.groupBox[-1], 1, 1)


    def make1WindowGrid(self):
        '''Splits window in 1 pane.'''
        self.groupBox[-1].hide()
        self.groupBox[-2].hide()
        self.groupBox[-3].hide()

    def make2WindowsGrid(self):
        '''Splits window in 2 panes.'''
        self.groupBox[-1].hide()
        self.groupBox[-2].hide()
        self.groupBox[-3].show()

    def make4WindowsGrid(self):
        '''Splits window in 4 panes.'''
        self.groupBox[-1].show()
        self.groupBox[-2].show()
        self.groupBox[-3].show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
