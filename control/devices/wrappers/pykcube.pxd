cdef extern from "cppkcube.hpp" namespace "thorlabs":
    cdef cppclass CppKcube:
        CppKcube(int) except +

        # Public Methods
        void cpp_close()

        int cpp_move(int newpos)
        int cpp_home()
        int cpp_set_vel(int newvel)
        int cpp_set_accel(int newaccel)

        int cpp_pos()
        int cpp_vel()
        int cpp_accel()

        # Private Attributes
        char _cpp_serialNo[9]
        char _cpp_desc[65]
        int _cpp_pos
        int _cpp_vel
        int _cpp_accel 
