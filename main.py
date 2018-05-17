from buildVerifier import BuildVerifier
# verify build
# execute makefile
bv = BuildVerifier()

import sys
import threading

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QScreen
from Windows.MainWindowTemplate import Ui_MainWindow

from multiprocessing_parse import MultiprocessingParse

from Windows.ChooseWidget import ChooseWidget
from Windows.PlayerWindow import PlayerWindow
from Windows.Select import Select

from WidgetHandler import WidgetHandler

from PopUp import PopUpWrapper
from Windows.Progress import ProgressBar

from settingsMediator.settingsPrompter import SettingsPrompter
from settingsMediator.settingsLoader import DataObjectHolder

from video_utils.video_composer import Movie

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                    NavigationToolbar2QT as NavigationToolbar)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.doh = DataObjectHolder()
        self.sp = SettingsPrompter(None)

        self.plot_data = ""
        self.setupUi(self)
        self.setWindowTitle("ESE - Early Spins Environment")
        self.setGeometry(10, 10, 1280, 768)  # size of window
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())

        # By default all options are locked and they
        # will be unlocked according to data loaded.
        self._BLOCK_ITERABLES_ = True
        self._BLOCK_STRUCTURES_ = True
        self._BLOCK_PLOT_ITERABLES_ = True

        self.actionAnimation.setDisabled(self._BLOCK_ITERABLES_)

        # keeps all widgets in list of library object that handles Widgets
        self.panes = []
        self.playerWindow = None
        self.makeGrid()  # create grid (4 Widgets) and stores them in arrays
        self.make1WindowGrid()  # shows default 1 widget Window
        self.events()  # create event listeners
        self._LOADED_FLAG_ = False
        self.screenshot_dir = 'Screenshots'

    def events(self):
        """Creates all listeners for Main Window"""
        # FILE SUBMENU
        self.actionLoad_Directory.triggered.connect(self.loadDirectoryWrapper)
        self.actionLoad_File.triggered.connect(self.loadFile)

        # EDIT SUBMENU
        self.actionAnimation.triggered.connect(self.showAnimationSettings)

        self.actionWindow0Delete.triggered.connect(lambda: self.deleteWidget(0))
        self.actionWindow1Delete.triggered.connect(lambda: self.deleteWidget(1))
        self.actionWindow2Delete.triggered.connect(lambda: self.deleteWidget(2))
        self.actionWindow3Delete.triggered.connect(lambda: self.deleteWidget(3))

        # OPTIONS SUBMENU
        self.actionPerformance.triggered.connect(self.setScreenshotFolder)
        self.actionMovie_composer.triggered.connect(self.composeMovie)
        self.actionText_select.triggered.connect(self.selectText)

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

        self.actionAnimation.setDisabled(self._BLOCK_ITERABLES_)

    def resizeEvent(self, event):
        """What happens when window is resized"""
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height() - 25)
        for i in range(4):
            self.panes[i].groupBox.setMinimumWidth(self.width() / 2 - 20)
            if WidgetHandler.visibleCounter > 2:
                self.panes[i].groupBox.setMaximumHeight(self.height() / 2 - 10)
            else:
                self.panes[i].groupBox.setMaximumHeight(self.height() - 10)

    def composeMovie(self):
        x = PopUpWrapper(
            title='Pick directory',
            msg='Pick directory where screenshots are located.' +
                'Current screenshot directory: {}'.format(self.screenshot_dir),
            more='Changed',
            yesMes=None, parent=self)
        self.setScreenshotFolder()
        mv = Movie(self.screenshot_dir)
        mv.create_video()

    def selectText(self):
        self.selectionWindow = Select()

    def promptDirectory(self):
        fileDialog = QtWidgets.QFileDialog()
        directory = str(
            fileDialog.getExistingDirectory(
                self,
                "Select Directory",
                options = QtWidgets.QFileDialog.ShowDirsOnly))
        fileDialog.close()
        return directory

    def setScreenshotFolder(self):
        selected_dir = self.promptDirectory()
        if selected_dir is not None:
            self.screenshot_dir = selected_dir
            x = PopUpWrapper(
                title='Screenshot directory changed',
                msg='Current screenshot directory: {}'.format(self.screenshot_dir),
                more='Changed',
                yesMes=None, parent=self)
        else:
            x = PopUpWrapper(
                title='Screenshot directory has not changed',
                msg='Current screenshot directory: {}'.format(self.screenshot_dir),
                more='Not changed',
                yesMes=None, parent=self)

    def loadFile(self):
        if self._LOADED_FLAG_:
            self.deleteLoadedFiles()
            if BuildVerifier.OS_GLOB_SYS == 'Linux':
                return 0
        self._LOADED_FLAG_ = False
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        fileLoaded = str(fileDialog.getOpenFileName(self, "Select File")[0])

        if fileLoaded is None or fileLoaded == "" or fileLoaded=="  ":
            msg = "Invalid directory: {}. Do you wish to abort?".format(fileLoaded)
            PopUpWrapper("Invalid directory", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, self.refreshScreen, self.loadFile)
            return 0

        if ".odt" in fileLoaded:
            self.doh.passListObject(('plot_data', 'iterations'),
                                        *MultiprocessingParse.readFile(fileLoaded))
            self._BLOCK_ITERABLES_ = False
            self._BLOCK_PLOT_ITERABLES_ = False

        elif ".omf" in fileLoaded or ".ovf" in fileLoaded:
            self.doh.passListObject(('color_vectors', 'file_header'),
                                        *MultiprocessingParse.readFile(fileLoaded))
            self._BLOCK_STRUCTURES_ = False
        else:
            raise ValueError("main.py/loadFile: File format is not supported!")

        self._LOADED_FLAG_ = True
        return 1

    def loadDirectoryWrapper(self):
        """Loads whole directory based on Parse class as simple as BHP"""
        if self._LOADED_FLAG_:
            self.deleteLoadedFiles()
            if BuildVerifier.OS_GLOB_SYS == 'Linux':
                return 0
        self._LOADED_FLAG_ = False
        directory = self.promptDirectory()
        if directory is None or directory == "" or directory=="  ":
            msg = "Invalid directory: {}. Do you wish to abort?".format(directory)
            PopUpWrapper("Invalid directory", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, self.refreshScreen,
                            self.loadDirectoryWrapper, parent=self)
            return 0
        else:
            try:
                t = threading.Thread(target=(lambda: self.loadDirectory(directory)))
                t.start()
                for i in range(WidgetHandler.visibleCounter):
                    self.panes[i].setDisabled(True)

                self.bar = ProgressBar(self)
                self.bar.dumbProgress()


            except ValueError as e:
                print(e.print_stack())
                msg = "Invalid directory: {}. \
                    Error Message {}\nDo you wish to reselect?".format(directory,
                                                                        str(e))
                x = PopUpWrapper("Invalid directory", msg, None,
                                QtWidgets.QMessageBox.Yes,
                                QtWidgets.QMessageBox.No,
                                self.loadDirectoryWrapper,
                                quit,
                                parent=self)
                return None
            except Exception as e:
                print(e)
                return None

            self._BLOCK_ITERABLES_ = False
            self._LOADED_FLAG_ = True
            self._BLOCK_STRUCTURES_ = False
            return 1

    def loadDirectory(self, directory):
        rawVectorData, header, plot_data, stages, trigger_list = \
                            MultiprocessingParse.readFolder(directory)

        self.doh.passListObject(('color_vectors', 'file_header',
                                 'iterations'),
                                rawVectorData, header, stages)
        if plot_data is not None:
            self.doh.setDataObject(plot_data, 'plot_data')
            # successfully loaded plot_data into DOH
            self._BLOCK_PLOT_ITERABLES_ = False
        else:
            self._BLOCK_PLOT_ITERABLES_ = True
        if trigger_list is not None:
            self.doh.setDataObject(trigger_list, 'trigger')
        if self.bar != None:
            # self.menubar.setDisabled(False) TODO
            for i in range(WidgetHandler.visibleCounter):
                self.panes[i].setDisabled(False)
            self.bar.close()

    def deleteLoadedFiles(self):
        # clearing all widgets it's not a problem even if it does not exist
        for i in range(WidgetHandler.visibleCounter):
            self.deleteWidget(i)
        self.doh.removeDataObject('__all__')

        self._LOADED_FLAG_ = False
        self._BLOCK_STRUCTURES_ = True
        self._BLOCK_ITERABLES_ = True
        self._BLOCK_PLOT_ITERABLES_ = True

    def showAnimationSettings(self):
        """Shows window to change animations settings"""
        self.playerWindow = PlayerWindow(self)
        if self.sp.request_parameter_existence(self.doh, 'trigger'):
            self.playerWindow.passTriggerList(\
                            self.doh.retrieveDataObject('trigger'))
        self.refreshIterators()

    def refreshIterators(self, toDelete=None):
        self.properPanesIterators = []
        for i, pane in enumerate(self.panes):
            if pane.isVisible() and pane.widget:
                if i == toDelete:
                    continue
                self.properPanesIterators.insert(i, pane.widget.set_i)

        self.playerWindow.setIterators(self.properPanesIterators)

    def showChooseWidgetSettings(self, number):
        if self.playerWindow != None:
            #animation is running and this is may be not first window
            if self.playerWindow.worker.running:
                PopUpWrapper("Alert",
                             "You may loose calculation!" +
                             " If you proceed animation will be restarted!", \
                             None,
                             QtWidgets.QMessageBox.Yes, \
                             QtWidgets.QMessageBox.No, \
                             None, \
                             self.refreshScreen())

                self.playerWindow.forceWorkerReset()
                self.playerWindow.closeMe()

        """Spawns Window for choosing widget for this pane"""
        if not self._LOADED_FLAG_:
            # spawn directory picker again
            self.loadDirectoryWrapper()
        else:
            self.new = ChooseWidget(number, \
                                    blockStructures = self._BLOCK_STRUCTURES_, \
                                    blockIterables = self._BLOCK_ITERABLES_,
                                    blockPlotIterables = self._BLOCK_PLOT_ITERABLES_,
                                    parent = self)
            self.new.setHandler(self.choosingWidgetReceiver)

    def choosingWidgetReceiver(self, value):
        """Data receiver for choosingWidget action"""
        self.panes[value[0]].clearBox()
        # value[0] stores widget number
        # value[1] stores widget name
        self.sp.swap_settings_type(value[1])
        # deduce object type based on passed string
        self.window = self.sp.\
            get_settings_window_constructor_from_file(self.doh)
        # all widgets get generalReceiver handler
        self.window.setEventHandler(self.generalReceiver)

        self.current_pane, self.current_widget_alias = value
        self.refreshScreen()

    def generalReceiver(self, options):
        """
        this allows to receive general type option structure that is passed
        on to the DataObjectHolder object that sends it to the right final object
        """
        if options is None:
            # delete widget
            self.deleteWidget(self.current_pane, null_delete=True)
            self.refreshScreen()

            return
        # fix that later in settings where it can be changed or not
        geom = (self.panes[self.current_pane].groupBox.width(),
                self.panes[self.current_pane].groupBox.height())

        self.doh.setDataObject(geom, 'geom')
        self.doh.setDataObject(0, 'current_state')
        self.doh.setDataObject(options, 'options')
        self.doh.setDataObject(self.screenshot_dir, 'screenshot_dir')

        self.panes[self.current_pane].addWidget(\
                self.sp.build_chain(self.current_widget_alias, self.doh, self))

        self.constructWidgetToolbar(self.panes[self.current_pane])
        # that fixes the problem of having not all slots filled in groupBox
        if self.playerWindow != None:
            self.refreshIterators()
        self.propagate_resize()
        self.refreshScreen()

    def constructWidgetToolbar(self, pane):
        """
        Construct toolbar for a given pane
        Function assumes object was created successfully
        """
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar = self.buildToolbar(pane.widget)
        if self.toolbar is not None:
            pane.layout.setMenuBar(self.toolbar)
            pane.layout.setContentsMargins(0,0,0,0)

    def buildToolbar(self, widget):
        """
        Build toolbar from parameters in doh - toolbar section
        """
        toolbar = QtWidgets.QToolBar()
        if 'toolbar' in self.doh.contains_lookup:
            toolbar_general = self.doh.retrieveDataObject('toolbar')
        else:
            return None
        if type(toolbar_general) == list:
            # toolbar needs to be defined if this parameter is a list
            for toolbar_option in toolbar_general:
                toolbar.addAction(toolbar_option[0],
                                            getattr(widget, toolbar_option[1]))
            return toolbar
        else:
            if toolbar_general == 'NavigationToolbar':
                toolbar = NavigationToolbar(widget.canvas, widget,
                                                                coordinates=True)
                widget.updateCanvasSettings()
            else:
                return None

    def deleteWidget(self, number, null_delete=False):
        if self.playerWindow:
            PopUpWrapper("Alert",
                "You may loose calculation!", \
                "If you proceed animation will be restarted and widget \
                will be deleted!", \
                QtWidgets.QMessageBox.Yes, \
                QtWidgets.QMessageBox.No, \
                None, \
                self.refreshScreen(), parent=self)

            self.playerWindow.forceWorkerReset()
            self.playerWindow.closeMe()
            self.playerWindow.worker.clearWidgetIterators()

        """
        null delete explanation:
        for some unknown reason if clearBox() is called on the pane
        that has no widget that causes a major bug
        Therefore if cancel was pressed and no widget was created - hence
        null_delete, then do not call
        """
        if not null_delete: self.panes[number].clearBox()
        self.panes[number].setUpDefaultBox()
        self.panes[number].button.clicked.connect(\
            lambda: self.showChooseWidgetSettings(number))
        self.refreshScreen()

    def propagate_resize(self):
        for i in range(4):
            if self.panes[i] is not None:
                try:
                    geom = (self.panes[i].groupBox.width(),
                            self.panes[i].groupBox.height())
                    self.panes[i].widget.on_resize_geometry_reset(geom)
                except (AttributeError, RuntimeError) as ae:
                    pass
                    # allow this, should implement this function but pass anyway
        self.refreshScreen()

    def makeGrid(self):
        """Initialize all subwindows"""
        for i in range(4):
            self.panes.append(WidgetHandler(i, self))

        self.gridLayout.addWidget(self.panes[0].groupBox, 0, 0)
        self.gridLayout.addWidget(self.panes[1].groupBox, 0, 1)
        self.gridLayout.addWidget(self.panes[2].groupBox, 1, 0)
        self.gridLayout.addWidget(self.panes[3].groupBox, 1, 1)

    def make1WindowGrid(self):
        """Splits window in 1 pane."""
        self.panes[1].hide()
        self.panes[2].hide()
        self.panes[3].hide()
        WidgetHandler.visibleCounter = 1

        self.propagate_resize()
        self.refreshScreen()

        self.actionWindow1Delete.setDisabled(True)
        self.actionWindow2Delete.setDisabled(True)
        self.actionWindow3Delete.setDisabled(True)

    def make2WindowsGrid(self):
        """Splits window in 2 panes."""
        self.panes[1].show()
        self.panes[2].hide()
        self.panes[3].hide()
        WidgetHandler.visibleCounter = 2

        self.propagate_resize()
        self.refreshScreen()

        self.actionWindow1Delete.setDisabled(False)
        self.actionWindow2Delete.setDisabled(True)
        self.actionWindow3Delete.setDisabled(True)

    def make4WindowsGrid(self):
        """Splits window in 4 panes."""
        self.panes[1].show()
        self.panes[2].show()
        self.panes[3].show()
        WidgetHandler.visibleCounter = 4

        self.propagate_resize()
        self.refreshScreen()
        self.actionWindow1Delete.setDisabled(False)
        self.actionWindow2Delete.setDisabled(False)
        self.actionWindow3Delete.setDisabled(False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
