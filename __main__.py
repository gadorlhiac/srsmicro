from PyQt5 import QtGui, QtWidgets
from gui.mainwindow import MainWindow
import sys
from control.maincontroller import MainController
from utilities.experimentresult import ExperimentResult

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()

    controller = MainController()
    controller.start()

    mw.gui_changed.connect(controller.parse_signal)
    # controller.device_state.connect(mw.parse_signal)

    result = ExperimentResult()
    mw.log_changed.connect(result.write_logs)
    # Clean shutdown
    app.aboutToQuit.connect(controller.stop)
    app.aboutToQuit.connect(result.stop)
    # app.aboutToQuit.connect(mw.stop)
    sys.exit(app.exec_())
