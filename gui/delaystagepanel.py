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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _status_widgets(self):
        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Delay Stage Status')
        label.setFont(self.headerfont)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, -1)

        # Position/velocity/acceleration
        # Variable names match corresponding variables
        # from delay stage's _cond_vars
        ###############################################

        label = QLabel('Position:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 1, 0, 1, 1)

        self.pos = QLabel('0')
        self.pos.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.pos, 1, 1, 1, 1)

        label = QLabel('Velocity:')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 2, 0, 1, 1)

        self.vel = QLabel('0')
        self.vel.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.vel, 2, 1, 1, 1)

        label = QLabel('Acceleration')
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label, 3, 0, 1, 1)

        self.accel = QLabel('0')
        self.accel.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.accel, 2, 1, 1, 1)

        widget.setLayout(layout)
        return widget

    def _control_widgets(self):
        widget = QWidget()
        layout = QGridLayout()

        label = QLabel('Delay Stage Controls')
        label.setFont(self.headerfont)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, -1)

        # Need to add trigger actions to all buttons

        # Control buttons
        self._stage_on_btn = pg.FeedbackButton('Delay Stage On')
        # self._stage_on_btn.clicked.connect(self._stage_on)
        layout.addWidget(self._stage_on_btn, 1, 0, 1, 1)

        self._home_btn = pg.FeedbackButton('Home')
        # self._home_btn.clicked.connect(self._home)
        layout.addWidget(self._home_btn, 1, 1, 1, 1)

        self._abs_mv_box = QLineEdit()
        layout.addWidget(self._abs_mv_box, 2, 0, 1, 1)
        self._abs_mv_btn = pg.FeedbackButton('Move Absolute')
        layout.addWidget(self._abs_mv_btn, 2, 1, 1, 1)

        label = QLabel('Relative Move:')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 3, 1, 1, 1)
        self._rel_neg_btn = pg.FeedbackButton('<<')
        layout.addWidget(self._rel_neg_btn, 4, 0, 1, 1)
        # add action for triggering
        self._rel_mv_box = QLineEdit()
        layout.addWidget(self._rel_mv_box, 4, 1, 1, 1)
        self._rel_pos_btn = pg.FeedbackButton('>>')
        layout.addWidget(self._rel_pos_btn, 4, 2, 1, 1)
        # add action for triggering

        self._vel_box = QLineEdit()
        layout.addWidget(self._vel_box, 5, 0, 1, 1)
        self._vel_set_btn = pg.FeedbackButton('Set Velocity')
        # add action for triggering
        layout.addWidget(self._vel_set_btn, 5, 1, 1, 1)

        self._accel_box = QLineEdit()
        layout.addWidget(self._accel_box, 6, 0, 1, 1)
        self._accel_set_btn = pg.FeedbackButton('Set Acceleration')
        # add action for triggering
        layout.addWidget(self._accel_set_btn, 6, 1, 1, 1)

        widget.setLayout(layout)
        return widget


    def _turnon(self):
        self.expmt_msg.emit('Insight: Turning on')

    def _alignmode(self):
        self.expmt_msg.emit('Alignment mode')

    def _tunewl(self):
        self.expmt_msg.emit('Tuning OPO')
