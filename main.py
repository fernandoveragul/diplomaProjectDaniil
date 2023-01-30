import sys

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication
from apps.application import Application
from dependencies.config import path_to_icon

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Application()
    window.setWindowIcon(QtGui.QIcon(f'{path_to_icon()}'))
    window.showMaximized()
    sys.exit(app.exec())
