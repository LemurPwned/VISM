import sys

from PyQt5.QtWidgets import QSizePolicy, QPushButton


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random

class PlotCanvas(FigureCanvas):
    dpi = 100
    objectCounter = 0

    def __init__(self, gridSize, parent=None, width=5, height=4, dpi=dpi):
        PlotCanvas.objectCounter += 1
        self.data = []
        self.plotType = "r-"
        self.plotTitle = "Plot"
        self.gridSize = gridSize

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()
        self.selectDataToPlot()

    def selectDataToPlot(self):
        self.selectDataButton = QPushButton("Select Data")
        print(self.gridSize)
        #self.selectDataButton.setGeometry()

    def __exit__(self):
        objectCounter -= 1

    def plot(self):
        self.fig.clf()
        #data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(self.data, self.plotType)
        ax.set_title(self.plotTitle)
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
