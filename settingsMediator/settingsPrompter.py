
from Windows.PlotSettings import PlotSettings
from Windows.PlayerWindow import PlayerWindow
from Windows.PerfOptions import PerfOptions
from Windows.vectorSettings import vectorSettings

from settingsMediator.settingsLoader import SettingsInterface
from settingsMediator.settingsLoader import DataObjectHolder

"""
available settings:
3D - 3D layers - both
BP - "Better 2d Plot"
MPL - Matplotlib 2d Plot
LP - Layer 2d Plot
"""

class SettingsPrompter(SettingsInterface):
    def __init__(self, settingsType):
        super().__init__()
        # settings_dict associates settings windows with classType
        self.settings_dict = {
                                "CUBIC": (PerfOptions, 'omf_header'),
                                "VECTOR": (PerfOptions, 'omf_header'),
                                "BP": (PlotSettings, 'odt_data'),
                                "MPL": (PlotSettings, 'odt_data'),
                                "LP": None,
                                }
        self.required_params = {
                                    "common":  ['iterations',
                                                'current_state',
                                                'title',
                                                'options'],
                                    "layered": ['omf_header',
                                                'color_vectors'],
                                }
        self.settingsType = settingsType
        # self.settingsType = allow_settings_type(settingsType)


    def has_required_parameters(self, CLASS_OBJECT):
        self.param_verfier_loop(CLASS_OBJECT, 'common')
        if CLASS_OBJECT.layered:
            self.param_verfier_loop(CLASS_OBJECT, 'layered')
        return True

    def param_verfier_loop(self, CLASS_OBJECT, param_type):
        for param_name in self.required_params[param_type]:
            if getattr(CLASS_OBJECT, param_name) is None:
                raise ValueError("REQUIRED PARAMETER NOT FOUND {}".\
                                    format(param_name))

    def allow_settings_type(self, settingsType):
        if settingsType.lower() not in settings_dict.keys():
            raise ValueError("Invalid settings window promoted {}".\
                                format(settingsType))
        else:
            return settingsType

    def prompt_settings_window(self, DataObjectHolder=None):
        # call the settings menu first
        if type(self.settings_dict[self.settingsType]) == tuple:
            return self.settings_dict[self.settingsType][0](DataObjectHolder.\
                    retrieveDataObject(self.settings_dict[self.settingsType][1]))
        else:
            return self.settings_dict[self.settingsType]()
