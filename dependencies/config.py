import os
import platform
import sys
import json

from dependencies.project_data import TypeDir
from dependencies.exceptions import InvalidFolderType, InvalidTestName


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
