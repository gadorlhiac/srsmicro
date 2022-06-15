from setuptools import setup, find_packages

from Cython.Build import cythonize

setup(name = 'srsmicro',
      version = 0.1,
      packages = find_packages(),
      entry_points = {'gui_scripts':['srsmicro=__main__.__main__']})
