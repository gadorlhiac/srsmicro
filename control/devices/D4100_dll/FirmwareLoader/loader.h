#ifndef LOADER_H__
#define LOADER_H__

#include <windows.h>
#include "CyAPI.h"

#define MAX_INTEL_HEX_RECORD_LENGTH 16

typedef struct _INTEL_HEX_RECORD
{
	BYTE  Length;
	WORD  Address;
	BYTE  Type;
	BYTE  Data[MAX_INTEL_HEX_RECORD_LENGTH];
} INTEL_HEX_RECORD, *PINTEL_HEX_RECORD;

int EZUSB_LoadUSBFirmware(CCyUSBDevice *dev);


#endif
