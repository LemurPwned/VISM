from PyQt5 import QtWidgets
import json

class ChooseWidget(QtWidgets.QWidget):
    """docstring for ChooseWidget."""
    def __init__(self, number, blockStructures=False, blockIterables=False):
        super(ChooseWidget, self).__init__()
        self.__WIDGET_LOC__ = "Windows/widget_pane.json"
        self.json_file_handler = None
        self.alias_list = ["3D cubes", "3D arrows", "2D plot", "2D layer plot",
                           "Better 2D plot"]
        self._BLOCK_STRUCTURES_ = blockStructures
        self._BLOCK_ITERABLES_ = blockIterables

        self.number = number
        self.setWindowTitle("Choose Widget")
        self.setGeometry(0,0,350,400)
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
                if self.list.currentItem().text() == \
                                    self.json_file_handler[widget_key]['alias']:
                    self.handler([self.number, widget_key])
                    self.close()
                    return
        else:
            print("JSON FILE NOT LOADED!")
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
            #TODO think about better solution, now i have better solution but have to change few things...

            if self.json_file_handler[widget_key]['object_type'] == "2d_object" and not self._BLOCK_ITERABLES_ or \
               self.json_file_handler[widget_key]['object_type'] == "3d_object" and not self._BLOCK_STRUCTURES_:
                self.list.addItem(self.json_file_handler[widget_key]['alias'])



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
        #... and so on
        self.addButton = QtWidgets.QPushButton("Add", self)
        self.layout.addWidget(self.addButton, 0, 1)
