import sys
import math

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from spin_gl import GLWidget
from MainWindowTemplate import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow, QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = GLWidget()

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()

        self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
        self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
        self.ySlider.valueChanged.connect(self.glWidget.setYRotation)
        self.glWidget.yRotationChanged.connect(self.ySlider.setValue)
        self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
        self.glWidget.zRotationChanged.connect(self.zSlider.setValue)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        self.setLayout(mainLayout)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        self.setWindowTitle("Hello GL")
        self.make1WindowGrid()
        #self.resizeEvent()

        self.addButtons() #temp function
        self.events()
        self.make1WindowGrid()
        #self.resizeEvent()

        self.addButtons() #temp function
        self.events()

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider

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


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
