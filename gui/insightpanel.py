"""!
@brief Definition of the InsightPanel class for providing the necessary GUI
elements for controlling the Insight DS+ parameters and device state.
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

# class InsightPanel(BasicPanel):
class InsightPanel(BasicPanel):
    """! The InsightPanel provides the GUI elements for interacting with the
    Insight DS+.
    """

    def __init__(self, *args, **kwargs):
        """! The InsightPanel constructor.
        @param statpath (str) The path to the text file containing the GUI's
        status elements. These elements only display information.
        @param ctrlpath (str) The path to the text file containing the GUI's
        control elements. These elements allow interaction with the associated
        device.
        """
        self.funcs = { '_turnon' : self._turnon,
                       '_alignmode' : self._alignmode,
                       '_main_shutter' : self._main_shutter,
                       '_fixed_shutter' : self._fixed_shutter,
                       '_tunewl' : self._tunewl }
        super().__init__(*args, **kwargs)

    def _turnon(self, *args):
        """! Function associated to the button to turn the Insight DS+ on. Emits
        the appropriate signal.
        """
        self.cmd.emit('Insight', 'op_state', 'RUN')

    def _alignmode(self):
        """! Function associated to the button to put the Insight DS+ into
        alignment mode. Emits the appropriate signal.
        """
        self.cmd.emit('Insight', 'align', 'Change mode')
        # self.expmt_msg.emit('Alignment mode')

    def _tunewl(self):
        """! Function associated to the button and form to change the wavelength
        the Insight DS+ OPO is tuned to. Emits the appropriate signal.
        """
        self.cmd.emit('Insight', 'opo_wl', self.control_vars['wl_box'].text())
        # self.expmt_msg.emit('Tuning OPO')

    def _main_shutter(self):
        """! Function associated to the button to open or close the main OPO
        shutter of the Insight DS+. Emits the appropriate signal.
        """
        self.cmd.emit('Insight', 'main_shutter', 'Toggle shutter')

    def _fixed_shutter(self):
        """! Function associated to the button to open or close the fixed 1040 nm
        shutter of the Insight DS+. Emits the appropriate signal.
        """
        self.cmd.emit('Insight', 'fixed_shutter', 'Toggle shutter')

    def _update_controls(self, param, val):
        """! Function to update the control GUI element appearance depending on
        the Insight DS+ status. The function updates the display color of buttons
        to indicate laser emission/open shutters.
        """
        if param == 'op_state':
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
                self.control_vars['alignmode_btn'].setStyleSheet('background-color: red')
            else:
                self.control_vars['alignmode_btn'].setStyleSheet('background-color: light gray')
