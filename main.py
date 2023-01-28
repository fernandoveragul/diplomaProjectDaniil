import os
import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget
from display import main_window, test_window
from files.examples import inf

class Test(QWidget, test_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)



class Application(QMainWindow, main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.vtextTutorialInfo.settings().setAttribute(
            self.vtextTutorialInfo.settings().WebAttribute.PluginsEnabled, True
        )

        self.vtextTutorialInfo.settings().setAttribute(
            self.vtextTutorialInfo.settings().WebAttribute.PdfViewerEnabled, True
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    p = os.path.dirname(sys.argv[0])
    f = os.listdir(f'{os.path.dirname(sys.argv[0])}/files/examples')
    print(f)
    print(f"file://{p}/files/examples/{f[0]}")
    window.vtextTutorialInfo.setUrl(QUrl(f"file://{p}/files/examples/{f[0]}"))
    sys.exit(app.exec())
