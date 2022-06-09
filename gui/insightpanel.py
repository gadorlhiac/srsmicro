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
class InsightPanel(BasicPanel):
    expmt_msg = Signal(str)
    def __init__(self, **args):
        super().__init__(**args)

        # layout = QGridLayout()
        self.addWidget(self._control_widgets(), 0, 0, 1, -1)
        self.addWidget(self._status_widgets(), 2, 0, 1, -1)
        # layout.addLayout(self.lda_options(), 1, 0, 3, 1)
        # layout.addLayout(self.tsvd_options(), 4, 0, 1, 1)

        # self.addLayout(layout)

    def _control_widgets(self):
        headerfont = QtGui.QFont()
        headerfont.setFamily("Verdana")
        headerfont.setPointSize(18)

        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Laser Controls')
        label.setFont(headerfont)
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

    def _status_widgets(self):
        headerfont = QtGui.QFont()
        headerfont.setFamily("Verdana")
        headerfont.setPointSize(18)

        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Laser Status')
        label.setFont(headerfont)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, -1)

        ###

        label = QLabel('OPO Wavelength:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 2, 0, 1, 1)

        ###

        label = QLabel('Diode 1 Hours:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 4, 0, 1, 1)

        label = QLabel('Diode 2 Hours:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 6, 0, 1, 1)

        # Leave space to actually include the variables

        label = QLabel('Diode 1 Current:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 4, 6, 1, 1)

        label = QLabel('Diode 2 Current:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 6, 6, 1, 1)

        ###

        widget.setLayout(layout)
        return widget

    def _turnon(self):
        self.expmt_msg.emit('Insight: Turning on')

    def _alignmode(self):
        self.expmt_msg.emit('Alignment mode')

    def _tunewl(self):
        self.expmt_msg.emit('Tuning OPO')
