import os
import platform
import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLayout, QPushButton, QMessageBox
from display import main_window, test_window
from dependencies.config import get_filtered_files_list, get_paths_to_files


class Test(QWidget, test_window):
    def __init__(self, test_name: str):
        super().__init__()
        self.setupUi(self)
        self.test_name = test_name


class Application(QMainWindow, main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__window_with_test = None
        self.__enable_special_settings()

        self.__create_tutorials_buttons(self.layTutorial)
        self.__create_examples_buttons(self.layExample)
        self.btnRunTest.clicked.connect(self.__open_window_with_current_test)

    def __create_tutorials_buttons(self, layout: QLayout):
        def add_function_to_button(*, index: int):
            paths: list[str] = get_paths_to_files(folder_name="tutorials")
            self.vtextTutorialInfo.setUrl(QUrl(f"file://{paths[index]}"))

        files: list[str] = get_filtered_files_list(folder_name="tutorials")
        for i, file in enumerate(files):
            chapter, current = file.split(".")[0].split("_")
            _btn_ = QPushButton()
            _btn_.setObjectName(f"btnTutorial{chapter}_{current}")
            _btn_.setText(f"ГЛАВА {current}")
            _btn_.clicked.connect(lambda ch, ind=i: add_function_to_button(index=ind))
            layout.addWidget(_btn_)

    def __create_examples_buttons(self, layout: QLayout) -> None:
        def add_function_to_button(*, index: int):
            paths: list[str] = get_paths_to_files(folder_name="examples")
            self.vtextExampleInfo.setUrl(QUrl(f"file://{paths[index]}"))

        files: list[str] = get_filtered_files_list(folder_name="examples")
        for i, file in enumerate(files):
            chapter, current = file.split(".")[0].split("_")
            _btn_ = QPushButton()
            _btn_.setObjectName(f"btnExample{chapter}_{current}")
            _btn_.setText(f"ЗАДАНИЕ {current}")
            _btn_.clicked.connect(lambda ch, ind=i: add_function_to_button(index=ind))
            layout.addWidget(_btn_)

    def __open_window_with_current_test(self):
        separator: str = "/" if platform.system() == "Linux" else "\\"
        test_name = self.vtextExampleInfo.url().path().split(f'{separator}')[-1].replace(".pdf", ".json")
        print(test_name)
        current_tests: list[str] = get_filtered_files_list(folder_name="tests")
        print(current_tests)
        if test_name in current_tests:
            self.__window_with_test = Test(test_name=test_name)
        else:
            QMessageBox.warning(self, "Ошибка", "Такого теста пока не существует")

    def __enable_special_settings(self):
        self.vtextTutorialInfo.settings().setAttribute(
            self.vtextTutorialInfo.settings().WebAttribute.PluginsEnabled, True
        )
        self.vtextTutorialInfo.settings().setAttribute(
            self.vtextTutorialInfo.settings().WebAttribute.PdfViewerEnabled, True
        )
        self.vtextExampleInfo.settings().setAttribute(
            self.vtextExampleInfo.settings().WebAttribute.PluginsEnabled, True
        )
        self.vtextExampleInfo.settings().setAttribute(
            self.vtextExampleInfo.settings().WebAttribute.PdfViewerEnabled, True
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())
