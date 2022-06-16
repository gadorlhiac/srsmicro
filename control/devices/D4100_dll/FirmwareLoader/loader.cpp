#include "loader.h"
#include "firmware1.h"
#include "firmware2.h"
#include "CyAPI.h"

//
// Vendor specific request code for Anchor Upload/Download
//
// This one is implemented in the core
//
#define ANCHOR_LOAD_INTERNAL  0xA0

//
// This command is not implemented in the core.  Requires firmware
//
#define ANCHOR_LOAD_EXTERNAL  0xA3

//
// This is the highest internal RAM address for the AN2131Q
//
#define MAX_INTERNAL_ADDRESS  0x1B3F

#define INTERNAL_RAM(address) ((address <= MAX_INTERNAL_ADDRESS) ? 1 : 0)

//
// EZ-USB Control and Status Register.  Bit 0 controls 8051 reset
//
#define CPUCS_REG_EZUSB			0x7F92

#define CPUCS_REG_FX2			0xE600

static int EZUSB_8051Reset(CCyUSBDevice *dev, UCHAR resetBit);
static int EZUSB_DownloadIntelHex(CCyUSBDevice *dev, PINTEL_HEX_RECORD hexRecord);

int EZUSB_LoadUSBFirmware(CCyUSBDevice *dev)
{
   //
   // First download loader firmware.  The loader firmware implements a vendor
   // specific command that will allow us to anchor load to external ram
   //
   EZUSB_8051Reset(dev,1);
   EZUSB_DownloadIntelHex(dev,firmware1);
   EZUSB_8051Reset(dev,0);

   //
   // Now download the device firmware
   //
   EZUSB_DownloadIntelHex(dev, firmware2);
   EZUSB_8051Reset(dev,1);
   EZUSB_8051Reset(dev,0);

   return 1;
}

static int EZUSB_8051Reset(CCyUSBDevice *dev, UCHAR resetBit)
//   Uses the ANCHOR LOAD vendor specific command to either set or release the
//   8051 reset bit in the EZ-USB chip.
{
	LONG bytesToSend;
	CCyControlEndPoint  *ept = dev->ControlEndPt;

    // toggle the EZ-USB reset bit (harmless on FX2)
	  
	ept->Target   = TGT_DEVICE;
	ept->ReqType  = REQ_VENDOR;
	ept->ReqCode  = ANCHOR_LOAD_INTERNAL;
	ept->Value    = CPUCS_REG_EZUSB;
	ept->Index    = 0;
	bytesToSend   = 1;
	if(!ept->Write(&resetBit,  bytesToSend))
		return 0;

    // toggle the FX2 reset bit (harmless on EZ-USB)
	ept->Target   = TGT_DEVICE;
	ept->ReqType  = REQ_VENDOR;
	ept->ReqCode  = ANCHOR_LOAD_INTERNAL;
	ept->Value    = CPUCS_REG_FX2;
	ept->Index    = 0;
	bytesToSend   = 1;

	if(!ept->Write(&resetBit,  bytesToSend))
		return 0;

   return 1;
}


static int EZUSB_DownloadIntelHex(CCyUSBDevice *dev, PINTEL_HEX_RECORD hexRecord)
// This function downloads Intel Hex Records to the EZ-USB device.  If any of the hex records
// are destined for external RAM, then the caller must have previously downloaded firmware
// to the device that knows how to download to external RAM (ie. firmware that implements
// the ANCHOR_LOAD_EXTERNAL vendor specific command).
{
	CCyControlEndPoint  *ept = dev->ControlEndPt;
	PINTEL_HEX_RECORD ptr;
	LONG bytesToSend;
	//
	// The download must be performed in two passes.  The first pass loads all of the
	// external addresses, and the 2nd pass loads to all of the internal addresses.
	// why?  because downloading to the internal addresses will probably wipe out the firmware
	// running on the device that knows how to receive external RAM downloads.
	//
	
	//
	// First download all the records that go in external RAM
	//
	ptr = hexRecord;
	while (ptr->Type == 0)
	{
		if (!INTERNAL_RAM(ptr->Address))
		{

			ept->Target   = TGT_DEVICE;
			ept->ReqType  = REQ_VENDOR;
			ept->ReqCode  = ANCHOR_LOAD_EXTERNAL;
			ept->Value    = ptr->Address;
			ept->Index    = 0;
			bytesToSend   = ptr->Length;

			if(!ept->Write(ptr->Data,  bytesToSend))
				return 0;
		}
		ptr++;
	}

	//
	// Now download all of the records that are in internal RAM.  Before starting
	// the download, stop the 8051.
	//
	EZUSB_8051Reset(dev, 1);
	ptr = hexRecord;

	while (ptr->Type == 0)
	{
		if (INTERNAL_RAM(ptr->Address))
		{
			ept->Target   = TGT_DEVICE;
			ept->ReqType  = REQ_VENDOR;
			ept->ReqCode  = ANCHOR_LOAD_INTERNAL;
			ept->Value    = ptr->Address;
			ept->Index    = 0;
			bytesToSend   = ptr->Length;

			if(!ept->Write(ptr->Data,  bytesToSend))
				return 0;
		}
		ptr++;
	}

   return 1;
}
