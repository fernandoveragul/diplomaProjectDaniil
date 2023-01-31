from typing import Generator

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QMessageBox

from dependencies.config import get_gen_questions_slide, load_current_test, get_gen_test_text
from display import test_window


class Test(QWidget, test_window):
    def __init__(self, path_to_test: str):
        super().__init__()
        self.setupUi(self)
        self.path_to_test = path_to_test

        self.__test = load_current_test(path_to_test=path_to_test)
        self.__questions = list(get_gen_questions_slide(questions=self.__test["ex"]))

        self.setup_non_interactive_elements()
        self.setup_interactive_elements()

    def setup_interactive_elements(self):
        buttons: list[QPushButton] = [self.btnAnswer_1, self.btnAnswer_2, self.btnAnswer_3, self.btnAnswer_4]
        gen: Generator = get_gen_test_text(label=self.tbrQuestion, buttons=buttons, data=self.__questions)

        self.btnAnswer_1.clicked.connect(lambda: self.__next_question(gen, buttons=buttons))
        self.btnAnswer_2.clicked.connect(lambda: self.__next_question(gen, buttons=buttons))
        self.btnAnswer_3.clicked.connect(lambda: self.__next_question(gen, buttons=buttons))
        self.btnAnswer_4.clicked.connect(lambda: self.__next_question(gen, buttons=buttons))

        self.btnLogin.clicked.connect(lambda: self.__parse_auth_data())
        self.btnFinish.clicked.connect(lambda: self.__message_about_sending_results(self.__equal_answers_from_user))

    def setup_non_interactive_elements(self):
        self.progressBar.setRange(0, len(self.__test["ex"]) - 1)
        self.progress_bar_counter: int = -1

        self.lblTimer.setText("00:10:00")

        self.timer: QTimer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(lambda: self.__minus_sec())

    def __add_percent_in_progress_bar(self):
        self.progress_bar_counter += 1
        self.progressBar.setValue(self.progress_bar_counter)

    def __minus_sec(self):
        hours, minutes, seconds = list(map(int, self.lblTimer.text().split(":")))

        if hours == 0 and minutes == 0 and seconds == 0:
            self.__message_about_sending_results(self.__equal_answers_from_user)

        if 0 < seconds < 60:
            seconds -= 1
        else:
            seconds = 59
            if 0 < minutes < 60:
                minutes -= 1
            else:
                if 0 < hours < 24:
                    minutes = 59
                    hours -= 1
                else:
                    QMessageBox.critical(self, "КРИТИЧЕСКАЯ ОШИБКА", "НЕЛЬЗЯ ДАВАТЬ ТАКИЕ ТЕСТЫ")
        self.lblTimer.setText(f'{hours if hours > 9 else f"0{hours}"}:'
                              f'{minutes if minutes > 9 else f"0{minutes}"}:'
                              f'{seconds if seconds > 9 else f"0{seconds}"}')

    def __next_question(self, gen: Generator, buttons: list[QPushButton]):
        if not self.timer.isActive():
            self.timer.start()

        self.__text_answers_from_user: list = []
        text_answer = [btn.text() for btn in buttons if btn.isChecked()]

        dt = next(gen, False)
        if dt is False:
            self.__calculate_score(self.__text_answers_from_user[1:], self.__test["ex"])
            self.__message_about_sending_results(self.__equal_answers_from_user)
            self.close()
        else:
            self.__text_answers_from_user.append(text_answer)
        self.__add_percent_in_progress_bar()
        [btn.setCheckable(False) for btn in buttons if btn.isChecked()]
        [btn.setCheckable(True) for btn in buttons if not btn.isChecked()]

    def __calculate_score(self, answers: list[str], origin_data: list[dict]):
        self.__equal_answers_from_user: list[bool] = []

        for ind, ans in enumerate(answers):
            for _, v in origin_data[ind].items():
                if isinstance(v, list):
                    for val in v:
                        self.__equal_answers_from_user.append(val["is_true"] if val["answer"] == ans[0] else False)

    def __parse_auth_data(self):
        self.second_name = self.ledtSecondName.text()
        self.group_name = self.ledtGroupName.text()
        self.stackedWidget.setCurrentWidget(self.pgTest)

    def __message_about_sending_results(self, answers: list[bool]):
        msg = QMessageBox(self)
        msg.setWindowTitle("Поздравляю!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"{self.second_name} {self.group_name}, количество ваших баллов равно: {sum(answers)}")
        btn_continue = msg.addButton("Продолжить выполнять тесты", QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(btn_continue)
        msg.exec()
