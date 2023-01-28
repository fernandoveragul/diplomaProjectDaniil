import os
import sys


def func_get_path():
    files = os.listdir()
    path_to_files = os.path.dirname(os.path.abspath(sys.argv[0]))
    return f'file//{path_to_files}/{files[0]}'

inf = func_get_path()

# print(f'file://{path_to_files}/{files[0]}')
