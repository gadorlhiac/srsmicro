#include <fstream>
#include "D4100_usb.h"

#include "RegisterDefines.h"
#include "CyAPI.h"
#include "loader.h"

#define MAX_TRANSFER_SIZE	63488	// In bytes, make a multiple of 512
#define DLLVERSION_MAJOR	2
#define DLLVERSION_MINOR	1
#define USB_VID_DEFAULT		0x0451	// Default Vender ID. Needs USB firmware update
#define USB_PID_DEFAULT		0xAF32	// Product ID

/* Loging debug information to file */
#if 0
#define LOG_DATA(...) \
	do {\
		FILE *fp = NULL;\
		fopen_s(&fp, "D:\\D4100_usb.log", "a");\
		if(fp)\
		{\
			fprintf(fp,__VA_ARGS__);\
			fclose(fp);\
		}\
	} while (0);
#else
#define LOG_DATA(...)
#endif

/* Logging the entry to each DLL function */
#define openDevice(devNum)	openDeviceFunc(devNum, __FUNCTION__)

// Open the USB device and return the pointer
// If failed return null
CCyUSBDevice *openDeviceOnce(short devNumber)
{
	CCyUSBDevice *dev = new CCyUSBDevice();

	if(!dev->Open((UCHAR)devNumber))
	{
		delete dev;
		return NULL;
	}

	return dev;
}

// Close the device and release any associated memory
//
void closeDevice(CCyUSBDevice *dev)
{
	delete dev;
}

// Open the USB device and checks for valid firmware.
// return the pointer to the device
// If failed return null
CCyUSBDevice *openDeviceFunc(short devNumber, char const *funcName)
{
	CCyUSBDevice *dev = openDeviceOnce(devNumber);

	LOG_DATA("%s\n", funcName);
	
	if (dev == NULL)
		return NULL;
#if 0
	USB_DEVICE_DESCRIPTOR desc;
	dev->GetDeviceDescriptor(&desc);

	/* If the USB controller has default firmware */
	if (desc.idVendor == USB_VID_DEFAULT && desc.idProduct == USB_PID_DEFAULT)
	{
		/* Download Custom firmware */
		EZUSB_LoadUSBFirmware(dev);

		/* Re-enumeration should happen now */
		/* Try opening again */
		closeDevice(dev);
		for (int i = 0; i < 20; i++) /* Timeout after 2 second */
		{
			Sleep(100);
			dev = openDeviceOnce(devNumber);
			if (dev != NULL)
			{
				break;
			}
		}
	}
#endif
	return dev;
}


// Revers bits of each byte in an input array and copy it to the output array
// The output array size is MAX_TRANSFER_SIZE
static void bitReverse(UCHAR *src, UCHAR *dst, int size)
{
	static UCHAR BitField[256];
	static int firstTime = 1;
	int i;

	// Create the Lookup table for bit reverse in byte
	// Only one time
	if(firstTime)
	{
		for(i = 0; i < 256; i++) 
		{
			UCHAR k = i;
			UCHAR v = 0;
			for(int b = 0; b < 8; b++)
			{
				v <<= 1;
				v |= k&1;
				k >>= 1;
			}
			BitField[i] = v;
		}
		firstTime = 0;
	}
	
	if(size > MAX_TRANSFER_SIZE)
		size = MAX_TRANSFER_SIZE;

	for(i = 0; i < size; i++)
	{
		// Use lookup table to revese the bits
		dst[i] = BitField[src[i]];
	}

	// Must zero out the last transfer to make it a nice even transfer
	for(; i < MAX_TRANSFER_SIZE; i++) 
		dst[i] = 0;
}

// Send a vender request out
static int vendRequestOut(UCHAR request, CCyUSBDevice *dev)
{
	UCHAR buf[2] = { 0, 0 };
	LONG bytesToSend = 2;
	CCyControlEndPoint  *ept = dev->ControlEndPt;
	ept->Target   = TGT_DEVICE;
	ept->ReqType  = REQ_VENDOR;
	ept->ReqCode  = request;
	ept->Value    = 0;
	ept->Index    = 0;
	if(!ept->Write(buf,  bytesToSend))
		return -1;
	return 1;
}

// Send a vender request in
static int vendRequestIn(UCHAR request, UCHAR buf[2], CCyUSBDevice *dev)
{
	CCyControlEndPoint  *ept = dev->ControlEndPt;
	LONG bytesToRead = 2;
	ept->Target  = TGT_DEVICE;
	ept->ReqType = REQ_VENDOR;
	ept->ReqCode = request;
	ept->Value   = 0;
	ept->Index   = 0;
	if(!ept->Read(buf, bytesToRead))
		return -1;
	return 1;
}

// Write the data to the given register location on device
static int registerWrite(unsigned short regAddress, unsigned short data, CCyUSBDevice *dev)
{
	CCyControlEndPoint  *ept = dev->ControlEndPt;
	UCHAR buf[2];
	LONG bytesToSend = 2;

	ept->Target   = TGT_DEVICE;
	ept->ReqType  = REQ_VENDOR;
	ept->ReqCode  = 0xBA;
	ept->Value    = regAddress;
	ept->Index    = 0;

	buf[1] = data & 0xFF;
	buf[0] = (data >> 8) & 0xFF;

	if(!ept->Write(buf,  bytesToSend))
		return -1;

	return 1;
}


// Returns the value at location Register on Device DeviceNumber
static int registerRead(unsigned short int regAddress, CCyUSBDevice *dev)
{
	CCyControlEndPoint  *ept = dev->ControlEndPt;
	LONG bytesToSend = 2;
	UCHAR buf[2];
	int result;

	ept->Target   = TGT_DEVICE;
	ept->ReqType  = REQ_VENDOR;
	ept->ReqCode  = 0xBA;
	ept->Value    = regAddress;
	ept->Index    = 0;

	if(!ept->Read(buf,  bytesToSend))
		result = -2;
	else
		result = buf[1] | (buf[0] << 8);

	return result;
}

// Modify one bit in the register value
static short registerWriteBit(unsigned short regAddress, unsigned short mask, 
										unsigned short value, CCyUSBDevice *dev)
{
	short result = 1;
	int curValue = registerRead(regAddress, dev);

	if(curValue < 0)
	{
		result = 0;
	}
	else 
	{
		if(value == 1)
			curValue |= mask;
		else
			curValue &= ~mask;

		if(registerWrite(regAddress, curValue, dev) < 0)
			result = 0;
	}

	return result;
}

// Transfer bulk data to the device
static int dataWrite(UCHAR *buffer, long size, CCyUSBDevice *dev, int pipeNum = 0)
{
	int result = 1;
	LONG lastSize = (size % 512);
	LONG firstSize = size - lastSize;
	LONG padding = (512 - lastSize) % 512;

	CCyBulkEndPoint *ept = dev->BulkOutEndPt; /* First bulk endpoint */

	LOG_DATA("Data Write (%d) : %d\n", pipeNum, size);

	/* If pipe 1 is requested look for the second bulk endpoint */
	/* This is used for FPGA firmware update */
	if(pipeNum == 1)
	{
		int eptCount = dev->EndPointCount();
		for(int i = 1; i < eptCount;  i++)
		{
			bool bIn = dev->EndPoints[i]->bIn;
			bool bBulk =  (dev->EndPoints[i]->Attributes == 2);
			if(bBulk && bIn == false && ept != (CCyBulkEndPoint *) dev->EndPoints[i])
			{
				ept = (CCyBulkEndPoint *) dev->EndPoints[i];
				break;
			}
		}
	}

	ept->TimeOut = 2000; /* 2 second timout */

	if (firstSize != 0)
	{
		/* Send the first part of the data (multiples of 512) */
		if (!ept->XferData(buffer, firstSize))
			return -1;
	}

	if(padding != 0)
	{
		/* Send last part of the data */
		UCHAR *padBuffer = new UCHAR[512];
		int i;
		/* Copy the data into 512 byte array */
		for(i = 0; i < lastSize; i++)
			padBuffer[i] = buffer[firstSize+i];

		/* Pad the remaining to 0 */
		for(; i < 512; i++)
			padBuffer[i] = 0;


		/* Send the 512 byte data */
		LONG pktSize = 512;
		if(!ept->XferData(padBuffer, pktSize))
			result = -1;

		delete [] padBuffer;
	}

	return result;
}



// Read build data from the device (multiples of 512)
static int dataRead(UCHAR *buffer, long size, CCyUSBDevice *dev)
{
	if(vendRequestOut(0xB3, dev) < 0)
		return -1;

	/* Read only 512 bytes multiples */
	size = size - (size % 512);

	dev->BulkInEndPt->TimeOut = 2000; /* 2 second timeout */

	if(!dev->BulkInEndPt->XferData(buffer, size))
		return -1;

	return size; //Return the number of bytes transfered
}




short loadControl(CCyUSBDevice *dev)
{
	short result = 1;

	//Set the FPGA to do 1 command at a time
	if(registerWrite(D4100_ADDR_NUMROWS, 0x0001, dev) < 0)
		result = -2;

	//Start state
	if(registerWrite(D4100_ADDR_CTL1, D4100_CTLBIT_WRITEBLOCK, dev) < 0)
		result = -2;

	return result;
}

// Public DLL functions
extern "C"
{
	// Closes the handles at the end to keep the USB device from freezing 
	// if one is unplugged then plugged back in
	// Each funtion will re-open the handles, and then close them when it is done

	// Returns the number of connected devices
	short int GetNumDev()
	{
		CCyUSBDevice *dev = new CCyUSBDevice();
		int devices = dev->DeviceCount();
		closeDevice(dev);
		return devices;
	}

	// Reads the device descriptor and returns the content in an array
	int GetDescriptor(int* Array, short int DeviceNumber)
	{
		USB_DEVICE_DESCRIPTOR desc;

		CCyUSBDevice *dev = NULL;
		
		dev = openDevice(DeviceNumber);
		if (dev == NULL)
			return -1;

		dev->GetDeviceDescriptor(&desc);

		//Assign a value in the array for each descriptor value
		Array[0] = desc.bLength;
		Array[1] = desc.bDescriptorType;
		Array[2] = desc.bcdUSB;
		Array[3] = desc.bDeviceClass;
		Array[4] = desc.bDeviceSubClass;
		Array[5] = desc.bDeviceProtocol;
		Array[6] = desc.bMaxPacketSize0;
		Array[7] = desc.idVendor;
		Array[8] = desc.idProduct;
		Array[9] = desc.bcdDevice;
		Array[10] = desc.iManufacturer;
		Array[11] = desc.iProduct;
		Array[12] = desc.iSerialNumber;
		Array[13] = desc.bNumConfigurations;

		closeDevice(dev);

		// Return the number of bytes read
		return sizeof(desc);
	}

	//Send a vendor request to get the firmware version number
	unsigned int GetFirmwareRev(short int DeviceNumber)
	{
		UCHAR buf[2];
		int result;

		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;

		if(vendRequestIn(0xBD, buf, dev) <= 0)
		{
			result = -2;
		}
		else
		{
			result = (buf[0] << 8) | buf[1];
		}
		
		closeDevice(dev);

		return result;
	}

	// Get DLL Version number MS 16 bits major, LS 16 bits minor
	long GetDLLRev()
	{
		return (DLLVERSION_MAJOR << 16) | DLLVERSION_MINOR;
	}

	// Poll for reset complete and return 1 on success
	short GetRESETCOMPLETE(int waittime, short int DeviceNumber)
	{
		// We will poll every 100 milliseconds, if loop time = 0 loop forever
		int loopCount = (waittime + 99)/100;
		short resetComplete = 0; 

		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return 0;

		//enable extrnal resets, clearing it and setting it clears the reset complete flag on the D4100
		registerWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_EXTRESET, 1, dev);
		
		while(1)
		{
			if(registerRead(D4100_RESET_COMPLETE, dev) == 1)
			{
				resetComplete = 1;
				break;
			}
			if(loopCount > 0)
			{
				loopCount--;
				if(loopCount == 0)
				{
					break;
				}
			}

			Sleep(100);
		}

		if(resetComplete == 1)
		{
			//send two no-ops
			registerWrite(D4100_ADDR_BLKMD, 0, dev);
			registerWrite(D4100_ADDR_BLKAD, 0, dev);

			loadControl(dev);
			loadControl(dev);

			registerWrite(D4100_GPIORESETFLAG, 1, dev);
			registerWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_EXTRESET, 0, dev);
		}

		closeDevice(dev);

		return resetComplete;
	}

	// Get the GPIO reset complete status
	short SetGPIORESETCOMPLETE(short int DeviceNumber)
	{
		return RegisterWrite(D4100_GPIORESETFLAG, 1, (UCHAR)DeviceNumber);
	}

	// Get the FPGA configration version number
	unsigned int GetFPGARev(short int DeviceNumber)
	{
		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;

		unsigned int output = 0;
		short upper = registerRead(0, dev); //Upper 16 bit version info
		short lower = registerRead(1, dev); //Lower 16 bit version info
		
		closeDevice(dev);

		return (upper << 16) | lower;
	}

	// Get the USB driver version number
	unsigned int GetDriverRev(short int DeviceNumber)
	{
		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;

		unsigned version = dev->DriverVersion;
		closeDevice(dev);
		return version;
	}

	// Get the USB device speed
	// 0 = flow low speed, 1 = for high speed, negative on failure
	short int GetUsbSpeed(short int DeviceNumber)
	{
		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;

		unsigned bcdUSB = dev->BcdUSB;

		closeDevice(dev);

		if(bcdUSB == 0x0110 || bcdUSB == 0x0100) //USB 1.1 or USB 1.0
		{
			return 0;
		}
		else if(bcdUSB == 0x0200) //USB 2.0
		{
			return 1;
		}
		else //Differs from expected values
		{
			return -3;
		}
	}

	short LoadControl(short DeviceNumber)
	{
		short result = 1;
		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;

		//Set the FPGA to do 1 command at a time
		if(loadControl(dev) <= 0)
			result = -2;

		closeDevice(dev);
		return result;
	}

	short ClearFifos(short DeviceNumber)
	{
		return RegisterWrite(D4100_ADDR_CTL1, D4100_CTLBIT_CLRFIFO, DeviceNumber); //Clear the FIFOs
	}
	
	short SetBlkMd(short value, short DeviceNumber) 
	{
		return RegisterWrite(D4100_ADDR_BLKMD, value, DeviceNumber);
	}
	
	short GetBlkMd(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_BLKMD, DeviceNumber);
	}
	
	short SetBlkAd(short value, short DeviceNumber) 
	{
		return RegisterWrite(D4100_ADDR_BLKAD, value, DeviceNumber);
	}
	
	short GetBlkAd(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_BLKAD, DeviceNumber);
	}
	
	short SetRST2BLKZ(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_RST2BLKZ, value, DeviceNumber);
	}
	
	short GetRST2BLKZ(short DeviceNumber) 
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_RST2BLKZ, DeviceNumber);
	}

	short SetLoad4(short value, short DeviceNumber)
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_LOAD4, value, DeviceNumber);
	}

	short GetLoad4(short DeviceNumber)
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_LOAD4, DeviceNumber);
	}

	short SetRowMd(short value, short DeviceNumber) 
	{
		return RegisterWrite(D4100_ADDR_ROWMD, value, DeviceNumber);
	}
	
	short GetRowMd(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_ROWMD, DeviceNumber);
	}
	
	short SetRowAddr(short value, short DeviceNumber) 
	{
		return RegisterWrite(D4100_ADDR_ROWAD, value, DeviceNumber);
	}
	
	short GetRowAddr(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_ROWAD, DeviceNumber);
	}
	
	short SetSTEPVCC(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_STEPVCC, value, DeviceNumber);
	}
	
	short GetSTEPVCC(short DeviceNumber) 
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_STEPVCC, DeviceNumber);
	}
	
	short SetCOMPDATA(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_COMPDATA, value, DeviceNumber);
	}
	
	short GetCOMPDATA(short DeviceNumber) 
	{	
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_COMPDATA, DeviceNumber);
	}
	
	short SetNSFLIP(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_NSFLIP, value, DeviceNumber);
	}
	
	short GetNSFLIP( short DeviceNumber) 
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_NSFLIP, DeviceNumber);
	}
	
	short SetWDT(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_WDT, value, DeviceNumber);
	}
	
	short GetWDT(short DeviceNumber) 
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_WDT, DeviceNumber);
	}
	
	// Set the power float
	short SetPWRFLOAT(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_PWRFLOATZ, value, DeviceNumber);
	}
	
	// Get the Power float status
	short GetPWRFLOAT(short DeviceNumber) 
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_PWRFLOATZ, DeviceNumber);
	}
	
	// Set the External reset enable
	short SetEXTRESETENBL(short value, short DeviceNumber) 
	{
		return RegisterWriteBit(D4100_ADDR_CTL2, D4100_CTLBIT_EXTRESET, value, DeviceNumber);
	}
	
	// Get External reset enable status
	short GetEXTRESETENBL(short DeviceNumber) 
	{
		return RegisterReadBit(D4100_ADDR_CTL2, D4100_CTLBIT_EXTRESET, DeviceNumber);
	}
	
	// Set the GPIO values
	short SetGPIO(short value, short DeviceNumber) 
	{
		return RegisterWrite(D4100_ADDR_GPIO, value, DeviceNumber);
	}
	
	// Get GPIO values
	short GetGPIO(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_GPIO, DeviceNumber);
	}
	
	// Get the DMD type information
	short GetDMDTYPE(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_DMDTYPE, DeviceNumber);
	}

	// Get the DLP Discovery controller version
	short GetDDCVERSION(short DeviceNumber) 
	{
		return RegisterRead(D4100_ADDR_DDCVERSION, DeviceNumber);
	}
	
	// NOTE:  At this time the RowData FIFO format is not defined and is not handled here
	int LoadData(UCHAR* RowData,long length, short DevType, short DeviceNumber) 
	{
		short result = 1;
		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;

		int NumberOfRows = 0;

		if(registerWrite(D4100_ADDR_CTL1, D4100_CTLBIT_CLRFIFO, dev) <= 0)
			result = -2;

		if(DevType == 0 || DevType == 4 || DevType == 5) // Device is a 1080p, 1080p Diamond or a WUXGA
			NumberOfRows = length / 240; 
		else if ( DevType == 1 || DevType ==2 || DevType == 3 ) // Device is an XGA
			NumberOfRows = length / 128; //Devide by XGA row length (in bytes)
        else if ( DevType == 7)
            NumberOfRows = length / 160; //Devide by WXGA row length (in bytes)
		else
			result = -2;

		if(NumberOfRows != 0)
		{
			if(dataWrite(RowData, length, dev) < 0 )
				result = -2;
			//Set the FPGA to do NumberofRows commands
			else if(registerWrite(D4100_ADDR_NUMROWS, NumberOfRows, dev) < 0)
				result = -2;
			//Start State
			else if (registerWrite(D4100_ADDR_CTL1, D4100_CTLBIT_WRITEBLOCK, dev) < 0)
				result = -2;
		}

		closeDevice(dev);
		return result;		
	}

	// Download FPGA configration image to the EVM
	int program_FPGA(UCHAR *write_buffer, LONG write_size, short int DeviceNumber)
	{
		BOOL result = 0;
		
		CCyUSBDevice *dev = openDevice(DeviceNumber);

		if(dev == NULL)
			return -1;
		
		UCHAR *buffer_swapped = new UCHAR[MAX_TRANSFER_SIZE];

		vendRequestOut(0xBB, dev); //Request for FPGA program
		
		while(write_size > 0)
		{
			bitReverse(write_buffer, buffer_swapped, write_size);

			if(dataWrite(buffer_swapped, MAX_TRANSFER_SIZE, dev, 1) <= 0)
			{
				break;
			}

			write_size -= MAX_TRANSFER_SIZE;
			write_buffer += MAX_TRANSFER_SIZE;
		}

		if(write_size <= 0) // Loading complted
		{
			// Wait for 0xBC01 to come back from 0xBC request to signify firmware received		
			for(int c = 0; c < 10; c++) //Only try a couple times, timeout after
			{
				UCHAR buf[2];
				if(vendRequestIn(0xBC, buf, dev) <= 0)
				{
					result = 0;
					break;
				}
				if(buf[0] == 0xBC && buf[1] == 0x01) //Means it received the FPGA data successfully
				{
					result = 1;
					break;
				}

				Sleep(200); //Wait a little bit before requesting again
			}
		}

		delete [] buffer_swapped;
		closeDevice(dev);
		return result;	//Timed out waiting for confirmation
	}


	short GetTPGEnable(short int DeviceNumber)
	{
		return RegisterReadBit(D4100_TPG_SELECT, D4100_TPG_SELECT_TPG_EN, DeviceNumber);
	}

	short SetTPGEnable(short value, short int DeviceNumber)
	{
		return RegisterWriteBit(D4100_TPG_SELECT, D4100_TPG_SELECT_TPG_EN, value, DeviceNumber);
	}

	short GetSWOverrideEnable(short int DeviceNumber)
	{
		return RegisterReadBit(D4100_TPG_SELECT, D4100_TPG_SELECT_SW_EN, DeviceNumber);
	}

	short SetSWOverrideEnable(short value, short int DeviceNumber)
	{
		return RegisterWriteBit(D4100_TPG_SELECT, D4100_TPG_SELECT_SW_EN, value, DeviceNumber);
	}


	short GetPatternForce(short int DeviceNumber)
	{
		return RegisterReadBit(D4100_TPG_SELECT, D4100_TPG_SELECT_PAT_FORCE, DeviceNumber);
	}

	short SetPatternForce(short value, short int DeviceNumber)
	{
		return RegisterWriteBit(D4100_TPG_SELECT, D4100_TPG_SELECT_PAT_FORCE, value, DeviceNumber);
	}

	short GetSWOverrideValue(short int DeviceNumber)
	{
		return RegisterRead(D4100_SW_OVERRIDE, DeviceNumber);
	}

	short SetSWOverrideValue(short value, short int DeviceNumber)
	{
		return RegisterWrite(D4100_SW_OVERRIDE, value, DeviceNumber);
	}

	short GetPatternSelect(short int DeviceNumber)
	{
		return RegisterRead(D4100_PATTERN_SELECT, DeviceNumber);
	}

	short SetPatternSelect(short value, short int DeviceNumber)
	{
		return RegisterWrite(D4100_PATTERN_SELECT, value, DeviceNumber);
	}

    // Write the data to the given register location on device
    int RegisterWrite(unsigned short regAddress, unsigned short data, short devNumber)
    {
        int result = 1;
        CCyUSBDevice *dev = openDevice(devNumber);

        if (dev == NULL)
            return -1;

        result = registerWrite(regAddress, data, dev);

        closeDevice(dev);

        return result;
    }
    

    // Returns the value at location Register on Device DeviceNumber
    int RegisterRead(unsigned short int regAddress, short devNumber)
    {
        int result;

        CCyUSBDevice *dev = openDevice(devNumber);

        if (dev == NULL)
            return -1;

        result = registerRead(regAddress, dev);

        closeDevice(dev);

        return result;
    }
    
    // Modify one bit in the register value
    short RegisterWriteBit(unsigned short regAddress, unsigned short mask,
        unsigned short value, short devNumber)
    {
        short result = 1;
        CCyUSBDevice *dev = openDevice(devNumber);

        if (dev == NULL)
            return 0;

        result = registerWriteBit(regAddress, mask, value, dev);

        closeDevice(dev);

        return result;
    }

    // Read one bit from the device register
    short RegisterReadBit(unsigned short regAddress, unsigned short mask, short devNumber)
    {
        int value = RegisterRead(regAddress, devNumber);
        if (value < 0)
            return value;
        else if ((value & mask) != 0)
            return 1;
        else
            return 0;
    }

    // Transfer bulk data to the device
    int DataWrite(UCHAR *buffer, long size, UCHAR devNumber, int pipeNum = 0)
    {
        int result;

        CCyUSBDevice *dev = openDevice(devNumber);

        if (dev == NULL)
            return -1;

        result = dataWrite(buffer, size, dev, pipeNum);

        closeDevice(dev);

        return result;
    }

    // Read build data from the device number (multiples of 512)
    int DataRead(UCHAR *buffer, long size, UCHAR devNumber)
    {
        int result;

        CCyUSBDevice *dev = openDevice(devNumber);

        if (dev == NULL)
            return -1;

        result = dataRead(buffer, size, dev);

        closeDevice(dev);

        return result;
    }
}
