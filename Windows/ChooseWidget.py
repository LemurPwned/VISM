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


    def returnChoice(self):
        print(self.list.currentItem().text())

    def loadAvailWidgets(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.list = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.list)
        self.list.addItem("3D structure Widget")
        self.list.addItem("2D plot Widget")
        self.list.addItem("2D layer plot Widget")
        #self.list.addItem("item4")
        self.addButton = QtWidgets.QPushButton("Add", self)
        self.layout.addWidget(self.addButton, 0, 1)
