from PyQt5 import QtGui
from PyQt5.QtWidgets import (QMenu, QMenuBar, QStatusBar, QMainWindow,
                             QStatusBar, QAction,)
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree.parameterTypes import ListParameter
from .basicpanel import BasicPanel

# class InsightPanel(BasicPanel):
class InsightPanel(BasicPanel):
    def __init__(self, **args):
        super().__init__(**args)

        self._control_widgets()

    def _control_widgets(self):
        self._laseron_btn = pg.FeedbackButton('Laser On')
        self._laseron_btn.clicked.connect(self._turnon)
        self.addWidget(self._laseron_btn, 2, 1)

        self._main_shutter_btn = pg.FeedbackButton('Main Shutter')
        self.addWidget(self._main_shutter_btn, 3, 0)
        self._fixed_shutter_btn = pg.FeedbackButton('Fixed Shutter')
        self.addWidget(self._fixed_shutter_btn, 3, 2)

    def _turnon(self):
        self.expmt_msg.emit('Insight: Turning on')
