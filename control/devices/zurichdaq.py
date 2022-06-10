import zhinst.ziPython as ziPython
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal as Signal
import time
import numpy as np

class ZurichDaq(QObject):
    """The class for managing the Lock-in amplifier's data acquisition module.
    Intended for management on a background thread. Multiple ZurichDaqs can be
    created to sample from different data streams. Wraps the DAQ module from
    the ZI API for smoother integration with the Qt framework.
    """
    data = Signal(object)
    shutdown = Signal()

    def __init__(self, daq, devname, path):
        """! The ZurichDaq constructor.
        @param devname (str) The lock-in device name, needed for the parameter hierarchy.
        @param daq (dataAcquisitionModule) A lock-in dataAcquisitionModule.
        @param
        """
        super().__init__()
        self._daq = daq
        self._devname = devname
        self._path = path

        # Path is of format '/dev/demods/0/sample'
        # We subscribe to the R value from this node
        # Maintaining path this way allows using it more simply for retrieving
        # the trigger node
        self._daq.subscribe('{}.r'.format(self._path))

        self._pixeldwell = 3e-6
        self._stop = False
        # self._rows = 512
        # self._cols = 512

        ## @var _parameters
        # (list[list[str]]) list containing lists with the path to a parameter and its setting
        #
        # This list is continually rewritten to as it is only used to pass the
        # parameters to the DAQ; maintaing a copy allows retrieving the last
        # settings that were attempted for debugging.
        # Key parameters:
        # - type - indicates triggering type, each trigger has it's own settings.
        #          Refer to the Zurich API
        #        - 0: Trigger off
        #        - 1: Analog edge trigger on source
        #        - 2: Digital trigger on DIO
        #        - 3: Analog pulse trigger on source
        #        - 4: Analog tracking trigger on source
        #        - 5: Change trigger
        #        - 6: Hardware trigger on trigger line source
        #        - 7: Tracking edge trigger on source
        #        - 8: Event count trigger on counter source
        # - duration - The duration of one row of the scan (dwell_time*num_pixels)
        self._parameters = [['dataAcquisitionModule/enable', 1],
                            ['dataAcquisitionModule/device', self._devname],
                            ['dataAcquisitionModule/type', 0], # No trigger
                            ['dataAcquisitionModule/refreshrate', 200],
                            ['dataAcquisitionModule/endless', 1],
                            ['dataAcquisitionModule/delay', 0],
                            ['dataAcquisitionModule/count', 512],
                            ['dataAcquisitionModule/holdoff/time', 0],
                            ['dataAcquisitionModule/holdoff/count', 0]]
        self._daq.set(self._parameters)

    # Setup for imaging
    ############################################################################

    def setup_scan(self, rows=512, cols=512, repetitions=1, interp=2, delay=0):
        self._parameters = [['dataAcquisitionModule/grid/rows', rows],
                            ['dataAcquisitionModule/grid/cols', cols],
                            ['dataAcquisitionModule/grid/direction', 0],
                            ['dataAcquisitionModule/grid/repetitions', repetitions],
                            ['dataAcquisitionModule/grid/mode', interp],
                            ['dataAcquisitionModule/duration', self._pixeldwell*cols], # row duration
                            ['dataAcquisitionModule/delay', 0]]
        self._daq.set(self._parameters)

    def setup_trigger(self, type=1, node='auxin0', edge=1, level=2.5):
        """! The trigger inputs.
        On object construction the DAQ is set to run without trigger. This
        method allows setting an input trigger from, e.g., the Olympus. Defaults
        parameter values are set for the most common configuration used currently.
        @param type (int) Trigger type. See _parameters documentation. Default: 1 (edge)
        @param node (str) Input node for the trigger. Default: 'auxin1' (Auxillary input 1 on the lock-in)
        @param edge (int) Which edge of the signal to trigger on. Default: 1 (positive)
        @param level (float) Voltage level for the trigger. Default: 2.5 (V)
        """
        self._parameters = [['dataAcquisitionModule/type', 1],
                            ['dataAcquisitionModule/triggernode',
                             '{}.{}'.format(self._path, node)],
                            ['dataAcquisitionModule/edge', 1],
                            ['dataAcquisitionModule/level', level]]
        self._daq.set(self._parameters)

    def start(self):
        self.setup_scan()
        self.setup_trigger()
        self._daq.execute()
        while True:
            time.sleep(1)
            try:
                self.read_daq()
            except KeyError as err:
                print('{}.r'.format(self._path))
            if self.stop:
                return

    def read_daq(self):
        img = self._daq.read(True)['{}.r'.format(self._path)][0]['value'].T
        # img = np.random.random([512, 512])
        self.data.emit(img)

    # Properties for controlling acquisition
    ############################################################################
    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, val):
        self._stop = val

    # On application close
    ############################################################################
    def exit(self):
        self._daq.clear()
        self.deleteLater()
