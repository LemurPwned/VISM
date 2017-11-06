from Parser import Parser
from PyQt5.QtWidgets import QApplication
import sys


if __name__=="__main__":
    app = QApplication(sys.argv)
    parser = Parser()
    Parser.readFolder("/Users/pawelkulig/Desktop/spintronics-visual/data/firstData")
    sys.exit(app.exec_())
