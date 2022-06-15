from .devices.insight import Insight
from .devices.delaystage import DelayStage
from .devices.zurichlockin import ZurichLockin
from .devices.zurichlockin import ZurichLockin
# from .devices.pykcube import PyKcube
from .statusreporter import StatusReporter
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import QThread, QObject
import time

class MainController(QObject):
    """! The MainController class for interfacing the GUI elements with device
    objects. The MainController holds instances of all the devices and through
    appropriate Signals and Slots passes information to and from the GUI.
    """
    ## @var device_state
    # (Signal) Emitted with the name of the device, and its settings as the
    # two parameters.
    device_state = Signal(object, object)

    ## @var data
    # (Signal) Emitted with new data for plotting/display.
    data = Signal(object)

    ## @var log
    # (Signal) Emitted with a message to be recorded on the GUIs log.
    log = Signal(str)

    ## @var log
    # (Signal) Emitted with a message to be recorded on the GUIs log.
    insight_cmd = Signal(object, object)

    def __init__(self):
        """! The MainController class constructor."""
        super().__init__()

        # Instantiate all devices here
        # They don't need to be connected the object just has to be available
        # to the controller.
        # Physical connection status and error handling due to unavailability
        # is handeled by the device itself.

        # Create instances of all devices
        ## @var _insight
        # Instance of the Insight device for controlling the laser.
        self._insight = Insight(name='Insight')
        self.insight_cmd.connect(self._insight.parse_cmd)

        ## @var _delaystage
        # Instance of the DelayStage device for controlling the delay stage.
        self._delaystage = DelayStage(name='Delay Stage')

        ## @var _zi
        # Instance of the ZurichLockin device for controlling the lock-in amplifier.
        self._zi = ZurichLockin(name='Lockin')
        # self._kcube = PyKcube()
        # self._dmd = DMD()

        # Connect all devices' independent state Signals to the controllers
        # global device_state Signal
        self._insight.state.connect(self.device_state)
        self._delaystage.state.connect(self.device_state)
        self._zi.state.connect(self.device_state)

        # Connect all devices' independent cmd_result Signals to the controller
        self._insight.cmd_result.connect(self._read_result)
        self._delaystage.cmd_result.connect(self._read_result)
        self._zi.cmd_result.connect(self._read_result)
        # self.cmd_result = ''

        # Connect the ZI's data Signal to the controller's parse_data to
        # take the appropriate action with it.
        self._zi.data.connect(self.parse_data)

        # Separate thread for infinite state querying at specified intervals

        ## @var _status_thread
        # A separate thread for running the StatusReporter worker.
        self._status_thread = QThread()

        ## @var _reporter
        # Instance of a StatusReporter which takes a list of devices and queries
        # their state on a loop.
        self._reporter = StatusReporter([self._insight, self._zi])
        self._reporter.moveToThread(self._status_thread)
        self._status_thread.started.connect(self._reporter.query_state)

        # Cleanup on shutdown
        self._reporter.shutdown.connect(self._status_thread.quit)
        self._reporter.shutdown.connect(self._reporter.deleteLater)
        self._status_thread.finished.connect(self._status_thread.deleteLater)

        # Start the query thread
        self._status_thread.start()

    def init_devices(self):
        """! Run the startup procedure for the various devices and handle
        any messages/errors.
        """
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
        """! Receive the result of the last action taken."""
        ## @var cmd_result
        # Holds the result of the last attempted action on any device.
        self.cmd_result = msg

    def parse_data(self, type, data):
        """! Appropriately package data for display as the multiple types of
        output (images, plots, etc) may be expected.
        """
        if type == 'Image':
            self.data.emit(data)

    # def parse_signal(self, mw, device: str, parameter: str, val: str):
    def distribute_cmd(self, device, param, val):
        """! Parse messages from the GUI and pass them to the appropriate
        devices."""
        # MainWindow emits a signal with a reference to GUI component, the device
        # to communicate with, the parameter affected, and the value to input
        # MainWindow refernce is passed in order to communicate back the
        # response from the device
        # Each device case is handled by separate function
        # Can't use match-case because computer running software is too old
        if device == 'Global':
            resp = self.global_control(param, val)

        elif device == 'Insight':
            # resp = 'Insight: Not configured yet'
            self.insight_cmd.emit(param, val)

        elif device == 'Delay Stage':
            resp = 'Not configured yet'

        elif device == 'Lockin':
            resp = 'Not configured yet'

        elif device == 'kcube':
            resp = 'Not configured yet'

        self.log.emit('Functionality not implemented. Request failed.')
        # mw.statusbar = resp


    def global_control(self, parameter: str, val: str) -> str:
        """! Manage device responses to what are currently called "global"
        parameters, including COM ports etc. This method will be
        deprecated.
        """
        if parameter == 'Experiment Type':
            resp = 'Experiment Type changed to: {}'.format(str(val))
        elif parameter == 'Insight COM Port':
            # self._insight.comport = resp
            resp = 'Insight COM Port changed to: {}'.format(str(val))
        elif parameter == 'Delay Stage COM Port':
            resp = 'Delay Stage COM Port changed to: {}'.format(str(val))
        return resp

    def return_device_conditions(self):
        """! Method will be deprecated."""
        return self._insight.cond_vars

    def exit(self):
        """! Run the shutdown procedures for each device in turn. Handle any
        errors as needed.
        """
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
