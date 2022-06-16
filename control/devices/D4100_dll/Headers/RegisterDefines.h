
//D4100 USB Register Adresses
#define D4100_ADDR_DMDTYPE		0x0010
#define	D4100_ADDR_DDCVERSION	0x0011
#define D4100_ADDR_BLKMD		0x0017
#define D4100_ADDR_BLKAD		0x0018
#define D4100_ADDR_ROWMD		0x0014
#define D4100_ADDR_ROWAD		0x0015
#define D4100_ADDR_CTL1			0x0003
#define D4100_ADDR_CTL2			0x0016
#define	D4100_ADDR_GPIO			0x0019
#define D4100_ADDR_NUMROWS      0x0020
#define D4100_RESET_COMPLETE	0x0021
#define D4100_GPIORESETFLAG		0x0022
#define D4100_TPG_SELECT 		0x0024
#define D4100_SW_OVERRIDE       0x0025
#define D4100_PATTERN_SELECT	0x0026

//D4100 USB Control register 0x03 bits
#define D4100_CTLBIT_WRITEBLOCK	0x0001
#define D4100_CTLBIT_RESETCMLPT 0x0008
#define D4100_CTLBIT_CLRFIFO	0x0010

//D4100 USB Control register 0x16 bits
#define	D4100_CTLBIT_STEPVCC	0x0001
#define D4100_CTLBIT_COMPDATA	0x0002
#define D4100_CTLBIT_NSFLIP		0x0004
#define D4100_CTLBIT_WDT		0x0008
#define D4100_CTLBIT_PWRFLOATZ	0x0010
#define D4100_CTLBIT_EXTRESET	0x0020
#define	D4100_CTLBIT_RST2BLKZ	0x0040
#define	D4100_CTLBIT_LOAD4   	0x0080

//D4100 Define Block modes and Row Modes
#define D4100_BLKMD_NOOP	0
#define D4100_BLKMD_CLBLK   1
#define D4100_BLKMD_RSTBLK	2
#define D4100_BLKMD_11		3
#define D4100_ROWMD_NOOP	0
#define D4100_ROWMD_INC		1
#define D4100_ROWMD_SET		2
#define D4100_ROWMD_SETPNT	3

// D4100 TPG Select Bits
#define D4100_TPG_SELECT_TPG_EN		0x0001
#define D4100_TPG_SELECT_SW_EN		0x0002
#define D4100_TPG_SELECT_PAT_FORCE	0x0004

// D4100 SW override bits 
#define D4100_SW_OVERRIDE_BIT1		0x0001
#define D4100_SW_OVERRIDE_BIT2		0x0002
#define D4100_SW_OVERRIDE_BIT3		0x0004
#define D4100_SW_OVERRIDE_BIT4		0x0008
#define D4100_SW_OVERRIDE_BIT5		0x0010
#define D4100_SW_OVERRIDE_BIT6		0x0020
#define D4100_SW_OVERRIDE_BIT7		0x0040
#define D4100_SW_OVERRIDE_BIT8		0x0080
