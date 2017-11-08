from Parser import Parser
from Canvas3D import Canvas3D
def _shareData():
    test_folder = "./data/firstData"
    rawVectorData, omf_header, odt_data, stages = Parser.readFolder(test_folder)
    target_dict = {
                    'omf_header':  omf_header,
                    'multiple_data': rawVectorData,
                    'iterations': stages,
                    'current_layer': 1,
                    'title': '3dgraph',
                    'i': 0
    }
    new_canvas = Canvas3D()
    new_canvas.shareData(**target_dict)
    new_canvas.createPlotCanvas()
    new_canvas.loop()

if __name__ == "__main__":
    _shareData()
