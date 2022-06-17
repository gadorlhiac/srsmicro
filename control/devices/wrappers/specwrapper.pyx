# distutils: language = c++
from Spec cimport CppSpec

cdef class SpecWrapper:
    cdef CppSpec *cpp_spec
    cdef int _pos
    cdef int _vel
    cdef int _accel

    def __cinit__(self, int poll_time):
        self.cpp_kcube = new CppKcube(poll_time)

    def __dealloc__(self):
        self.cpp_kcube.cpp_close()
        del self.cpp_kcube

    @property
    def pos(self):
        self._pos = self.cpp_kcube.cpp_pos()
        return self._pos

    @pos.setter
    def pos(self, int val):
        self._pos = self.cpp_kcube.cpp_move(val)

    @property
    def vel(self):
        self._vel = self.cpp_kcube.cpp_vel()
        return self._vel

    @vel.setter
    def vel(self, int val):
        self._vel = self.cpp_kcube.cpp_set_vel(val)

    @property
    def accel(self):
        self._accel = self.cpp_kcube.cpp_accel()
        return self._accel

    @accel.setter
    def accel(self, int val):
        self._accel = self.cpp_kcube.cpp_set_accel(val)
