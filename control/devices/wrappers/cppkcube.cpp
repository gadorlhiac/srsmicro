#include "cppkcube.hpp"

/**
Class using the thorlabs API for control of a KCube motor.
This class is reimplemented and compiled in Cython for direct import
into the python-based control software.
@param poll_time an interger argument for serial communication polling time.
*/

thorlabs::CppKcube::CppKcube(int poll_time=100)
{
    if (TLI_BuildDeviceList() == 0)
    {
        short num = TLI_GetDeviceListSize();
        char serialNos[100];

        TLI_GetDeviceListByTypeExt(serialNos, 100, 27);
        {
            char *searchContext = nullptr;
            char *p = strtok_s(serialNos, ",", &searchContext);
            while (p != nullptr)
            {
            	TLI_DeviceInfo deviceInfo;
                TLI_GetDeviceInfo(p, &deviceInfo);
                strncpy_s(_cpp_desc, deviceInfo.description, 64);
                _cpp_desc[64] = '\0';

                strncpy_s(_cpp_serialNo, deviceInfo.serialNo, 8);
                _cpp_serialNo[8] = '\0';

                p = strtok_s(nullptr, ",", &searchContext);
            }
        }

        printf(_cpp_serialNo);
    }

    // CC_Open connects to device, returns 0 if successful
    if(CC_Open(_cpp_serialNo) == 0)
    {
        CC_StartPolling(_cpp_serialNo, poll_time);

        // Initialiaze parameters
        _cpp_pos = CC_GetPosition(_cpp_serialNo);
        CC_GetVelParams(_cpp_serialNo, &_cpp_accel, &_cpp_vel);
    }

    return;
}

/**
Member function for homing the motor.
@return _cpp_pos an integer representing the motor position.
*/
int thorlabs::CppKcube::cpp_home()
{
    CC_ClearMessageQueue(_cpp_serialNo);
    CC_Home(_cpp_serialNo);

    // Wait for completion
    WORD messageType;
    WORD messageId;
    DWORD messageData;

    CC_WaitForMessage(_cpp_serialNo, &messageType, &messageId, &messageData);

    while(messageType != 2 || messageId != 1)
    {
        CC_WaitForMessage(_cpp_serialNo, &messageType, &messageId, &messageData);
    }

    return cpp_pos();
}

/**
Member function for returning the current motor position.
@return _cpp_pos an integer representing the motor position.
*/
int thorlabs::CppKcube::cpp_pos()
{
    _cpp_pos = CC_GetPosition(_cpp_serialNo);

    return _cpp_pos;
}

/**
Member function for returning the current motor velocity.
@return _cpp_vel an integer representing the motor velocity.
*/
int thorlabs::CppKcube::cpp_vel()
{
    CC_GetVelParams(_cpp_serialNo, &_cpp_accel, &_cpp_vel);

    return _cpp_vel;
}

/**
Member function for returning the current motor acceleration.
@return _cpp_accel an integer representing the motor acceleration.
*/
int thorlabs::CppKcube::cpp_accel()
{
    CC_GetVelParams(_cpp_serialNo, &_cpp_accel, &_cpp_vel);

    return _cpp_accel;
}

/**
Member function for setting the motor velocity.
@param newvel an integer for what the new velocity should be set to.
@return _cpp_vel an integer representing the current velocity.
*/
int thorlabs::CppKcube::cpp_set_vel(int newvel)
{
    CC_SetVelParams(_cpp_serialNo, _cpp_accel, newvel);

    return cpp_vel();
}

/**
Member function for setting the motor acceleration.
@param newaccel an integer for what the new acceleration should be set to.
@return _cpp_accel an integer representing the current acceleration.
*/
int thorlabs::CppKcube::cpp_set_accel(int newaccel)
{
    CC_SetVelParams(_cpp_serialNo, newaccel, _cpp_vel);

    return cpp_accel();
}

/**
Member function for moving the motor to a new position.
@param newpos an integer for what the new velocity should be set to.
@return _cpp_pos an integer representing the motor position.
*/
int thorlabs::CppKcube::cpp_move(int newpos)
{
    CC_ClearMessageQueue(_cpp_serialNo);
    CC_MoveToPosition(_cpp_serialNo, newpos);

    // Wait for completion
    WORD messageType;
    WORD messageId;
    DWORD messageData;
    CC_WaitForMessage(_cpp_serialNo, &messageType, &messageId, &messageData);
    while(messageType != 2 || messageId != 1)
    {
        CC_WaitForMessage(_cpp_serialNo, &messageType, &messageId, &messageData);
    }

    _cpp_pos = CC_GetPosition(_cpp_serialNo);

    return _cpp_pos;
}

/**
Member function for closing communication with the KCubee.
@return void.
*/
void thorlabs::CppKcube::cpp_close()
{
    CC_StopPolling(_cpp_serialNo);
    CC_Close(_cpp_serialNo);

    return;
}
