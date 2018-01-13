import sys
from PyQt5 import QtWidgets
from Windows.MainWindowTemplate import Ui_MainWindow

from Canvas import Canvas
from CanvasLayer import CanvasLayer
from multiprocessing_parse import MultiprocessingParse
from openGLContext import OpenGLContext
from arrowGLContex import ArrowGLContext

from Windows.ChooseWidget import ChooseWidget
from Windows.PlotSettings import PlotSettings
from Windows.PlayerWindow import PlayerWindow
from WidgetHandler import WidgetHandler


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.odt_data = ""
        self.setupUi(self)
        self.setWindowTitle("ESE - Early Spins Environment")
        self.setGeometry(10, 10, 1280, 768)  # size of window
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())

        # keeps all widgets in list of library object that handles Widgets
        self.panes = []
        self.makeGrid()  # create grid (4 Widgets) and stores them in arrays
        self.make1WindowGrid()  # shows default 1 widget Window
        self.events()  # create event listeners

        self._LOADED_FLAG_ = False

    def events(self):
        """Creates all listeners for Main Window"""
        # FILE SUBMENU
        self.actionLoad_Directory.triggered.connect(self.loadDirectory)

        # EDIT SUBMENU
        self.actionPlot.triggered.connect(self.showPlotSettings)
        self.actionAnimation.triggered.connect(self.showAnimationSettings)

        # VIEW SUBMENU
        self.action1_Window_Grid.triggered.connect(self.make1WindowGrid)
        self.action2_Windows_Grid.triggered.connect(self.make2WindowsGrid)
        self.action4_Windows_Grid.triggered.connect(self.make4WindowsGrid)

        # GRID BUTTONS
        # lambda required to pass parameter - which button was pressed
        self.panes[0].button.clicked.connect(lambda: self.showChooseWidgetSettings(0))
        self.panes[1].button.clicked.connect(lambda: self.showChooseWidgetSettings(1))
        self.panes[2].button.clicked.connect(lambda: self.showChooseWidgetSettings(2))
        self.panes[3].button.clicked.connect(lambda: self.showChooseWidgetSettings(3))

    def refreshScreen(self):
        """weird stuff is happening when u want to update window u need to
        resize i think this is a bug"""
        self.resize(self.width() - 1, self.height())
        self.resize(self.width() + 1, self.height())

    def resizeEvent(self, event):
        """What happens when window is resized"""
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height() - 25)
        self.panes[0].groupBox.setMinimumWidth(self.width() / 2 - 20)
        self.panes[1].groupBox.setMinimumWidth(self.width() / 2 - 20)
        self.panes[2].groupBox.setMinimumWidth(self.width() / 2 - 20)
        self.panes[3].groupBox.setMinimumWidth(self.width() / 2 - 20)

    def loadDirectory(self):
        """Loads whole directory based on Parse class as simple as BHP"""
        directory = str(QtWidgets.QFileDialog.getExistingDirectory(self,
                                                            "Select Directory"))

        if directory is None or directory == "":
            return 0

        # should be thrown into separate thread by pyqt
        self.rawVectorData, self.omf_header, self.odt_data, \
        self.stages = MultiprocessingParse.readFolder(directory)
        self._LOADED_FLAG_ = True

    def showAnimationSettings(self):
        """Shows window to change animations settings"""
        self.playerWindow = PlayerWindow(self)
        self.properPanesIterators = []
        for pane in self.panes:
            if pane.isVisible() and pane.widget:
                self.properPanesIterators.append(pane.widget.set_i)

        self.playerWindow.setIterators(self.properPanesIterators)

    def showPlotSettings(self):
        """Spawns window for plot settings"""
        counter = 0
        # to know how many plots are there to show correct plotMenu
        for _, pane in enumerate(self.panes):
            if type(pane.widget) is Canvas:
                counter = counter + 1

        self.plotSettingsWindow = PlotSettings(list(self.odt_data), counter)
        self.plotSettingsWindow.setEventHandler(self.plotSettingsReceiver)

    def plotSettingsReceiver(self, value):
        # [string whatToPlot, synchronizedPlot, instantPlot]
        if not value:
            print("No data to plot")
            return

        temp_val = 0  # fast_fix rethink it later

        for i, pane in enumerate(self.panes):
            if not pane.isVisible():
                continue
            data_dict = {}
            param_dict = {}
            if type(pane.widget) is CanvasLayer:
                data_dict = self.compose_dict('2dLayer')
            # separated both classes, type is unique now
            if type(pane.widget) is Canvas:
                picked_column = value[temp_val][0]
                param_dict = {
                    'color': value[temp_val][3],
                    'line_style': value[temp_val][5],
                    'marker': value[temp_val][4],
                    'marker_size': value[temp_val][6],
                    'marker_color': value[temp_val][3]
                }
                # check if we want synchronizedPlot
                counter = 0
                if value[temp_val][2]:
                    counter = self.stages
                data_dict = self.compose_dict('2dPlot', current_state=counter,
                                              column=picked_column)
                temp_val = temp_val + 1

            if data_dict != {}:
                pane.widget.shareData(**data_dict)
                # pane.widget.setPlotParameters(param_dict)
                pane.widget.createPlotCanvas()

        self.refreshScreen()

    def showChooseWidgetSettings(self, number):
        """Spawns Window for choosing widget for this pane"""
        self.new = ChooseWidget(number)
        self.new.setHandler(self.choosingWidgetReceiver)

    def choosingWidgetReceiver(self, value):
        """Data receiver for choosingWidget action"""
        self.panes[value[0]].clearBox()
        if value[1] == 'OpenGLCubes':
            type_value = "OpenGL"
            # CAN't be here!!!!
            if not self._LOADED_FLAG_:
                msg = "Data has not been uploaded before accessing GL"
                raise ValueError(msg)
            gl_dict = self.compose_dict(type_value)
            self.panes[value[0]].addWidget(OpenGLContext(data_dict=gl_dict))
            self.refreshScreen()
        elif value[1] == 'OpenGLArrows':
            # CAN't be here!!!!
            type_value = "OpenGL"
            if not self._LOADED_FLAG_:
                msg = "Data has not been uploaded before accessing GL"
                raise ValueError(msg)
            gl_dict = self.compose_dict(type_value)
            self.panes[value[0]].addWidget(ArrowGLContext(data_dict=gl_dict))
            self.refreshScreen()
        elif value[1] == '2dPlot':
            self.panes[value[0]].addWidget(Canvas())
            self.refreshScreen()

        elif value[1] == '2dLayer':
            layer_dict = self.compose_dict(value[1])
            self.panes[value[0]].addWidget(CanvasLayer())
            self.refreshScreen()

    def createNewSubWindow(self):
        """Helper function creates layout and button for widget selection"""
        self.panes.append(WidgetHandler())
        self.panes[-1].button = QtWidgets.QPushButton("Add Widget", self)
        self.panes[-1].groupBox = QtWidgets.QGroupBox("Window " + \
                                                      str(len(self.panes)), self)
        self.panes[-1].layout = QtWidgets.QGridLayout()

    def makeGrid(self):
        """Initialize all subwindows"""
        for i in range(4):
            self.createNewSubWindow()
        self.gridLayout.addWidget(self.panes[0].groupBox, 0, 0)
        self.gridLayout.addWidget(self.panes[1].groupBox, 0, 1)
        self.gridLayout.addWidget(self.panes[2].groupBox, 1, 0)
        self.gridLayout.addWidget(self.panes[3].groupBox, 1, 1)

    def make1WindowGrid(self):
        """Splits window in 1 pane."""
        self.panes[1].hide()
        self.panes[2].hide()
        self.panes[3].hide()

    def make2WindowsGrid(self):
        """Splits window in 2 panes."""
        self.panes[1].show()
        self.panes[2].hide()
        self.panes[3].hide()

    def make4WindowsGrid(self):
        """Splits window in 4 panes."""
        self.panes[1].show()
        self.panes[2].show()
        self.panes[3].show()

    def compose_dict(self, widgetType, column=None, current_state=0):
        if widgetType == 'OpenGL':
            data_dict = {
                'omf_header': self.omf_header,
                'color_list': self.rawVectorData,
                'iterations': self.stages,
                'i': current_state
            }
        elif widgetType == '2dPlot':
            data_dict = {
                'i': current_state,
                'iterations': self.stages,
                'graph_data': self.odt_data[column].tolist(),
                'title': column
            }
        elif widgetType == '2dLayer':
            data_dict = {
                'omf_header': self.omf_header,
                'multiple_data': self.rawVectorData,
                'iterations': self.stages,
                'current_layer': 0,
                'title': '3dgraph',
                'i': current_state
            }
        else:
            msg = "Invalid argument {}".format(widgetType)
            raise ValueError(msg)
        return data_dict


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
