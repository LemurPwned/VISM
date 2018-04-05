import sys
import time
from buildVerifier import BuildVerifier

from PyQt5 import QtWidgets, QtCore
from Windows.MainWindowTemplate import Ui_MainWindow

from multiprocessing_parse import MultiprocessingParse

from Windows.ChooseWidget import ChooseWidget
from Windows.PlayerWindow import PlayerWindow

from WidgetHandler import WidgetHandler

from PopUp import PopUpWrapper

from settingsMediator.settingsPrompter import SettingsPrompter
from settingsMediator.settingsLoader import DataObjectHolder

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.doh = DataObjectHolder()
        self.sp = SettingsPrompter(None)

        self.odt_data = ""
        self.setupUi(self)
        self.setWindowTitle("ESE - Early Spins Environment")
        self.setGeometry(10, 10, 1280, 768)  # size of window
        self.gridLayoutWidget.setGeometry(0, 0, self.width(), self.height())

        # keeps all widgets in list of library object that handles Widgets
        self.panes = []
        self.playerWindow = None
        self.makeGrid()  # create grid (4 Widgets) and stores them in arrays
        self.make1WindowGrid()  # shows default 1 widget Window
        self.events()  # create event listeners
        self._LOADED_FLAG_ = False

    def events(self):
        """Creates all listeners for Main Window"""
        # FILE SUBMENU
        self.actionLoad_Directory.triggered.connect(self.loadDirectory)

        # EDIT SUBMENU
        self.actionAnimation.triggered.connect(self.showAnimationSettings)
        self.actionWindow0Delete.triggered.connect(lambda: self.deleteWidget(0))
        self.actionWindow1Delete.triggered.connect(lambda: self.deleteWidget(1))
        self.actionWindow2Delete.triggered.connect(lambda: self.deleteWidget(2))
        self.actionWindow3Delete.triggered.connect(lambda: self.deleteWidget(3))

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
        # print("panes counter: ", self.panes[0].counter)
        if WidgetHandler.visibleCounter > 2:
            self.panes[0].groupBox.setMaximumHeight(self.height() / 2 - 10)
            self.panes[0].groupBox.setMaximumHeight(self.height() / 2 - 10)
            self.panes[0].groupBox.setMaximumHeight(self.height() / 2 - 10)
            self.panes[0].groupBox.setMaximumHeight(self.height() / 2 - 10)
        else:
            self.panes[0].groupBox.setMaximumHeight(self.height() - 10)
            self.panes[0].groupBox.setMaximumHeight(self.height() - 10)
            self.panes[0].groupBox.setMaximumHeight(self.height() - 10)
            self.panes[0].groupBox.setMaximumHeight(self.height() - 10)


    def loadDirectory(self):
        """Loads whole directory based on Parse class as simple as BHP"""
        fileDialog = QtWidgets.QFileDialog()

        directory = str(
            fileDialog.getExistingDirectory(
                self,
                "Select Directory",
                options = QtWidgets.QFileDialog.ShowDirsOnly))
        fileDialog.close()

        if directory is None or directory == "":
            msg = "Invalid directory: {}. Do you wish to abort?".format(directory)
            self._LOADED_FLAG_ = False
            PopUpWrapper("Invalid directory", msg, None, QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No, self.close(), None)
            return 0
        else:
            try:
                sub = "Data is currently being loaded using all cpu power, app may stop responding for a while."
                x = PopUpWrapper("Loading", sub, "Please Wait...")

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
            self.loadDirectory()
        else:
            self.new = ChooseWidget(number)
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
        # fix that later in settings where it can be changed or not
        geom = (self.panes[self.current_pane].groupBox.width(),
                self.panes[self.current_pane].groupBox.height())

        self.doh.setDataObject(geom, 'geom')
        self.doh.setDataObject(0, 'current_state')
        self.doh.setDataObject(options, 'options')

        self.panes[self.current_pane].addWidget(\
                self.sp.build_chain(self.current_widget_alias, self.doh))
        # that fixes the problem of having not all slots filled in groupBox
        self.propagate_resize()
        self.refreshScreen()

    def deleteWidget(self, number):

        if self.playerWindow:
            PopUpWrapper("Alert",
                "You may loose calculation!", \
                "If you proceed animation will be restarted and widget \
                will be deleted!", \
                QtWidgets.QMessageBox.Yes, \
                QtWidgets.QMessageBox.No, \
                None, \
                self.refreshScreen())

            self.playerWindow.forceWorkerReset()
            self.playerWindow.closeMe()

        self.panes[number].clearBox()
        self.panes[number].setUpDefaultBox()
        self.panes[number].button.clicked.connect(\
            lambda: self.showChooseWidgetSettings(number))
        self.playerWindow.worker.clearWidgetIterators()

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
                    #  print("AttributeError/RuntimeError {}".format(ae))
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
    # verify build
    # execute makefile
    bv = BuildVerifier()

    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
