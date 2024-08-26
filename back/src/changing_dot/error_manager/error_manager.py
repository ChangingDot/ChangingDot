from abc import ABC, abstractmethod

import grpc
from changing_dot.config.environment import ANAYLZER_URL
from changing_dot.custom_types import CompileError, RestrictionOptions
from changing_dot.generated_grpc.feedback_server_pb2 import (
    GetCompileErrorsRequest,
    HasSyntaxErrorsRequest,
)
from changing_dot.generated_grpc.feedback_server_pb2_grpc import (
    FeedbackServerStub,
)
from changing_dot_visualize.observer import Observer

grpc_options = [
    ("grpc.max_send_message_length", 50 * 1024 * 1024),  # Example: 50 MB
    ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # Example: 50 MB
]


class IErrorManager(ABC):
    @abstractmethod
    def get_compile_errors(
        self, files: list[str], observer: Observer
    ) -> list[CompileError]:
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

    def get_compile_errors(
        self, files: list[str], observer: Observer
    ) -> list[CompileError]:
        hardcoded_errors = self.list_of_hardcoded_errors[self.i]
        self.i += 1
        return hardcoded_errors

    def has_syntax_errors(self) -> bool:
        return False


class RoslynErrorManager(IErrorManager):
    solution_file_path: str
    analyzer_url: str
    restriction_options: RestrictionOptions

    def __init__(
        self, solution_file_path: str, restriction_options: RestrictionOptions
    ) -> None:
        self.solution_file_path = solution_file_path
        self.restriction_options = restriction_options
        assert ANAYLZER_URL is not None
        self.analyzer_url = ANAYLZER_URL

    def get_compile_errors(
        self, files: list[str], observer: Observer
    ) -> list[CompileError]:
        with grpc.insecure_channel(self.analyzer_url, options=grpc_options) as channel:
            stub = FeedbackServerStub(channel)
            error_response = stub.GetCompileErrors(
                GetCompileErrorsRequest(filePath=self.solution_file_path)
            )
            compile_errors: list[CompileError] = [
                {
                    "text": error.errorText,
                    "file_path": error.filePath,
                    "project_name": error.projectName,
                    "pos": tuple(error.position),
                }
                for error in error_response.Errors
            ]

            unique_line_pos_tuples = set()
            result: list[CompileError] = []

            # Remove when 2 errors are on the same line for now
            for error in compile_errors:
                new_line_pos_tuple = (error["file_path"], error["pos"][0])
                if new_line_pos_tuple not in unique_line_pos_tuples:
                    unique_line_pos_tuples.add(new_line_pos_tuple)
                    result.append(error)

            observer.log(f"found {len(result)} compile_errors")

            filtered_errors = filter_restricted_errors(
                result, self.restriction_options, observer
            )

            return filtered_errors

    def has_syntax_errors(self) -> bool:
        with grpc.insecure_channel(self.analyzer_url, options=grpc_options) as channel:
            stub = FeedbackServerStub(channel)
            has_syntax_error_response = stub.HasSyntaxErrors(
                HasSyntaxErrorsRequest(filePath=self.solution_file_path)
            )
            has_syntax_errors: bool = has_syntax_error_response.HasSyntaxErrors
            return has_syntax_errors


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
            if error["file_path"] == restriction_options.restrict_change_to_single_file
        ]

        observer.log(f"We now have {len(filtered_errors)} compile_errors")

    if restriction_options.restrict_to_project is not None:
        observer.log(
            f"Limiting errors to project {restriction_options.restrict_to_project}"
        )

        filtered_errors = [
            error
            for error in filtered_errors
            if error["project_name"] == restriction_options.restrict_to_project
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
            if error["project_name"] not in project_blacklist
        ]

        observer.log(f"We now have {len(filtered_errors)} compile_errors")

    return filtered_errors
