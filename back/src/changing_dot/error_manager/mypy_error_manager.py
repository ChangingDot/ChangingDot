import os

from changing_dot.custom_types import CompileError, RestrictionOptions
from changing_dot.error_manager.error_manager import IErrorManager
from changing_dot_visualize.observer import Observer
from python_analyzer.python_analyzer import MypyAnalyzer


class MypyErrorManager(IErrorManager):
    restriction_options: RestrictionOptions

    def __init__(
        self, directory_path: str, restriction_options: RestrictionOptions
    ) -> None:
        self.directory_path = directory_path
        self.analyzer = MypyAnalyzer(directory_path)
        self.restriction_options = restriction_options

    def get_compile_errors(self, observer: Observer) -> list[CompileError]:
        mypy_errors = self.analyzer.get_errors()
        observer.log(f"Got errors : {mypy_errors}")

        return [
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

    def has_syntax_errors(self) -> bool:
        return self.analyzer.has_syntax_errors()
