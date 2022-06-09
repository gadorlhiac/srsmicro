from PyQt5 import QtGui, QtWidgets
from gui.mainwindow import MainWindow
import sys
from control.maincontroller import MainController
from utilities.experimentresult import ExperimentResult

if __name__ == '__main__':
    # Application and GUI
    ############################################################################
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()

    # Device controller
    ############################################################################
    controller = MainController()

    # Signals/Slots for relaying GUI changes to controller, and device status
    # updates back to the GUI
    ############################################################################
    mw.gui_changed.connect(controller.parse_signal)
    controller.log.connect(mw.update_log)
    # controller.device_state.connect(mw.parse_signal)

    # Data and log management
    ############################################################################
    result = ExperimentResult()
    # When logs are updated on GUI, update them in the result object
    mw.log_changed.connect(result.write_logs)


    # Cleanup on shutdown
    ############################################################################
    app.aboutToQuit.connect(controller.stop)
    app.aboutToQuit.connect(result.stop)
    # app.aboutToQuit.connect(mw.stop)

    # Start application and device communication
    controller.init_devices()
    sys.exit(app.exec_())
