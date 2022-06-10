from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from pyqtgraph.dockarea import Dock
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal as Signal

class BasicPanel(Dock):
    """! The BasicPanel serves as a template class for device specific GUI
    elements. Basic organizational units are included, as are global parameters
    like font sizes/choices.
    """
    ## @var expmt_msg
    # Signal to emit a change from the GUI element for downstream parsing.
    expmt_msg = Signal(str)

    def __init__(self, *args, **kwargs):
        """! The BasicPanel constructor."""
        super().__init__('Experiment Panel', *args, **kwargs)

        ## @var headerfont
        # (QtGui.QFont) The font used for section headers on the panel.
        self.headerfont = QtGui.QFont()
        self.headerfont.setFamily("Verdana")
        self.headerfont.setPointSize(18)

        self.addWidget(self._status_widgets(), 0, 0, 1, -1)
        self.addWidget(self._control_widgets(), 2, 0, 1, -1)
        self.addWidget(self._log_widget(), 4, 0, 1, -1)

    def _status_widgets(self):
        """! The a widget and layout scheme to organize reporting features.
        These widgets give an overview of the corresponding device's state.
        """
        widget = QWidget()
        layout = QGridLayout()

        # Add device specific state readouts here

        widget.setLayout(layout)
        return widget

    def _control_widgets(self):
        """! The a widget and layout scheme to organize control features that
        are meant to affect device parameters. (On/off buttons, changing values,
        etc.)
        """
        widget = QWidget()
        layout = QGridLayout()

        # Add device specifics buttons for performing actions here

        widget.setLayout(layout)
        return widget

    def _log_widget(self):
        """! A widget to maintain device specific logging information. This can
        include more detailed information (such as specific hardware failures)
        than the more general experiment logs.
        """
        # Device logs

        ## @var _log
        # The GUI element that maintains the log. Its content can be written to
        # a file.
        self._log_label: QLabel = QLabel('Experiment Logs')
        self._log_label.setAlignment(Qt.AlignCenter)
        self._logs: QPlainTextEdit = QPlainTextEdit()
        return self._logs

    def _display_widget(self):
        pass

    def update_data(self, data):
        """! Slot to update display upon receipt of new data.
        @param data The new data to be displayed.
        """
        pass

    def update_state(self, params):
        """! Slot to update status widgets.
        @param params Device parameters and the values to be displayed.
        """
        pass

    # Device specific logging
    ############################################################################
    def update_log(self, msg):
        """! Slot to update the device log.
        @param msg Text to be added to the log.
        """
        self._logs.insertPlainText('{}: {}\n'.format(time.asctime(time.localtime(time.time())),
                                                    msg))
