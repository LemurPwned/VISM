from Canvas import Canvas
from Parser import Parser

def _shareData():
    test_odt = "test_folder/voltage-spin-diode.odt"
    odt_data = Parser.getOdtData(test_odt)
    print("DETECTED COLUMNS:")
    print(odt_data[0].columns)

    #create data dict that is then passed to canvas
    #this is the exemplary dict, the order must be preserved
    data_dict = {
                'i': 0,
                'iterations': odt_data[1],
                'graph_data': odt_data[0]
                }
    new_canvas = Canvas()
    new_canvas.shareData(**data_dict)
    _runCanvas()

def _runCanvas():
    new_canvas = Canvas()
    new_canvas.createPlotCanvas()
    new_canvas.replot()

if __name__ == "__main__":
    _shareData()
