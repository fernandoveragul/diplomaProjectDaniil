from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget

from dependencies.config import get_gen_questions_slide, load_current_test
from display import test_window


class Test(QWidget, test_window):
    def __init__(self, path_to_test: str):
        super().__init__()
        self.setupUi(self)
        self.path_to_test = path_to_test

        self.__test = load_current_test(path_to_test=path_to_test)
        self.__questions = list(get_gen_questions_slide(self.__test.get("ex")))

