import os
import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLayout, QPushButton
from display import main_window, test_window
from dependencies.config import get_filtered_files_list


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

        self.__create_tutorials_buttons(self.verticalLayout_2)
        self.__create_examples_buttons(self.verticalLayout_3)

    def __create_tutorials_buttons(self, layout: QLayout):
        files: list[str] = get_filtered_files_list(name_folder="tutorials")
        for f in files:
            chapter, current = f.split(".")[0].split("_")
            _btn_ = QPushButton()
            _btn_.setObjectName(f"btnExample{chapter}_{current}")
            _btn_.setText(f"{current}")
            _btn_.clicked.connect()

    def __create_examples_buttons(self, layout: QLayout) -> None:
        files: list[str] = get_filtered_files_list(name_folder="examples")
        tests: list[str] = get_filtered_files_list(name_folder="tests")


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
