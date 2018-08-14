import re 
import numpy as np
from PopUp import PopUpWrapper



class GeneralPerf:
    def general_initialization(self):
        self.subsampling = 1
        self.options = None
        self.color_selection = 'Standard'
        self.comboBox.activated[str].connect(self.changeColorPolicy)
        self.changeColorPolicy(self.color_selection)

    def layerChange(self):
        val = self.horizontalSlider_2.value()
        self.label_3.setText("Layer: {}".format(val))

    def subsamplingChange(self):
        self.subsampling = self.horizontalSlider.value()
        self.label.setText("Subsampling: {}".format(self.subsampling))    
    
    def sizeChange(self):
        val = self.horizontalSlider_3.value()
        self.label_4.setText("Size: {}".format(val))

    def parseVectors(self):
        vector1 = self.lineEdit.text()
        vector2 = self.lineEdit_2.text()
        vector3 = self.lineEdit_3.text()
        result_group = []
        for v in [vector1, vector2, vector3]:
            p = self.isVectorEntryValid(v)
            if not p:
                raise IOError("Invalid entry in vector specification")
            result_group.append(p)
        return result_group

    def isVectorEntryValid(self, entry):
        match_string = '^\[(-?[0-1]),\s?(-?[0-1]),\s?(-?[0-1])\]'
        rg = re.compile(match_string)
        m = rg.search(entry)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            z = int(m.group(3))
            norm = np.sqrt(x**2 + y**2 + z**2)  
            xval = x/norm if x != 0 else 0
            yval = y/norm if y != 0 else 0
            zval = z/norm if z != 0 else 0
            return [xval, yval, zval]
        else:
            return False

    def setEventHandler(self, handler):
        self.eventHandler = handler

    def accept(self):
        self.hide()
        try:
            self.options = self.optionsVerifier()
            if self.options is not None:
                self.eventHandler(self.options)
            self.close()
        except IOError as e:
            x = PopUpWrapper(
                title='Invalid format',
                msg='Vectors must be in format [x,y,z] {}'.format(e),
                more='',
                yesMes=None, parent=self)
            self.show()

    def reject(self):
        self.options = None
        self.eventHandler(None)
        self.deleteLater()

    def getOptions(self):
        if self.options is not None:
            return self.options

    def reset(self):
        self.lineEdit.setText('[1, 0, 0]')
        self.lineEdit_2.setText('[0, 1, 0]')
        self.lineEdit_3.setText('[0, 0, 1]')

    def changeColorPolicy(self, text):
        if text == 'Standard':
            self.color_selection = 'Standard'
            self.label_5.setText('D')
            self.label_6.setText('C+')
            self.label_7.setText('C-')  
        else:
            self.color_selection = 'RGB policy'
            self.label_5.setText('R')
            self.label_6.setText('G')
            self.label_7.setText('B')
