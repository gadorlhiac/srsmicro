import pyqtgraph as pg
from pyqtgraph.dockarea import Dock
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal

class FemtoRamanPanel(Dock):
    #expmt_msg = Signal(str, str)
    expmt_msg = Signal(str)
    def __init__(self, **args):
        super().__init__('Experiment Panel', **args)
        # Need basic log/report area, controls area, and an output area
        # self.addWidget(self._display_widget(), 0, 0, 1, -1)

        # label = QLabel('Controls and Status')
        # label.setAlignment(Qt.AlignCenter)
        # self.addWidget(label, 1, 0, 1, -1)
        self.data = np.random.random([512,512])
        self.addWidget(self._display_widget(), 0, 0, 1, -1)

    def _display_widget(self):
        self.imv = pg.ImageView()
        self.imv.show()
        self.imv.setImage(self.data)
        return self.imv

    def _controls_widgets(self):
        pass

    def update_data(self, data):
        self.data = data
        self.imv.setImage(self.data)
