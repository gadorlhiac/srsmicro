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

class DelayStagePanel(BasicPanel):
    expmt_msg = Signal(str)
    def __init__(self, **args):
        super().__init__(**args)

        # layout = QGridLayout()
        self.addWidget(self._control_widgets(), 0, 0, 1, -1)
        # self.addWidget(self._status_widgets(), 2, 0, 1, -1)
        # layout.addLayout(self.lda_options(), 1, 0, 3, 1)
        # layout.addLayout(self.tsvd_options(), 4, 0, 1, 1)

        # self.addLayout(layout)

    def _control_widgets(self):
        headerfont = QtGui.QFont()
        headerfont.setFamily("Verdana")
        headerfont.setPointSize(18)

        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Delay Stage Controls')
        label.setFont(headerfont)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, -1)

        # Need to add trigger actions to all buttons

        # Control buttons
        self._stage_on_btn = pg.FeedbackButton('Delay Stage On')
        # self._stage_on_btn.clicked.connect(self._stage_on)
        layout.addWidget(self._stage_on_btn, 1, 0, 1, 1)

        self._home_btn = pg.FeedbackButton('Home')
        # self._home_btn.clicked.connect(self._home)
        layout.addWidget(self._home_btn, 1, 2, 1, 1)

        self._abs_mv_box = QLineEdit()
        layout.addWidget(self._abs_mv_box, 3, 0, 1, 1)
        self._abs_mv_btn = pg.FeedbackButton('Move Absolute')
        layout.addWidget(self._abs_mv_btn, 3, 1, 1, 1)

        label = QLabel('Relative Move:')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 5, 1, 1, 1)
        self._rel_neg_btn = pg.FeedbackButton('<<')
        layout.addWidget(self._rel_neg_btn, 6, 0, 1, 1)
        # add action for triggering
        self._rel_mv_box = QLineEdit()
        layout.addWidget(self._rel_mv_box, 6, 1, 1, 1)
        self._rel_pos_btn = pg.FeedbackButton('>>')
        layout.addWidget(self._rel_pos_btn, 6, 2, 1, 1)
        # add action for triggering

        self._vel_box = QLineEdit()
        layout.addWidget(self._vel_box, 7, 0, 1, 1)
        self._vel_set_btn = pg.FeedbackButton('Set Velocity')
        # add action for triggering
        layout.addWidget(self._vel_set_btn, 7, 1, 1, 1)

        self._accel_box = QLineEdit()
        layout.addWidget(self._accel_box, 9, 0, 1, 1)
        self._accel_set_btn = pg.FeedbackButton('Set Acceleration')
        # add action for triggering
        layout.addWidget(self._accel_set_btn, 9, 1, 1, 1)

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
