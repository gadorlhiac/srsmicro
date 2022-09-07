#ifndef DLP_HPP_INCLUDED
#define DLP_HPP_INCLUDED

#include <fstream>
#include "D4100_usb.h"

#include "RegisterDefines.h"
#include "CyAPI.h"
#include "loader.h"

namespace ti
{
    class CppDlp
    {
        public:
            // Methods
            CppDlp(int img[800][1280]);

            int cpp_LoadData();

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
            int _img[800][1280];
            CCyUSBDevice _lowLevelDev;
            short _numDevs;
            short _devNumber; /* Should be 0, unless there are multiple devices
                                 connected to the machine */
            short _dmdType; /* 0: DLP9500/UV, 1: DLP7000/UV, 7: DLP650LNIR (ours)
                               15: DMD not attached/unrecognized */
            int _descriptor[14];
            unsigned int _driverRev; // Upper 16 bits major, lower 16 bits minor revision
            unsigned int _firmwareRev; /* High byte contains all digits before decimal,
                                low byte all digits after. */
            short _usbSpeed; /* 0 if USB 1.1, 1 if USB 2.0, -1 if failed to open.
                             -2 if Device Descriptor failed, -3 if USB different
                             from expected (not 2.0 or 1.1) */
            unsigned int _fpgaRev;
            short _dlpcVer; // Version number in bits 2, 1, and 0

            // Methods
            int reprogram_FPGA(UCHAR* write_buffer, long write_size, short DevNumber);
    };
}

#endif
