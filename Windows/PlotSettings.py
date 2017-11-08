import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, QVBoxLayout, QRadioButton, QLabel
from Windows.PlotSettingsTemplate import Ui_PlotSettings

class PlotSettings(QWidget, Ui_PlotSettings):
    def __init__(self, plotOptions=[None], gridSize=2):
        super(PlotSettings, self).__init__()
        self.setupUi(self)
        self.GroupCounter = 0
        if len(plotOptions) == 0:
            self.showMessage("There is no data to show. Load data with File > Load Directory")

        else:
            #self.EventListeners()
            self.comboBox = []
            self.radioButton = []

            for i in range(3):
                self.additionalSetup(plotOptions)


        self.setGeometry(10,10,300, 500)
        self.eventListeners()
        self.setWindowTitle("Plot Settings")
        self.show()

    def showMessage(self, msg):
        label = QLabel(msg, self)
        #groupLayout = QVBoxLayout(self)
        self.verticalLayout.insertWidget(0, label)
        label.setWordWrap(True)

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def eventListeners(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def additionalSetup(self, plotOptions=[None]):
        #for i in range(gridSize-1):
        groupBox = QGroupBox("Plot"+str(self.GroupCounter), self)
        groupLayout = QVBoxLayout(self) #layout to put in group
        self.comboBox.append(QComboBox(self))
        for option in plotOptions:
            self.comboBox[self.GroupCounter].addItem(option)

        #radioButton = []
        self.radioButton.append(QRadioButton("Run synchronized with Animation", self))
        self.radioButton[self.GroupCounter*2].setChecked(True)
        self.radioButton.append(QRadioButton("Show Plot", self))

        self.verticalLayout.insertWidget(self.GroupCounter, groupBox)
        groupLayout.addWidget(self.comboBox[self.GroupCounter])

        groupLayout.addWidget(self.radioButton[self.GroupCounter*2])
        groupLayout.addWidget(self.radioButton[(self.GroupCounter*2)+1])

        groupBox.setLayout(groupLayout)
        self.GroupCounter += 1

    def resizeEvent(self, event):
        self.verticalLayoutWidget.setGeometry(9,9, self.width()-18, self.height()-80)

    def accept(self):
        ret = []
        for i in range(self.GroupCounter):
            ret.append([self.comboBox[i].currentText(), self.radioButton[i*2].isChecked(), self.radioButton[(i*2)+1].isChecked()])

        self.eventHandler(ret)
        self.close()

    def reject(self):
        self.close()



'''maybe it's stupid but it works if, we want to return some value from our class without using signals we can create function which we pass to o class and then we can execute some code after window closes'''

def hand(x):
    print("hand: ", x)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = PlotSettings("", 3)
    settings.setEventHandler(hand) # we pass handler function to execute code after closing Window
    sys.exit(app.exec_())
