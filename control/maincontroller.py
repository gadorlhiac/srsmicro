from .devices.insight import Insight
from .devices.delaystage import DelayStage
from .devices.zurichlockin import ZurichLockin
from .statusreporter import StatusReporter
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import QThread, QObject
import time

class MainController(QObject):
    device_state = Signal(object, object, object)
    data = Signal(object)
    log = Signal(str)

    def __init__(self):
        super().__init__()

        # Instantiate all devices here
        # They don't need to be connected the object just has to be available
        # to the controller.
        # Physical connection status and error handling due to unavailability
        # is handeled by the device itself.

        # Create instances of all devices
        self._insight = Insight(name='Insight')
        self._delaystage = DelayStage(name='Delay Stage')
        self._zi = ZurichLockin(name='Lockin')
        # self._zi = ZurichInstruments()
        # self._kcube = PyKCube()
        # self._dmd = DMD()

        self._insight.cmd_result.connect(self._read_result)
        self._delaystage.cmd_result.connect(self._read_result)
        self._zi.cmd_result.connect(self._read_result)
        # self.cmd_result = ''

        # Signal/slot connections for ZI data
        self._zi.data.connect(self.parse_data)

        # Separate thread for infinite state querying at specified intervals
        self._status_thread = QThread()
        self._reporter = StatusReporter([self._insight])
        self._reporter.moveToThread(self._status_thread)
        self._status_thread.started.connect(self._reporter.query_state)

        # Cleanup on shutdown
        self._reporter.shutdown.connect(self._status_thread.quit)
        self._reporter.shutdown.connect(self._reporter.deleteLater)
        self._status_thread.finished.connect(self._status_thread.deleteLater)

        # Start the query thread
        self._status_thread.start()

    def init_devices(self):
        msg = 'Opening communication with Insight....\n\t\t'
        self._insight.open()
        msg += self.cmd_result
        self.log.emit(msg)

        msg = 'Opening communication with the Delay Stage....\n\t\t'
        self._delaystage.open()
        msg += self.cmd_result
        self.log.emit(msg)

        msg = 'Opening communication with the Lockin....\n\t\t'
        self._zi.open()
        msg += self.cmd_result
        self.log.emit(msg)

    def _read_result(self, msg):
        self.cmd_result = msg

    def parse_data(self, type, data):
        if type == 'Image':
            self.new_data.emit(data)

    def parse_signal(self, mw, device: str, parameter: str, val: str):
        # MainWindow emits a signal with a reference to GUI component, the device
        # to communicate with, the parameter affected, and the value to input
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

    def exit(self):
        self.running = False
        print('Shutting down controller')
        print('....Exiting device status thread')
        self._status_thread.quit()
        print('Closing devices connections....')
        print('....Insight entering hibernation mode. Serial port closed.')
        self._insight.exit()
        print('....Delay stage serial port closed.')
        self._delaystage.exit()
        print('....ZI lock-in server connection closed.')
        self._zi.exit()
        # print('....KCube connection closed.')
