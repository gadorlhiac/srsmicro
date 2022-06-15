"""!
@brief Definition of the DelayStagePanel class for providing the necessary GUI
elements for controlling the Newport FCL200 delay stage's parameters.
"""

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
    """! The DelayStagePanel provides the GUI elements for interacting with the
    Newport FCL200 optical delay stage.
    """

    def __init__(self, *args, **kwargs):
        """! The DelayStagePanel constructor.
        @param statpath (str) The path to the text file containing the GUI's
        status elements. These elements only display information.
        @param ctrlpath (str) The path to the text file containing the GUI's
        control elements. These elements allow interaction with the associated
        device.
        """
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
        """! Function associated to the button and form to move to an absolute
        Delay Stage position. Emits the appropriate signal.
        """
        self.cmd.emit('Delay Stage', 'abs_move', self.control_vars['abs_mv_box'].text())

    def _rel_neg(self):
        """! Function associated to the button and form to move the Delay Stage
        relative to its current position, in the negative direction. Emits the
        appropriate signal.
        """
        self.cmd.emit('Delay Stage', 'rel_move_neg', self.control_vars['rel_mv_box'].text())

    def _rel_pos(self):
        """! Function associated to the button and form to move the Delay Stage
        relative to its current position in the positive direction. Emits the
        appropriate signal.
        """
        self.cmd.emit('Delay Stage', 'rel_move_pos', self.control_vars['rel_mv_box'].text())

    def _set_vel(self):
        """! Function associated to the button and form to set the Delay Stage
        velocity. Emits the appropriate signal.
        """
        self.cmd.emit('Delay Stage', 'vel', self.control_vars['vel_set_box'].text())

    def _set_accel(self):
        """! Function associated to the button and form to set the Delay Stage
        acceleration. Emits the appropriate signal.
        """
        self.cmd.emit('Delay Stage', 'accel', self.control_vars['accel_set_box'].text())
