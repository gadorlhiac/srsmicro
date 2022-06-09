"""!
@brief Definition of base class for devices using serial communication.
"""

from .device import Device
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
from serial import Serial
import time

class SerialDevice(Device):
    """The base class for serial devices.

    Defines the base class used by devices whose serial communication is managed
    directly. Currently includes:
    - Prior sample stage
    - Insight DS+ femtosecond laser/OPO
    - Newport FCL200 optical delay stage
    """

    def __init__(self, name='Serial Device'):
        """! The SerialDevice base class constructor."""
        super().__init__(name)
        ## @var _sercom
        # Serial object to manage communication.
        self._sercom = Serial(timeout=0)

        ## @var _comport
        # Serial communication port. E.g. 'COM1'
        self._comport: str = ''

        ## @var _isconnected
        # (Boolean) Is the serial port open or closed.
        self._isconnected = False

        ## @var _baudrate
        # Baud rate for serial communication.
        self._baudrate: int = 115200

    # Connecting and communicating
    ############################################################################
    def _open(self):
        """! Private function which opens communication over a serial port."""
        self._sercom.port = self.comport
        self._sercom.open()

    def _close(self):
        """! Private function which closes communication over a serial port."""
        self._sercom.close()

    def write(self, cmd, waittime):
        """! Write a command to the serial device.
        @param cmd (str) The command to be written
        @param waittime (float) The time to wait after writing a command. Blocks
        communication, preventing writing multiple commands before the
        device can respond.
        """
        self._sercom.write(b'{}\n'.format(cmd))
        time.sleep(waittime)

    def read(self):
        """! Read back an answer from the serial device.
        @return (str) The ASCII decoded result from reading back from the device.
        """
        return self._sercom.readline().decode('ascii')

    # Properties for setting values and retrieving results
    ############################################################################
    @property
    def baudrate(self):
        """! Property for the communication baud rate.
        @return _baudrate (int) Communication baud rate.
        """
        return self._baudrate

    @baudrate.setter
    def baudrate(self, val):
        """! Property setter for the communication baud rate.
        @param val (int) Baud rate.
        """
        self._baudrate = val
        # self.cmd_result = 'Baud rate set to: {}'.format(val)

    @property
    def comport(self):
        """! Property for the communication port.
        @return _comport (str) Communication port. E.g. 'COM1'
        """
        return self._comport

    @comport.setter
    def comport(self, val):
        """! Property setter for changing the communication port.
        @param val (str) New communication port. E.g. 'COM1'
        """
        try:
            if type(val) != str:
                raise TypeError('Communication port must be str.')

            if val[:3] != 'COM':
                if val[3] not in range(1, 9):
                    raise ValueError('Communication port must be in format \'COMX\' \
                                      where X is an integer.')

            self._comport = val
            # self.cmd_result = 'COM port set to: {}'.format(val)

        except TypeError as err:
            # self.cmd_result = 'COM port not changed. {}'.format(str(err))
            self.cmd_result.emit('COM port not changed. {}'.format(str(err)))

        except ValueError as err:
            # self.cmd_result = 'COM port not changed. {}'.format(str(err))
            self.cmd_result.emit('COM port not changed. {}'.format(str(err)))

        except Exception as err:
            # self.cmd_result = 'COM port not changed. Error: {}'.format(str(err))
            self.cmd_result.emit('COM port not changed. Error: {}'.format(str(err)))

            self._comport = val
            # self.cmd_result = 'COM port set to: {}'.format(val)
            self.cmd_result.emit('COM port set to: {}'.format(val))
