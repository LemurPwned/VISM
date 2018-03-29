import os
import platform
import subprocess

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

    def cython_builds(self):
        # enforce cython build
        if self.__OSTYPE__ == "Windows":
            result = subprocess.run(['python', 'cython_modules/ex_setup.py',
                                    'build_ext', '--build-lib',
                                    'cython_modules/build',
                                    '--inplace'], stdout=subprocess.PIPE)
            print(result.stdout.decode('utf-8'))
            print("If above build failed, please follow instructions on webpage to build cython manually")
        else:
            # build from makefile
            result = subprocess.run(['make', 'cython'], stdout=subprocess.PIPE)
            print(result.stdout.decode('utf-8'))
