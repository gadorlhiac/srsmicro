"""!
@brief Definition of base class for devices using serial communication.
"""

from serial import Serial
import time

class SerialDevice:
    """The base class for serial devices.

    Defines the base class used by devices whose serial communication is managed
    directly. Currently includes:
    - Prior sample stage
    - Insight DS+ femtosecond laser/OPO
    - Newport FCL200 optical delay stage
    """

    def __init__(self):
        """! The SerialDevice base class initializer."""
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
        self._cmd_result: str = ''

        ## @var _comtime
        # Time (in seconds) to wait before reading back the result of a command.
        self._comtime: float = 0.1

    def open_com(self):
        """! Open communication for the device on port: comport"""
        try:
            self._sercom.open()
            self._isconnected = True
        except:
            pass

    def close_com(self):
        """! Close communication for the device on port: comport"""
        if self._isconnected:
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
    def cmd_result(self):
        """! Property for the private _cmd_result
        @return _cmd_result (str) The last message read from the device.
        """
        return self._cmd_result

    @cmd_result.setter
    def cmd_result(self, val):
        """! Property setter for the command result.
        @param val (str) String to set the command result to. Intended to hold
        description of the last action taken, e.g. setting a parameter such as the
        COM port, or a device specific error message.
        """
        self._cmd_result = val

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
        self.cmd_result = 'Baud rate set to: {}'.format(val)

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
            self.cmd_result = 'COM port set to: {}'.format(val)

        except TypeError as err:
            self.cmd_result = 'COM port not changed. {}'.format(str(err))

        except ValueError as err:
            self.cmd_result = 'COM port not changed. {}'.format(str(err))

        except Exception as err:
            self.cmd_result = 'COM port not changed. Error: {}'.format(str(err))

            self._comport = val
            self.cmd_result = 'COM port set to: {}'.format(val)

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
            self.cmd_result = 'Communication wait time set to: {}'.format(val)

        except TypeError as err:
            self.cmd_result = 'Communication time not changed. {}'.format(str(err))

        except Exception as err:
            self.cmd_result = 'Communication wait time not changed. Error: {}'.format(str(err))
