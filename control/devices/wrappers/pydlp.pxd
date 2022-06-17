cdef extern from "cppdlp.hpp" namespace "ti":
    cdef cppclass CppDlp:
        CppDlp(short) except +


        cdef extern from "mycppclass.h":
            cppclass MyCppClass:
                int some_var

                MyCppClass(int, char*)
                void doStuff(void*)
                char* getStuff(int)
