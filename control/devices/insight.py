from .serialdevice import SerialDevice
from PyQt5.QtCore import pyqtSignal as Signal

class Insight(SerialDevice):
    """The Insight class for controlling the SpectraPhysics Insight DS+ femtosecond laser/OPO.
    Extends the SerialDevice class with device specific methods and variables.
    """
    ## @var cmds
    # (dict[str]:str) Dictionary reference for the write commands to retrieve or set various laser variables. Keys are the shorthand used in code.
    cmds = {
             'd1_curr': 'READ:PLASer:DIODe1:CURRent' , # Operating current for diode 1
             'd1_hrs': ' READ:PLASer:DIODe1:HOURS', # Operating hours for diode 1
             'd1_temp': 'READ:PLASer:DIODe1:TEMPerature', # Diode 1 Temperature
             'd2_curr': 'READ:PLASer:DIODe2:CURRent', # Operating current for diode 2
             'd2_hrs': 'READ:PLASer:DIODe2:HOURS', # Operating hours for diode 2
             'd2_temp': 'READ:PLASer:DIODe2:TEMPerature', # Diode 2 temperature
             'humidity': 'READ:HUMidity',
             'dsm_max': 'CONT:SLMAX', # Maximum GVD compensation position for insight, given current wavelength
             'dsm_min': 'CONT:SLMIN', # Minimum GVD compensation position for insight, given current wavelength
             'dsm_pos': 'CONT:DSMPOS', # The current GVD compensation position for insight
             'fixed_shutter': 'IRSHUTter', # Open/close 1040 nm shutter
             'main_shutter': 'SHUTter', # Open/close main (OPO) shutter
             'opo_wl': 'WAVelength', # OPO wavelength
             'align' : 'MODE'
           }
    # insight_on: 'ON'
    # insight_off: 'OFF'
    # align_mode: 'ALIGN'
    # run_mode: 'RUN'

    ## @var fault_codes
    # (dict[str]:str) Dictionary reference for numerical fault code meanings
    # when read using the read history command.
    fault_codes = {
                    '000': 'Normal operation.',
                    '056': 'Fault: Hardware timeout. Notify SpectraPhysics if it continues.',
                    '066': 'Fault: Software timeout. Speak with system operator.',
                    '088': 'Fault: Diode thermistor short. Contact SpectraPhysics.',
                    '089': 'Fault: Diode thermistor open. Contact SpectraPhysics.',
                    '090': 'Fault: Diodes too hot (T>30).  Check cooling system.',
                    '091': 'Fault: Diodes warm (T>27).  Check cooling system.',
                    '092': 'Fault: Diodes cold (T<17). Check cooling system.',
                    '117': 'Fault: Internal interlock opened. Contact SpectraPhysics.',
                    '118': 'Fault: CDRH interlock open.',
                    '119': 'Fault: Power supply interlock. Check cable.',
                    '120': 'Fault: Key switch interlock. Turn key.',
                    '129': 'Fault: Very high humidity. Change purge cartridge.',
                    '130': 'Warning: High humidity. Change purge cartridge soon.',
                    '481': 'Fault: Slow diode ramp. Contact SpectraPhysics.',
                    '482': 'Fault: Low fs oscillator power. Contact SpectraPhysics.',
                    '483': 'Fault: low FTO power. Try different wavelengths. Contact SpectraPhysics.'
                 }

    ## @var op_errors
    # (dict[hex]:str) Dictionary reference for operational errors read using the
    # generic status command.
    op_errors = { 0x00000200 : 'User interlock open. Laser forced off.',
                  0x00000400 : 'Safety keyswitch interlock open. Laser forced off.',
                  0x00000800 : 'Power supply interlock open. Laser forced off.',
                  0x00001000 : 'Internal interlock open. Laser forced off.',
                  0x00004000 : 'Detecting a warning. Check history for cause.',
                  0x00008000 : 'Faul detected. Laser diodes turned off. Check history.',
                }

    # cmd_result = Signal(str)

    def __init__(self, name='Insight'):
        """! The Insight class initializer.
        Initiliazes comport (inherited from SerialDevice) to COM6
        """
        super().__init__(name)
        self.comport = 'COM6'
        # self._isconnected = False
        # self._cmd_result = ''

        # Status of laser and shutters (on, off, hibernating, etc)
        # self._op_state = 'Off'
        # self._main_shutter = 0
        # self._fixed_shutter = 0

        self._cond_vars = dict.fromkeys(Insight.cmds.keys(), '-')
        self._cond_vars['main_shutter'] = 0
        self._cond_vars['fixed_shutter'] = 0
        self._cond_vars['op_state'] = 'Ready to turn on'
        # self.name = name

    # Error checking
    ############################################################################
    def _query_state(self):
        """! Read the full status including operational state, history of error
        codes, and any current error codes. Also reads values such as humidity,
        current, and diode temperature.
        """
        self.write('{}'.format(self.cmds['align']), self.comtime)
        self._cond_vars['align'] = self.read()

        self.write('*STB?', self.comtime)
        resp = int(self.read())

        self._cond_vars['main_shutter'] = resp & 0x00000004
        self._cond_vars['fixed_shutter'] = resp & 0x00000008

        self._check_errors(resp)
        # self._cond_vars['history'] = self._read_history()
        self._read_history()
        self._cond_vars['op_state'] = self._parse_op_state((resp >> 16))
        # self._history = self._read_history()
        # self._op_state = self._parse_op_state((resp >> 16))

    def _check_errors(self, state: str):
        self._cond_vars['op_errors'] = ''
        found_error = False
        for key in self.op_errors:
            if (state & key):
                self._cond_vars['op_errors'] += self.op_errors[key]
                self.cmd_result.emit('Insight: {}'.format(self.op_errors[key]))
                found_error = True
        if not found_error:
            self._cond_vars['op_errors'] = 'None'
            self.cmd_result.emit('Insight: Checked for errors. None found.')

    def _read_history(self):
        """! Reads error code history from the insight startup buffer"""
        # Note: The Insight manual in the description of the serial commands
        # lists the history command as 'READ:HIStory?'. This is incorrect.
        # Appendix B, where the codes are explained is correct:
        # 'READ:AHIS?'
        try:
            self.write('READ:AHIS?', self.comtime)
            codes = self.read().strip().split(' ')
            history = ''
            for code in codes:
                history += '{}: {}\n'.format(code, self.fault_codes[code])

            self._cond_vars['history'] = history
            self.cmd_result = 'Read from history buffer. Appended to logs.'
        except Exception as e:
            err = 'Error while reading history: {}'.format(str(e))
            self._cond_vars['history'] = err
            self.cmd_result.emit(err)

    # Current laser status
    def _parse_op_state(self, resp: int) -> str:
        """! Return current state in text form.
        @param resp (int) Numeric code corresponding to operational state of laser.
        @return state (str) Text description of laser state.
        """
        if resp < 25:
            state = 'Initializing'
        elif resp == 25:
            state = 'Ready to turn on'
        elif resp < 50:
            return 'Turning on and/or optimizing'
        elif resp == 50:
            state = 'RUN'
        elif resp < 60:
            state = 'Moving to align mode'
        elif resp == 60:
            state = 'Align mode'
        elif resp < 70:
            state = 'Exiting align mode'
        else:
            state = 'Reserved'
        return state

    def _read_current_conditions(self):
        for cmd in self._cond_vars:
            self.write(b'{}?'.format(cmds[i]), self._comtime)
            self._cond_vars[i] = self.read().strip()

    def parse_cmd(self, param, val):
        if param == 'op_state':
            if val == 'RUN':
                self._cond_vars['op_state'] = 'RUN'
            # if self._cond_vars['op_state'] == 'RUN':
            #     self.write('OFF', self.comtime)
            # else:
            #     self.write('ON')
        elif param == 'main_shutter':
            if self._cond_vars['main_shutter']:
                self.write('{} 0'.format(self.cmds['main_shutter'], self.comtime))
            else:
                self.write('{} 1'.format(self.cmds['main_shutter'], self.comtime))
        elif param == 'fixed_shutter':
            if self._cond_vars['fixed_shutter']:
                self.write('{} 0'.format(self.cmds['main_shutter'], self.comtime))
            else:
                self.write('{} 1'.format(self.cmds['main_shutter'], self.comtime))
        elif param == 'opo_wl':
            self.write('{}{}'.format(self.cmds['opo_wl'], val), self.comtime)
        elif param == 'align':
            if self._cond_vars['align'] == 'RUN':
                self.write('{} ALIGN'.format(self.cmds['align'], val), self.comtime)
            else:
                self.write('{} RUN'.format(self.cmds['align'], val), self.comtime)


    # @property
    # def cond_vars(self) -> dict:
    #     return self._cond_vars

    # def return_state(self):
    #     pass

    # On application close
    ############################################################################
    def exit(self):
        if self._isconnected:
            self.write('OFF', self.comtime)
        self.close()
