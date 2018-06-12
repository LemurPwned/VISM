import os
import platform
import subprocess
import re
import glob


class BuildVerifier:
    OS_GLOB_SYS = platform.system()

    def __init__(self):
        self.__OSTYPE__ = self.os_deocde(platform.system())

    def os_deocde(self, os_string):
        if os_string == 'Darwin':
            return 'Macintosh'
        else:
            return os_string

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
            self.cleanup_procedure()
            raise ValueError("Invalid cython build")

        else:
            print("Cython build was successfull \n\n")

    def cleanup_procedure(self):
        # cleanup
        print("Cleaning...")
        root_dirs = ['', 'cython_modules', 'build']
        dirs_obj = ['*.so', '*.c']
        for obj_dir in root_dirs:
            for obj in dirs_obj:
                pathname = glob.glob(os.path.join(obj_dir, obj))
                for filename in pathname:
                    print(filename)
                    os.remove(filename)

    def cython_builds(self):
        # enforce cython build
# python3 cython_modules/ex_setup.py build_ext --build-lib cython_modules/build --inplace
        out = None
        if self.__OSTYPE__ == "Windows":
            result = subprocess.Popen(['python3', 'cython_modules/ex_setup.py',
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
