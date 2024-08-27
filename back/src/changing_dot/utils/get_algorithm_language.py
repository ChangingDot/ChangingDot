import os
from typing import Literal


def get_language(initial_change_file: str) -> Literal["python", "c_sharp"]:
    _, extension = os.path.splitext(initial_change_file)

    if extension == ".py":
        return "python"

    if extension == ".csproj" or extension == ".cs":
        return "c_sharp"

    else:
        raise NotImplementedError("Extention not recognized or implemented yet")
