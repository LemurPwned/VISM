from distutils.core import setup
from Cython.Build import cythonize
import numpy

"""
Use this file if cython is build INSIDE this directory
"""

setup(
    name='Spin python',
    ext_modules = cythonize(["cython_parse.pyx", "color_policy.pyx"]),
    include_dirs=[numpy.get_include()]
)
