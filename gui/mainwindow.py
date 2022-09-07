"""!
@brief Definition of the MainWindow class for organization and arrangement of
all GUI elements. Serves as the contact point for communication with the
controller/devices.
"""

import sys
import time
import __main__
from typing import ClassVar

from .basicpanel import BasicPanel
from .insightpanel import InsightPanel
from .delaystagepanel import DelayStagePanel
from .zipanel import ZiPanel
from .femtoramanpanel import FemtoRamanPanel
from .spectrumpanel import SpectrumPanel

from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtWidgets import (QMenu, QMenuBar, QStatusBar, QMainWindow,
                             QStatusBar, QAction, QLabel, QPlainTextEdit,
                             QMessageBox)
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
# from pyqtgraph.flowchart import Flowchart
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree.parameterTypes import ListParameter
from pyqtgraph.console import ConsoleWidget

class MainWindow(QMainWindow):
    """! The main SRS microscope window populated with the necessary
    elements for various experiment types and loading of data/projects.
    Contains a DockArea, to allow rearrangement of the various GUI
    modules.
    @todo Currently there is a bug requiring that titles of dock elements be
    hidden, which gets rid of the ability to move docks around and float them.
    """
    # Signals for the controller or experiment result connected through __main__
    ############################################################################

    ## @var gui_changed
    # (Signal) Emit GUI changes for parsing by the controller.
    cmd: ClassVar[Signal] = Signal(object, object, object)

    ## @var log_changed
    # (Signal) Emit log changes for parsing by the result file.
    log_changed: ClassVar[Signal] = Signal(str)

    # Signals for subcomponent GUI elements
    ############################################################################

    ## @var data
    # (Signal) Relays data to Slots on the experiment Docks.
    data: ClassVar[Signal] = Signal(object)

    ## @var insight_logs
    # (Signal) Emit insight specific logs.
    insight_logs: ClassVar[Signal] = Signal(object)
    insight_state: ClassVar[Signal] = Signal(dict)

    ## @var delaystage_logs
    # (Signal) Emit delay stage specific logs.
    delaystage_logs: ClassVar[Signal] = Signal(object)
    delaystage_state: ClassVar[Signal] = Signal(dict)

    ## @var zi_logs
    # (Signal) Emit lock-in amplifier specific logs.
    zi_logs: ClassVar[Signal] = Signal(object)
    zi_state: ClassVar[Signal] = Signal(dict)

    ## @var fssrs_logs
    # (Signal) Emit fsSRS experiment type specific logs.
    fssrs_logs: ClassVar[Signal] = Signal(object)

    ## @var spec_logs
    # (Signal) Emit spectrum acquisition specific logs.
    spec_logs: ClassVar[Signal] = Signal(object)

    def __init__(self):
        """! The MainWindow constructor."""
        super().__init__()
        self.setWindowTitle('SRS Microscope')

        ## @var _dock_area
        # The central DockArea for the window
        self._dock_area: DockArea = DockArea(self)
        self.setCentralWidget(self._dock_area)

        ## @var _statusbar
        # Statusbar that runs along the bottom of the window.
        self._statusbar: QStatusBar = QStatusBar(self)
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage('Starting with default settings.')

        # Top navigation in menu form (File... etc)
        self._create_menubar()

        # Create the system explorer tab
        self._create_explorer_dock()

        # Create the console, needs to be created after the explorer tab
        self._create_console_dock()

        # Create the actual experiment tab, must be made after explorer tab
        self._create_expmt_tab()

        self.update_log('Starting with default settings.')

    # Setup experiment explorer tab (Experiment parameters, Project hierarchy,
    # logging, etc)
    ############################################################################
    def _create_explorer_dock(self):
        """! Populate Dock GUI element containing general experiment parameters
        and logs.
        """
        ## @var _explorer_dock
        # Left aligned dock for global parameters and logs
        self._explorer_dock = Dock('Experiment Explorer', hideTitle=True)
        self._dock_area.addDock(self._explorer_dock, position='left')

        # Create the parameter tree widget and add to dock
        self._create_parameters_widget()
        self._param_label: QLabel = QLabel('Experiment Parameters')
        self._param_label.setAlignment(Qt.AlignCenter)
        self._explorer_dock.addWidget(self._param_label, 1, 0)
        self._explorer_dock.addWidget(self._parameters_widget, 2, 0)

        # Experiment logs
        self._log_label: QLabel = QLabel('Experiment Logs')
        self._log_label.setAlignment(Qt.AlignCenter)

        ## @var _logs
        # GUI element containing global logging information. This is written to
        # the results file on closing.
        self._logs: QPlainTextEdit = QPlainTextEdit()
        self._explorer_dock.addWidget(self._log_label, 3, 0)
        self._explorer_dock.addWidget(self._logs, 4, 0)

        # Adjust layout parameters
        self._explorer_dock.layout.setVerticalSpacing(10)
        self._explorer_dock.layout.setRowStretch(1, 0)
        self._explorer_dock.layout.setRowStretch(2, 3)
        self._explorer_dock.layout.setRowStretch(4, 3)

    def _create_parameters_widget(self):
        """! Create a ParameterTree for experiment parameters and add it to the
        _explorer_dock Dock widget.
        """
        ## @var _parameters_widget
        # ParameterTree widget for global parameters such as experiment type and
        # serial communincation ports
        self._parameters_widget = ParameterTree()

        ## @var _expmt_type
        # ListParameter for selecting which experiment dock is displayed
        self._expmt_type = ListParameter(name = 'Experiment Type',
                                         value = '------------',
                                         values = ['------------',
                                                   'Insight Controls',
                                                   'Delay Stage Controls',
                                                   'ZI Controls',
                                                   # 'Kcube Controls',
                                                   # 'DMD Controls',
                                                   'fsSRS',
                                                   'Spectrum Acquisition'])
                                                   # 'Spectral Focusing',
                                                   # 'Compressed Sensing',
                                                   # 'Time-0 Calibration'])

        # Signal/slot connections for updating the experiment display
        self._expmt_type.sigStateChanged.connect(self.global_changed)
        self._expmt_type.sigStateChanged.connect(self._update_expmt)

        ## @var _insight_com
        # ListParameter for selecting the physical COM port of the Insight
        self._insight_com = ListParameter(name = 'Insight COM Port',
                                          value = 'COM6',
                                          values = ['COM1', 'COM2', 'COM3',
                                                    'COM4', 'COM5', 'COM6',
                                                    'COM7', 'COM8'])

        # Relevant signals/slots
        self._insight_com.sigStateChanged.connect(self.global_changed)

        ## @var _delaystage_com
        # ListParameter for selecting the physical COM port of the delay stage
        self._delaystage_com = ListParameter(name = 'Delay Stage COM Port',
                                             value = 'COM7',
                                             values = ['COM1', 'COM2', 'COM3',
                                                       'COM4', 'COM5', 'COM6',
                                                       'COM7', 'COM8'])
        # Relevant signals/slots
        self._delaystage_com.sigStateChanged.connect(self.global_changed)

        # Add all the parameters to the ParameterTree
        self._parameters_widget.addParameters(self._expmt_type)
        self._parameters_widget.addParameters(self._insight_com)
        self._parameters_widget.addParameters(self._delaystage_com)

    # Create experiment tab, for specific control and image display depending
    # on experiment type
    ############################################################################
    def _create_expmt_tab(self):
        """! Create the docks to display all widgets and features specific to the
        selected experiment. Changes in experiment type will change which dock is
        displayed in the DockArea; however all docks are created immediately.
        This allows simple switching between experiment modes without loss of
        recorded data or GUI state, at the cost of a little more overhead.
        """
        # Create all tabs and connect relevant signals and slots for updating
        # the necessary gui components
        # The data signal is connected to the controllers data signal for
        # relaying data to the experiment tabs for display. Each tab handles
        # this in it's own way.
        # Each panel also has it's own corresponding log signal. E.g. ZI logs
        # don't require information on the Insight's OPO state.

        ## @var _current_panel
        # The current panel being displayed. Initialized to a BasicPanel but
        # updating the experiment type updates this variable to point to a
        # specific experiment panel
        self._current_panel = BasicPanel(hideTitle=True)
        self._dock_area.addDock(self._current_panel, position = 'right')
        self._current_panel.expmt_msg.connect(self.update_log)

        ## @var _insight_panel
        # Contains Insight specific GUI elements
        self._insight_panel = InsightPanel(hideTitle=True,
                                           statpath='srsmicro/gui/format/insight_status.fmt',
                                           ctrlpath='srsmicro/gui/format/insight_controls.ctrl')
        self._insight_panel.expmt_msg.connect(self.update_log)
        self._insight_panel.cmd.connect(self.cmd)
        self.data.connect(self._insight_panel.update_data)
        self.insight_logs.connect(self._insight_panel.update_log)
        self.insight_state.connect(self._insight_panel.update_state)

        ## @var _delaystage_panel
        # Contains delay stage specific GUI elements
        self._delaystage_panel = DelayStagePanel(hideTitle=True,
                                           statpath='srsmicro/gui/format/delaystage_status.fmt',
                                           ctrlpath='srsmicro/gui/format/delaystage_controls.ctrl')
        self._delaystage_panel.expmt_msg.connect(self.update_log)
        self._delaystage_panel.cmd.connect(self.cmd)
        self.data.connect(self._delaystage_panel.update_data)
        self.delaystage_logs.connect(self._delaystage_panel.update_log)
        self.delaystage_state.connect(self._delaystage_panel.update_state)

        ## @var _zi_panel
        # Contains lock-in amplifier specific GUI elements
        self._zi_panel = ZiPanel(hideTitle=True,
                                           statpath='srsmicro/gui/format/lockin_status.fmt',
                                           ctrlpath='srsmicro/gui/format/lockin_controls.ctrl')
        self._zi_panel.expmt_msg.connect(self.update_log)
        self._zi_panel.cmd.connect(self.cmd)
        self.data.connect(self._zi_panel.update_data)
        self.zi_logs.connect(self._zi_panel.update_log)
        self.zi_state.connect(self._zi_panel.update_state)

        ## @var _fssrs_panel
        # Contains GUI elements for running a simple SRS experiment and
        # displaying the images/results
        self._fssrs_panel = FemtoRamanPanel(hideTitle=True,
                                           statpath='srsmicro/gui/format/fssrs_status.fmt',
                                           ctrlpath='srsmicro/gui/format/fssrs_controls.ctrl')
        self._fssrs_panel.expmt_msg.connect(self.update_log)
        self._fssrs_panel.cmd.connect(self.cmd)
        self.data.connect(self._fssrs_panel.update_data)
        self.fssrs_logs.connect(self._fssrs_panel.update_log)

        ## @var _spec_panel
        # Contains GUI elements for collecting a scanned spectrum.
        self._spec_panel = SpectrumPanel(hideTitle=True,
                                         statpath='srsmicro/gui/format/spectrum_status.fmt',
                                         ctrlpath='srsmicro/gui/format/spectrum_controls.ctrl')
        self._spec_panel.expmt_msg.connect(self.update_log)
        self._spec_panel.cmd.connect(self.cmd)
        self.spec_logs.connect(self._spec_panel.update_log)
        # self.data.connect(self._fssrs_panel.update_data)


    def _update_expmt(self, obj, param, val):
        """! Slot for updating the experiment type parameter. Only the final
        val parameter is used; however, the other two are needed to match the
        emitted signal pattern.
        @param obj Reference to the GUI element.
        @param param The parameter that was changed.
        @param val The value to which the experiment was changed.
        """
        panels = { '------------' : BasicPanel(hideTitle=True),
                   'Insight Controls' : self._insight_panel,
                   'Delay Stage Controls' : self._delaystage_panel,
                   'ZI Controls' : self._zi_panel,
                   'fsSRS' : self._fssrs_panel,
                   'Spectrum Acquisition' : self._spec_panel }

        self._current_panel.close()
        self._current_panel = panels[str(val)]
        self._dock_area.addDock(self._current_panel, position='right')


    def parse_state(self, device, params):
        """! Slot for updating device specific GUI elements, e.g. to display a
        parameter change. This slot parses the signal and relays a separate
        signal to the appropriate GUI elements corresponding to the device.
        @param device (str) The device whose state was updated.
        @param params (dict) The parameters/settings for the device that changed.
        """
        if device == 'Insight':
            self.insight_state.emit(params)
        elif device == 'Insight+Logs':
            self.insight_logs.emit(params)

        elif device == 'Delay Stage':
            self.delaystage_state.emit(params)

        elif device == 'Delay Stage+Logs':
            self.delaystage_logs.emit(params)
        elif device == 'Lockin':
            self.zi_state.emit(params)
            
        elif device == 'Lockin+Logs':
            self.zi_logs.emit(params)

    # Console tab and related options
    ############################################################################
    def _create_console_dock(self):
        """! Create the dock to display a console to interact with the program.
        The Console widget contain within the dock inherits the __main__
        namespace (accesed through 'm.'') giving it access to all objects. This
        allows the user to send commands to specific devices if needed, but
        should be used sparingly unless the relevant device manuals have been
        read. The console is hidden by default but can be accessed through the
        File menu.
        """
        ## @var _console_dock
        # Dock GUI element containing the Console Widget
        self._console_dock = Dock('Console', hideTitle=True)
        self._dock_area.addDock(self._console_dock, position='bottom', relativeTo=self._explorer_dock)
        self._console_dock.hide()

        ## @var _console
        # The actual console widget. It inherits the __main__ namespace as m.
        # E.g. Access the controller like this: m.controller
        self._console = ConsoleWidget(namespace={'self':self, 'm':__main__})
        self._console.hide()
        self._showconsole = False

        # Redirect stdout and stderr to the console
        # sys.stdout = self._console
        # sys.stderr = self._console
        self._console_dock.addWidget(self._console)

    def _toggleconsole(self):
        """! Toggle visibility of the console. Accessed through File menu
        actions.
        """
        if not self._showconsole:
            self._console_dock.show()
            self._console.show()
            self._showconsole = True
        else:
            self._console_dock.hide()
            self._console.hide()
            self._showconsole = False

    # Emit on change
    ############################################################################
    def global_changed(self, obj, param, val):
        """! Emit a signal to be parsed by the controller."""
        parameter = str(obj).split('\'')[1]
        self.cmd.emit('Global', parameter, str(val))
        self.update_log('{} changed to {}'.format(parameter, str(val)))

    def expmt_changed(self, device, param, val):
        self.update_log('{} attempting to: {}'.format(device, param))
        self.gui_changed.emit(device, param, val)

    # Logging and status bar
    ############################################################################
    @property
    def statusbar(self):
        return None

    @statusbar.setter
    def statusbar(self, msg):
        """! Setter for the statusbar. Change the message that is displayed."""
        self._statusbar.showMessage(msg)

    def update_log(self, msg):
        """! Add text to the log widget.
        @param msg The text to be added to the logs.
        """
        self._logs.insertPlainText('{}: {}\n'.format(time.asctime(time.localtime(time.time())),
                                                    msg))
        self.statusbar = msg

    # Menubar options and actions
    ############################################################################
    def _create_menubar(self):
        """! Create the menubar and populate it."""
        ## @var _menubar
        # Menubar for experiment options. Open/Save, display console etc.
        self._menubar: QMenuBar = QMenuBar()
        self.setMenuBar(self._menubar)
        self._create_filemenu()
        self._menubar.addMenu(self._filemenu)
        self._create_routinesmenu()
        self._menubar.addMenu(self._routinesmenu)

    def _create_filemenu(self):
        """! Create the 'File' menu to be added to the menubar."""
        ## @var _filemenu
        # Contains general options for the experiment and display.
        self._filemenu: QMenu = QMenu('File', self)

        ## @var _open_act
        # QAction for the _filemenu open option. Not in use.
        self._open_act: QAction = QAction('Open', self)
        self._open_act.setStatusTip('Open Previous Project')
        self._open_act.triggered.connect(self._openfile)

        ## @var _save_im_act
        # QAction for the _filemenu Save Image option. Not in use.
        self._save_im_act: QAction = QAction('Save Image', self)
        self._save_im_act.setStatusTip('Save Current Image')
        self._save_im_act.triggered.connect(self._saveim)

        ## @var _save_state
        # QAction for the _filemenu Save ZI State option
        self._save_zistate_act: QAction = QAction('Save ZI State', self)
        self._save_zistate_act.setStatusTip('Save ZI Parameter Settings to File')
        self._save_zistate_act.triggered.connect(self._savezistate)

        ## @var _console_act
        # QAction for the _filemenu Console option. Toggles display of the
        # console Dock/Widget.
        self._console_act: QAction = QAction('&Console', self)
        self._console_act.setToolTip(('**WARNING** Read device manuals. '
                                      'Improper function calls can cause '
                                      'irreperable damage.'))
        self._console_act.setStatusTip('Open or Close the Console')
        self._console_act.triggered.connect(self._toggleconsole)
        self._console_act.setShortcut('Alt+C')

        # Add all options to the menu.
        self._filemenu.addAction(self._open_act)
        self._filemenu.addAction(self._save_im_act)
        self._filemenu.addAction(self._save_zistate_act)
        self._filemenu.addSeparator()
        self._filemenu.addAction(self._console_act)

        # Show mouse hover tool tips.
        self._filemenu.setToolTipsVisible(True)

    def _create_routinesmenu(self):
        """! Create the 'Routines' menu to be added to the menubar."""
        ## @var _routinesmenu
        # Contains options for running useful functions for generating data
        # that supports or augments experimental data.
        self._routinesmenu: QMenu = QMenu('Routines', self)

        ## @var _t0_act
        # QAction for selecting to run a time-zero calibration of laser temporal
        # coincidence.
        self._t0_act: QAction = QAction('&T0 Calibration', self)
        self._t0_act.setStatusTip('Run a time-zero calibration.')
        self._t0_act.triggered.connect(self._t0)
        self._t0_act.setShortcut('Alt+T')

        ## @var _t0_act
        # QAction for selecting to run a time-zero calibration of laser temporal
        # coincidence.
        self._specscan_act: QAction = QAction('Scan Spectrum', self)
        self._specscan_act.setStatusTip('With chirped lasers run collect a spectrum.')
        self._specscan_act.triggered.connect(self._specscan)

        # Add all options to the menu.
        self._routinesmenu.addAction(self._t0_act)
        self._routinesmenu.addAction(self._specscan_act)

        # Show mouse hover tool tips.
        self._routinesmenu.setToolTipsVisible(True)

    def _openfile(self):
        """! Open a file. Not currently in use."""
        pass
    def _saveim(self):
        """! Save an image. Not currently in use."""
        pass
    def _savezistate(self):
        """! Save a configuration/state. Not currently in use."""
        pass

    def _t0(self):
        """! Run a time-zero calibration.
        @todo Implement the signal parsing and multi-device coordination needed
        to produce a time-zero calibration.
        @todo Implement a storing mechanism for time-zero data.
        """
        pass

    def _specscan(self):
        """! Collect a spectrum using chirped lasers.
        @todo Implement the signal parsing and multi-device coordination needed
        to collect a chirped-laser spectrum.
        """
        pass

    # Application close and cleanup
    ############################################################################
    def closeEvent(self, event):
        """! Shutdown routine. On clicking the 'X' for closing a message will
        appear asking for confirmation. Acceptance closes the application
        and emits signals where needed to allow proper shutdown and logging.
        """
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
