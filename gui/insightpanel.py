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
    def __init__(self, *args, **kwargs):
        self.funcs = { '_turnon' : self._turnon,
                       '_alignmode' : self._alignmode,
                       '_main_shutter' : self._main_shutter,
                       '_fixed_shutter' : self._fixed_shutter,
                       '_tunewl' : self._tunewl }
        super().__init__(*args, **kwargs)

    def _turnon(self):
        # self.expmt_msg.emit('Insight: Turning on')
        self.param_change.emit('Insight', 'Turn on', 'On')

    def _alignmode(self):
        self.expmt_msg.emit('Alignment mode')

    def _tunewl(self):
        self.expmt_msg.emit('Tuning OPO')

    def _main_shutter(self):
        pass

    def _fixed_shutter(self):
        pass
