import json

class SettingsReader:
    def __init__(self):
        pass

class SettingsInterface:
    def __init__(self):
        self.associated_widgets = {
                                        "3D":
                                            {
                                                "CUBUC": CubeGLContext,
                                                "VECTOR": ArrowGLContext,
                                            },
                                        "2D": {
                                                "MLP": Canvas,
                                                "BP" : Canvas2Dupgraded,
                                                "LAYER": CanvasLayer
                                                }
                                    }
    
    def extract_specification_parameters(self):
        pass

    def invoke_object_toolchain(self, objectTypeA, objectTypeB):
        try:
            return self.associated_widgets[objectTypeA][objectTypeB]
        except KeyError as ke:
            raise ValueError("Invalid keys {} or {}".format(objectTypeA,
                                                            objectTypeB))

    def pass_class_data(self, receivedClassType):


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
