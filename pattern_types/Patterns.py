import inspect
import os
import glob
from util_tools.buildVerifier import BuildVerifier
from pattern_types.widget_counter import WidgetCounter
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from util_tools.PopUp import PopUpWrapper
from functools import wraps
from processing.workerthreads import ThreadingWrapper
from threading import Thread
from queue import Queue

import logging
import time
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("__main__")


class Singleton(type):
    """
    From StackOverflow on pythonic way to implement Singleton
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
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
                raise AttributeError(
                    "No attribute in lookup: {}".format(alias))
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
                if args[0].q is None:
                    logger.debug("Initiating thread queue for recording!")
                    args[0].q = Queue()
                    for i in range(1):
                        t = Thread(target=args[0].worker)
                        t.daemon = True
                        t.start()
                args[0].screenshot_manager()
            if not args[0].record and (args[0].q is not None):
                logger.debug("Killing a queue for recording!")
                args[0].q.join()
                args[0].q = None
                logger.debug("DONE RECORDING!")
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
    def loading_protector(loading_function):
        @wraps(loading_function)
        def _loading_protector(self, name=None):
            # check the name in the file
            loaded_obj = None
            try:
                if name is None:
                    raise AttributeError(
                        f"{name} is not a valid name for object loader")
                else:
                    name = "__all__"
                allowed_exts = self.sp.evaluate_needed_file_extensions(name)
                loaded_obj = loading_function(self)
                if os.path.isdir(loaded_obj):
                    for ext in allowed_exts:
                        l = glob.glob(os.path.join(loaded_obj, '*'+ext))
                        if l != []:
                            break
                    else:
                        raise ValueError(
                            f"Incorrectly loaded object {loaded_obj}")
                else:
                    # a file
                    ext = '.'+loaded_obj.split('.')[-1]
                    if not ext in allowed_exts:
                        raise ValueError(
                            f"Incorrectly loaded object {loaded_obj}")
                if loaded_obj is None or loaded_obj == "" or loaded_obj == " ":
                    raise ValueError(f"Incorrectly loaded object {loaded_obj}")
            except ValueError as e:
                buttonReply = QtWidgets.QMessageBox.question(self, "Invalid directory",
                                                             str(e),
                                                             QtWidgets.QMessageBox.Yes |
                                                             QtWidgets.QMessageBox.No,
                                                             QtWidgets.QMessageBox.Yes)
                if buttonReply == QtWidgets.QMessageBox.Yes:
                    fname = getattr(self, loading_function.__name__)
                    return fname(name=name)
                else:
                    return None
            return loaded_obj
        return _loading_protector

    def prompt_directory_selection_if_not_stateful(choose_widget_function):
        def _widget_selector(self, value):
            logger.debug(f"\tWidget selection decorator: {value}")
            logger.debug(
                f"\tWidget is stateful! Prompting stateful loading procedure")
            try:
                self.doh.retrieveDataObject('directory')
            except AttributeError:
                directory = self.promptDirectory(value[-1])
                self.doh.setDataObject(directory, 'directory')
            self._LOADED_FLAG_ = True
            self._BLOCK_ITERABLES_ = False  # unlock player
            choose_widget_function(self, value)
        return _widget_selector

    def window_resize_fix(qdialog_function):
        def _window_resize(main_window, *args, **kwargs):
            if WidgetCounter.OPENGL_WIDGET:
                normalWindowSize = main_window.size()
                main_window.hide()
                main_window.setWindowState(main_window.windowState())
                main_window.setFixedSize(main_window.size()-QtCore.QSize(0, 1))
                main_window.show()
                to_return = qdialog_function(main_window, *args, **kwargs)
                main_window.hide()
                main_window.setWindowState(main_window.windowState())
                main_window.setFixedSize(normalWindowSize)
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
                window.saved_parent.setFixedSize(
                    window.saved_parent.size()-QtCore.QSize(0, 1))
                window.saved_parent.show()
                to_return = qdialog_function(window)
                window.saved_parent.hide()
                window.setWindowState(window.saved_parent.windowState())
                window.saved_parent.setFixedSize(normalWindowSize)
                window.saved_parent.lower()  # reconcile context
                window.saved_parent.show()
            else:
                to_return = qdialog_function(window)
            return to_return
        return _window_resize
