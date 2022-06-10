from PyQt5 import QtGui
from PyQt5.QtWidgets import (QMenu, QMenuBar, QStatusBar, QMainWindow,
                             QStatusBar, QAction, QGridLayout, QLabel, QWidget,
                             QLineEdit)
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree.parameterTypes import ListParameter
from .basicpanel import BasicPanel

# class InsightPanel(BasicPanel):
class ZiPanel(BasicPanel):
    def __init__(self, **args):
        super().__init__(**args)

    def _status_widgets(self):
        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Lock-in Amplifier Settings')
        label.setFont(self.headerfont)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, -1)

        # OPO setting
        # Variable names match corresponding variables
        # from insight's _cond_vars
        ###############################################

        label = QLabel('OPO Wavelength:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 1, 0, 1, 1)

        # DSM settings
        # Variable names match corresponding variables
        # from insight's _cond_vars
        ###############################################

        label = QLabel('DSM Position:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 2, 0, 1, 1)

        self.dsm_pos = QLabel('0')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.dsm_pos, 2, 1, 1, 1)


        label = QLabel('DSM Min:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 2, 3, 1, 1)

        self.dsm_min = QLabel('0')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.dsm_min, 2, 4, 1, 1)

        label = QLabel('DSM Max:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 2, 6, 1, 1)

        self.dsm_max = QLabel('0')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.dsm_max, 2, 7, 1, 1)

        # Diode hours
        # Variable names match corresponding variables
        # from insight's _cond_vars
        ###############################################

        label = QLabel('Diode 1 Hours:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 3, 0, 1, 1)

        self.d1_hrs = QLabel('0')
        self.d1_hrs.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.d1_hrs, 3, 1, 1, 1)

        label = QLabel('Diode 2 Hours:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 4, 0, 1, 1)

        self.d2_hrs = QLabel('0')
        self.d2_hrs.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.d2_hrs, 4, 1, 1, 1)

        # Diode current
        # Variable names match corresponding variables
        # from insight's _cond_vars
        ###############################################

        label = QLabel('Diode 1 Current:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 3, 3, 1, 1)

        self.d1_curr = QLabel('0')
        self.d1_curr.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.d1_curr, 3, 4, 1, 1)

        label = QLabel('Diode 2 Current:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 4, 3, 1, 1)

        self.d2_curr = QLabel('0')
        self.d2_curr.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.d2_curr, 4, 4, 1, 1)

        ###

        widget.setLayout(layout)
        return widget

    def _control_widgets(self):
        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Lock-in Amplifier Controls')
        label.setFont(self.headerfont)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, -1)

        # Control buttons
        self._laseron_btn = pg.FeedbackButton('Laser On')
        self._laseron_btn.clicked.connect(self._turnon)
        layout.addWidget(self._laseron_btn, 1, 0, 1, 1)

        self._alignmode_btn = pg.FeedbackButton('Alignment Mode')
        self._alignmode_btn.clicked.connect(self._alignmode)
        layout.addWidget(self._alignmode_btn, 1, 2, 1, 1)

        self._main_shutter_btn = pg.FeedbackButton('Main Shutter')
        layout.addWidget(self._main_shutter_btn, 3, 0, 1, 1)
        self._fixed_shutter_btn = pg.FeedbackButton('Fixed Shutter')
        layout.addWidget(self._fixed_shutter_btn, 3, 2, 1, 1)

        # Wavelength control
        self._wl_box = QLineEdit()
        layout.addWidget(self._wl_box, 5, 0, 1, 1)
        self._tunewl_btn = pg.FeedbackButton('Set Wavelength')

        self._tunewl_btn.clicked.connect(self._tunewl)
        layout.addWidget(self._tunewl_btn, 5, 2, 1, 1)

        widget.setLayout(layout)
        return widget

    def _turnon(self):
        self.expmt_msg.emit('Insight: Turning on')

    def _alignmode(self):
        self.expmt_msg.emit('Alignment mode')

    def _tunewl(self):
        self.expmt_msg.emit('Tuning OPO')
