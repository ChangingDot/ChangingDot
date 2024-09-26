import os

from changing_dot.custom_types import CompileError, RestrictionOptions
from changing_dot.error_manager.error_manager import (
    IErrorManager,
    filter_restricted_errors,
)
from changing_dot_visualize.observer import Observer
from python_analyzer.python_analyzer import MypyAnalyzer


def find_requirements_file(directory: str) -> str | None:
    for root, _, files in os.walk(directory):
        if "requirements.txt" in files:
            return os.path.join(root, "requirements.txt")
    return None


class MypyErrorManager(IErrorManager):
    restriction_options: RestrictionOptions

    def __init__(
        self,
        directory_path: str,
        requirements_path: str | None,
        restriction_options: RestrictionOptions,
    ) -> None:
        self.directory_path = directory_path
        if requirements_path is None:
            requirements_path = find_requirements_file(directory_path)

        self.analyzer = MypyAnalyzer(directory_path, requirements_path)
        self.restriction_options = restriction_options

    def get_compile_errors(self, observer: Observer) -> list[CompileError]:
        mypy_errors = self.analyzer.get_errors()

        result = [
            CompileError(
                file_path=error.file_path,
                text=error.error_text,
                pos=(
                    error.postion[0],
                    error.postion[1],
                    error.postion[0],
                    error.postion[1],
                ),
                project_name=os.path.basename(self.directory_path),
            )
            for error in mypy_errors
        ]

        observer.log(f"found {len(result)} compile_errors")

        filtered_errors = filter_restricted_errors(
            result, self.restriction_options, observer
        )

        return filtered_errors

    def has_syntax_errors(self) -> bool:
        return self.analyzer.has_syntax_errors()
