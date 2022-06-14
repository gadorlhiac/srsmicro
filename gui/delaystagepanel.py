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
        pass

    def _home(self):
        pass

    def _abs_mv(self):
        pass

    def _rel_neg(self):
        pass

    def _rel_pos(self):
        pass

    def _set_vel(self):
        pass

    def _set_accel(self):
        pass
