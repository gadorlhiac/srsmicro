"""!
@brief Definition of the FemtoRamanPanel class for providing the necessary GUI
elements for controlling a fsSRS microscopy experiment.
"""
import pyqtgraph as pg
from pyqtgraph.dockarea import Dock
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal
from .basicpanel import BasicPanel

class SpectrumPanel(BasicPanel):
    """! The FemtoRamanPanel provides the GUI elements needed for performing
    femtosecond SRS microscopy measurements and displaying the results.
    """
    def __init__(self, *args, **kwargs):
        """! The FemtoRamanPanel constructor.
        @param statpath (str) The path to the text file containing the GUI's
        status elements. These elements only display information.
        @param ctrlpath (str) The path to the text file containing the GUI's
        control elements. These elements allow interaction with the associated
        device.
        """
        self.funcs = { '_acquire' : self._acquire }
        super().__init__(*args, **kwargs)

    def _acquire(self):
        pass
