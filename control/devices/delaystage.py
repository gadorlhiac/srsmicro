"""!
@brief Definition of the DelayStage class for interaction with the Newport FCL200 delay stage as well as
custom exception classes PositionerError and CommandError for parsing the corresponding error codes.
"""

from .serialdevice import SerialDevice
from PyQt5.QtCore import pyqtSignal as Signal

class DelayStage(SerialDevice):
    """The DelayStage class for controlling the Newport FCL200 delay stage.
    Extends the SerialDevice class with device specific methods and variables.
    """
    ## @var _controller_state
    # (dict[str]:str) Dictionary reference for definitions of two hexadecimal delay stage state responses.
    _controller_state = {
                          '0A': 'NOT REFERENCED from RESET.',
                          '0B' : 'NOT REFERENCED from HOMING.',
                          '0C' : 'NOT REFERENCED from CONFIGURATION.',
                          '0D' : 'NOT REFERENCED from DISABLE.',
                          '0E' : 'NOT REFERENCED from READY.',
                          'OF' : 'NOT REFERENCED from MOVING.',
                          '10' : 'NOT REFERENCED - NO PARAMETERS IN MEMORY.',
                          '14' : 'CONFIGURATION',
                          '1E' : 'HOMING.',
                          '28' : 'MOVING.',
                          '32' : 'READY from HOMING.',
                          '33' : 'READY from MOVING.',
                          '34' : 'READY from DISABLE.',
                          '3C' : 'DISABLE from READY.',
                          '3D' : 'DISABLE from MOVING.' }
    cmds = { 'pos' : '1TP',
             'vel' : '1VA',
             'accel' : '1AC' }
    # cmd_result = Signal(str)

    def __init__(self, name='Delay Stage'):
        """! The DelayStage class initializer.
        Initiliazes comport (inherited from SerialDevice) to COM7
        """
        super().__init__(name)
        self.comport = 'COM7'

        ## @var _cond_vars
        # (dict[str]:str) Holds current delay stage conditions. Keys: pos, vel, accel, cmd_err, pos_err
        self._cond_vars = {'pos':'', 'vel':'', 'accel':'',
                           'cmd_err': 'No Error.', 'pos_err' : '', 'op_state': ''}

    # State and error checking
    ############################################################################
    def check_errors(self):
        """! Check for command errors and also query state.
        Errors are accessed through raising a CommandError exception. The class
        definition for the exception contains the error code definitions.
        """
        try:
            # Query what the last command error was and store it.
            self.write(b'1TE', self.comtime)
            resp = self.read()[3:].strip()

            self._cond_vars['cmd_err'] = str(CommandError(resp))

            # Raise error if response is other than '@' (no error)
            if resp != '@':
                raise CommandError(resp)

        except CommandError as e:
                    # self.cmd_result = 'Command error: {}'.format(str(e))
            pass
        except Exception as e:
            # self.cmd_result = 'Error: {}'.format(str(e))
            pass

    def _query_state(self):
        """! Query device state and parse any positioner errors.
        Errors are accessed through raising a PositionerError exception. The
        class definition for the exception contains the error code definitions.
        """
        self.check_errors()
        self._read_current_conditions()
        try:
            # Query state which returns 6 characters
            self.write(b'1TS', self.comtime)
            resp = self.read()

            # The last two characters represent the delay stage state as a
            # hexadecimal number, but no processing is required. The state is
            # read directly from the class variable _controller_state defined
            # above.
            self._cond_vars['op_state'] = self._controller_state[resp[7:9]]

            # The first four characters are the error code and represent
            # hexadecimal digits. These form a 16-digit number in binary
            # representation. A 1 in any position flags an error, which is
            # defined in the class variable _pos_errors of the PositionerError.
            bin_repr = format(int(qs[3:7], 16), '0>16b')
            if '1' in bin_repr:
                raise PoisionerError(bin_repr)

            # self.cmd_result = 'Read state and checked for positioner errors.'

        except PositionerError as e:
            self._cond_vars['pos_err'] = str(e)
            # self.cmd_result = 'Positioner error: {}'.format(str(e))
            self.cmd_result.emit('Positioner error: {}'.format(str(e)))

        except Exception as e:
            # self.cmd_result = 'Error: {}'.format(str(e))
            self.cmd_result.emit('Error: {}'.format(str(e)))
            pass

    def _read_current_conditions(self):
        for cmd in self.cmds:
            self.write('{}?'.format(self.cmds[cmd]), self.comtime)
            self._cond_vars[cmd] = self.read()[3:].strip()
    # def return_state(self):
    #     pass

    # def _read_status(self):
    # """!
    # Full status including operational state, history of error codes,
    # and any current error codes. Also reads values such as humidity,
    # current, and diode temperature.
    # """
    #     # Query current position, velocity, acceleration and any errors
    #     for cmd in self._cond_vars.keys():
    #         self.write('{}?'.format(cmd), self.comtime)
    #         resp = self.read()[3:].strip()
    #
    #         if cmd == 'cmd_err':
    #             self._cond_vars[cmd] = str(CommandError(resp))
    #
    #         elif cmd == 'pos_err':
    #             self._cond_vars[cmd] = str(PositionerError(resp))
    #
    #         else:
    #             self._cond_vars[cmd] = resp

    # @property
    # def status(self):
    #     self._read_status()

    # Motion and parameter setting
    ############################################################################
    def _move_relative(self, val):
        """! Move the stage to a new absolute position.
        First calculates the time required to move to the new position. This
        time is used to block communication until the move is completed.
        @param val (float) The relative motion to make.
        """
        try:
            newpos = float(self._cond_vars['pos']) + val
            if newpos < -100 or newpos > 100:
                raise ValueError('Trying to move beyond the limits of the stage.')
            # Query the device to determine how long the relative move will take.
            self.write(b'1PT{:.4f}'.format(val), self.comtime)
            t = float(self.read()[3:])

            # Move to the new position, using the time calculated above as the amount
            # of time to wait/block further communication.
            self.write(b'1PR{:.4f}'.format(val), t + self.comtime)
            # self.cmd_result = self.read()
            self.cmd_result.emit(self.read())

            # Perform error checking
            self.check_errors()

            # Double check the position by querying the delay stage again.
            # Update the _cond_vars dictionary appropriately.
            self.write(b'1TP?', self.comtime)
            self._cond_vars['pos'] = self.read()[3:]

        except Exception as err:
            # self.cmd_result = 'Delay stage not moved. {}'.format(str(err))
            self.cmd_result.emit('Delay stage not moved. {}'.format(str(err)))

    def _move_absolute(self, val):
        """! Move the stage to a new absolute position.
        Makes use of the _move_relative method because obtaining an estimate
        of the time required to make the movement requires calculating the
        relative position difference.
        @param val (float) The absolute position to move the delay stage to.
        """
        try:
            if val < -100. or val > 100.:
                raise ValueError('Position must be between -100 and 100.')
            # Calculate the relative move between the current position and the
            # desired position.
            rel_mov = np.abs(val - float(self._cond_vars['pos']))
            self._move_relative(rel_mov)

        except Exception as err:
            # self.cmd_result = 'Delay stage not moved. {}.'.format(str(err))
            self.cmd_result.emit('Delay stage not moved. {}.'.format(str(err)))

    # On application close
    ############################################################################
    # Not needed, using super class routine is fine for this device.
    # def exit(self):
    #     if self._isconnected:
    #         self.write('OFF', self.comtime)
    #     self.close()


# PositionerError
################################################################################

class PositionerError(Exception):
    """Exception class for positioner errors for the Newport FCL200 delay stage.
    """
    ## @var _pos_errors
    # (list[str]:str) String definitions for given integer error codes. The definition is returned by using the error code as the index on the list.
    _pos_errors = ['Not used.',
                   'Not used.',
                   'Not used.',
                   'Not used.',
                   'Driver overheating.',
                   'Driver fault.',
                   'Not used.',
                   'Not used.',
                   'No parameters in memory.',
                   'Homing time out.',
                   'Not used.',
                   'Newport reserved.',
                   'RMS current limit.',
                   'Not used.',
                   'Positive end of run.',
                   'Negative end of run.']

    def __init__(self, error_code):
        """! PositionError class initializer.
        @param error_code (list[int]) List of error codes. Definitions are
        accessed through class array _pos_errors.
        """
        self.msg = ''
        # Run through the digits and append the errors.
        # Reading the 16 digit number from left to right, a 1 in that digit's
        # position gives the error contained in _pos_errors at that index. E.g.
        # A 1 in the fifth digit from left to right (array index 4, since
        # counting from 0) indicates an error _pos_errors[4] (Driver overheating.)
        for i in range(16):
            if error_code[i] == '1':
                self.msg += '{} '.format(self._pos_errors[i])

    def __str__(self):
        """! String representation of the PositionError on print
        @return self.msg (str)
        """
        return self.msg

# CommandError
################################################################################

class CommandError(Exception):
    """Exception class for command errors for the Newport FCL200 delay stage.
    """
    ## @var _cmd_errors
    # (dict[str]:str) String definitions for given command error codes. Command errors are given as characters which are the keys of the dictionary.
    _cmd_errors = {
        '@' : 'No error',
        'A' : 'Unknown message code or floating point controller address.',
        'B' : 'Controller address not correct.',
        'C' : 'Parameter missing or out of range.',
        'D' : 'Command not allowed.',
        'E' : 'Home sequence already started.',
        'G' : 'Displacement out of limits.',
        'H' : 'Command not allowed in NOT REFERENCED state.',
        'I' : 'Command not allowed in CONFIGURATION state.',
        'J' : 'Command not allowed in DISABLE state.',
        'K' : 'Command not allowed in READY state.',
        'L' : 'Command not allowed in HOMING state.',
        'M' : 'Command not allowed in MOVING state.',
        'N' : 'Current position out of software limit.',
        'S' : 'Communication Time Out.',
        'U' : 'Error during EEPROM access.',
        'V' : 'Error during command execution.'
    }
    def __init__(self, error_code):
        """! CommandError class initializer.
        @param error_code (str) Character for the received command error. Definitions
        are accessed through class dict _cmd_errors.
        """
        self.msg = self._cmd_errors[error_code]

    def __str__(self):
        """! String representation of the CommandError on print
        @return (str) self.msg
        """
        return self.msg
