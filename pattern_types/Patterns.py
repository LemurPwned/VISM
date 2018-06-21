import inspect
from buildVerifier import BuildVerifier
from widget_counter import WidgetCounter
from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class Singleton(type):
    """
    From StackOverflow on pythonic way to implement Singleton
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Proxy(object):
    def __init__(self, _obj):
        self._obj = _obj


class DataObjectHolderProxy(Proxy):
    """
    This is proxy wrapper around Data Holder
    Data Holder can either inherit or just import decorators
    The former is used right now.
    """
    def __init__(self):
        super().__init__(DataObjectHolder())

    def lookup(func):
        def _lookup(*args):
            obj_handler = args[0]
            alias = args[2]
            if type(alias) != str:
                raise ValueError("Alias is not a string")
            if alias not in obj_handler.contains_lookup:
                obj_handler.contains_lookup.append(alias)
            func(*args)
        return _lookup

    def get_lookup(func):
        def _get_lookup(*args):
            obj_handler = args[0]
            alias = args[1]
            if alias in obj_handler.contains_lookup:
                return func(*args)
            else:
                raise AttributeError("No attribute in lookup: {}".format(alias))
        return _get_lookup

    def is_removable(func):
        def _is_removable(*args):
            obj_handler = args[0]
            alias = args[1]
            if alias == '__all__':
                for element in obj_handler.contains_lookup:
                    obj_handler.removeDataObject(element)
            elif alias in obj_handler.contains_lookup:
                func(*args)
                obj_handler.contains_lookup.remove(alias)
            else:
                raise AttributeError("Trying to remove unexisting element: ")
        return _is_removable


class AbstractGLContextDecorators:
    def recording_decorator(drawing_function):
        def _rec(*args):
            drawing_function(*args)
            if args[0].record:
                args[0].screenshot_manager()
        return _rec

    def systemDisable(func):
        """
        Used for not working Font renderings on Mac
        """
        def _disable(*args):
            if BuildVerifier.OS_GLOB_SYS != 'Darwin':
                func(*args)
        return _disable


class MainContextDecorators:
    def window_resize_fix(qdialog_function):
        def _window_resize(main_window, *args, **kwargs):
            if WidgetCounter.OPENGL_WIDGET:
                normalWindowSize = main_window.size()
                main_window.hide()
                main_window.setWindowState(main_window.windowState())
                main_window.setFixedSize(main_window.size()-QtCore.QSize(0,1))
                main_window.show()
                to_return = qdialog_function(main_window, *args, **kwargs)
                main_window.hide()
                main_window.setWindowState(main_window.windowState())
                main_window.setFixedSize(normalWindowSize);
                main_window.show()
            else:
                to_return = qdialog_function(main_window, *args, **kwargs)
            return to_return
        return _window_resize

    def parent_window_resize_fix(qdialog_function):
        def _window_resize(window):
            if WidgetCounter.OPENGL_WIDGET:
                normalWindowSize = window.saved_parent.size()
                window.saved_parent.hide()
                window.setWindowState(window.saved_parent.windowState())
                window.saved_parent.setFixedSize(window.saved_parent.size()-QtCore.QSize(0,1))
                window.saved_parent.show()
                to_return = qdialog_function(window)
                window.saved_parent.hide()
                window.setWindowState(window.saved_parent.windowState())
                window.saved_parent.setFixedSize(normalWindowSize)
                window.saved_parent.lower() # reconcile context
                window.saved_parent.show()
            else:
                to_return = qdialog_function(window)
            return to_return
        return _window_resize
