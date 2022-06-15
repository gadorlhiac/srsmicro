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

    def _turnon(self, *args):
        # self.expmt_msg.emit('Insight: Turning on')
        # self.control_vars['_laseron_btn'].setStyleSheet('background-color: blue')
        # self.control_vars['_laseron_btn'].toggle()
        self.cmd.emit('Insight', 'op_state', 'RUN')

    def _alignmode(self):
        self.cmd.emit('Insight', 'align', 'Change mode')
        # self.expmt_msg.emit('Alignment mode')

    def _tunewl(self):
        self.cmd.emit('Insight', 'opo_wl', self.control_vars['wl_box'].text())
        # self.expmt_msg.emit('Tuning OPO')

    def _main_shutter(self):
        self.cmd.emit('Insight', 'main_shutter', 'Toggle shutter')

    def _fixed_shutter(self):
        self.cmd.emit('Insight', 'fixed_shutter', 'Toggle shutter')

    def _update_controls(self, param, val):
        if param == 'op_state':
            print(val)
            if val == 'RUN':
                self.control_vars['laseron_btn'].setStyleSheet('background-color: red')
            else:
                self.control_vars['laseron_btn'].setStyleSheet('background-color: light gray')
        if param == 'main_shutter':
            if val:
                self.control_vars['main_shutter_btn'].setStyleSheet('background-color: red')
            else:
                self.control_vars['main_shutter_btn'].setStyleSheet('background-color: light gray')
        elif param == 'fixed_shutter':
            if val:
                self.control_vars['fixed_shutter_btn'].setStyleSheet('background-color: red')
            else:
                self.control_vars['fixed_shutter_btn'].setStyleSheet('background-color: light gray')
        elif param == 'align':
            if val == 'ALIGN':
                self.control_vars['_alignmode_btn'].setStyleSheet('background-color: red')
            else:
                self.control_vars['_alignmode_btn'].setStyleSheet('background-color: light gray')
