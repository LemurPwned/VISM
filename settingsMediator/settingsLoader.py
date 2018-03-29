import json
from Canvas import Canvas
from CanvasLayer import CanvasLayer
from multiprocessing_parse import MultiprocessingParse
from openGLContext import OpenGLContext
from arrowGLContex import ArrowGLContext
from Widgets.Canvas2Dupgraded import Canvas2Dupgraded

class SettingsReader:
    def __init__(self):
        pass


class DataObjectHolder:
    def __init__(self):
        self.contains_lookup = []

    def setDataObject(self, data, alias):
        if self.isAllowed():
            if type(alias) == str:
                setattr(self, alias, data)
                self.contains_lookup.append(alias)
            else:
                raise ValueError("Alias is not a string")
        else:
            raise ValueError("Data type not allowed {} as {}".\
                                format(data, alias))

    def retrieveDataObject(self, alias):
        if alias in self.contains_lookup:
            if self.isAllowed():
                return getattr(self, alias)
        else:
            raise ValueError("No attribute {}".format(alias))

    def isAllowed(self):
        return True

    def passListObject(self, aliasList, *dataObjList, ):
        for dataObj, alias in zip(dataObjList, aliasList):
            self.setDataObject(dataObj, alias)

class SettingsInterface:
    def __init__(self):
        self.associated_widgets = {
                                        "3D":
                                            {
                                                "CUBUC": None,
                                                "VECTOR": ArrowGLContext,
                                            },
                                        "2D": {
                                                "MLP": Canvas,
                                                "BP" : Canvas2Dupgraded,
                                                "LAYER": CanvasLayer
                                                }
                                    }

    def invoke_object_toolchain(self, objectTypeA, objectTypeB):
        try:
            return self.associated_widgets[objectTypeA][objectTypeB]()
        except KeyError as ke:
            raise ValueError("Invalid keys {} or {}".format(objectTypeA,
                                                            objectTypeB))

    def request_parameter_existence(self, DataObjectHolder, parameter_alias):
        if type(DataObjectHolder) != DataObjectHolder:
            raise ValueError("Passed Invalid object, cannot request parameter")
        if parameter_alias in self.DataObjectHolder.contains_lookup:
            return True
        else:
            return False

    def request_parameter(self, DataObjectHolder, parameter_alias):
        if self.request_parameter_existence(DataObjectHolder, parameter_alias):
            return DataObjectHolder.retrieveDataObject(parameter_alias)

    def compose_parameter_dict(self, widgetType, column=None,
                                current_state=0):
        if widgetType == 'OpenGL':
            data_dict = {
                'omf_header': self.omf_header,
                'color_list': self.rawVectorData,
                'iterations': self.stages,
                'i': current_state,
                'opt': self.optionsParser(),
                'vector_set' : self.vectorParser()
            }
        elif widgetType == '2dPlot':
            data_dict = {
                'i': current_state,
                'iterations': self.stages,
                'graph_data': self.odt_data[column].tolist(),
                'title': column
            }
        elif widgetType == '2dLayer':
            data_dict = {
                'omf_header': self.omf_header,
                'multiple_data': self.rawVectorData,
                'iterations': self.stages,
                'current_layer': 0,
                'title': '3dgraph',
                'i': current_state
            }
        else:
            msg = "Invalid argument {}".format(widgetType)
            raise ValueError(msg)
        return data_dict
