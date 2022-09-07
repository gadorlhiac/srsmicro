"""!
@brief Definition of the DelayStage class for interaction with the Newport FCL200 delay stage as well as
custom exception classes PositionerError and CommandError for parsing the corresponding error codes.

Classes:
DelayStage
PositionError
CommandError
"""

from .serialdevice import SerialDevice
from serial.serialutil import PortNotOpenError
from PyQt5.QtCore import pyqtSignal as Signal

class DelayStage(SerialDevice):
    """! The DelayStage class for controlling the Newport FCL200 delay stage.

    Extends the SerialDevice class with device specific methods and variables.

    Properties:
    -----------

    Methods:
    --------
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
    ## @var cmds
    # (dict[str]:str) Dictionary reference for serial commands to the delay stage.
    cmds = { 'pos' : '1TP',
             'vel' : '1VA',
             'accel' : '1AC' }
    # cmd_result = Signal(str)

    def __init__(self, name = 'Delay Stage'):
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
    def _query_state(self):
        """! Query device state and parse any positioner errors.
        Errors are accessed through raising a PositionerError exception. The
        class definition for the exception contains the error code definitions.
        """
        self.check_errors()
        self._read_current_conditions()
        try:
            # Query state which returns 6 characters
            self.write('1TS', self.comtime)
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
            bin_repr = format(int(resp[3:7], 16), '0>16b')
            if '1' in bin_repr:
                raise PoisionerError(bin_repr)

            # self.cmd_result = 'Read state and checked for positioner errors.'

        except PositionerError as err:
            self._cond_vars['pos_err'] = str(e)
            # self.cmd_result = 'Positioner error: {}'.format(str(e))
            self.cmd_result.emit(f'Positioner error: {str(err)}')

        except PortNotOpenError as err:
            pass
            # self.log('Not connected to Insight.')
            # self.cmd_result.emit('Not connected to Insight.')

        except Exception as e:
            # self.cmd_result = 'Error: {}'.format(str(e))
            self.cmd_result.emit(f'Error: {str(err)}')
            pass

    def check_errors(self):
        """! Check for command errors and also query state.
        Errors are accessed through raising a CommandError exception. The class
        definition for the exception contains the error code definitions.
        """
        try:
            # Query what the last command error was and store it.
            self.write('1TE', self.comtime)
            resp = self.read()[3:].strip()

            self._cond_vars['cmd_err'] = str(CommandError(resp))

            # Raise error if response is other than '@' (no error)
            if resp != '@':
                raise CommandError(resp)

        except CommandError as err:
            # self.cmd_result = 'Command error: {}'.format(str(e))
            pass
        except PortNotOpenError as err:
            pass
            # self.cmd_result.emit('Not connected to delay stage.')
        # except Exception as e:
        #     # self.cmd_result = 'Error: {}'.format(str(e))
        #     pass

    def _read_current_conditions(self):
        for cmd in self.cmds:
            try:
                self.write(f'{self.cmds[cmd]}?', self.comtime)
                self._cond_vars[cmd] = self.read()[3:].strip()
            except PortNotOpenError as err:
                self._cond_vars[cmd] = '-'
                # self.cmd_result.emit('Not connected to delay stage.')

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
            self.write(f'1PT{abs(val):.4f}', self.comtime)
            t = float(self.read()[3:])

            # Move to the new position, using the time calculated above as the amount
            # of time to wait/block further communication.
            self.write(f'1PR{val:.4f}', t + self.comtime)
            # self.cmd_result = self.read()
            self.cmd_result.emit(self.read())

            # Perform error checking
            self.check_errors()

            # Double check the position by querying the delay stage again.
            # Update the _cond_vars dictionary appropriately.
            self.write('1TP?', self.comtime)
            self._cond_vars['pos'] = self.read()[3:]
        except PortNotOpenError as err:
            self.log('Not connected to delay stage.')
            self.cmd_result.emit('Not connected to delay stage.')

        except Exception as err:
            self.log('Not connected to delay stage.')
            # self.cmd_result = 'Delay stage not moved. {}'.format(str(err))
            self.cmd_result.emit(f'Delay stage not moved. {str(err)}')

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
            rel_mov = val - float(self._cond_vars['pos'])
            self._move_relative(rel_mov)
        except PortNotOpenError as err:
            self.log('Not connected to delay stage.')
            self.cmd_result.emit('Not connected to delay stage.')

        except Exception as err:
            self.log('Not connected to delay stage.')
            # self.cmd_result = 'Delay stage not moved. {}.'.format(str(err))
            self.cmd_result.emit(f'Delay stage not moved. {str(err)}.')

    def parse_cmd(self, param, val):
        try:
            if param == 'abs_move':
                self._move_absolute(float(val))
            elif param == 'rel_move_neg':
                self._move_relative(-1*float(val))
            elif param == 'rel_move_pos':
                self._move_relative(float(val))
            elif param == 'vel':
                self.write(f'{self.cmds["vel"]}{val}', self.comtime)
            elif param == 'accel':
                self.write(f'{self.cmds["accel"]}{val}', self.comtime)

        except PortNotOpenError as err:
            self.log('Not connected to delay stage.')
            self.cmd_result.emit('Not connected to delay stage.')

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
    """! Exception class for positioner errors for the Newport FCL200 delay
    stage.
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
                self.msg += f'{self._pos_errors[i]} '

    def __str__(self):
        """! String representation of the PositionError on print
        @return self.msg (str)
        """
        return self.msg

# CommandError
################################################################################

class CommandError(Exception):
    """! Exception class for command errors for the Newport FCL200 delay stage.
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
