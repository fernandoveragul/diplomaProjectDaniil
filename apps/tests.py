from PyQt6.QtWidgets import QWidget
from display import test_window


class Test(QWidget, test_window):
    def __init__(self, test_name: str):
        super().__init__()
        self.setupUi(self)
        self.test_name = test_name
