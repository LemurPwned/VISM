import sys

from PyQt5.QtCore import QTimer, QPoint, pyqtSlot
from PyQt5 import QtWidgets
from Windows.MainWindowTemplate import Ui_MainWindow


from Canvas import Canvas
from CanvasLayer import CanvasLayer
from Parser import Parser
from Windows.ChooseWidget import ChooseWidget
from Windows.animationSettings import AnimationSettings
from Windows.PlotSettings import PlotSettings
from WidgetHandler import WidgetHandler
from spin_gl import GLWidget

import threading

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.odt_data = ""
        self.setupUi(self)
        self.setWindowTitle("ESE - Early Spins Enviroment")
        self.setGeometry(10,10,1280, 768) #size of window
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())

        # keeps all widgets in list of library object that handles Widgets
        self.panes = []
        self.makeGrid() #create grid (4 Widgets) and stores them in arrays
        self.make1WindowGrid() #shows default 1 widget Window
        self.events() #create event listeners
        self.threads = []

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
        self.panes[0].button.clicked.connect(lambda:self.showChooseWidgetSettings(0))
        self.panes[1].button.clicked.connect(lambda:self.showChooseWidgetSettings(1))
        self.panes[2].button.clicked.connect(lambda:self.showChooseWidgetSettings(2))
        self.panes[3].button.clicked.connect(lambda:self.showChooseWidgetSettings(3))

    def refreshScreen(self):
        '''weird stuff is happening when u want to update window u need to
        resize i think this is a bug'''
        self.resize(self.width()-1, self.height())
        self.resize(self.width()+1, self.height())

    def resizeEvent(self, event):
        '''What happens when window is resized'''
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height()-25)

    def loadDirectory(self):
        '''Loads whole directory based on Parse class as simple as BHP'''
        directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, \
                        "Select Directory"))

        if directory == None or directory == "":
            return 0

        #should be thrown into separate thread by pyqt
        self.rawVectorData, self.omf_header, self.odt_data, \
                        self.stages =  Parser.readFolder(directory)

    def showAnimationSettings(self):
        '''Shows window to change animations settings'''
        self.animationSettingsWindow = AnimationSettings()

    def showPlotSettings(self):
        """Spawns window for plot settings"""
        counter = 0
        #to know how many plots are there to show correct plotMenu
        for _, pane in enumerate(self.panes):
            if type(pane.widget) is Canvas:
                counter = counter + 1


        self.plotSettingsWindow = PlotSettings(list(self.odt_data), counter)
        self.plotSettingsWindow.setEventHandler(self.plotSettingsReceiver)

    def plotSettingsReceiver(self, value):
        #[string whatToPlot, synchronizedPlot, instantPlot]
        if value == []:
            print("No data to plot")
            return

        temp_val = 0 #fast_fix rethink it later

        for i, pane in enumerate(self.panes):
            if not pane.isVisible():
                continue
            data_dict = {}
            #change order, because CanvasLayer is of type Canvas
            if type(pane.widget) is CanvasLayer:
                data_dict = {
                            'omf_header':  self.omf_header,
                            'multiple_data': self.rawVectorData,
                            'iterations': self.stages,
                            'current_layer': 0,
                            'title': '3dgraph',
                            'i': 0
                            }

            if type(pane.widget) is Canvas:
                picked_column = value[temp_val][0]
                #check if we want synchronizedPlot
                counter = 0
                if value[temp_val][2]:
                    counter = self.stages
                data_dict = {
                            'i': counter,
                            'iterations': self.stages,
                            'graph_data': self.odt_data[picked_column].tolist(),
                            'title' : picked_column
                            }
                temp_val = temp_val+1

            if data_dict != {}:
                pane.widget.shareData(**data_dict)
                pane.widget.createPlotCanvas()
                try:
                    x = threading.Thread(target=\
                                pane.widget.loop, daemon=True)
                    x.start()
                except (KeyboardInterrupt, SystemExit):
                    msg = "Ending thread due to system sigkill"
                    print(msg)
                    sys.exit()

    def showChooseWidgetSettings(self, number):
        '''Spawns Window for choosing widget for this pane'''
        self.new = ChooseWidget(number)
        self.new.setHandler(self.choosingWidgetReceiver)

    def choosingWidgetReceiver(self, value):
        '''Data receiver for choosingWidget action'''
        self.panes[value[0]].clearBox()

        if value[1] == "OpenGL":
            self.panes[value[0]].addWidget(GLWidget())
            self.refreshScreen()
            print(self.panes[value[0]].widget)

        if value[1] == '2dPlot':
            self.panes[value[0]].addWidget(Canvas())
            self.refreshScreen()

        elif value[1] == '2dLayer':
            self.panes[value[0]].addWidget(CanvasLayer())
            self.refreshScreen()

    def createNewSubWindow(self):
        '''Helper function creates layout and button for widget selection'''
        self.panes.append(WidgetHandler())
        self.panes[-1].button = QtWidgets.QPushButton("Add Widget", self)
        self.panes[-1].groupBox = QtWidgets.QGroupBox("Window " + \
                                                    str(len(self.panes)), self)
        self.panes[-1].layout = QtWidgets.QGridLayout()

    def makeGrid(self):
        '''Initialize all subwindows'''
        for i in range(4):
            self.createNewSubWindow()
        self.gridLayout.addWidget(self.panes[0].groupBox, 0, 0)
        self.gridLayout.addWidget(self.panes[1].groupBox, 0, 1)
        self.gridLayout.addWidget(self.panes[2].groupBox, 1, 0)
        self.gridLayout.addWidget(self.panes[3].groupBox, 1, 1)

    def make1WindowGrid(self):
        '''Splits window in 1 pane.'''
        self.panes[1].hide()
        self.panes[2].hide()
        self.panes[3].hide()

    def make2WindowsGrid(self):
        '''Splits window in 2 panes.'''
        self.panes[1].show()
        self.panes[2].hide()
        self.panes[3].hide()

    def make4WindowsGrid(self):
        '''Splits window in 4 panes.'''
        self.panes[1].show()
        self.panes[2].show()
        self.panes[3].show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
