from PyQt5.QtCore import QThread, QObject
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
import time

class StatusReporter(QObject):
    """The class for device status querying.

    Executes query functions for every device reference it is passed.
    """
    shutdown = Signal()

    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.pause = False

    def query_state(self):
        while True:
            time.sleep(2)
            for device in self.devices:
                device.emit_state()
            if self.pause:
                return

    def add_device(self, device):
        self.devices.append(device)
        device.state.connect(self.parse_status)
        self.pause = False
