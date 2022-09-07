"""!
@brief Definition of the ZiPanel class for providing the necessary GUI
elements for interacting with the Zurich Instruments HF2LI lock-in amplifier.
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
class ZiPanel(BasicPanel):
    def __init__(self, *args, **kwargs):
        """! The ZiPanel constructor.
        @param statpath (str) The path to the text file containing the GUI's
        status elements. These elements only display information.
        @param ctrlpath (str) The path to the text file containing the GUI's
        control elements. These elements allow interaction with the associated
        device.
        """
        self.funcs = { '_set_freq0' : self._set_freq0,
                       '_set_freq1' : self._set_freq1 }
        super().__init__(*args, **kwargs)
        # self._cond_vars = {}
        # self._update_cond_vars()

    # Oscillator frequency settings
    ###############################
    def _set_freq0(self):
        self.cmd.emit('Lockin', 'freq_osc0',
                                self.control_vars['freq0_set_box'].text())

    def _set_freq1(self):
        self.cmd.emit('Lockin', 'freq_osc1',
                                self.control_vars['freq1_set_box'].text())

    # Filter settings
    #################


    # def _update_cond_vars(self):
    #     pass

    # def update_state(self, params):
    #     # self.sigin0_ac.setText(str(params['/dev1292/sigins/0/ac']))
    #     # self.sigin0_imp50.setText(str(params['/dev1292/sigins/0/imp50']))
    #     # self.sigin0_range.setText(str(params['/dev1292/sigins/0/range']))
    #     # self.sigin0_diff.setText(str(params['/dev1292/sigins/0/diff']))
    #     #
    #     # self.sigin1_ac.setText(str(params['/dev1292/sigins/1/ac']))
    #     # self.sigin1_imp50.setText(str(params['/dev1292/sigins/1/imp50']))
    #     # self.sigin1_range.setText(str(params['/dev1292/sigins/1/range']))
    #     # self.sigin1_diff.setText(str(params['/dev1292/sigins/1/diff']))
    #     pass
