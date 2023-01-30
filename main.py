import sys
from PyQt6.QtWidgets import QApplication
from apps.application import Application

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())
