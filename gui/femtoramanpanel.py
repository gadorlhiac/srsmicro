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

class FemtoRamanPanel(BasicPanel):
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
        self.funcs = { '_set_dwell' : self._set_dwell }
        super().__init__(*args, **kwargs)

    def _set_dwell(self):
        """! Function associated to the button and form to update the pixel
        dwell time during image raster scanning. Emits the appropriate signal.
        """
        pass
        # Need basic log/report area, controls area, and an output area
        # self.addWidget(self._display_widget(), 0, 0, 1, -1)

        # label = QLabel('Controls and Status')
        # label.setAlignment(Qt.AlignCenter)
        # self.addWidget(label, 1, 0, 1, -1)
    #     self.data = np.random.random([512,512])
    #     self.addWidget(self._display_widget(), 0, 0, 1, -1)
    #
    # def _display_widget(self):
    #     self.imv = pg.ImageView()
    #     self.imv.show()
    #     self.imv.setImage(self.data)
    #     return self.imv
    #
    # def _controls_widgets(self):
    #     pass
    #
    def update_data(self, data):
        self.data = data
        self.control_vars['imv'].setImage(self.data)
