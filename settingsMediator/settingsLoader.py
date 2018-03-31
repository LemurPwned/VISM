import os
import imp
import glob
import json

from Widgets.openGL_widgets.CubicGLContext import CubicGLContext
from Widgets.openGL_widgets.VectorGLContext import VectorGLContext
from Widgets.plot_widgets.Canvas2Dupgraded import Canvas2Dupgraded

from Widgets.plot_widgets.Canvas import Canvas
from Widgets.plot_widgets.CanvasLayer import CanvasLayer

from multiprocessing_parse import MultiprocessingParse
from functools import reduce


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
        self.__WIDGET_LOC__ = "Windows/widget_pane.json"
        self.widget_pane_handler = json.load(open(self.__WIDGET_LOC__))

    def evaluate_string_as_class_object(self, obj_str, object_type):
        """
        WARNING: class name must match file name in case of widgets
        """
        try:
            # CHANGE PATH HERE IF NECESSARY!!!
            if object_type == 'settings_object':
                module_path = 'Windows'
            elif object_type == '3d_object':
                module_path = os.path.join('Widgets', 'openGL_widgets')
            elif object_type == '2d_object':
                module_path = os.path.join('Widgets', 'plot_widgets')
            else:
                raise ValueError("Invalid object type {}".format(object_type))

            # if paths do not exist, raise error
            if not os.path.isdir(module_path):
                raise ValueError("Module path: {} does not exist")

            module = None
            # if there is a build, prefer .pyc files
            if os.path.isdir(os.path.join(module_path, '__pycache__')):
                module_path = os.path.join(module_path, '__pycache__')
                module = imp.load_compiled(obj_str, self.search_obj_file(module_path,
                                            obj_str, '.pyc'))
            else:
                # if not, then fetch .py file
                module = imp.load_source(obj_str, os.path.join(module_path,
                                                    obj_str + '.py'))

            if module is None:
                raise ValueError("Module not found: module is None")
            # get the class instance
            if hasattr(module, obj_str):
                return getattr(module, obj_str)
            else:
                print("There is no {} class in {} module".format(obj_str, module))
        except AttributeError as ae:
            print("Trying to access or invoke unexisting class {}".format(ae))


    def search_obj_file(self, path, filename, ext):
        file_list_in_dir = glob.glob(os.path.join(path, filename) + '*' + ext)
        if file_list_in_dir is not None:
            return file_list_in_dir[-1]

    def build_chain(self, object_alias, doh):
        if type(doh) != DataObjectHolder:
            print(type(doh))
            raise ValueError("Passed invalid data object, cannot request parameter")
        try:
            # get the necessary parameters for object construction
            # specified in field 'required'
            passing_dict = \
                        self.get_and_verify_class_parameters(\
                            self.widget_pane_handler[object_alias]['required'],
                            doh)
            # construct object and pass dict as parameter
            return self.evaluate_string_as_class_object(\
                        self.widget_pane_handler[object_alias]['object'],
                        self.widget_pane_handler[object_alias]['object_type'])(data_dict=passing_dict)
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

    def get_and_verify_class_parameters(self, parameter_list, doh):
        shared_dictionary = {}
        for param in parameter_list:
            shared_dictionary[param] = self.request_parameter(doh, param)
        return shared_dictionary
