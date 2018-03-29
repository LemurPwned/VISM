from distutils.core import setup
from setuptools import Extension
from Cython.Build import cythonize
import numpy

"""
Use this file if cython is build outside this directory
"""
ext_modules= cythonize('cython_modules/*.pyx')

setup(
    name='External cython build',
    ext_modules = ext_modules,
    include_dirs=[numpy.get_include()]
)
