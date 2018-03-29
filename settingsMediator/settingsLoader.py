import json
from Canvas import Canvas
from CanvasLayer import CanvasLayer
from multiprocessing_parse import MultiprocessingParse
from openGLContext import OpenGLContext
from arrowGLContex import ArrowGLContext
from Widgets.Canvas2Dupgraded import Canvas2Dupgraded


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
                                                "CUBIC":  OpenGLContext,
                                                "VECTOR": ArrowGLContext,
                                            },
                                        "2D": {
                                                "MPL": Canvas,
                                                "BP" : Canvas2Dupgraded,
                                                "LP": CanvasLayer
                                                }
                                    }

    def invoke_object_build_chain(self, objectTypeA, objectTypeB, doh):
        if type(doh) != DataObjectHolder:
            print(type(doh))
            raise ValueError("Passed invalid data object, cannot request parameter")
        try:
            passing_dict = \
                        self.verify_class_parameters(\
                        self.associated_widgets[objectTypeA][objectTypeB],
                        doh)
            return self.associated_widgets[objectTypeA][objectTypeB](\
                        data_dict=passing_dict)
        except KeyError:
            raise ValueError("Invalid keys {} or {}".format(objectTypeA,
                                                            objectTypeB))

    def request_parameter_existence(self, doh, parameter_alias):
        if parameter_alias in doh.contains_lookup:
            return True
        else:
            return False

    def request_parameter(self, doh, parameter_alias):
        if self.request_parameter_existence(doh, parameter_alias):
            return doh.retrieveDataObject(parameter_alias)

    def verify_class_parameters(self, class_name, doh):
        parameter_list = json.load(open('settingsMediator/spec.json'))
        print(class_name.__name__)
        shared_dictionary = {}
        for param in parameter_list[class_name.__name__]:
            shared_dictionary[param] = self.request_parameter(doh, param)

        print(shared_dictionary.keys())
        return shared_dictionary
