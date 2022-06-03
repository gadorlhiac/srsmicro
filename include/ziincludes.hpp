#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <map>
#include <string>

#include "ziAPI.h"
#include "ziUtils.hpp"

// These may be modified to match the device's configuration.
#define DEMOD_COUNT 1
#define PID_COUNT 0
#define DEV_ID "dev1292"
#define PORT 8005
#define DEV_INTFC "USB" // Can be "USB, 1GbE" or "PCIe"
