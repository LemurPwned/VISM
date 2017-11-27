from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='Parsing module',
    ext_modules = cythonize("cython_parse.pyx")
)
