import json
import os
import subprocess
import sys

import mypy.api
import pkg_resources
from changing_dot.config.constants import CDOT_PATH
from pydantic import BaseModel


class MypyError(BaseModel):
    error_text: str
    file_path: str
    postion: tuple[int, int]  # line, column


class MypyOutput(BaseModel):
    has_syntax_errors: bool
    semantic_errors: list[MypyError]


def run_mypy(project_path: str, venv_path: str) -> MypyOutput:
    python_executable_path = f"{venv_path}/bin/python"

    result_stdout, result_stderr, exit_status = mypy.api.run(
        [
            "--output=json",
            "--config-file",
            pkg_resources.resource_filename("python_analyzer", "setup.cfg"),
            "--python-executable",
            python_executable_path,
            project_path,
        ]
    )

    if exit_status == 2:
        raise Exception(f"Mypy failed with exit status {exit_status}:\n{result_stderr}")

    if "[syntax]" in result_stdout:
        return MypyOutput(has_syntax_errors=True, semantic_errors=[])

    # No type errors
    if exit_status == 0:
        return MypyOutput(has_syntax_errors=False, semantic_errors=[])

    semantic_errors = []

    for raw_error in result_stdout.split("\n"):
        if raw_error.strip() == "":
            continue
        json_error = json.loads(raw_error)

        semantic_errors.append(
            MypyError(
                error_text=json_error["message"],
                file_path=json_error["file"],
                postion=(json_error["line"], json_error["column"]),
            )
        )
    return MypyOutput(has_syntax_errors=False, semantic_errors=semantic_errors)


class MypyAnalyzer:
    def __init__(self, project_path: str, requirements_path: str | None):
        self.project_path = project_path
        self.requirements_path = requirements_path
        self.venv_path = os.path.join(CDOT_PATH, "temporary_env", "venv")

    def has_syntax_errors(self) -> bool:
        return run_mypy(self.project_path, self.venv_path).has_syntax_errors

    def get_errors(self) -> list[MypyError]:
        assert not self.has_syntax_errors()
        self.install_libs()
        return run_mypy(self.project_path, self.venv_path).semantic_errors

    def install_libs(self) -> None:
        if self.requirements_path is None:
            return

        subprocess.run(
            [
                f"{self.venv_path}/bin/pip",
                "install",
                "-r",
                self.requirements_path,
            ],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=True,
        )
