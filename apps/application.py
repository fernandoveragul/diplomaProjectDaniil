import hashlib
import json
import os.path
import platform
import sys
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow, QLayout, QPushButton, QMessageBox, QFileDialog

from apps.check_knowledge import Test
from display import main_window
from dependencies.config import get_filtered_files_list, get_paths_to_files, copy_file_to_files, load_current_test, \
    save_current_test, change_current_test
from dependencies.exceptions import InvalidFolderType


class Application(QMainWindow, main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tabWidget.setCurrentWidget(self.tabTutorial)
        self.stackedAdminPanel.setCurrentWidget(self.pgLogin)
        self.__path_to_test = get_paths_to_files(folder_name="tests")[0]  # DEFAULT
        self.vtextTutorialInfo.setUrl(QUrl.fromLocalFile(get_paths_to_files(folder_name="tutorials")[0]))  # DEFAULT
        self.vtextExampleInfo.setUrl(QUrl.fromLocalFile(get_paths_to_files(folder_name="examples")[0]))  # DEFAULT

        self.__current_test_path: dict = {}
        self.__current_test: dict = {}
        self.__current_question_counter: int = 0
        self.__current_questions: list = []

        self.__window_with_test = None
        self.__test_schema = load_current_test(str(Path(Path.cwd(), 'files', 'test_schema.json')))
        self.__counter_questions: int = 0

        self.__enable_special_settings()
        self.__create_buttons(self.layTutorial, "tutorials")
        self.__create_buttons(self.layExample, "examples")
        self.__create_buttons_tests(self.layTests, "tests")
        self.setup_static_buttons_and_changed_text_event()

    def __create_buttons(self, layout: QLayout, folder_name: str):
        def add_function_to_button(*, index: int):
            paths: list[str] = get_paths_to_files(folder_name=folder_name)
            if folder_name == "tutorials":
                self.vtextTutorialInfo.setUrl(QUrl.fromLocalFile(f"{paths[index]}"))
            elif folder_name == "examples":
                self.vtextExampleInfo.setUrl(QUrl.fromLocalFile(f"{paths[index]}"))
                try:
                    self.__path_to_test = get_paths_to_files(folder_name="tests")[index]
                except IndexError:
                    self.__path_to_test = os.path.dirname(sys.argv[0])
                finally:
                    self.__window_with_test = None
            else:
                raise InvalidFolderType()

        files: list[str] = get_filtered_files_list(folder_name=folder_name)
        for i, file in enumerate(files):
            chapter, current = file.split(".")[0].split("_")
            _btn_ = QPushButton()
            _btn_.setObjectName(f"btn{folder_name.capitalize()}{chapter}_{current}")
            _btn_.setText(f"ГЛАВА {current}") if folder_name == "tutorials" else _btn_.setText(
                f"ЗАДАНИЕ К ГЛАВЕ {current}")
            _btn_.clicked.connect(lambda ch, ind=i: add_function_to_button(index=ind))
            layout.addWidget(_btn_)

    def __open_window_with_current_test(self):
        path_to_test = self.__path_to_test.replace(".pdf", ".json")
        exist_tests: list[str] = get_paths_to_files(folder_name="tests")
        if path_to_test in exist_tests:
            self.__window_with_test = Test(path_to_test=path_to_test)
            self.__window_with_test.show()
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

    def setup_static_buttons_and_changed_text_event(self):
        self.ledtAnswerFirst.textChanged.connect(lambda: self.rbtnAnswerFirst.setText(self.ledtAnswerFirst.text()))
        self.ledtAnswerSecond.textChanged.connect(lambda: self.rbtnAnswerSecond.setText(self.ledtAnswerSecond.text()))
        self.ledtAnswerThird.textChanged.connect(lambda: self.rbtnAnswerThird.setText(self.ledtAnswerThird.text()))
        self.ledtAnswerFour.textChanged.connect(lambda: self.rbtnAnswerFour.setText(self.ledtAnswerFour.text()))

        self.ledtChAnswerFirst.textChanged.connect(lambda: self.rbtnAnswerFirst.setText(self.ledtChAnswerFirst.text()))
        self.ledtChAnswerSecond.textChanged.connect(
            lambda: self.rbtnAnswerSecond.setText(self.ledtChAnswerSecond.text()))
        self.ledtChAnswerThird.textChanged.connect(lambda: self.rbtnAnswerThird.setText(self.ledtChAnswerThird.text()))
        self.ledtChAnswerFour.textChanged.connect(lambda: self.rbtnAnswerFour.setText(self.ledtChAnswerFour.text()))

        self.btnRunTest.clicked.connect(self.__open_window_with_current_test)
        self.btnLogin.clicked.connect(lambda: self.__login_admin())
        self.btnAddQuestion.clicked.connect(lambda: self.clear_text_editors(is_end=False))
        self.btnEndCreateTest.clicked.connect(lambda: self.clear_text_editors(is_end=True))

        self.btnAddTutorial.clicked.connect(lambda: self.__add_file_to_files(folder_name="tutorials"))
        self.btnAddExample.clicked.connect(lambda: self.__add_file_to_files(folder_name="examples"))
        self.btnDelTutorial.clicked.connect(lambda: self.__delete_file_from_files(folder_name="tutorials"))
        self.btnDelExample.clicked.connect(lambda: self.__delete_file_from_files(folder_name="examples"))
        self.btnDelTest.clicked.connect(lambda: self.__delete_file_from_files(folder_name="tests"))

        self.btnChangeTest.clicked.connect(lambda: self.stackedAdminPanel.setCurrentWidget(self.pgChangeTest))
        self.btnChNext.clicked.connect(lambda: self.__display_current_question(is_origin=False, is_up=True))
        self.btnChPerv.clicked.connect(lambda: self.__display_current_question(is_origin=False, is_up=False))
        self.btnChFinish.clicked.connect(lambda: self.__save())

    ####################################################################################################################
    # FIRST ADMIN PAGE ESSENCE
    ####################################################################################################################
    def __login_admin(self):
        path_to_login_data: str = str(Path(Path.cwd(), 'display', 'origin_files', '.login_data.json'))
        login: str = hashlib.sha256(self.ledtLogin.text().encode()).hexdigest()
        password: str = hashlib.sha256(self.ledtPassword.text().encode()).hexdigest()

        with open(path_to_login_data, 'r') as login_data:
            dt: dict = json.loads(login_data.read())

        if login == dt['login'] and password == dt['password']:
            self.stackedAdminPanel.setCurrentWidget(self.pgOperationWithFiles)
        else:
            QMessageBox.information(self, "НЕУДАЧА", 'Неверный логин или пароль')

        self.stackedAdminPanel.setCurrentWidget(self.pgOperationWithFiles)

    def clear_text_editors(self, is_end: bool = False):
        meta_data: list = self.ledtTimeToDo.text().split()
        if len(meta_data) > 1:
            self.__add_question(time_for_test=meta_data[-1])
        else:
            self.__add_question()
        if not is_end:
            self.__clear_editors()
        else:
            self.__final_adding_question(meta_data=meta_data)

    def __clear_editors(self):
        self.ledtAnswerFirst.setText("")
        self.ledtAnswerSecond.setText("")
        self.ledtAnswerThird.setText("")
        self.ledtAnswerFour.setText("")
        self.ptedQuestion.setPlainText("")

    def __add_file_to_files(self, folder_name: str):
        def_folder: str = str(Path(Path.home()))
        try:
            cp_from: str = QFileDialog.getOpenFileName(self, "PDF файл",
                                                       directory=def_folder,
                                                       filter="All Files (*);;EXAMPLES Files (*.pdf)")[0]
            copy_file_to_files(copy_from=cp_from, folder_cp=folder_name)
        except FileNotFoundError:
            QMessageBox.critical(self, "ОШИБКА", "ОКНО ЗАКРЫТО БЕЗ ВЫБОРА ФАЙЛА\nЛИБО НЕ СУЩЕСТВУЕТ ТАКОГО ФАЙЛА")

    def __delete_file_from_files(self, folder_name: str):
        def_folder: str = str(Path(Path.cwd(), "files", folder_name))
        try:
            deleting_file: str = QFileDialog.getOpenFileName(self, "Open File",
                                                             directory=def_folder,
                                                             filter="All Files (*);;Tutorial or Example Files (*.pdf);;"
                                                                    "Tests Files (*.json)")[0]
            os.remove(deleting_file)
        except FileNotFoundError:
            QMessageBox.critical(self, "ОШИБКА", "ОКНО ЗАКРЫТО БЕЗ ВЫБОРА ФАЙЛА\nЛИБО НЕ СУЩЕСТВУЕТ ТАКОГО ФАЙЛА")

    def __add_question(self, time_for_test: int = 10):
        for_adding_dictionary: dict = {'question': self.__counter_questions, 'time_in_minutes': int(time_for_test),
                                       'text': self.ptedQuestion.toPlainText(), 'answers': [
                {'answer': self.ledtAnswerFirst.text(), "is_true": self.rbtnAnswerFirst.isChecked()},
                {'answer': self.ledtAnswerSecond.text(), "is_true": self.rbtnAnswerSecond.isChecked()},
                {'answer': self.ledtAnswerThird.text(), "is_true": self.rbtnAnswerThird.isChecked()},
                {'answer': self.ledtAnswerFour.text(), "is_true": self.rbtnAnswerFour.isChecked()}
            ]}

        self.__test_schema['ex'].append(for_adding_dictionary)
        self.__counter_questions += 1

        QMessageBox.information(self, "УСПЕХ", f"Вопрос был добавлен к текущему тесту")

    def __final_adding_question(self, meta_data: list[str]):
        if len(meta_data) == 0:
            QMessageBox.critical(self, "КРИТИЧЕСКАЯ ОШИБКА", "НЕЛЬЗЯ СОЗДАТЬ ТЕСТ БЕЗ ЕГО НОМЕРА")
        else:
            self.__test_schema['ex'].append({"question": self.__counter_questions + 1,
                                             'time_in_minutes': 0,
                                             'text': "Спасибо за прохождение теста",
                                             'answers': [
                                                 {"answer": "Нажмите, чтобы продолжить", "is_true": False},
                                                 {"answer": "Нажмите, чтобы продолжить", "is_true": False},
                                                 {"answer": "Нажмите, чтобы продолжить", "is_true": False},
                                                 {"answer": "Нажмите, чтобы продолжить", "is_true": False}
                                             ]})
            save_current_test(path_to_save=str(Path(Path.cwd(), 'files', 'tests', f'1_{meta_data[0]}.json')),
                              test=self.__test_schema)
            self.__clear_editors()
            QMessageBox.information(self, "УСПЕХ", "Тест был создан, перезапустите приложение, "
                                                   "чтобы он инициализировался")
            self.ledtTimeToDo.setText('')
            self.__counter_questions = 0
            self.__test_schema = load_current_test(str(Path(Path.cwd(), 'files', 'test_schema.json')))

    ####################################################################################################################
    # SECOND ADMIN PAGE ESSENCE
    ####################################################################################################################
    def __create_buttons_tests(self, layout: QLayout, folder_name: str):
        def add_function_to_button(*, index: int):
            paths: list[str] = get_paths_to_files(folder_name=folder_name)
            self.__current_test = load_current_test(path_to_test=paths[index])
            self.__current_test_path["test"] = paths[index]
            self.__current_question_counter = 0
            self.__current_questions = self.__current_test["ex"]
            self.__display_current_question(is_origin=True, is_up=True)

        files: list[str] = get_filtered_files_list(folder_name=folder_name)
        for i, file in enumerate(files):
            chapter, current = file.split(".")[0].split("_")
            _btn_ = QPushButton()
            _btn_.setObjectName(f"btn{folder_name.capitalize()}{chapter}_{current}")
            _btn_.setText(f"ТЕСТ {current}")
            _btn_.clicked.connect(lambda ch, ind=i: add_function_to_button(index=ind))
            layout.addWidget(_btn_)
        self.setup_default_texts()

    def setup_default_texts(self):
        self.ledtChAnswerFirst.setText('Нажмите "СЛЕДУЮЩИЙ", чтобы загрузить тест')
        self.ledtChAnswerSecond.setText('Нажмите "СЛЕДУЮЩИЙ", чтобы загрузить тест')
        self.ledtChAnswerThird.setText('Нажмите "СЛЕДУЮЩИЙ", чтобы загрузить тест')
        self.ledtChAnswerFour.setText('Нажмите "СЛЕДУЮЩИЙ", чтобы загрузить тест')

    def __update_all_questions(self, current_data: list, replacement: dict) -> list:
        for ind, q in enumerate(self.__current_questions):
            if current_data[ind]["question"] == replacement["question"]:
                current_data[ind] = replacement
        return current_data

    def __get_text(self):
        return {"question": self.__current_question_counter,
                "time_in_minutes": int(self.ledtChNameTime.text().split()[-1]),
                "text": self.ptedChQuestion.toPlainText(),
                "answers": [
                    {"answer": self.ledtChAnswerFirst.text(),
                     "is_true": self.rbtnChAnswerFirst.isChecked()},
                    {"answer": self.ledtChAnswerSecond.text(),
                     "is_true": self.rbtnChAnswerSecond.isChecked()},
                    {"answer": self.ledtChAnswerThird.text(),
                     "is_true": self.rbtnChAnswerThird.isChecked()},
                    {"answer": self.ledtChAnswerFour.text(),
                     "is_true": self.rbtnChAnswerFour.isChecked()}
                ]}

    def __post_text(self, dt: dict, q_index: int):
        data = dt['ex'][q_index]
        self.ledtChAnswerFirst.setText(data["answers"][0].get("answer"))
        self.ledtChAnswerSecond.setText(data["answers"][1].get("answer"))
        self.ledtChAnswerThird.setText(data["answers"][2].get("answer"))
        self.ledtChAnswerFour.setText(data["answers"][3].get("answer"))
        self.ptedChQuestion.setPlainText(data["text"])

    def __save(self):
        change_current_test(self.__current_test_path["test"],
                            self.__update_all_questions(self.__current_questions, self.__get_text()))

    def __display_current_question(self, is_origin: bool, is_up: bool):
        try:
            if is_origin:  # WITH LOADING CURRENT TEST
                self.__post_text(dt=self.__current_test, q_index=self.__current_question_counter)
                name = self.__current_test_path["test"].split("/" if platform.system() == "Linux" else "\\")
                self.ledtChNameTime.setText(
                    f'{name[-1].split(".")[0].split("_")[-1]} {self.__current_test["ex"][0]["time_in_minutes"]}')
            else:  # CLICKED NEXT OR PERV
                self.__update_all_questions(self.__current_questions, self.__get_text())
                if is_up is True:
                    self.__current_question_counter += 1
                else:
                    self.__current_question_counter -= 1
                self.__post_text(dt=self.__current_test, q_index=self.__current_question_counter)

            # FOR CAROUSEL
            if self.__current_question_counter < 0:
                c = -1 * self.__current_question_counter
                self.__current_question_counter += c
                self.__post_text(dt=self.__current_test, q_index=self.__current_question_counter)
            if self.__current_question_counter > len(self.__current_test["ex"]) - 2:
                c = 1 * self.__current_question_counter
                self.__current_question_counter -= c
                self.__post_text(dt=self.__current_test, q_index=self.__current_question_counter)
        except IndexError as ex:
            print(repr(ex))
