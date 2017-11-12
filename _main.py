import unittest
import sys
from PyQt5 import QtWidgets#.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from main import MainWindow
from Parser import Parser
from Canvas import Canvas
from CanvasLayer import CanvasLayer
from spin_gl import GLWidget

App = QtWidgets.QApplication(sys.argv)

class _MainTester(unittest.TestCase):
    def setUp(self):
        self.mainGui = MainWindow()

    def initializeData(self):
        test_folder = "data/test_data"
        self.rawVectorData, self.omf_header, self.odtData, self.stages = Parser.readFolder(test_folder)

    def test_initialGui(self):
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
        print(self.mainGui.children())
        self.mainGui.actionLoad_Directory.trigger()
        self.assertTrue(len(self.mainGui.odt_data) > 0)'''


    def test_ViewListeners(self):
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


    def test_PlotSettingsNoData(self):
        self.initializeData()

        self.mainGui.actionPlot.trigger()
        self.assertEqual(self.mainGui.plotSettingsWindow.children()[0].children()[2].text(), "There is no data to show. Load data with File > Load Directory")
        accept = self.mainGui.plotSettingsWindow.buttonBox.children()[1]
        print(accept.text())
        QTest.mouseClick(accept, Qt.LeftButton)

    def test_Widgets(self):
        for i in range(4):
            QTest.mouseClick(self.mainGui.panes[i].button, Qt.LeftButton)
            self.mainGui.new.list.setCurrentRow(0) #openGLWidget
            QTest.mouseClick(self.mainGui.new.addButton, Qt.LeftButton)
            self.assertEqual(type(self.mainGui.panes[i].widget), GLWidget)

        #this one is problem because of threading - program is not endig after tests completed because of threads in background
    def test_plotSettingsProperData(self):
        self.initializeData()
        self.mainGui.rawVectorData = self.rawVectorData
        self.mainGui.omf_header = self.omf_header
        self.mainGui.odt_data = self.odtData
        self.mainGui.stages = self.stages

        #add 2D plot Widget
        QTest.mouseClick(self.mainGui.panes[0].button, Qt.LeftButton)
        self.mainGui.new.list.setCurrentRow(1)
        QTest.mouseClick(self.mainGui.new.addButton, Qt.LeftButton)

        self.assertEqual(type(self.mainGui.panes[0].widget), Canvas)
        self.assertNotEqual(type(self.mainGui.panes[0].widget), CanvasLayer)

        self.mainGui.actionPlot.trigger()
        #print(self.mainGui.plotSettingsWindow.children()[0].children()[2].children()[1])
        self.mainGui.plotSettingsWindow.comboBox[0].setCurrentIndex(5)
        #self.mainGui.plotSettingsWindow.radioButton[1].setChecked(True)


        print(self.mainGui.plotSettingsWindow.buttonBox.children()[1].text())
        QTest.mouseClick(self.mainGui.plotSettingsWindow.buttonBox.children()[1], Qt.LeftButton)


if __name__ == "__main__":
    unittest.main()