from .devices.insight import Insight
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import QThread
class MainController(QThread):
    device_state = Signal(object, object, object, object)

    def __init__(self):
        super().__init__()

        # Instantiate all devices here
        # They don't need to be connected the object just has to be available
        # to the controller.
        # Physical connection status and error handling due to unavailability
        # is handeled by the device itself.

        self._insight = Insight()
        # self._delaystage = DelayStage()
        # self._zi = ZurichInstruments()
        # self._kcube = PyKCube()
        # self._dmd = DMD()

        # One signal emitted from main gui which is then parsed here
        # self._mw.gui_changed.connect(self.parse_signal)

        # self._mw.update_dev_conds(['Insight'], len(self._insight.cond_vars),
        #                           self._insight.cond_vars)

    def parse_signal(self, mw, device: str, parameter: str, val: str):
        # MainWindow emits a signal with a reference to itself, the device to
        # communicate with, the parameter affected, and the value to input
        # MainWindow refernce is passed in order to communicate back the
        # response from the device
        # Each device case is handled by separate function
        # Can't use match-case because computer running software is too old
        if device == 'global':
            resp = self.global_control(parameter, val)

        elif device == 'insight':
            resp = 'Not configured yet'

        elif device == 'delaystage':
            resp = 'Not configured yet'

        elif device == 'zilockin':
            resp = 'Not configured yet'

        elif device == 'kcube':
            resp = 'Not configured yet'

        mw.statusbar = resp


    def global_control(self, parameter: str, val: str) -> str:
        if parameter == 'Experiment Type':
            print('Experiment Type Changed')
            resp = 'Experiment Type changed to: {}'.format(str(val))
        elif parameter == 'Insight COM Port':
            # self._insight.comport = resp
            resp = 'Insight COM Port changed to: {}'.format(str(val))

        elif parameter == 'Delay Stage COM Port':
            print('Delay Stage COM Port Changed')
            resp = 'Delay Stage COM Port changed to: {}'.format(str(val))
        return resp

    def return_device_conditions(self):
        return self._insight.cond_vars

    def stop(self):
        self.running = False
        print('Shutting down controller')
        print('Closing devices connections....')
        print('....Insight entering hibernation mode. Serial port closed.')
        print('....Delay stage serial port closed.')
        print('....ZI lock-in server connection closed.')
        print('....KCube connection closed.')
        print('All logs and data written to output file.')
