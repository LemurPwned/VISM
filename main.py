import sys

from PyQt5.QtCore import QTimer, QPoint, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QGroupBox, QGridLayout, QLabel
from PyQt5.QtWidgets import (QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)
from Windows.MainWindowTemplate import Ui_MainWindow


from Canvas import Canvas
from Canvas3D import Canvas3D

from Parser import Parser
from Windows.ChooseWidget import ChooseWidget
from Windows.animationSettings import AnimationSettings
from spin_gl import GLWidget
from Windows.PlotSettings import PlotSettings
import threading

class MainWindow(QMainWindow, Ui_MainWindow, QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.odt_data = ""
        self.setupUi(self)
        self.setWindowTitle("ESE - Early Spins Enviroment")
        self.setGeometry(10,10,1280, 768) #size of window
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())

        self.groupBox = [] #we store here groupBoxes for all widgets one Widget in one groupBox
        self.button = [] #we need to store these globaly to set event listeners
        self.gridSize = 0 # how many windows visible
        self.makeGrid() #create grid (4 Widgets) and stores them in arrays
        self.make1WindowGrid() #shows default 1 widget Window
        self.events() #create event listeners

    def events(self):
        '''Creates all listeners for Main Window'''
        #FILE SUBMENU
        self.actionLoad_Directory.triggered.connect(self.loadDirectory)

        #EDIT SUBMENU
        self.actionPlot.triggered.connect(self.showPlotSettings)
        self.actionAnimation.triggered.connect(self.showAnimationSettings)

        #VIEW SUBMENU
        self.action1_Window_Grid.triggered.connect(self.make1WindowGrid)
        self.action2_Windows_Grid.triggered.connect(self.make2WindowsGrid)
        self.action4_Windows_Grid.triggered.connect(self.make4WindowsGrid)

        #GRID BUTTONS
        #lambda required to pass parameter - which button was pressed
        self.button[0].clicked.connect(lambda: self.showChooseWidgetSettings(0))
        self.button[1].clicked.connect(lambda: self.showChooseWidgetSettings(1))
        self.button[2].clicked.connect(lambda: self.showChooseWidgetSettings(2))
        self.button[3].clicked.connect(lambda: self.showChooseWidgetSettings(3))

    def refreshScreen(self):
        '''weird stuff is happening when u want to update window u need to resize i think this is a bug'''
        self.resize(self.width()-1, self.height())
        self.resize(self.width()+1, self.height())

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
        """Spawns window for plot settings"""
        self.plotSettingsWindow = PlotSettings(list(self.odt_data), self.gridSize)
        self.plotSettingsWindow.setEventHandler(self.plotSettingsReceiver)
        #plotSettingsWindow.show()

    def plotSettingsReceiver(self, value):
        """Plot data receiver"""
        #value = [[string typeOfPlot, bool synchronizedPlot, bool instaPlot], [], [], []] next sublists are for other plots format is the same
        if value == []: #if no plot was enabled or no data selected it returns empty list
            return
        picked_column = value[0][0]
        start  = 0
        if len(self.groupBox) > 1:
            if value[0][1] == False: #instaPlot
                start = self.stages

            data_dict = {
                    'i': start,
                    'iterations': self.stages,
                    'graph_data': self.odt_data[picked_column].tolist(),
                    'title' : picked_column
                    }

            self.canvasPlot.shareData(**data_dict)
            self.canvasPlot.createPlotCanvas()
            #TODO: FIND A WAY TO KILL THIS THREAD EXTERNALLY
            try:
                threading.Thread(target=self.canvasPlot.loop).start()
            except RuntimeError:
                print("THREADS CLOSED")

    def showChooseWidgetSettings(self, number):
        '''Spawns Window for choosing widget for this pane'''
        self.new = ChooseWidget(number)
        self.new.setHandler(self.choosingWidgetReceiver)

    def choosingWidgetReceiver(self, value):
        '''Data receiver for choosingWidget action'''
        #value = [number_of_widget, what_to_add_name];
        self.groupBox[value[0]].children()[1].deleteLater()
        self.groupBox[value[0]].children()[1].setParent(None)
        if value[1] == "OpenGL":
            self.openGLWidget = GLWidget()
            self.groupBox[value[0]].children()[0].addWidget( self.openGLWidget)

        elif value[1] == "2dPlot":
            self.canvasPlot = Canvas(self)
            self.groupBox[value[0]].children()[0].addWidget(self.canvasPlot)
            self.canvasPlot.show()

        self.refreshScreen()

    def createNewSubWindow(self):
        '''Helper function creates layout and button for widget selection'''
        self.button.append(QPushButton("Add Widget", self))
        self.button[-1].setFixedSize(150, 50)

        self.groupBox.append(QGroupBox("Window " + str(len(self.groupBox)), self))

        layout = (QGridLayout())
        self.groupBox[-1].setLayout(layout)
        layout.addWidget(self.button[-1])

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
        self.gridSize = 1
        self.groupBox[-1].hide()
        self.groupBox[-2].hide()
        self.groupBox[-3].hide()
        #self.refreshScreen()

    def make2WindowsGrid(self):
        '''Splits window in 2 panes.'''
        self.gridSize = 2
        self.groupBox[-1].hide()
        self.groupBox[-2].hide()
        self.groupBox[-3].show()
        #self.refreshScreen()

    def make4WindowsGrid(self):
        '''Splits window in 4 panes.'''
        self.gridSize = 4
        self.groupBox[-1].show()
        self.groupBox[-2].show()
        self.groupBox[-3].show()
        #self.refreshScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
