import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QGroupBox, \
                QVBoxLayout, QRadioButton, QLabel, QSlider
from PyQt5 import QtCore
from Windows.PlotSettingsTemplate import Ui_PlotSettings


class PlotSettings(QWidget, Ui_PlotSettings):
    def __init__(self, plotOptions=[None], gridSize=1):
        super(PlotSettings, self).__init__()
        self.setupUi(self)
        self.GroupCounter = 0
        if len(plotOptions) == 0:
            self.showMessage("There is no data to show. Load data with File > Load Directory")
        elif gridSize<1:
            self.showMessage("No plot pane selected, Go to MainWindow and select pane type meant to show plot.")
        else:
            self.comboBox = []
            self.comboBox2 = []
            self.comboBox3 = []
            self.comboBox4 = []

            self.radioButton = []

            for i in range(gridSize):
                self.additionalSetup(plotOptions)

        self.setGeometry(10,10,750, 600)
        self.eventListeners()
        self.setWindowTitle("Plot Settings")
        self.gridLayout_2.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.ret = []
        self.refreshScreen()
        self.show()

    def refreshScreen(self):
       self.resize(self.width(), self.height()-1)
       self.resize(self.width(), self.height()+1)

    def resizeEvent(self, event):
        self.buttonBox.setGeometry(\
        self.width() - 10, self.height() - 20, 200, 20)
        self.gridLayoutWidget.setGeometry(10, 10, self.width()-10, self.height()-20)

    def showMessage(self, msg):
        label = QLabel(msg, self)
        self.gridLayout_2.addWidget(label)
        label.setWordWrap(True)
        label.setObjectName("textLabel")

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def eventListeners(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def additionalSetup(self, plotOptions=[None]):
        groupBox = QGroupBox("Plot"+str(self.GroupCounter), self)
        groupLayout = QVBoxLayout(self) #layout to put in group

        self.comboBox.append(QComboBox(self))
        self.comboBox2.append(QComboBox(self))
        self.comboBox3.append(QComboBox(self))
        self.comboBox4.append(QComboBox(self))


        #set options
        colorOptions = ['blue', 'red', 'green', 'cyan', 'magenta','yellow',
                        'black']
        markerOptions = ['*', 'p', 's', 'h', 'H', 'x', '+', 'D',
                         'd', '|', '_', 'o',  'v', '^']
        linestyleOptions = ['-', '--', ':', '-.']

        #define label
        self.markersize_label = QLabel("Marker Size: 1", self)
        self.markerOptions_label = QLabel("Marker type", self)
        self.colorOptions_label = QLabel("Color", self)
        self.linestyle_label = QLabel("Linestyle", self)

        #definde slider
        self.slider_markersize = QSlider(QtCore.Qt.Horizontal, self)
        self.slider_markersize.setMaximum(15)
        self.slider_markersize.setMinimum(1)
        self.slider_markersize.setValue(3)
        self.slider_markersize.setSingleStep(1)
        for option in plotOptions:
            self.comboBox[self.GroupCounter].addItem(option)
        for color in colorOptions:
            self.comboBox2[self.GroupCounter].addItem(color)
        for marker in markerOptions:
            self.comboBox3[self.GroupCounter].addItem(marker)
        for line in linestyleOptions:
            self.comboBox4[self.GroupCounter].addItem(line)

        self.radioButton.append(QRadioButton("Run synchronized with Animation",
                                                                        self))
        self.radioButton[self.GroupCounter*2].setChecked(True)
        self.radioButton.append(QRadioButton("Show Plot", self))

        groupLayout.addWidget(self.comboBox[self.GroupCounter])
        groupLayout.addWidget(self.colorOptions_label)
        groupLayout.addWidget(self.comboBox2[self.GroupCounter])
        groupLayout.addWidget(self.markerOptions_label)
        groupLayout.addWidget(self.comboBox3[self.GroupCounter])
        groupLayout.addWidget(self.linestyle_label)
        groupLayout.addWidget(self.comboBox4[self.GroupCounter])

        groupLayout.addWidget(self.markersize_label)
        groupLayout.addWidget(self.slider_markersize)
        self.markersizeEvent()

        groupLayout.addWidget(self.radioButton[self.GroupCounter*2])
        groupLayout.addWidget(self.radioButton[(self.GroupCounter*2)+1])

        groupBox.setLayout(groupLayout)

        if self.GroupCounter == 0:
            self.gridLayout_2.addWidget(groupBox,0,0)

        if self.GroupCounter == 1:
            self.gridLayout_2.addWidget(groupBox,1,0)

        if self.GroupCounter == 2:
            self.gridLayout_2.addWidget(groupBox,0,1)

        if self.GroupCounter == 3:
            self.gridLayout_2.addWidget(groupBox,1,1)

        self.GroupCounter += 1
        self.refreshScreen()

    def markersizeEvent(self):
        self.slider_markersize.valueChanged.connect(self.sizeChange)

    def sizeChange(self):
        self.markersize_label.setText("Marker Size: " + \
                                    str(self.slider_markersize.value()))

    def accept(self):
        i = 0
        param_dict = {
                        'column': self.comboBox[i].currentText(),
                        'synchronizedPlot': self.radioButton[i*2].isChecked(),
                        'color': self.comboBox2[i].currentText(),
                        'line_style': self.comboBox4[i].currentText(),
                        'marker': self.comboBox3[i].currentText(),
                        'marker_color': 'blue',
                        'marker_size': self.slider_markersize.value()
                     }
        self.ret = param_dict

        # for i in range(self.GroupCounter):
        #     self.ret.append([self.comboBox[i].currentText(),
        #                 self.radioButton[i*2].isChecked(),
        #                 self.radioButton[(i*2)+1].isChecked(),
        #                 self.comboBox2[i].currentText(),
        #                 self.comboBox3[i].currentText(),
        #                 self.comboBox4[i].currentText(),
        #                 self.slider_markersize.value()])

        self.eventHandler(self.ret)
        self.close()

    def reject(self):
        self.close()

    def getOptions(self):
        return self.ret

'''maybe it's stupid but it works if, we want to return some value from
our class without using signals we can create function which we pass to o
class and then we can execute some code after window closes'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = PlotSettings(["black", "red"], 3)
    settings.setEventHandler(hand)
    # we pass handler function to execute code after closing Window
    sys.exit(app.exec_())
