import platform

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QLayout, QPushButton, QMessageBox

from apps.tests import Test
from display import main_window
from dependencies.config import get_filtered_files_list, get_paths_to_files
from dependencies.exceptions import InvalidFolderType


class Application(QMainWindow, main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__window_with_test = None
        self.__enable_special_settings()

        self.__create_buttons(self.layTutorial, "tutorials")
        self.__create_buttons(self.layExample, "examples")
        self.btnRunTest.clicked.connect(self.__open_window_with_current_test)

    def __create_buttons(self, layout: QLayout, folder_name: str):
        def add_function_to_button(*, index: int):
            paths: list[str] = get_paths_to_files(folder_name=folder_name)
            if folder_name == "tutorials":
                self.vtextTutorialInfo.setUrl(QUrl(f"file://{paths[index]}"))
            elif folder_name == "examples":
                self.vtextExampleInfo.setUrl(QUrl(f"file://{paths[index]}"))
            else:
                raise InvalidFolderType()

        files: list[str] = get_filtered_files_list(folder_name=folder_name)
        for i, file in enumerate(files):
            chapter, current = file.split(".")[0].split("_")
            _btn_ = QPushButton()
            _btn_.setObjectName(f"btn{folder_name.capitalize()}{chapter}_{current}")
            _btn_.setText(f"ГЛАВА {current}")
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