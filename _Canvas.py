from Canvas import Canvas
from Parser import Parser

def _shareData():
    test_odt = "test_folder/voltage-spin-diode.odt"
    odt_data = Parser.getOdtData(test_odt)
    print("DETECTED COLUMNS:")
    print(odt_data[0].columns)
    picked_column = 'MR::Energy'

    #create data dict that is then passed to canvas
    #this is the exemplary dict, the order must be preserved
    data_dict = {
                'i': 0,
                'iterations': odt_data[1],
                'graph_data': odt_data[0][picked_column].tolist(),
                'title' : picked_column
                }
    new_canvas = Canvas()
    new_canvas.shareData(**data_dict)
    new_canvas.check_instance()
    _runCanvas(new_canvas, odt_data[1])

def _runCanvas(canvas, iterations):
    canvas.createPlotCanvas()
    print("DONE CREATING CANVAS... PREPARING OT RUN...")
    #canvas.runCanvas()
    _iterateCanvas(canvas, iterations)

def _iterateCanvas(canvas, iterations):
    while(iterations):
        canvas.replot()
        print(canvas.i)
        canvas.increaseIterator()
        iterations -= 1

if __name__ == "__main__":
    _shareData()
