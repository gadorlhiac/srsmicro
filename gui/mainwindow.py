import sys
import time
import __main__
from typing import ClassVar

from .basicpanel import BasicPanel
from .insightpanel import InsightPanel
from .delaystagepanel import DelayStagePanel
from .femtoramanpanel import FemtoRamanPanel

from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtWidgets import (QMenu, QMenuBar, QStatusBar, QMainWindow,
                             QStatusBar, QAction, QLabel, QTableWidget,
                             QTableWidgetItem, QPlainTextEdit, QWidget, QMessageBox)
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
# from pyqtgraph.flowchart import Flowchart
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree.parameterTypes import ListParameter
from pyqtgraph.console import ConsoleWidget

class MainWindow(QMainWindow):
    gui_changed: ClassVar[Signal] = Signal(object, str, str, str)
    log_changed: ClassVar[Signal] = Signal(str)
    data: ClassVar[Signal] = Signal(object)

    def __init__(self):
        """
        The main SRS microscope window populated with the necessary elements
        for various experiment types and loading of data/projects.
        """
        super().__init__()
        self.setWindowTitle('SRS Microscope')

        # Create the central dock area for the window
        self._dock_area: DockArea = DockArea(self)
        # self._dock_area: QWidget = QWidget()
        self.setCentralWidget(self._dock_area)

        # Create the status bar and menubar. Create the statusbar first.
        self._statusbar: QStatusBar = QStatusBar(self)
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage('Starting with default settings.')

        self._create_menubar()

        # Create the system explorer tab
        self._create_explorer_tab()

        # Create the console, needs to be created after the explorer tab
        self._create_console_tab()

        # Create the actual experiment tab, must be made after explorer tab
        self._create_expmt_tab()

        self.update_log('Starting with default settings.')

    # Setup experiment explorer tab (Experiment parameters, Project hierarchy,
    # logging, etc)
    ############################################################################
    def _create_explorer_tab(self):
        """
        Populated Dock GUI element containing experiment parameters, data, and
        directory exploration.
        """
        # Create explorer dock and add to central dock area.
        self._explorer_tab = Dock('Experiment Explorer', hideTitle=True)
        self._dock_area.addDock(self._explorer_tab, position='left')

        # Create the parameter tree widget and add to dock
        self._create_parameters_widget()
        self._param_label: QLabel = QLabel('Experiment Parameters')
        self._param_label.setAlignment(Qt.AlignCenter)
        self._explorer_tab.addWidget(self._param_label, 1, 0)
        self._explorer_tab.addWidget(self._parameters_widget, 2, 0)

        # Experiment logs
        self._log_label: QLabel = QLabel('Experiment Logs')
        self._log_label.setAlignment(Qt.AlignCenter)
        self._logs: QPlainTextEdit = QPlainTextEdit()
        self._explorer_tab.addWidget(self._log_label, 3, 0)
        self._explorer_tab.addWidget(self._logs, 4, 0)

        # Adjust layout parameters
        self._explorer_tab.layout.setVerticalSpacing(10)
        self._explorer_tab.layout.setRowStretch(1, 0)
        self._explorer_tab.layout.setRowStretch(2, 3)
        self._explorer_tab.layout.setRowStretch(4, 3)

    def _create_parameters_widget(self):
        self._parameters_widget = ParameterTree()
        self._expmt_type = ListParameter(name = 'Experiment Type',
                                         value = '------------',
                                         values = ['------------',
                                                   'Insight Controls',
                                                   'Delay Stage Controls',
                                                   'ZI Controls',
                                                   'Kcube Controls',
                                                   'DMD Controls',
                                                   'fsSRS',
                                                   'Spectral Focusing',
                                                   'Compressed Sensing',
                                                   'Time-0 Calibration'])

        self._expmt_type.sigStateChanged.connect(self.global_changed)
        self._expmt_type.sigStateChanged.connect(self._update_expmt)

        self._insight_com = ListParameter(name = 'Insight COM Port',
                                          value = 'COM6',
                                          values = ['COM1', 'COM2', 'COM3',
                                                    'COM4', 'COM5', 'COM6',
                                                    'COM7', 'COM8'])
        self._insight_com.sigStateChanged.connect(self.global_changed)

        self._delay_stage_com = ListParameter(name = 'Delay Stage COM Port',
                                             value = 'COM7',
                                             values = ['COM1', 'COM2', 'COM3',
                                                       'COM4', 'COM5', 'COM6',
                                                       'COM7', 'COM8'])
        self._delay_stage_com.sigStateChanged.connect(self.global_changed)

        self._parameters_widget.addParameters(self._expmt_type)
        self._parameters_widget.addParameters(self._insight_com)
        self._parameters_widget.addParameters(self._delay_stage_com)

    # Create experiment tab, for specific control and image display depending
    # on experiment type
    ############################################################################
    def _create_expmt_tab(self):
        """
        The dock to display all widgets and features specific to the selected
        experiment. Changes in experiment type will reconstruct what is
        displayed in this dock.
        """
        self._expmt_tab = BasicPanel(hideTitle=True)
        self._dock_area.addDock(self._expmt_tab, position = 'right')
        self._expmt_tab.expmt_msg.connect(self.update_log)

    def _update_expmt(self, obj, param, val):
        new_panels = {'Insight Controls': InsightPanel(hideTitle=True),
                      'Delay Stage Controls': DelayStagePanel(hideTitle=True),
                      'fsSRS': FemtoRamanPanel(hideTitle=True)}

        self._expmt_tab.close()

        panel = new_panels[str(val)]
        self._expmt_tab = self._dock_area.addDock(dock=panel,
                                                  name = 'Experiment Panel',
                                                  position = 'right',
                                                  relativeTo = self._explorer_tab)
        self._expmt_tab.expmt_msg.connect(self.update_log)
        self.data.connect(self._expmt_tab.update)

    def new_data(self, data):
        self.data.emit(data)

    def parse_signal(self, ref, obj, changed, val):
        print(ref, obj, changed, val)

    # Console tab and related options
    ############################################################################
    def _create_console_tab(self):
        self._console_tab = Dock('Console', hideTitle=True)
        self._dock_area.addDock(self._console_tab, position='bottom', relativeTo=self._explorer_tab)
        self._console_tab.show()
        self._console = ConsoleWidget(namespace={'self':self, 'm':__main__})
        self._console.show()
        self._showconsole = True

        # sys.stdout = self._console
        # sys.stderr = self._console
        self._console_tab.addWidget(self._console)

    def _toggleconsole(self):
        if not self._showconsole:
            self._console_tab.show()
            self._console.show()
            self._showconsole = True
        else:
            self._console_tab.hide()
            self._console.hide()
            self._showconsole = False

    # Emit on change
    ############################################################################
    def global_changed(self, obj, param, val):
        parameter = str(obj).split('\'')[1]
        self.gui_changed.emit(self, 'global', parameter, str(val))
        self.update_log('{} changed to {}'.format(parameter, str(val)))

    def expmt_changed(self, obj, param, val):
        pass

    # Logging and status bar
    ############################################################################
    @property
    def statusbar(self):
        return None

    @statusbar.setter
    def statusbar(self, msg):
        self._statusbar.showMessage(msg)

    def update_log(self, msg):
        self._logs.insertPlainText('{}: {}\n'.format(time.asctime(time.localtime(time.time())),
                                                    msg))

    # Application close and cleanup
    ############################################################################
    def closeEvent(self, event):
        result = QMessageBox.question(self, 'Confirm Exit',
                                      'Are you sure you want to exit ?',
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            sys.stdout = sys.__stdout__
            self.update_log('Shutting down.')
            self.log_changed.emit(self._logs.toPlainText())
            # with open('logs.txt', 'a') as f:
            #     f.write(self._logs.toPlainText())
            event.accept()

    # Menubar options and actions
    ############################################################################
    def _create_menubar(self):
        self._menubar: QMenuBar = QMenuBar()
        self.setMenuBar(self._menubar)
        self._create_filemenu()
        self._menubar.addMenu(self._filemenu)

    def _create_filemenu(self):
        self._filemenu: QMenu = QMenu('&File', self)

        self._open_act: QAction = QAction('&Open', self)
        self._open_act.setStatusTip('Open Previous Project')
        self._open_act.triggered.connect(self._openfile)

        self._save_im_act: QAction = QAction('&Save Image', self)
        self._save_im_act.setStatusTip('Save Current Image')
        self._save_im_act.triggered.connect(self._saveim)

        self._save_state_act: QAction = QAction('&Save State', self)
        self._save_state_act.setStatusTip('Save GUI Configuration')
        self._save_state_act.triggered.connect(self._savestate)

        # To open or close the console
        self._console_act: QAction = QAction('&Console', self)
        self._console_act.setToolTip(('**WARNING** Read device manuals. '
                                      'Improper function calls can cause '
                                      'irreperable damage.'))
        self._console_act.setStatusTip('Open or Close the Console')
        self._console_act.triggered.connect(self._toggleconsole)

        self._filemenu.addAction(self._open_act)
        self._filemenu.addAction(self._save_im_act)
        self._filemenu.addAction(self._save_state_act)
        self._filemenu.addSeparator()
        self._filemenu.addAction(self._console_act)

        self._filemenu.setToolTipsVisible(True)

    def _openfile(self):
        pass
    def _saveim(self):
        pass
    def _savestate(self):
        pass
