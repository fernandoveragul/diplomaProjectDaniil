import os
import platform
import sys
import json
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PyQt6.QtWidgets import QLabel, QPushButton

from dependencies.project_data import TypeDir
from dependencies.exceptions import InvalidFolderType, InvalidTestName


########################################################################################################################
# START BLOCK WITH CONFIG FOR Application()
########################################################################################################################
def get_path_list_files(*, folder_name: str) -> str | bool:
    types = [i.name for i in TypeDir]
    for folder in types:
        if folder == folder_name:
            return TypeDir[folder_name].value
    if folder_name not in types:
        raise InvalidFolderType


def get_list_files(*, folder_name: str) -> list[str | None]:
    file_extensions: list[str] = ["json", "pdf"]
    files = os.listdir(f'{os.path.dirname(sys.argv[0])}{get_path_list_files(folder_name=folder_name)}')
    return list(map(lambda file: file if file.split(".")[-1] in file_extensions else None, files))


def get_filtered_files_list(*, folder_name: str) -> list[str]:
    list_files: list = get_list_files(folder_name=folder_name)
    return list((file for file in list_files if file))


def path_to_icon() -> str:
    path: str = os.path.dirname(sys.argv[0])
    sp: str = "/" if platform.system() == "Linux" else "\\"
    return f'{path}{sp}display{sp}origin_files{sp}icon.png'


def get_paths_to_files(*, folder_name: str) -> list[str]:
    files: list = get_list_files(folder_name=folder_name)
    default_path = f'{os.path.dirname(sys.argv[0])}{get_path_list_files(folder_name=folder_name)}'
    paths: list[str] = []
    sp: str = "/" if platform.system() == "Linux" else "\\"
    for file in files:
        if file:
            paths.append(f'{default_path}{sp}{file}')
    return paths


########################################################################################################################
# END BLOCK WITH CONFIG FOR Application()
########################################################################################################################
# START BLOCK WITH CONFIG FOR Test()
########################################################################################################################
def load_current_test(path_to_test: str) -> dict[str, list]:
    with open(path_to_test, 'r') as test:
        current_test: dict = json.loads(test.read())
    return current_test


def save_current_test(path_to_save: str, test: list[dict]) -> None:
    with open(path_to_save, 'w') as file_test:
        file_test.write(json.dumps(test, indent=4))


def add_question(questions: list, question: dict) -> list[dict]:
    questions.append(question)
    return questions


def change_current_test(path_to_test: str, new_data: list[dict]) -> None:
    old_test: dict[str, list] = load_current_test(path_to_test=path_to_test)
    new_test = old_test.update({"ex": new_data}) if old_test else None
    with open(path_to_test, 'w') as file_test:
        if new_test:
            file_test.write(json.dumps(new_test))
        else:
            raise InvalidTestName()


def get_gen_questions_slide(questions: list[dict]):
    for q in questions:
        yield q


def get_gen_test_text(*, label: QLabel, buttons: list[QPushButton], data: list[dict]):
    for ind_dt, dt in enumerate(data):
        label.setText(dt.get("text"))
        for ind, btn in enumerate(buttons):
            btn.setText(dt.get("answers")[ind].get("answer"))
        yield dt


########################################################################################################################
# END BLOCK WITH CONFIG FOR Test()
########################################################################################################################
# START BLOCK FOR SEND EMAIL WITH RESULT Test()
########################################################################################################################
def _init_smtp_server():
    contex = ssl.create_default_context()
    return smtplib.SMTP_SSL("smtp.gmail.com", 587, context=contex)


def _init_message(*, send_from: str, send_to: str, send_subject: str, student: dict, result: dict):
    msg = MIMEMultipart()
    msg["From"] = send_from
    msg["To"] = send_to
    msg["Subject"] = send_subject
    message_text = f"""\
    <html>
        <body>
            <div>
                <h1>{student.get("name")} {student.get("group")}</h1>
            </div>
            <div>
                <h3>Тест по практической работе номер {result.get("test_number")}</h3>
            </div>
            <div>
                <h3>Количество баллов {sum(result.get("result"))}</h3>
            </div>
        </body>
    </html>
    """
    message = MIMEText(message_text, "html")
    msg.attach(message)
    return msg


def send_message(*, login_data: dict, receiver_email: str, message):
    sender_email, password = login_data.get("sender_email"), login_data.get("password")
    with _init_smtp_server() as server:
        server.login(sender_email, password=password)
        server.send_message(sender_email, receiver_email, message)
