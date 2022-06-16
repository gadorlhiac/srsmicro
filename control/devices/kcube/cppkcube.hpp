#ifndef KCUBE_HPP_INCLUDED
#define KCUBE_HPP_INCLUDED

#include <stdlib.h>
#include <cstdio>
#include <conio.h>
#include "Thorlabs.MotionControl.KCube.DCServo.h"

namespace thorlabs
{
    class CppKcube
    {
        public:
            // Methods
            CppKcube(int poll_time=100);
            void cpp_close();


            int cpp_move(int newpos);
            int cpp_home();
            int cpp_set_vel(int newvel);
            int cpp_set_accel(int newaccel);

            int cpp_pos();
            int cpp_vel();
            int cpp_accel();

        private:
            // Attributes
            char _cpp_serialNo[9];
            char _cpp_desc[65];
            int _cpp_pos;
            int _cpp_vel;
            int _cpp_accel;
    };
}

#endif