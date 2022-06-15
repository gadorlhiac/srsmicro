"""!
@brief Definition of the StatusReporter class which is intended as a worker
on a separate thread for reporting device status updates.
"""

from PyQt5.QtCore import QThread, QObject
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
import time

class StatusReporter(QObject):
    """! Worker class for device status querying.

    Executes query functions for every device reference it is passed.
    """
    shutdown = Signal()

    def __init__(self, devices):
        """! The StatusReporter constructor.
        @param devices (List) A list of all devices to have their state queried.
        """
        super().__init__()

        ## @var devices
        # (list) List of device references. Used only for querying status.
        self.devices = devices

        ## @var pause
        # (bool) Variable to block device status queries. Set to true while the
        # controller/device object is communicating with the physical device.
        self.pause = False

    def query_state(self):
        """! Method to query device state. Runs infinitely, unless an interrupt
        signal is received, asking devices to emit their state conditions.
        """
        while True:
            time.sleep(1)
            for device in self.devices:
                if self.pause:
                    break
                device.query_state()

    def add_device(self, device):
        """! Method to add a device to the query list if it was not included
        during object initiliazation.
        @param device (Device) The device object to be added to the list.
        """
        self.devices.append(device)
        self.pause = False
