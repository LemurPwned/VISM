from util_tools.buildVerifier import BuildVerifier
# verify build
# execute makefile
if BuildVerifier.OS_GLOB_SYS == "Windows":
    pass
else:
    bv = BuildVerifier()
    bv.cython_builds()

import sys
import threading

from processing.workerthreads import *

from PyQt5 import QtWidgets, QtCore

# template imports
from Windows.Templates.MainWindowTemplate import Ui_MainWindow
from Windows.ChooseWidget import ChooseWidget
from Windows.PlayerWindow import PlayerWindow

from processing.multiprocessing_parse import MultiprocessingParse
from multiprocessing import TimeoutError

from Widgets.WidgetHandler import WidgetHandler

from util_tools.PopUp import PopUpWrapper

from settingsMediator.settingsPrompter import SettingsPrompter
from settingsMediator.settingsLoader import DataObjectHolder

from video_utils.video_composer import Movie

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                    NavigationToolbar2QT as NavigationToolbar)
from pattern_types.Patterns import MainContextDecorators

from Widgets.openGL_widgets.AbstractGLContext import AbstractGLContext
from Windows.Progress import ProgressBar


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.doh = DataObjectHolder()
        self.sp = SettingsPrompter(None)
        self.plot_data = ""
        self.setupUi(self)
        # we cannot add menu actions from QT Designer level
        self.playerAction = self.menubar.addAction("Player")
        self.setWindowTitle("ESE - Early Spins Environment")
        # app = QtCore.QCoreApplication.instance()
        # screen_resolution = app.desktop().screenGeometry()
        # self.scr_width, self.scr_height = screen_resolution.width(), screen_resolution.height()
        # self.setGeometry((self.scr_width - self.width()) / 2,
        #                  (self.scr_height - self.height()) / 2, 1200, 768)
        # self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())
        # By default all options are locked and they
        # will be unlocked according to data loaded.
        self._BLOCK_ITERABLES_ = True
        self._BLOCK_STRUCTURES_ = True
        self._BLOCK_PLOT_ITERABLES_ = True

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

        # ANIMATION MENU
        self.playerAction.triggered.connect(self.showAnimationSettings)
        # EDIT SUBMENU
        self.actionWindow0Delete.triggered.connect(lambda: self.deleteWidget(0))
        self.actionWindow1Delete.triggered.connect(lambda: self.deleteWidget(1))
        self.actionWindow2Delete.triggered.connect(lambda: self.deleteWidget(2))
        self.actionWindow3Delete.triggered.connect(lambda: self.deleteWidget(3))
        self.actionDeleteAllWindows.triggered.connect(lambda: self.deleteAllWidgets())

        # VIEW SUBMENU
        self.action1_Window_Grid.triggered.connect(self.make1WindowGrid)
        self.action2_Windows_Grid.triggered.connect(self.make2WindowsGrid)
        self.action4_Windows_Grid.triggered.connect(self.make4WindowsGrid)

        # OPTIONS SUBMENU
        self.actionPerformance.triggered.connect(self.setScreenshotFolder)
        self.actionMovie_composer.triggered.connect(self.composeMovie)

        # GRID BUTTONS
        # lambda required to pass parameter - which button was pressed
        self.panes[0].button.clicked.connect(lambda: self.showChooseWidgetSettings(0))
        self.panes[1].button.clicked.connect(lambda: self.showChooseWidgetSettings(1))
        self.panes[2].button.clicked.connect(lambda: self.showChooseWidgetSettings(2))
        self.panes[3].button.clicked.connect(lambda: self.showChooseWidgetSettings(3))

    def reset_variables(self):
        self._LOADED_FLAG_ = False
        self._BLOCK_ITERABLES_ = True
        self._BLOCK_STRUCTURES_ = True
        self._BLOCK_PLOT_ITERABLES_ = True

    def refreshScreen(self):
        """weird stuff is happening when u want to update window u need to
        resize i think this is a bug"""
        self.resize(self.width() - 1, self.height())
        self.resize(self.width() + 1, self.height())

        self.playerAction.setDisabled(self._BLOCK_ITERABLES_)

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
        self.setScreenshotFolder()
        if self.screenshot_dir not in [None, "", " "]:
            mv = Movie(self.screenshot_dir)
            try:
                mv.create_video()
            except EnvironmentError:
                x = PopUpWrapper(
                    title='Movie Composer',
                    msg='Pick directory where screenshots are located.' +
                        'Proper files not found in current screenshot directory: {}'.format(self.screenshot_dir),
                    more='',
                    yesMes=None, parent=self)

    @MainContextDecorators.window_resize_fix
    def promptDirectory(self):
        fileDialog = QtWidgets.QFileDialog()
        directory = str(
            fileDialog.getExistingDirectory(
                self,
                "Select Directory",
                options = QtWidgets.QFileDialog.ShowDirsOnly))
        fileDialog.close()
        return directory

    @MainContextDecorators.window_resize_fix
    def promptFile(self):
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        fileLoaded = str(fileDialog.getOpenFileName(self, "Select File")[0])
        return fileLoaded

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
        self._LOADED_FLAG_ = False

        fileLoaded = self.promptFile()

        if fileLoaded is None or fileLoaded == "" or fileLoaded=="  ":
            msg = "Invalid directory: {}. Do you wish to abort?".format(fileLoaded)
            PopUpWrapper("Invalid directory", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, self.refreshScreen, self.loadFile)
            return 0

        if ".odt" in fileLoaded or ".txt" in fileLoaded:
            self.doh.passListObject(('plot_data', 'iterations'),
                                        *MultiprocessingParse.readFile(fileLoaded))
            self._BLOCK_ITERABLES_ = False
            self._BLOCK_PLOT_ITERABLES_ = False

        elif ".omf" in fileLoaded or ".ovf" in fileLoaded:
            self.doh.passListObject(('color_vectors', 'file_header'),
                                        *MultiprocessingParse.readFile(fileLoaded))
            self._BLOCK_STRUCTURES_ = False
        else:
            msg = "Invalid file: {}.".format(fileLoaded)
            PopUpWrapper("Invalid file", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, self.refreshScreen,
                            self.loadDirectoryWrapper, parent=self)
            self._LOADED_FLAG_ = False
            return -1
        self._LOADED_FLAG_ = True
        return 1

    def raise_thread_exception(self):
        self.reset_variables()
        self.enablePanes()
        
    def loadDirectoryWrapper(self):
        """Loads whole directory based on Parse class as simple as BHP"""
        if self._LOADED_FLAG_:
            self.deleteLoadedFiles()

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
                self.p = ThreadingWrapper(completeAction=None,
                                          exceptionAction=self.raise_thread_exception, 
                                          parent=self)
                self.p.collapse_threads(self.loadDirectory, directory)
                self.disablePanes()

            except ValueError as e:
                msg = "Invalid directory: {}. \
                    Error Message {}\nDo you wish to reselect?".format(directory,
                                                                        str(e))
                x = PopUpWrapper("Invalid directory", msg, None,
                                QtWidgets.QMessageBox.Yes,
                                QtWidgets.QMessageBox.No,
                                self.loadDirectoryWrapper,
                                quit,
                                parent=self)
                to_return = None
            except Exception as e:
                print(e)
                to_return = None
            else:
                self._BLOCK_ITERABLES_ = False
                self._LOADED_FLAG_ = True
                self._BLOCK_STRUCTURES_ = False
                to_return = 1
            return to_return

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
        self.enablePanes()

    def enablePanes(self):
        for i in range(WidgetHandler.visibleCounter):
            self.panes[i].setDisabled(False)

    def disablePanes(self):
        for i in range(WidgetHandler.visibleCounter):
            self.panes[i].setDisabled(True)

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
            # animation is running and this is may be not first window
            if self.playerWindow.worker.running:
                PopUpWrapper("Alert",
                             "You may lose calculation!" +
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
        self.doh.setDataObject(value[1], 'object_alias')
        # deduce object type based on passed string
        self.window = self.sp.\
            get_settings_window_constructor_from_file(self.doh, parent=self)
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

        try:
            self.panes[self.current_pane].addWidget(\
                self.sp.build_chain(self.current_widget_alias, self.doh, self))
        except (MemoryError, TimeoutError):
            x = PopUpWrapper("Insufficient resource", msg="You ran out of memory for this calculation" 
                    + "or timeout appeared. "+"It is suggested to increase subsampling or decrease resolution",
                    more="You can do that in settings menu")
            self.deleteWidget(self.current_pane, null_delete=True)
            self.refreshScreen()
            return
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
            pane.layout.setContentsMargins(0, 0, 0, 0)

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
                # for now not all of functions work
                return None
                toolbar = NavigationToolbar(widget.canvas, widget, coordinates=True)
                widget.canvas.toolbar = toolbar
                widget.updateCanvasSettings()
            else:
                return None

    def deleteAllWidgets(self):
        self.deleteWidget(0)
        for i in range(WidgetHandler.visibleCounter - 1):
            self.deleteWidget(i+1, False, False)

    def deleteWidget(self, number, null_delete=False, verbose=True):
        if self.playerWindow:
            if verbose:
                PopUpWrapper("Alert",
                    "You may lose calculation!", \
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
        that has no widget, it causes a major bug
        Therefore if cancel was pressed and no widget was created - hence
        null_delete, then do not call
        """
        if not null_delete: 
            self.panes[number].clearBox()
            self.panes[number].removeWidget(self.panes[number].widget)
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
                    self.panes[i].widget.initial_transformation()
                except (AttributeError, RuntimeError, NameError) as ae:
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

        self.refreshScreen()
        self.propagate_resize()

        self.actionWindow1Delete.setDisabled(True)
        self.actionWindow2Delete.setDisabled(True)
        self.actionWindow3Delete.setDisabled(True)

    def make2WindowsGrid(self):
        """Splits window in 2 panes."""
        self.panes[1].show()
        self.panes[2].hide()
        self.panes[3].hide()
        WidgetHandler.visibleCounter = 2

        self.refreshScreen()
        self.propagate_resize()

        self.actionWindow1Delete.setDisabled(False)
        self.actionWindow2Delete.setDisabled(True)
        self.actionWindow3Delete.setDisabled(True)

    def make4WindowsGrid(self):
        """Splits window in 4 panes."""
        self.panes[1].show()
        self.panes[2].show()
        self.panes[3].show()
        WidgetHandler.visibleCounter = 4

        self.refreshScreen()
        self.propagate_resize()
        self.actionWindow1Delete.setDisabled(False)
        self.actionWindow2Delete.setDisabled(False)
        self.actionWindow3Delete.setDisabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
