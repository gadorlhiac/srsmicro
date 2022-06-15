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
        self.funcs = {}
        super().__init__(*args, **kwargs)
        # self._cond_vars = {}
        self._update_cond_vars()

    # def _status_widgets(self):
    #     widget = QWidget()
    #     layout = QGridLayout()
    #
    #     label = QLabel('Lock-in Amplifier Settings')
    #     label.setFont(self.headerfont)
    #     label.setAlignment(Qt.AlignCenter)
    #     layout.addWidget(label, 0, 0, 1, -1)
    #
    #     # General settings
    #     # Setup to match the ziPython api's dictionary
    #     # hierarchy
    #     ###############################################
    #     label = QLabel('Oscillator:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 1, 0, 1, 1)
    #
    #     self.oscselect = QLabel('0')
    #     self.oscselect.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.oscselect, 1, 1, 1, 1)
    #
    #     label = QLabel('Demodulator:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 2, 0, 1, 1)
    #
    #     self.demod = QLabel('0')
    #     self.demod.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.demod, 2, 1, 1, 1)
    #
    #     label = QLabel('Frequency:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 3, 0, 1, 1)
    #
    #     self.freq = QLabel('10280000')
    #     self.freq.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.freq, 3, 1, 1, 1)
    #
    #     label = QLabel('Time Constant:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 4, 0, 1, 1)
    #
    #     self.timeconstant = QLabel('3e-6')
    #     self.timeconstant.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.timeconstant, 4, 1, 1, 1)
    #
    #     ################################################
    #
    #     label = QLabel('Sampling Rate:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 1, 3, 1, 1)
    #
    #     self.rate = QLabel('10000')
    #     self.rate.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.rate, 1, 4, 1, 1)
    #
    #     label = QLabel('Demodulation Harmonic:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 2, 3, 1, 1)
    #
    #     self.harm = QLabel('1')
    #     self.harm.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.harm, 2, 4, 1, 1)
    #
    #     label = QLabel('Filter Order:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 3, 3, 1, 1)
    #
    #     self.order = QLabel('4')
    #     self.order.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.order, 3, 4, 1, 1)
    #
    #     label = QLabel('External Clock:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 4, 3, 1, 1)
    #
    #     self.extclk = QLabel('1')
    #     self.extclk.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.extclk, 4, 4, 1, 1)
    #
    #     # Sigin 0
    #     ################################################
    #
    #     label = QLabel('Signal In 0')
    #     label.setAlignment(Qt.AlignCenter)
    #     layout.addWidget(label, 5, 0, 1, -1)
    #
    #     label = QLabel('In Use:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 6, 0, 1, 1)
    #
    #     self.sigin0 = QLabel('1')
    #     self.sigin0.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin0, 6, 1, 1, 1)
    #
    #     label = QLabel('AC Coupling:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 7, 0, 1, 1)
    #
    #     self.sigin0_ac = QLabel('903')
    #     self.sigin0_ac.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin0_ac, 7, 1, 1, 1)
    #
    #     label = QLabel('50 Ohm Impedance:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 6, 3, 1, 1)
    #
    #     self.sigin0_imp50 = QLabel('1')
    #     self.sigin0_imp50.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin0_imp50, 6, 4, 1, 1)
    #
    #     label = QLabel('Differential Input:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 7, 3, 1, 1)
    #
    #     self.sigin0_diff = QLabel('0')
    #     self.sigin0_diff.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin0_diff, 7, 4, 1, 1)
    #
    #     label = QLabel('Range:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 8, 0, 1, 1)
    #
    #     self.sigin0_range = QLabel('0.01')
    #     self.sigin0_range.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin0_range, 8, 1, 1, 1)
    #
    #     # Sigin 1
    #     ################################################
    #
    #     label = QLabel('Signal In 1')
    #     label.setAlignment(Qt.AlignCenter)
    #     layout.addWidget(label, 9, 0, 1, -1)
    #
    #     label = QLabel('In Use:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 10, 0, 1, 1)
    #
    #     self.sigin1 = QLabel('0')
    #     self.sigin1.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin1, 10, 1, 1, 1)
    #
    #     label = QLabel('AC Coupling:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 11, 0, 1, 1)
    #
    #     self.sigin1_ac = QLabel('0')
    #     self.sigin1_ac.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin1_ac, 11, 1, 1, 1)
    #
    #     label = QLabel('50 Ohm Impedance:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 10, 3, 1, 1)
    #
    #     self.sigin1_imp50 = QLabel('1')
    #     self.sigin1_imp50.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin1_imp50, 10, 4, 1, 1)
    #
    #     label = QLabel('Differential Input:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 11, 3, 1, 1)
    #
    #     self.sigin1_diff = QLabel('0')
    #     self.sigin1_diff.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin1_diff, 11, 4, 1, 1)
    #
    #     label = QLabel('Range:')
    #     label.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(label, 12, 0, 1, 1)
    #
    #     self.sigin1_range = QLabel('0.01')
    #     self.sigin1_range.setAlignment(Qt.AlignLeft)
    #     layout.addWidget(self.sigin1_range, 12, 1, 1, 1)
    #
    #     widget.setLayout(layout)
    #     return widget
    #
    # def _control_widgets(self):
    #     widget = QWidget()
    #     layout = QGridLayout()
    #
    #     label = QLabel('Lock-in Amplifier Controls')
    #     label.setFont(self.headerfont)
    #     label.setAlignment(Qt.AlignCenter)
    #     layout.addWidget(label, 0, 0, 1, -1)
    #
    #     # # Control buttons
    #     self.extclk_btn = pg.FeedbackButton('External Clock')
    #     # self.extclk_btn.clicked.connect(self._turnon)
    #     layout.addWidget(self.extclk_btn, 1, 0, 1, 1)
    #     #
    #     # self._alignmode_btn = pg.FeedbackButton('Alignment Mode')
    #     # self._alignmode_btn.clicked.connect(self._alignmode)
    #     # layout.addWidget(self._alignmode_btn, 1, 2, 1, 1)
    #     #
    #     # self._main_shutter_btn = pg.FeedbackButton('Main Shutter')
    #     # layout.addWidget(self._main_shutter_btn, 3, 0, 1, 1)
    #     # self._fixed_shutter_btn = pg.FeedbackButton('Fixed Shutter')
    #     # layout.addWidget(self._fixed_shutter_btn, 3, 2, 1, 1)
    #     #
    #     # # Wavelength control
    #     # self._wl_box = QLineEdit()
    #     # layout.addWidget(self._wl_box, 5, 0, 1, 1)
    #     # self._tunewl_btn = pg.FeedbackButton('Set Wavelength')
    #     #
    #     # self._tunewl_btn.clicked.connect(self._tunewl)
    #     # layout.addWidget(self._tunewl_btn, 5, 2, 1, 1)
    #
    #     widget.setLayout(layout)
    #     return widget

    def _update_cond_vars(self):
        pass

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
