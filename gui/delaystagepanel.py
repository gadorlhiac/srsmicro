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
    def __init__(self, *args, **kwargs):
        self.funcs = { '_turnon' : self._turnon,
                       '_home' : self._home,
                       '_abs_mv' : self._abs_mv,
                       '_rel_neg' : self._rel_neg,
                       '_rel_pos' : self._rel_pos,
                       '_set_vel' : self._set_vel,
                       '_set_accel' : self._set_accel }
        super().__init__(*args, **kwargs)

    def _turnon(self):
        self.cmd.emit('Delay Stage', 'enable', 'RUN')

    def _home(self):
        self.cmd.emit('Delay Stage', 'home', 'RUN')

    def _abs_mv(self):
        self.cmd.emit('Delay Stage', 'abs_move', self.control_vars['abs_mv_box'].text())

    def _rel_neg(self):
        self.cmd.emit('Delay Stage', 'rel_move_neg', self.control_vars['rel_mv_box'].text())

    def _rel_pos(self):
        self.cmd.emit('Delay Stage', 'rel_move_pos', self.control_vars['rel_mv_box'].text())

    def _set_vel(self):
        self.cmd.emit('Delay Stage', 'vel', self.control_vars['vel_set_box'].text())

    def _set_accel(self):
        self.cmd.emit('Delay Stage', 'accel', self.control_vars['accel_set_box'].text())
