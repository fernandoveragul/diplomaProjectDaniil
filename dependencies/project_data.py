import platform
from enum import Enum


class TypeDir(Enum):
    examples: str = "/files/examples" if platform.system() == "Linux" else "\\files\\examples"
    tests: str = "/files/tests" if platform.system() == "Linux" else "\\files\\tests"
    tutorials: str = "/files/tutorials" if platform.system() == "Linux" else "\\files\\tutorials"


# print(TypeDir["examples"].value)
