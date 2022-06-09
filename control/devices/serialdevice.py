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
        """! The SerialDevice base class initializer."""
        super(SerialDevice, self).__init__(name)
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

        ## @var _cmd_result
        # Last message read back from the device. Used to report results.
        # self._cmd_result: str = ''

        ## @var _comtime
        # Time (in seconds) to wait before reading back the result of a command.
        self._comtime: float = 0.1

        ## @var name
        # Device identifier for simplifying signal and slot operation
        self.name = name

        ## @var _cond_vars
        # (dict) Dictionary with device parameters and their associated values
        self._cond_vars = {}

        ## @var _logs
        # (str) Device specific logging
        self._logs = ''

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
    # @property
    # def cmd_result(self):
    #     """! Property for the private _cmd_result
    #     @return _cmd_result (str) The last message read from the device.
    #     """
    #     return self._cmd_result
    #
    # @cmd_result.setter
    # def cmd_result(self, val):
    #     """! Property setter for the command result.
    #     @param val (str) String to set the command result to. Intended to hold
    #     description of the last action taken, e.g. setting a parameter such as the
    #     COM port, or a device specific error message.
    #     """
    #     self._cmd_result = val

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

    @property
    def comtime(self):
        """! Property for the default time to wait after writing a command.
        @return _comtime (float) Wait time in seconds.
        """
        return self._comtime

    @comtime.setter
    def comtime(self, val):
        """! Property setter for changing the default time to wait after writing
        a command.
        @param val (float) Wait time in seconds.
        """
        try:
            if type(val) != float:
                raise TypeError('Communication wait time must be float.')
            self._comtime = val
            # self.cmd_result = 'Communication wait time set to: {}'.format(val)
            self.cmd_result.emit('Communication wait time set to: {}'.format(val))

        except TypeError as err:
            # self.cmd_result = 'Communication time not changed. {}'.format(str(err))
            self.cmd_result.emit('Communication time not changed. {}'.format(str(err)))

        except Exception as err:
            # self.cmd_result = 'Communication wait time not changed. Error: {}'.format(str(err))
            self.cmd_result.emit('Communication wait time not changed. Error: {}'.format(str(err)))

    @property
    def cond_vars(self):
        """! Property for returning the device parameters and values
        """
        return self._cond_vars

    def return_state(self):
        """! Performs device specific status queries. Intended for execution
        on a separate thread, so it can be run infinitely at given intervals.
        Must be overloaded on a per device basis to account for differences in
        communication syntax. Has no return value. Instead emits a signal with
        the necessary information.
        """
        self.state.emit(self.name, 'loop', 'loop')

    @property
    def logs(self):
        """! Property to return device specific log information, such as
        errors and communication updates over the serial port. There is no
        setter for this property as the device manages its logs internally.
        """
        return self._logs

    @property
    def current_time(self):
        """! Property to return current time. Useful for logging purposes."""
        return time.asctime(time.localtime(time.time()))
