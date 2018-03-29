import sys
from buildVerifier import BuildVerifier

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
from Windows.PerfOptions import PerfOptions
from Windows.vectorSettings import vectorSettings

from WidgetHandler import WidgetHandler

from Widgets.Canvas2Dupgraded import Canvas2Dupgraded
from PopUp import PopUpWrapper
from ColorPolicy import ColorPolicy

from settingsMediator.settingsPrompter import SettingsPrompter
from settingsMediator.settingsLoader import DataObjectHolder

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.doh = DataObjectHolder()

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
        self.defaultOptionSet = ['Standard', 5, 3, 1]
        self.defaultVectorSet = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self._LOADED_FLAG_ = False

    def events(self):
        """Creates all listeners for Main Window"""
        # FILE SUBMENU
        self.actionLoad_Directory.triggered.connect(self.loadDirectory)

        # EDIT SUBMENU
        self.actionAnimation.triggered.connect(self.showAnimationSettings)

        # VIEW SUBMENU
        self.action1_Window_Grid.triggered.connect(self.make1WindowGrid)
        self.action2_Windows_Grid.triggered.connect(self.make2WindowsGrid)
        self.action4_Windows_Grid.triggered.connect(self.make4WindowsGrid)

        # OPTIONS SUBMENU

        # VECTORS SUBMENU

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
            msg = "Invalid directory: {}. Do you wish to abort?".format(directory)
            self._LOADED_FLAG_ = False
            PopUpWrapper("Invalid directory", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, quit, None)
            return 0
        else:
            try:
                x = PopUpWrapper("Loading", "Data is currently loading",
                        more="Please Wait...")
                self.doh.passListObject(('color_vectors', 'omf_header',
                                        'odt_data', 'iterations'),
                                        *MultiprocessingParse.readFolder(directory))
                print(self.doh.contains_lookup)
                x.close()
            except ValueError as e:
                msg = "Invalid directory: {}. \
                    Error Message {}\nDo you wish to reselect?".format(directory,
                                                                        str(e))
                x = PopUpWrapper("Invalid directory", msg, None,
                                QtWidgets.QMessageBox.Yes,
                                QtWidgets.QMessageBox.No,
                                self.loadDirectory, quit)
            finally:
                self._LOADED_FLAG_ = True
            return 1

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
            if type(pane.widget) is Canvas or \
                    type(pane.widget) is Canvas2Dupgraded \
                    and pane.isVisible():
                counter = counter + 1

        self.odt_data = self.doh.retrieveDataObject('odt_data')
        self.plotSettingsWindow = PlotSettings(list(self.odt_data), counter)
        self.plotSettingsWindow.setEventHandler(self.plotSettingsReceiver)


    def plotSettingsReceiver(self, value):
        # [string whatToPlot, synchronizedPlot, instantPlot]
        if not value:
            msg = "There is no data to display on the plot. Continue?"
            PopUpWrapper("No data", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, None, quit)
            return

        temp_val = 0  # fast_fix rethink it later

        for i, pane in enumerate(self.panes):
            if not pane.isVisible():
                continue
            data_dict = {}
            param_dict = {}
            if type(pane.widget) is CanvasLayer:
                data_dict = self.compose_dict('2dLayer')
            # separated both classes, type is uniqe now
            if type(pane.widget) is Canvas \
                    or type(pane.widget) is Canvas2Dupgraded:
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
                pane.widget.createPlotCanvas()

        self.refreshScreen()

    def showChooseWidgetSettings(self, number):
        """Spawns Window for choosing widget for this pane"""
        if not self._LOADED_FLAG_:
            # spawn directory picker again
            self.loadDirectory()
        else:
            self.new = ChooseWidget(number)
            self.new.setHandler(self.choosingWidgetReceiver)

    def choosingWidgetReceiver(self, value):
        """Data receiver for choosingWidget action"""

        self.panes[value[0]].clearBox()

        self.sp = SettingsPrompter(value[1].split('_')[1])
        self.window = self.sp.prompt_settings_window(self.doh)
        self.window.setEventHandler(self.plotSettingsReceiver)
        self.refreshScreen()

    def createNewSubWindow(self):
        """Helper function creates layout and button for widget selection"""
        self.panes.append(WidgetHandler())
        self.panes[-1].button = QtWidgets.QPushButton("Add Widget", self)
        self.panes[-1].groupBox = QtWidgets.QGroupBox("Window " + \
                                                      str(len(self.panes)), self)
        self.panes[-1].layout = QtWidgets.QGridLayout()

    def optionsParser(self):
        try:
            selectedOptionsSet = self.optionsMenu.getOptions()
        except AttributeError as ae:
            selectedOptionsSet = self.defaultOptionSet
        return selectedOptionsSet

    def vectorParser(self):
        try:
            selectedVectorSet = self.vectorMenu.getOptions()
        except AttributeError as ae:
            selectedVectorSet = self.defaultVectorSet
        return selectedVectorSet

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

if __name__ == "__main__":
    # verify build
    # execute makefile
    bv = BuildVerifier()

    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
