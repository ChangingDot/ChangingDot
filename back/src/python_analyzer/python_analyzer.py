import json

import mypy.api
from pydantic import BaseModel


class MypyError(BaseModel):
    error_text: str
    file_path: str
    postion: tuple[int, int]  # line, column


class MypyOutput(BaseModel):
    has_syntax_errors: bool
    semantic_errors: list[MypyError]


def run_mypy(project_path: str) -> MypyOutput:
    result_stdout, result_stderr, exit_status = mypy.api.run(
        ["--output=json", project_path]
    )

    if "[syntax]" in result_stdout:
        return MypyOutput(has_syntax_errors=True, semantic_errors=[])

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
    def __init__(self, project_path: str):
        self.project_path = project_path

    def has_syntax_errors(self) -> bool:
        return run_mypy(self.project_path).has_syntax_errors

    def get_errors(self) -> list[MypyError]:
        assert not self.has_syntax_errors()
        return run_mypy(self.project_path).semantic_errors
