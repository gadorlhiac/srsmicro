#! /usr/bin/env python

import numpy as np
import time
from .device import *

# Commands from sub-class devices don't need to include the newline
# character as it is included here


class SampleStage(SerialDevice):
    """
    Facilitates serial communication with Prior Scientific sample stage.
    Sample stage is needed for Y-dimension motion while acquiring hyperspectral
    images, to avoid scanning spectrum across Y.

    Args:
    """
    def __init__(self):
        super().__init__()
        self._baudrate = 9600
