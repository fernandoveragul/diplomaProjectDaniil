import os
import platform
import sys

from dependencies.project_data import TypeDir
from dependencies.exceptions import InvalidFolderType


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


def get_paths_to_files(*, folder_name: str):
    files: list = get_list_files(folder_name=folder_name)
    default_path = f'{os.path.dirname(sys.argv[0])}{get_path_list_files(folder_name=folder_name)}'
    paths: list[str] = []
    separator: str = "/" if platform.system() == "Linux" else "\\"
    for file in files:
        if file:
            paths.append(f'{default_path}{separator}{file}')
    return paths



