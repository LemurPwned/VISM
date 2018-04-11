import sys
from PyQt5 import QtWidgets#.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from main import MainWindow
from multiprocessing_parse import MultiprocessingParse


class Debugger:
    def __init__(self):
        self.path = "data/firstData/"
        self.mainGui = MainWindow()
        self.doh = self.mainGui.doh
        self.sp = self.mainGui.sp


    def loadData(self):
        # self.sp.swap_settings_type(value[1])
        self.doh.passListObject(('color_vectors', 'omf_header',
                                 'odt_data', 'iterations'),
                                *MultiprocessingParse.readFolder("data/firstData/"))
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
    debugger.setupPanes(1)
    # debugger.makeAllPanes2DPlot()
    sys.exit(app.exec_())
