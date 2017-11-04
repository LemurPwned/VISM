import sys

from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import (QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from MainWindowTemplate import Ui_MainWindow

#from mainWindow import GLWidget, Helper
from structureDrawer import DrawData
from plotCanvas import PlotCanvas
from animationSettings import AnimationSettings

class MainWindow(QMainWindow, Ui_MainWindow, QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMouseTracking(True)
        self.glWidget = DrawData()
        self.setupUi(self)
        self.setWindowTitle("ESE - Early Spins Enviroment")
        self.setGeometry(10,10,1280, 768)
        self.setupGL()
        self.gridSize = 1

        self.make1WindowGrid()
        #self.resizeEvent()

        self.addButtons() #temp function
        self.events()

    def setupGL(self):
        self.openGLWidget.initializeGL()

        self.canvas = DrawData()
        self.canvas.initialSettings()
        self.openGLWidget.paintGL = self.canvas.paintGL

        timer = QTimer(self)
        timer.timeout.connect(self.openGLWidget.update)
        timer.start(0)

    def events(self):
        #FILE SUBMENU
        #self.actionLoad_File.clicked.connect()
        #self.actionLoad_Directory.clicked.connect()

        #EDIT SUBMENU
        #self.actionPlot.clicked.connect()
        self.actionAnimation.triggered.connect(self.showAnimationSettings)

        #VIEW SUBMENU
        self.action1_Window_Grid.triggered.connect(self.make1WindowGrid)
        self.action2_Windows_Grid.triggered.connect(self.make2WindowsGrid)
        self.action4_Windows_Grid.triggered.connect(self.make4WindowsGrid)

    def resizeEvent(self, event):
        print(event)
        self.verticalLayoutWidget.setGeometry(0, 0, self.width()-5, self.height()-5)
        self.progressBar.setGeometry(5, (self.height()-35), (self.width()-10), self.height()-25)
        self.statusBar_label.setGeometry(5, self.height()-45, self.width()-10, self.height()-35)

        if self.gridSize == 1:
            self.make1WindowGrid()
        elif self.gridSize == 2:
            self.make2WindowsGrid()
        elif self.gridSize == 4:
            self.make4WindowsGrid()

    def showAnimationSettings(self):
        self.animationSettingsWindow = AnimationSettings()

    def make1WindowGrid(self):
        self.gridSize = 1
        try:
            self.canvasPlot1.hide()
        except:
            pass

        try:
            self.canvasPlot2.hide()
        except:
            pass

        try:
            self.canvasPlot3.hide()
        except:
            pass

        self.openGLWidget.setGeometry(0, 0, self.width()-100, self.height()-100)


    def make2WindowsGrid(self):
        self.gridSize = 2
        middlePos = (self.width())/2
        self.openGLWidget.setGeometry(0,0, middlePos-5, self.height()-20)

        #create matplotlib window
        try:
            self.canvasPlot1.show()
        except:
            self.canvasPlot1 = PlotCanvas(self.gridSize, self, width=5, height=4)
        self.canvasPlot1.setGeometry(middlePos+5, 0, self.width()/2-5, self.height()-50)
        #self.canvasPlot1.resize((, self.height()-25)
        self.canvasPlot1.show()

        try:
            self.canvasPlot2.hide()
            self.canvasPlot3.hide()
        except:
            pass

    def make4WindowsGrid(self):
        self.gridSize = 4
        middleWidthPos = (self.width())/2
        middleHeightPos = (self.height())/2

        self.openGLWidget.setGeometry(0, 0, middleWidthPos - 5, middleHeightPos - 5)

        #create matplotlib window right top corner
        try:
            self.canvasPlot1.show()
        except:
            self.canvasPlot1 = PlotCanvas(self.gridSize, self, width=5, height=4)
        self.canvasPlot1.setGeometry(middleWidthPos + 5, 0, (self.width()/2 - 5), (self.height()/2)-5)
        self.canvasPlot1.show()

        #create matplotlib window left bottom corner
        try:
            self.canvasPlot2.show()
        except:
            self.canvasPlot2 = PlotCanvas(self.gridSize, self, width=5, height=4)
        self.canvasPlot2.setGeometry(0, middleHeightPos + 5, (self.width()/2-5), (self.height()/2)-50)
        self.canvasPlot2.show()

        #create matplotlib window left bottom corner
        try:
            self.canvasPlot3.show()
        except:
            self.canvasPlot3 = PlotCanvas(self.gridSize, self, width=5, height=4)
        self.canvasPlot3.setGeometry(middleWidthPos + 5, middleHeightPos + 5, (self.width()/2-5), (self.height()/2)-50)
        self.canvasPlot3.show()

    def addButtons(self):
        '''temp function unless mouse operation disabled'''
        camLeft = QPushButton("Camera Left", self)
        camRight = QPushButton("Camera Right", self)
        camLeft.move(1000, 200)
        camRight.move(1000, 250)
        camLeft.clicked.connect(self.canvas.cameraLeft)
        camRight.clicked.connect(self.canvas.cameraRight)
        #self.openGLWidget.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
