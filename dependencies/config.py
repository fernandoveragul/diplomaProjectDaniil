import os
import sys

from dependencies.project_data import TypeDir
from dependencies.exceptions import InvalidFolderType


def get_path_list_files(*, type_dir: str) -> str | bool:
    types = [i.name for i in TypeDir]
    for folder in types:
        if folder == type_dir:
            return TypeDir[type_dir].value
    if type_dir not in types:
        raise InvalidFolderType


def get_list_files(*, name_dir: str) -> list[str | None]:
    file_extensions: list[str] = ["json", "pdf"]
    files = os.listdir(f'{os.path.dirname(sys.argv[0])}{get_path_list_files(type_dir=name_dir)}')
    return list(map(lambda file: file if file.split(".")[-1] in file_extensions else None, files))


def do_filer_file_list(*, files: list[str | None]):
    return list((file for file in files if file))
