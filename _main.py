import unittest
import sys
from PyQt5 import QtWidgets#.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from main import MainWindow
from Parser import Parser

class _MainTester(unittest.TestCase):

    def initialize(self):
        self.mainGui = MainWindow()

    def initialize_data(self):
        self.initialize()
        test_folder = "data/firstData"
        self.rawVectorData, self.omf_header, self.odtData, self.stages = Parser.readFolder(test_folder)

    def test_initialGui(self):
        self.initialize()
        self.assertEqual(self.mainGui.windowTitle(), "ESE - Early Spins Enviroment")
        self.assertTrue(self.mainGui.width() > 200)
        self.assertTrue(self.mainGui.height() > 100)
        self.assertTrue(len(self.mainGui.panes) == 4)
        self.assertTrue(self.mainGui.panes[0].isVisible())
        self.assertFalse(self.mainGui.panes[1].isVisible())
        self.assertFalse(self.mainGui.panes[2].isVisible())
        self.assertFalse(self.mainGui.panes[3].isVisible())

    '''def test_loadDirectory(self):
        self.initialize()
        self.mainGui.actionLoad_Directory.trigger()
        self.assertTrue(len(self.mainGui.odt_data) > 0)'''

    def test_ViewListeners(self):
        self.initialize()

        self.mainGui.action2_Windows_Grid.trigger()
        self.assertTrue(self.mainGui.panes[0].isVisible())
        self.assertTrue(self.mainGui.panes[1].isVisible())
        self.assertFalse(self.mainGui.panes[2].isVisible())
        self.assertFalse(self.mainGui.panes[3].isVisible())

        self.mainGui.action4_Windows_Grid.trigger()
        self.assertTrue(self.mainGui.panes[0].isVisible())
        self.assertTrue(self.mainGui.panes[1].isVisible())
        self.assertTrue(self.mainGui.panes[2].isVisible())
        self.assertTrue(self.mainGui.panes[3].isVisible())

        self.mainGui.action2_Windows_Grid.trigger()
        self.assertTrue(self.mainGui.panes[0].isVisible())
        self.assertTrue(self.mainGui.panes[1].isVisible())
        self.assertFalse(self.mainGui.panes[2].isVisible())
        self.assertFalse(self.mainGui.panes[3].isVisible())

        self.mainGui.action1_Window_Grid.trigger()
        self.assertTrue(self.mainGui.panes[0].isVisible())
        self.assertFalse(self.mainGui.panes[1].isVisible())
        self.assertFalse(self.mainGui.panes[2].isVisible())
        self.assertFalse(self.mainGui.panes[3].isVisible())


        #self.assertEqual(type(self.mainGui.panes[0].button), type(QtWidgets.QPushButton()))

        #self.mainGui.action2_Windows_Grid.trigger()
    def test_PlotSettings(self):
        self.initialize_data()
        self.mainGui.actionPlot.trigger()
        self.mainGui.plotSettingsWindow.accept.click()

        #QTest.mouseClick(self.window.browseButton_2, QtCore.Qt.LeftButton)
        #self.initialize()

        #self.

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    unittest.main()
