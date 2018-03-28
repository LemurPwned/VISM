import sys
from PyQt5 import QtWidgets#.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from main import MainWindow
from Parser import Parser
from Canvas import Canvas
from CanvasLayer import CanvasLayer



class Debugger:
    def __init__(self):
        self.path = "data/firstData/"
        self.mainGui = MainWindow()

    def loadData(self):
        self.rawVectorData, self.omf_header, self.odtData, \
                self.stages = Parser.readFolder(self.path)
        self.mainGui.rawVectorData = self.rawVectorData
        self.mainGui.omf_header = self.omf_header
        self.mainGui.odt_data = self.odtData
        self.mainGui.stages = self.stages
        self.mainGui._LOADED_FLAG_ = True


    def setupPanes(self, count):
        self.count = count
        if count == 2:
            self.mainGui.action2_Windows_Grid.trigger()
        elif count == 4:
            self.mainGui.action4_Windows_Grid.trigger()
        else:
            self.mainGui.action1_Window_Grid.trigger()


    def makeAllPanes2DPlot(self):
        for i in range(self.count):
            QTest.mouseClick(self.mainGui.panes[i].button, Qt.LeftButton)
            self.mainGui.new.list.setCurrentRow(3)  # Plot2D
            QTest.mouseClick(self.mainGui.new.addButton, Qt.LeftButton)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    debugger = Debugger()
    debugger.mainGui.show()
    debugger.loadData()
    debugger.setupPanes(4)
    debugger.makeAllPanes2DPlot()
    sys.exit(app.exec_())
