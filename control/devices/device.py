"""!
@brief Definition of base class for communicating with physical devices.
"""

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
import time

class Device(QObject):
    """! The base device class.

    Provides basic interface for interacting with device parameters, logging,
    and using Qt Signals and Slots.
    """
    ## @var cmd_result
    # (Signal) For relaying device parameters and values.
    state = Signal(object, object)

    ## @var cmd_result
    # (Signal) Last message read back from the device. Used to report results.
    cmd_result = Signal(str)

    def __init__(self, name='Device'):
        """! The SerialDevice base class initializer."""
        super().__init__()

        ## @var name
        # Device identifier for simplifying signal and slot operation
        self.name = name

        ## @var _isconnected
        # (Boolean) Is the serial port open or closed.
        self._isconnected: bool = False

        ## @var _cond_vars
        # (dict) Dictionary with device parameters and their associated values
        self._cond_vars: dict = {}

        ## @var _comtime
        # Time (in seconds) to wait before reading back the result of a command.
        self._comtime: float = 0.1

        ## @var _logs
        # (str) Device specific logging
        self._logs: str = ''

    # Connecting and communicating
    ############################################################################
    def open(self):
        """! Open communication with the physical device."""
        try:
            self._open()
            self._isconnected = True
            self._logs += '{} Opened communication with {}\n'.format(self.current_time, self.name)
            self.cmd_result.emit('Succesfully opened communication.')

        except Exception as err:
            self._logs += '{} Unable to open communication with {}: {}'.format(self.current_time, self.name, str(err))
            self.cmd_result.emit('Unable to open communication: {}'.format(str(err)))

    def close(self):
        """! Close communication for the physical device if needed"""
        if self._isconnected:
            try:
                self._close()
                self._isconnected = False
                self._logs += '{} Closed communication with {}.\n'.format(self.current_time, self.name)
                self.cmd_result.emit('Succesfully closed serial port.')

            except Exception as err:
                self._logs += '{} Unable to close communication with {}: {}'.format(self.current_time, self.name, str(err))
                self.cmd_result.emit('Unable to close serial port: {}'.format(str(err)))
        else:
            self._logs += '{} Cannot close communication with {}: not currently \
                           connected.\n'.format(self.current_time, self.name)

    def _open(self):
        """! Private function overwritten by subclasses for the actual device
        specific opening communication.
        """
        pass

    def _close(self):
        """! Private function overwritten by subclasses for the actual device
        specific closing communication.
        """
        pass


    # Properties for setting values and retrieving results
    ############################################################################
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
            self.cmd_result.emit('Communication wait time set to: {}'.format(val))

        except TypeError as err:
            self.cmd_result.emit('Communication time not changed. {}'.format(str(err)))

        except Exception as err:
            self.cmd_result.emit('Communication wait time not changed. Error: {}'.format(str(err)))

    # @property
    # def cond_vars(self):
    #     """! Property for returning the device parameters and values."""
    #     return self._cond_vars

    def parse_cmd(self, param, val):
        """! This function is overwritten by subclasses to perform the actions
        appropriately upon parsing messages from the GUI.
        """
        pass

    def query_state(self):
        """! Performs device specific status queries. Intended for execution
        on a separate thread, so it can be run infinitely at given intervals.
        The associated private method should be overloaded on a per device basis
        to account for differences in communication syntax. This method has no
        return value. Instead the associated private method updates the
        internally managed state and then a signal is emitted with new parameter
        value pairs.
        """
        self._query_state()
        self.state.emit(self.name, self._cond_vars)
        # print(self.name, self._cond_vars.keys(), self._cond_vars.values())

    def _query_state(self):
        pass

    def log(self, msg: str):
        """! Method to emit signal to log a device specific message.
        @param msg (str) Message to be logged.
        """
        self.state.emit(f'{self.name}+Logs', msg)

    @property
    def current_time(self):
        """! Property to return current time. Useful for logging purposes."""
        return time.asctime(time.localtime(time.time()))

    # On application close
    ############################################################################
    def exit(self):
        """! Device shutdown method. Overwritten by subclasses."""
        pass
