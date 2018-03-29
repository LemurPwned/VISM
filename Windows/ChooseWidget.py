from PyQt5 import QtWidgets

class ChooseWidget(QtWidgets.QWidget):
    """docstring for ChooseWidget."""
    def __init__(self, number):
        super(ChooseWidget, self).__init__()
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

    def loadAvailWidgets(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.list = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.list)
        self.list.addItem("3D cubes")
        self.list.addItem("3D arrows")
        self.list.addItem("2D plot")
        self.list.addItem("2D layer plot")
        self.list.addItem("Better 2D plot")
        #... and so on
        self.addButton = QtWidgets.QPushButton("Add", self)
        self.layout.addWidget(self.addButton, 0, 1)
