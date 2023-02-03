import json
import platform
from pathlib import Path
from typing import Generator

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QMessageBox

from dependencies.config import get_gen_questions_slide, load_current_test, get_gen_test_text, \
    get_smtp_server, get_message, send_message, decode_dt
from display import test_window


class Test(QWidget, test_window):
    def __init__(self, path_to_test: str):
        super().__init__()
        self.__student: dict = {}
        self.__auth_data: dict = {}
        self.__result: dict = {}
        self.setupUi(self)
        self.path_to_test = path_to_test

        self.__test = load_current_test(path_to_test=self.path_to_test)
        self.__questions = list(get_gen_questions_slide(questions=self.__test["ex"]))
        self.__init_time_for_test()

        self.setup_non_interactive_elements()
        self.setup_interactive_elements()
        self.setup_vars()
        self.setup_placeholders()

    def setup_vars(self):
        self.__text_answers_from_user: list = []
        self.__equal_answers_from_user: list[bool] = []
        self.buttons: list[QPushButton] = [self.btnAnswer_1, self.btnAnswer_2, self.btnAnswer_3, self.btnAnswer_4]
        self.gen: Generator = get_gen_test_text(label=self.tbrQuestion, buttons=self.buttons, data=self.__questions)
        self.progressBar.setRange(0, len(self.__test["ex"]) - 1)
        self.progress_bar_counter: int = -1

    def setup_interactive_elements(self):
        self.btnAnswer_1.clicked.connect(lambda: self.__next_question(self.gen, buttons=self.buttons))
        self.btnAnswer_2.clicked.connect(lambda: self.__next_question(self.gen, buttons=self.buttons))
        self.btnAnswer_3.clicked.connect(lambda: self.__next_question(self.gen, buttons=self.buttons))
        self.btnAnswer_4.clicked.connect(lambda: self.__next_question(self.gen, buttons=self.buttons))
        self.btnLogin.clicked.connect(lambda: self.__parse_auth_data())
        self.btnFinish.clicked.connect(lambda: self.finish_program())

    def setup_non_interactive_elements(self):
        timer_dt: list = self.__init_time_for_test()
        if len(timer_dt) > 1:
            h, m = self.__init_time_for_test()
            self.lblTimer.setText(f"{f'0{h}' if h < 9 else h}:{m}:00")
        else:
            self.lblTimer.setText(f"00:10:00" if timer_dt[0] == 0 else f"00:{timer_dt[0]}:00")
        self.timer: QTimer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(lambda: self.__minus_sec())

    def setup_placeholders(self):
        self.ledtReceiverEMail.setPlaceholderText("Введите адрес почты преподавателя")
        self.ledtSecondName.setPlaceholderText("Введите свою фамилию")
        self.ledtGroupName.setPlaceholderText("Введите номер группы. (Например 403 ИСП)")

    def finish_program(self):
        self.timer.stop()
        self.__calculate_score(self.__text_answers_from_user[1:], self.__test["ex"])
        self.__message_about_sending_results(self.__equal_answers_from_user)
        self.close()

    def __init_time_for_test(self):
        minutes: int = self.__test['ex'][0].get("time_in_minutes")
        if minutes > 59:
            hours: int = minutes // 60
            minutes = minutes - hours * 60
            return [hours, minutes]
        else:
            return [minutes]

    def __add_percent_in_progress_bar(self):
        self.progress_bar_counter += 1
        self.progressBar.setValue(self.progress_bar_counter)

    def __minus_sec(self):
        hours, minutes, seconds = list(map(int, self.lblTimer.text().split(":")))
        if hours == 0 and minutes == 0 and seconds == 0:
            self.finish_program()
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
        text_answer = [btn.text() for btn in buttons if btn.isChecked()]
        dt = next(gen, False)
        if dt is False:
            self.finish_program()
        else:
            self.__text_answers_from_user.append(text_answer)
        self.__add_percent_in_progress_bar()
        [btn.setCheckable(False) for btn in buttons if btn.isChecked()]
        [btn.setCheckable(True) for btn in buttons if not btn.isChecked()]

    def __calculate_score(self, answers: list[str], origin_data: list[dict]):
        for ind, ans in enumerate(answers):
            for _, v in origin_data[ind].items():
                if isinstance(v, list):
                    for val in v:
                        self.__equal_answers_from_user.append(val["is_true"] if val["answer"] == ans[0] else False)

    def __parse_auth_data(self):
        default_data: str = str(Path(Path.cwd(), 'display', 'origin_files', '.login_data.json'))
        with open(default_data, 'r') as file:
            dt = json.loads(file.read())
        lg, ps = decode_dt(dt=dt)
        self.__auth_data["sender_email"] = lg
        self.__auth_data["password"] = ps
        self.__student["name"] = self.ledtSecondName.text()
        self.__student["group"] = self.ledtGroupName.text()

        self.stackedWidget.setCurrentWidget(self.pgTest)

    def __send_email_to_teacher(self):
        with get_smtp_server() as server:
            message = get_message(send_from=self.__auth_data['sender_email'], send_to=self.ledtReceiverEMail.text(),
                                  send_subject=self.__student['group'], student=self.__student, result=self.__result)
            send_message(server=server, login_data=self.__auth_data, receiver_email=self.ledtReceiverEMail.text(),
                         message=message)

    def __message_about_sending_results(self, answers: list[bool]):
        sp: str = '/' if platform.system() == "Linux" else "\\"
        self.__result["test_number"] = self.path_to_test.split(sp)[-1].split(".")[0]
        self.__result["result"] = answers

        msg = QMessageBox(self)
        msg.setWindowTitle("Поздравляю!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"{self.__student['name']} {self.__student['group']},\n"
                    f"количество баллов равно: {sum(answers)}\n"
                    f"Результат будет выслан на почту {self.ledtReceiverEMail.text()}")
        btn_continue = msg.addButton("Отправить результат", QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(btn_continue)
        btn_continue.clicked.connect(lambda: self.__send_email_to_teacher())
        msg.exec()
