from abc import ABC, abstractmethod

from changing_dot.custom_types import CompileError, RestrictionOptions
from changing_dot_visualize.observer import Observer


class IErrorManager(ABC):
    @abstractmethod
    def get_compile_errors(self, observer: Observer) -> list[CompileError]:
        pass

    @abstractmethod
    def has_syntax_errors(self) -> bool:
        pass


class HardCodedErrorManager(IErrorManager):
    i: int = 0

    list_of_hardcoded_errors: list[list[CompileError]]

    def __init__(self, list_of_hardcoded_errors: list[list[CompileError]]) -> None:
        self.list_of_hardcoded_errors = (
            list_of_hardcoded_errors + list_of_hardcoded_errors
        )

    def get_compile_errors(self, observer: Observer) -> list[CompileError]:
        hardcoded_errors = self.list_of_hardcoded_errors[self.i]
        self.i += 1
        return hardcoded_errors

    def has_syntax_errors(self) -> bool:
        return False


def filter_restricted_errors(
    errors: list[CompileError],
    restriction_options: RestrictionOptions,
    observer: Observer,
) -> list[CompileError]:
    if len(errors) == 0:
        return errors

    observer.log(f"We have {len(errors)} compile_errors")

    filtered_errors = errors

    if restriction_options.restrict_change_to_single_file is not None:
        observer.log(
            f"Limiting errors to file {restriction_options.restrict_change_to_single_file}"
        )

        filtered_errors = [
            error
            for error in filtered_errors
            if error.file_path == restriction_options.restrict_change_to_single_file
        ]

        observer.log(f"We now have {len(filtered_errors)} compile_errors")

    if restriction_options.restrict_to_project is not None:
        observer.log(
            f"Limiting errors to project {restriction_options.restrict_to_project}"
        )

        filtered_errors = [
            error
            for error in filtered_errors
            if error.project_name == restriction_options.restrict_to_project
        ]

        observer.log(f"We now have {len(filtered_errors)} compile_errors")

    if restriction_options.project_blacklist is not None:
        observer.log(
            f"Blacklisting errors from projects {restriction_options.project_blacklist}"
        )

        project_blacklist: list[str] = restriction_options.get("project_blacklist")  # type: ignore

        filtered_errors = [
            error
            for error in filtered_errors
            if error.project_name not in project_blacklist
        ]

        observer.log(f"We now have {len(filtered_errors)} compile_errors")

    return filtered_errors
