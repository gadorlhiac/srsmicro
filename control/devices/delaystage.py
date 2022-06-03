from .serialdevice import SerialDevice
class DelayStage(SerialDevice):
    def __init__(self):
        super().__init__()
        self._comport = 'COM7'
        self._cond_vars = {'pos':'', 'vel':'', 'accel':''}

    # Error checking
    ############################################################################
    def _read_status(self):
        """
        Full status including operational state, history of error codes,
        and any current error codes. Also reads values such as humidity,
        current, and diode temperature.
        """
        for cmd in self._cond_vars.keys():
            self.write('{}?'.format(cmd), self._comtime)
            resp = self.read()[3:].strip()
            self._cond_vars = resp

    def _move_stage(self, val):
        rel_mov = np.abs(val - float(self._cond_vars['pos']), self._comtime)
        self.write(b'1PT{:.4f}'.format(rel_mov))
        t = float(self.read()[3:])

        self.write(b'1PA{:.4f}'.format(val), t + self._comtime)
        self.read()
        self.check_errors()

        self.write(b'1TP?', self._comtime)
        self._cond_vars['pos'] = self.read()[3:]


    def _check_errors(self, s):
        """Check for command errors and also query state"""
        try:
            self.write(b'1TE', self._com_time) # Last command error
            self._status['cmd_err'] = self.read()[3:].strip()
            if self._cmd_error != '@':
                self._status['pos_err'] = 'Not read.'
                raise CommandError(self._status['cmd_err'])

            self.write(b'1TS', self._status['com_time'])
            qs = self.read()

            self._status['state'] = self._states[qs[7:9]]

            pos_err = qs[3:7]
            mask = 0b1111111111101111
            error_code = bin(int(pos_error, 16))[2:].zfill(16)
            if int(error_code, 2) & mask:
                raise PositionerError(error_code)
            self._status['last_action'] = 'Read state and checked errors.'
        except PositionerError as e:
            self._status['pos_err'] = str(e)
            self._status['last_action'] = 'Positioner error: {}'.format(str(e))
        except CommandError as e:
            self._status['cmd_err'] = str(e)
            self._status['last_action'] = 'Command error: {}'.format(str(e))
        except Exception as e:
            self._status['last_action'] = 'Error: {}'.format(str(e))

    @property
    def status(self):
        self._read_status()

class PositionerError(Exception):
    _pos_errors = np.array(
        [
          'Not used', 'Not used', 'Not used', 'Not used',
          'Driver overheating', 'Driver fault', 'Not used', 'Not used',
          'No parameters in memory', 'Homing time out', 'Not used',
          'Newport reserved', 'RMS current limit', 'Not used',
          'Positive end of run', 'Negative end'
        ]
     )

    """Exception for positioner error"""
    def __init__(self, error_code):
        mask = []
        for b in error_code:
            mask.append(bool(int(b)))

        self.msg = ', '.join(self._pos_errors[mask])

    def __str__(self):
        return self.msg

class CommandError(Exception):
    _cmd_errors = {
        '@' : 'No error',
        'A' : 'Unknown message code or floating point controller address',
        'B' : 'Controller address not correct',
        'C' : 'Parameter missing or out of range',
        'D' : 'Command not allowed',
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
        self.msg = self._cmd_errors[error_code]

    def __str__(self):
        return self.msg         
