from PyQt5 import QtGui, QtWidgets
from gui.mainwindow import MainWindow
import sys
from control.maincontroller import MainController

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()

    controller = MainController()
    # controller.run()

    mw.gui_changed.connect(controller.parse_signal)
    # controller.device_state.connect(mw.parse_signal)

    sys.exit(app.exec_())
