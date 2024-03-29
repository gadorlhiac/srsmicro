#include "cppdlp.hpp"
#include "cppdlp.cpp"

/**
Class using the low level TI API/development library for control of their DLP
evaluation modules which manage a DMD.
This class is reimplemented and compiled with Cython to facilitate interaction
using a Python class integrated into the Python API for the microscope control.
*/

// Images need to be 1280 pixels/row x 800 rows!!

using namespace ti;

CppDlp::CppDlp(UCHAR img)
{
    _numDevs = GetNumDev();
    if (_numDevs > 0)
    {
        _devNumber = 0;
        // Include some message about multiple devices
    } else {
        _devNumber = _numDevs;
    }
    _lowLevelDev = openDeviceOnce(_devNumber);
    GetDescriptor(&_descriptor, _devNumber);

    _driverRev = GetDriverRev(_devNumber);

    _firmwareRev = GetFirmwareRev(_devNumber);

    _usbSpeed = GetUsbSpeed(_devNumber);

    _fpgaRev = GetFPGARev(_devNumber);

    _dlpcVer = GetDDCVERSION(_devNumber);

    _dmdType = GetDMDTYPE(_devNumber);

    _img = img;
    return
}

int CppDlp:cpp_LoadData()
{
    cpp_reset();
    for(int i = 0; i < 800; i++)
    {
        uchar* tmp = _img[i];
        LoadData(tmp, _dmdType, _devNumber);
    }
    return 1; // Add checking for actual return values
}

int cpp_LoadControl()
{
    short result;
    result = LoadControl(_devNumber);
}

short CppDlp:cpp_reset()
{
    // Either load control returns 1 if successful
    short result = 1;
    // C++
    if (loadControl(_lowLevelDev))
    {
        // extern C function
        ClearFifos(_devNumber);
    }
    // C
    //if (LoadControl(_devNumber))
    //{
    //    ClearFifos(_devNumber);
    //}
}

void CppDlp::cpp_close()
{
    closeDevice(lowLevelDev);
}
