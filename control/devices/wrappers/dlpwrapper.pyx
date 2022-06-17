# distutils: language = c++
from Dlp cimport CppDlp

cdef class DlpWrapper:
    """The PyKcube class definition for controlling Thorlabs KCubes.
    Minimal Cython wrapper for the cppkcube class written in C++.
    """
    cdef CppKcube *cpp_kcube
    cdef int _pos
    cdef int _vel
    cdef int _accel

            cdef class MyClass:

                # the public-modifier will make the attribute public for cython,
                # not for python. Maybe you need to access the internal C++ object from
                # outside of the class. If not, you better declare it as private by just
                # leaving out the `private` modifier.
                # ---- EDIT ------
                # Sorry, this statement is wrong. The `private` modifier would make it available to Python,
                # so the following line would cause an error es the Pointer to MyCppClass
                # couldn't be converted to a Python object.
                #>> cdef public MyCppClass* cobj
                # correct is:
                cdef MyCppClass* obj

                def __init__(self, int some_var, char* some_string):
                    self.cobj = new MyCppClass(some_var, some_string)
                    if self.cobj == NULL:
                        raise MemoryError('Not enough memory.')

                def __del__(self):
                    del self.cobj

                property some_var:
                    def __get__(self):
                        return self.cobj.some_var
                    def __set__(self, int var):
                        self.cobj.some_var = var
