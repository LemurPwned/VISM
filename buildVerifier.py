import os
import platform
import subprocess
import re
class BuildVerifier:
    def __init__(self):
        self.__OSTYPE__ = self.os_deocde(platform.system())
        self.cython_builds()

    def os_deocde(self, os_string):
        if os_string == 'Darwin':
            return 'Macintosh'
        else:
            return os_string

	# python3 cython_modules/ex_setup.py build_ext --build-lib cython_modules/build --inplace
    def intercept_failed_build(self, cython_traceback):
        error_msg = 'Error compiling Cython file:'
        print("If above build failed, please follow instructions on " +
                "webpage to build cython manually")
        if error_msg in cython_traceback:
            print(type(cython_traceback))
            catcher = '(-{55,60})(.*)(-{55,60})'
            # catcher = ''
            print(catcher)
            cutout_error = re.compile(catcher)
            m = cutout_error.match(cython_traceback)
            print(cython_traceback)
            raise ValueError("Invalid cython build")
        else:
            print("Cython build was successfull \n\n")

    def cython_builds(self):
        # enforce cython build
        out = None
        if self.__OSTYPE__ == "Windows":
            result = subprocess.Popen(['python', 'cython_modules/ex_setup.py',
                                    'build_ext', '--build-lib',
                                    'cython_modules/build',
                                    '--inplace'], stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
        else:
            # build from makefile
            result = subprocess.Popen(['make', 'cython'], stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE)
        out, err = result.communicate()
        self.intercept_failed_build(err.decode('utf-8'))
        print(out.decode('utf-8'))
