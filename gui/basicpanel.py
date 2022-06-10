from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from pyqtgraph.dockarea import Dock
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal as Signal

class BasicPanel(Dock):
    #expmt_msg = Signal(str, str)
    expmt_msg = Signal(str)
    def __init__(self, **args):
        super().__init__('Experiment Panel', **args)
        self.headerfont = QtGui.QFont()
        self.headerfont.setFamily("Verdana")
        self.headerfont.setPointSize(18)

        self.addWidget(self._status_widgets(), 0, 0, 1, -1)
        self.addWidget(self._control_widgets(), 2, 0, 1, -1)
        self.addWidget(self._log_widget(), 4, 0, 1, -1)

    def _control_widgets(self):
        widget = QWidget()
        layout = QGridLayout()

        # Add device specifics buttons for performing actions here

        widget.setLayout(layout)
        return widget


    def _status_widgets(self):
        widget = QWidget()
        layout = QGridLayout()

        # Add device specific state readouts here

        widget.setLayout(layout)
        return widget

    def _log_widget(self):
        # Device logs
        self._log_label: QLabel = QLabel('Experiment Logs')
        self._log_label.setAlignment(Qt.AlignCenter)
        self._logs: QPlainTextEdit = QPlainTextEdit()
        return self._logs

    def _display_widget(self):
        pass

    def update_data(self, data):
        pass

    # Device specific logging
    ############################################################################
    def update_log(self, msg):
        self._logs.insertPlainText('{}: {}\n'.format(time.asctime(time.localtime(time.time())),
                                                    msg))
