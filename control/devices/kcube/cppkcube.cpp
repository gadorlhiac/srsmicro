#include "cppkcube.hpp"

thorlabs::CppKcube::CppKcube(int poll_time)
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

int thorlabs::CppKcube::cpp_pos()
{
    _cpp_pos = CC_GetPosition(_cpp_serialNo);
    return _cpp_pos;
}

int thorlabs::CppKcube::cpp_vel()
{
    CC_GetVelParams(_cpp_serialNo, &_cpp_accel, &_cpp_vel);
    return _cpp_vel;
}

int thorlabs::CppKcube::cpp_accel()
{
    CC_GetVelParams(_cpp_serialNo, &_cpp_accel, &_cpp_vel);
    return _cpp_accel;
}

int thorlabs::CppKcube::cpp_set_vel(int newvel)
{
    CC_SetVelParams(_cpp_serialNo, _cpp_accel, newvel);
    return cpp_vel();
}


int thorlabs::CppKcube::cpp_set_accel(int newaccel)
{
    CC_SetVelParams(_cpp_serialNo, newaccel, _cpp_vel);
    return cpp_accel();
}

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

void thorlabs::CppKcube::cpp_close()
{
    CC_StopPolling(_cpp_serialNo);
    CC_Close(_cpp_serialNo);
    return;
}
