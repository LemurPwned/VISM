import os
import imp
import glob
import json
from pattern_types.Patterns import Singleton, DataObjectHolderProxy


class DataObjectHolder(metaclass=Singleton):
    def __init__(self):
        self.contains_lookup = []

    @DataObjectHolderProxy.lookup
    def setDataObject(self, data, alias):
        setattr(self, alias, data)

    @DataObjectHolderProxy.get_lookup
    def retrieveDataObject(self, alias):
        return getattr(self, alias)

    def passListObject(self, aliasList, *dataObjList):
        for dataObj, alias in zip(dataObjList, aliasList):
            self.setDataObject(dataObj, alias)

    @DataObjectHolderProxy.is_removable
    def removeDataObject(self, alias):
        setattr(self, alias, None)

class SettingsInterface:
    def __init__(self):
        self.__WIDGET_LOC__ = "Windows/widget_pane.json"
        self.widget_pane_handler = json.load(open(self.__WIDGET_LOC__))

    def evaluate_string_as_class_object(self, obj_str, object_type,
                                        debug=True):
        """
        :param obj_str: object name specifed in the file
        :param object_type: type of object to be created, needed to set the
                            correct path
        :return object constructor of type obj_str
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
            # actually do not if this is debug, won't see changes
            # otherwise
            if debug:
                module = imp.load_source(obj_str, os.path.join(module_path,
                                                        obj_str + '.py'))
            else:
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
        """
        Attempts to find module path of a given extension
        in a specified location
        :param path: path to module
        :param filename: filename of a module file (without extension)
        :param ext: extension of module i.e. .pyc or .py. Note the dot
        :return module file
        """
        file_list_in_dir = glob.glob(os.path.join(path, filename) + '*' + ext)
        if file_list_in_dir is not None:
            return file_list_in_dir[-1]

    def build_chain(self, object_alias, doh, parent=None):
        """
        Returns the Widget object (not the constructor!) created by
        evaluating the file in __WIDGET_LOC__.
        :param object_alias: object to created
        :param doh: DataObjectHolder object with necessary arguemnts inside
        :return object of object_alias type
        """
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
            if 'optional' in self.widget_pane_handler[object_alias]:
                optional_dict = self.get_and_verify_class_parameters(\
                                self.widget_pane_handler[object_alias]['optional'],
                                doh)
                passing_dict = {**optional_dict, **passing_dict}
            # construct object and pass dict as parameter
            return self.evaluate_string_as_class_object(\
                        self.widget_pane_handler[object_alias]['object'],
                        self.widget_pane_handler[object_alias]['object_type'])(data_dict=passing_dict,
                                                                               parent=parent)
        except KeyError:
            raise ValueError("Invalid key {}".format(object_alias))

    def request_parameter_existence(self, doh, parameter_alias):
        if parameter_alias in doh.contains_lookup:
            return True
        else:
            return False

    def request_parameter(self, doh, parameter_alias):
        if self.request_parameter_existence(doh, parameter_alias):
            return doh.retrieveDataObject(parameter_alias)

    def get_and_verify_class_parameters(self, parameter_list, doh):
        """
        Verifies if all parameters are contains in DataObjectHolder instance
        :param parameter_list: list of parameters
        :param doh: DataObjectHolder instance
        """
        shared_dictionary = {}
        for param in parameter_list:
            shared_dictionary[param] = self.request_parameter(doh, param)
        return shared_dictionary
