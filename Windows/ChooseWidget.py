from PyQt5 import QtWidgets
import json

import logging
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ChooseWidget(QtWidgets.QWidget):
    """docstring for ChooseWidget."""

    def __init__(self, number, blockStructures=False, blockIterables=False,
                 blockPlotIterables=False, parent=None):
        super(ChooseWidget, self).__init__()
        self.__WIDGET_LOC__ = "Widgets/widget_pane.json"
        self.json_file_handler = None

        self._BLOCK_STRUCTURES_ = blockStructures
        self._BLOCK_ITERABLES_ = blockIterables
        if not self._BLOCK_ITERABLES_:
            self._BLOCK_PLOT_ITERABLES_ = blockPlotIterables
        else:
            self._BLOCK_PLOT_ITERABLES_ = True
        self.number = number
        self.setWindowTitle("Choose Widget")
        if parent == None:
            self.setGeometry(0, 0, 350, 400)
        else:
            self.setGeometry(parent.width()/2 - 350/2,
                             parent.height()/2 - 400/2,
                             350, 400)
        self.loadAvailWidgets()
        self.events()
        self.show()

    def events(self):
        self.addButton.clicked.connect(self.returnChoice)

    def setHandler(self, handler):
        self.handler = handler

    def returnChoice(self):
        if self.json_file_handler is not None:
            for widget_key in self.json_file_handler.keys():
                if widget_key == "__all__":
                    continue
                if self.list.currentItem().text() == \
                        self.json_file_handler[widget_key]['alias']:
                    self.handler([self.number, widget_key])
                    self.close()
                    return
        else:
            raise FileNotFoundError(
                "widget_pane.json was not found in {}".format(self.__WIDGET_LOC__))
            """
            this is getaway handling, should not be used
            """
            if self.list.currentItem().text() == "3D cubes":
                self.handler([self.number, "3D_CUBIC"])
            elif self.list.currentItem().text() == "2D plot":
                self.handler([self.number, "2D_MPL"])
            elif self.list.currentItem().text() == "2D layer plot":
                self.handler([self.number, "2D_MPL"])
            elif self.list.currentItem().text() == "Better 2D plot":
                self.handler([self.number, "2D_BP"])
            elif self.list.currentItem().text() == "3D arrows":
                self.handler([self.number, "3D_VECTOR"])
            self.close()

    def loadWidgetsFromFile(self):
        self.json_file_handler = json.load(open(self.__WIDGET_LOC__))
        for widget_key in self.json_file_handler.keys():
            if widget_key == "__all__":
                continue
            itm = self.json_file_handler[widget_key]['alias']
            if (not self._BLOCK_ITERABLES_) and (not self._BLOCK_STRUCTURES_) \
                    and (not self._BLOCK_PLOT_ITERABLES_):
                logger.debug(f"All blocks disabled: adding item {itm}")
                self.list.addItem(itm)
            else:
                if self._BLOCK_PLOT_ITERABLES_ and \
                        self.json_file_handler[widget_key]['iterable_type'] == 'structure':
                    logger.debug(
                        f"Iterables blocked, adding structure item {itm}")
                    self.list.addItem(
                        itm)
                elif self._BLOCK_STRUCTURES_ and \
                        self.json_file_handler[widget_key]['iterable_type'] == 'plot':
                    logger.debug(
                        f"Structures blocked, adding plot item {itm}")
                    self.list.addItem(
                        itm)

    def loadAvailWidgets(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.list = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.list)
        # load from file if possible
        try:
            if self.json_file_handler is None:
                self.loadWidgetsFromFile()
        except FileNotFoundError:
            for item in self.alias_list:
                self.list.addItem(item)
        # ... and so on
        self.addButton = QtWidgets.QPushButton("Add", self)
        self.layout.addWidget(self.addButton, 0, 1)
