from PyQt5 import QtWidgets

class ChooseWidget(QtWidgets.QWidget):
    """docstring for ChooseWidget."""
    def __init__(self, number):
        super(ChooseWidget, self).__init__()
        self.number = number
        self.setWindowTitle("Choose Widget")
        self.setGeometry(0,0,300,500)
        self.loadAvailWidgets()
        self.events()
        self.show()

    def events(self):
        self.addButton.clicked.connect(self.returnChoice)

    def setHandler(self, handler):
        self.handler = handler

    def returnChoice(self):
        if self.list.currentItem().text() == "3D structure Widget - cubes":
            self.handler([self.number, "3D_CUBIC"])
        elif self.list.currentItem().text() == "2D plot Widget":
            self.handler([self.number, "2D_MPL"])
        if self.list.currentItem().text() == "2D layer plot Widget":
            self.handler([self.number, "2D_LAYER"])
        if self.list.currentItem().text() == "Better 2D plot Widget":
            self.handler([self.number, "2D_BP"])

        elif self.list.currentItem().text() == "3D structure Widget - arrows":
            self.handler([self.number, "3D_VECTOR"])
        self.close()

    def loadAvailWidgets(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.list = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.list)
        self.list.addItem("3D structure Widget - cubes")
        self.list.addItem("3D structure Widget - arrows")
        self.list.addItem("2D plot Widget")
        self.list.addItem("2D layer plot Widget")
        self.list.addItem("Better 2D plot Widget")
        #... and so on
        self.addButton = QtWidgets.QPushButton("Add", self)
        self.layout.addWidget(self.addButton, 0, 1)
