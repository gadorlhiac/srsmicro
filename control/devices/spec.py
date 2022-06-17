"""!
@brief Definition of the Spec class for interacting with the Optosky spectrometer.
"""

from .device import Device
# from .wrappers.spec import SpecWrapper
from PyQt5.QtCore import pyqtSignal as Signal

class Spec(Device):
    """! See Kcube definition.
    """

    def __init__(self, name='Insight'):
        """! The Insight class initializer.
        Initiliazes comport (inherited from SerialDevice) to COM6
        """
        super().__init__(name)

        # self._wrapper = KcubeWrapper()

        self._cond_vars['pos'] = 0
        self._cond_vars['vel'] = 0
        self._cond_vars['accel'] = 'Ready to turn on'
        # self.name = name

    # Error checking
    ############################################################################
    def _query_state(self):
        """! Read the full status including operational state, history of error
        codes, and any current error codes. Also reads values such as humidity,
        current, and diode temperature.
        """
        pass
        # self.write('{}'.format(self.cmds['align']), self.comtime)
        # self._cond_vars['align'] = self.read()
        # self._read_current_conditions()
        # try:
        #     self.write('*STB?', self.comtime)
        #     resp = int(self.read())
        #
        #     self._cond_vars['main_shutter'] = resp & 0x00000004
        #     self._cond_vars['fixed_shutter'] = resp & 0x00000008
        #
        #     self._check_errors(resp)
        #     # self._cond_vars['history'] = self._read_history()
        #     self._read_history()
        #     self._cond_vars['op_state'] = self._parse_op_state((resp >> 16))
        #     # self._history = self._read_history()
        #     # self._op_state = self._parse_op_state((resp >> 16))
        # except:
        #     self._cond_vars['main_shutter'] = 0
        #     self._cond_vars['fixed_shutter'] = 0
        #     self._cond_vars['op_state'] = 'Ready to turn on'
        #     self._cond_vars['op_errors'] = 'Insight off'
        #     self._cond_vars['history'] = 'Insight off'

    def parse_cmd(self, param, val):
        pass
        # if param == 'op_state':
        #     if val == 'RUN':
        #         # self._cond_vars['op_state'] = 'RUN'
        #         if self._cond_vars['op_state'] == 'RUN':
        #             self.write('OFF', self.comtime)
        #             self.cmd_result.emit('Turning laser off.')
        #         else:
        #             self.write('ON', self.comtime)
        #             self.cmd_result.emit('Turning laser on.')
        # elif param == 'main_shutter':
        #     if self._cond_vars['main_shutter']:
        #         self.write('{} 0'.format(self.cmds['main_shutter']), self.comtime)
        #     else:
        #         self.write('{} 1'.format(self.cmds['main_shutter']), self.comtime)
        # elif param == 'fixed_shutter':
        #     if self._cond_vars['fixed_shutter']:
        #         self.write('{} 0'.format(self.cmds['fixed_shutter']), self.comtime)
        #     else:
        #         self.write('{} 1'.format(self.cmds['fixed_shutter']), self.comtime)
        # elif param == 'opo_wl':
        #     self.write('{}{}'.format(self.cmds['opo_wl'], val), self.comtime)
        # elif param == 'align':
        #     if self._cond_vars['align'] == 'RUN':
        #         self.write('{} ALIGN'.format(self.cmds['align'], val), self.comtime)
        #     else:
        #         self.write('{} RUN'.format(self.cmds['align'], val), self.comtime)


    # @property
    # def cond_vars(self) -> dict:
    #     return self._cond_vars

    # def return_state(self):
    #     pass

    # On application close
    ############################################################################
    def exit(self):
        if self._cond_vars['op_state'] == 'RUN':
            self.write('OFF', self.comtime)
        # if self._isconnected:
        #     self.write('OFF', self.comtime)
        self.close()
