from distutils.core import setup, Extension

from Cython.Build import cythonize

setup(ext_modules=cythonize(Extension("pykcube",
                                      sources=["pykcube.pyx", "cppkcube.cpp"],
                                      libraries=["Thorlabs.MotionControl.KCube.DCServo"],
                                      language="c++"), annotate=True))