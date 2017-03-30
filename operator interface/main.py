import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal)
from core.gui.gui_controller import Controller
from core.robot.robot_controller import Robot
from messages import command_container

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()

    champ = Robot()
    gui = Controller(dialog, command_container)

    champ.set_partner_add_to_queue_method(gui.message_queue.put)
    gui.set_partner_add_to_queue_method(champ.message_queue.put)

    champ.start()
    gui.start()

    dialog.show()
    sys.exit(app.exec_())
