from settingsMediator.settingsLoader import SettingsInterface
import json

"""
available settings:
3D - 3D layers - both
BP - "Better 2d Plot"
MPL - Matplotlib 2d Plot
LP - Layer 2d Plot
"""


class SettingsPrompter(SettingsInterface):
    """
    @settingsType is a tuple string indicating settings object for a given object
                    and constructor parameters for that settings object
    """
    def __init__(self, settingsType):
        super().__init__()
        self.settingsType = settingsType

    def swap_settings_type(self, settingsType):
        self.settingsType = settingsType

    def get_settings_window_constructor_from_file(self, DataObjectHolder=None,
                                                  parent=None):
        """
        :param DataObjectHolder: object holder instance
        this function extracts the settings window object from file specified
        in __WIDGET_LOC__. Returns created object window.
        """
        if self.widget_pane_handler is None:
            self.widget_pane_handler = json.load(open(self.__WIDGET_LOC__))
        # required parameters follow after class name
        settings_args_str = self.widget_pane_handler[self.settingsType]['settings'][1:]
        settings_args_param = []
        for setting_parameter in settings_args_str:
            # get the parameter if all are in DataObjectHolder
            # if not, this should raise exception, we do not catch then
            # since it is a programmers error
            # firstly check if a given parameter is accessible in DataObjectHolde
            settings_args_param.append(DataObjectHolder.retrieveDataObject(setting_parameter))
        # return a proper settings object constructed using params above
        # parent must be always the last parameter
        return self.evaluate_string_as_class_object(self.\
                    widget_pane_handler[self.settingsType]['settings'][0],
                    'settings_object')(*settings_args_param, parent=parent)

