"""!
@brief Definition of the BasicPanel class for providing the parsing functions to
populate device specific GUI panels.
"""

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from pyqtgraph.dockarea import Dock
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QPlainTextEdit,
                             QLineEdit, QPushButton)
from PyQt5.QtCore import pyqtSignal as Signal
import pyqtgraph as pg
import numpy as np
import re


class BasicPanel(Dock):
    """! The BasicPanel serves as a template class for device specific GUI
    elements. Basic organizational units are included, as are global parameters
    like font sizes/choices.
    """
    ## @var expmt_msg
    # (Signal) Emit a log message/statusbar update.
    expmt_msg = Signal(str)

    ## @var param_change
    # (Signal) Emit a parameter change attempt for controller/device processing.
    cmd = Signal(object, object, object)

    def __init__(self, *args, **kwargs):
        """! The BasicPanel constructor.
        @param statpath (str) The path to the text file containing the GUI's
        status elements. These elements only display information.
        @param ctrlpath (str) The path to the text file containing the GUI's
        control elements. These elements allow interaction with the associated
        device.
        """
        super().__init__('Experiment Panel', *args, hideTitle=kwargs['hideTitle'])

        ## @var h1font
        # (QtGui.QFont) The font used for section headers on the panel.
        self.h1font = QtGui.QFont()
        self.h1font.setFamily("Verdana")
        self.h1font.setPointSize(18)

        ## @var h2font
        # (QtGui.QFont) The font used for subsection headers on the panel.
        self.h2font = QtGui.QFont()
        self.h2font.setFamily("Verdana")
        self.h2font.setPointSize(14)

        ## @var h1_patn
        # (str) Regex pattern for matching header 1 type text
        # (?<^# ) Looks behind for the line starting with '# ' pattern
        # (.*) Matches any type and any number of characters following it
        self.h1_patn = '(?<=^# )(.*)'

        ## @var h2_patn
        # (str) Regex pattern for matching header 1 type text
        # (?<^## ) Looks behind for the line starting with '## ' pattern
        # (.*) Matches any type and any number of characters following it
        self.h2_patn = '(?<=^## )(.*)'

        ## @var status_vars
        # (dict) Contains GUI elements that report on device parameters.
        # These elements do not take user input.
        self.status_vars = {}

        ## @var control_vars
        # (dict) Contains GUI elements that modify device parameters.
        # These elements, like buttons, take user input.
        self.control_vars = {}

        ## @var cmd_patn
        # (str) Regex pattern for matching a command.
        # (?<=\$) Looks behind for a '$' character
        # (.*) Then matches any number of characters before
        # (?=\$) which matches a terminating '$' character
        self.cmd_patn = '(?<=\$)(.*)(?=\$)'

        ## @var param_patn
        # (str) Regex pattern for matching command parameters. Must be used with
        # re.findall (not search) to capture all parameters.
        # (?<=\{) Looks behind for a '{}' character
        # (.*) Then matches any number of characters before
        # (?=\}) which matches a terminating '}' character
        self.param_patn = '(?<=\{)(.*?)(?=\})'

        if 'statpath' in kwargs.keys():
            widget = self._status_widgets(kwargs['statpath'])
            self.addWidget(widget, 0, 0, 1, -1)
        else:
            self.addWidget(QLabel('Device Status'), 0, 0, 1, -1)
            # self.parse_format('srsmicro/gui/format/defaultstatus.fmt')

        # self.addWidget(self._status_widgets(), 0, 0, 1, -1)
        if 'ctrlpath' in kwargs.keys():
            widget = self._control_widgets(kwargs['ctrlpath'], self.funcs)
            self.addWidget(widget, 2, 0, 1, -1)
        else:
            self.addWidget(QLabel('Device Controls'), 2, 0, 1, -1)
        # self.addWidget(self._control_widgets(), 2, 0, 1, -1)
        self.addWidget(self._log_widget(), 4, 0, 1, -1)

    # Parse text to GUI elements
    ############################################################################
    def _status_widgets(self, path):
        """! Parses a provided text file (.fmt extension) to populate the status
        GUI elements. Saves the elements in the object's status_vars variable
        allowing them to be updated automatically based upon the associated
        device's status.
        @param path (str) Path to the format file.
        """
        widget = QWidget()
        layout = QGridLayout()
        row = 0
        col = 0
        with open(path) as f:
            for line in f:
                s = line.split('&')
                for object in s:
                    if re.search(self.h1_patn, object):
                        text = re.search(self.h1_patn, object).group()
                        label = QLabel('{}'.format(text))
                        label.setAlignment(Qt.AlignCenter)
                        label.setFont(self.h1font)
                        layout.addWidget(label, row, col, 1, -1)
                        row += 1
                    elif re.search(self.h2_patn, object):
                        text = re.search(self.h2_patn, object).group()
                        label = QLabel('{}'.format(text))
                        label.setAlignment(Qt.AlignCenter)
                        label.setFont(self.h2font)
                        layout.addWidget(label, row, col, 1, -1)
                        row += 1
                    else:
                        obj = object.lstrip()
                        if '*' in obj:
                            obj = obj.strip()
                            obj = obj[1:]
                            self.status_vars[obj] = QLabel('0')
                            self.status_vars[obj].setAlignment(Qt.AlignLeft)
                            layout.addWidget(self.status_vars[obj], row, col, 1, 1)
                        else:
                            label = QLabel('{}'.format(obj))
                            label.setAlignment(Qt.AlignLeft)
                            layout.addWidget(label, row, col, 1, 1)
                    col += 1
                col = 0
                row += 1
        widget.setLayout(layout)
        return widget

    def _control_widgets(self, path, funcs):
        """! Parses a provided text file (.ctrl extension) to populate the control
        GUI elements. Saves the elements in the object's control_vars variable
        allowing them to be updated automatically based upon the associated
        device's status. Associates functions to the GUI elements.
        @param path (str) Path to the format file.
        @param funcs (dict) Dictionary of str:method pairs associating function
        names written in the text file to the actual python methods.
        """
        widget = QWidget()
        layout = QGridLayout()
        row = 0
        col = 0
        with open(path) as f:
            for line in f:
                s = line.split('&')
                for object in s:
                    if re.search(self.h1_patn, object):
                        text = re.search(self.h1_patn, object).group()
                        label = QLabel('{}'.format(text))
                        label.setAlignment(Qt.AlignCenter)
                        label.setFont(self.h1font)
                        layout.addWidget(label, row, col, 1, -1)
                        row += 1
                    elif re.search(self.h2_patn, object):
                        text = re.search(self.h2_patn, object).group()
                        label = QLabel('{}'.format(text))
                        label.setAlignment(Qt.AlignCenter)
                        label.setFont(self.h2font)
                        layout.addWidget(label, row, col, 1, -1)
                        row += 1
                    elif re.search(self.cmd_patn, object):
                        cmd = re.search(self.cmd_patn, object).group()
                        params = re.findall(self.param_patn, object)
                        if cmd == 'btn':
                            dispname = params[0]
                            varname = params[1]
                            funcname = params[2]
                            btn = QPushButton(dispname)#pg.FeedbackButton(dispname)
                            # btn.setText(dispname)
                            try:
                                btn.clicked.connect(self.funcs[funcname])
                            except KeyError as err:
                                print('No function associated with button.')
                            self.control_vars[varname] = btn
                            layout.addWidget(self.control_vars[varname], row, col, 1, 1)
                        elif cmd == 'form':
                            varname = params[0]
                            form = QLineEdit()
                            self.control_vars[varname] = form
                            layout.addWidget(self.control_vars[varname], row, col, 1, 1)
                        elif cmd == 'imv':
                            varname = params[0]
                            dataname = params[1]
                            imv = pg.ImageView()
                            self.control_vars[varname] = imv
                            self.control_vars[dataname] = np.random.random([512, 512])
                            self.control_vars[varname].show()
                            self.control_vars[varname].setImage(self.control_vars[dataname])
                            layout.addWidget(self.control_vars[varname], row, col, 1, 1)
                    col += 1
                col = 0
                row += 1
        widget.setLayout(layout)
        return widget

    # Methods for updating GUI display - may be overwritten by subclasses
    ############################################################################
    def update_state(self, params):
        """! Slot to update status widgets.
        @param params Device parameters and the values to be displayed.
        """
        for param in params:
            if param in self.status_vars:
                try:
                    self.status_vars[param].setText('{:.3g}'.format(params[param]))
                except ValueError as err:
                    self.status_vars[param].setText('{}'.format(params[param]))
            else:
                self._update_controls(param, params[param])

    def _update_controls(self, param, val):
        """! Private, device specific, function called by the update_state slot
        to perform updating of control GUI elements. This allows changing the
        display of those elements to provide additional information to that
        provided by the status elements. E.g button colors or toggling for
        indicating activation.
        @param param The parameter from the associated device.
        @val The value of that parameter.
        """
        pass

    def update_data(self, data):
        """! Slot to update display upon receipt of new data.
        @param data The new data to be displayed.
        """
        pass

    # Logging methods
    ############################################################################
    def _log_widget(self):
        """! A widget to maintain device specific logging information. This can
        include more detailed information (such as specific hardware failures)
        than the more general experiment logs.
        """
        ## @var _log
        # The GUI element that maintains the log. Its content can be written to
        # a file.
        self._log_label: QLabel = QLabel('Experiment Logs')
        self._log_label.setAlignment(Qt.AlignCenter)
        self._logs: QPlainTextEdit = QPlainTextEdit()
        return self._logs

    def update_log(self, msg):
        """! Slot to update the device log.
        @param msg Text to be added to the log.
        """
        self._logs.insertPlainText('{}: {}\n'.format(time.asctime(time.localtime(time.time())),
                                                    msg))

        def _display_widget(self):
            pass
