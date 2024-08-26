import grpc
from changing_dot.config.environment import ANAYLZER_URL
from changing_dot.custom_types import CompileError, RestrictionOptions
from changing_dot.error_manager.error_manager import (
    IErrorManager,
    filter_restricted_errors,
)
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

    def get_compile_errors(self, observer: Observer) -> list[CompileError]:
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
