import os
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict


def validate_and_convert_path(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Path must be a string")
    if os.path.exists(value) or not os.path.isabs(value):
        return os.path.abspath(value)
    else:
        raise ValueError(f"Invalid path: {value}")


class ErrorInitialization(TypedDict):
    init_type: Literal["error"]
    initial_error: str
    initial_file_path: str
    initial_error_position: tuple[int, int, int, int]


Initialization = ErrorInitialization


class CompileError(TypedDict):
    text: str
    file_path: str
    project_name: str
    pos: tuple[int, int, int, int]


class Instruction(TypedDict):
    edit_type: Literal["replace"] | Literal["add"] | Literal["remove"]
    programming_language: str
    file_path: str
    line_number: int
    error: str
    solution: str


class ReplaceEdit(TypedDict):
    edit_type: Literal["replace"]
    file_path: str
    line_number: int
    before: str
    after: str


class AddEdit(TypedDict):
    edit_type: Literal["add"]
    file_path: str
    line_number: int
    line_to_add: str


class RemoveEdit(TypedDict):
    edit_type: Literal["remove"]
    file_path: str
    line_number: int
    line_to_remove: str


# TODO: add to class if edits ever become a class
def edit_to_diff(edit: ReplaceEdit | AddEdit | RemoveEdit) -> str:
    if edit["edit_type"] == "replace":
        return f"""
        ```diff
        - {edit['before']}
        + {edit['after']}
        ```
        """

    if edit["edit_type"] == "add":
        return f"""
        ```diff
        + {edit['line_to_add']}
        ```
        """

    if edit["edit_type"] == "remove":
        return f"""
        ```diff
        - {edit['line_to_remove']}
        ```
        """


Edit = ReplaceEdit | AddEdit | RemoveEdit

Edits = list[Edit]


NodeStatus = Literal["pending"] | Literal["handled"] | Literal["failed"]


class SolutionNode(TypedDict):
    index: int
    node_type: Literal["solution"]
    status: NodeStatus
    instruction: Instruction
    edits: Edits


class ProblemNode(TypedDict):
    index: int
    node_type: Literal["problem"]
    status: NodeStatus
    error: CompileError


class ErrorSolutionNode(TypedDict):
    index: int
    node_type: Literal["error_solution"]
    status: NodeStatus
    instruction: Instruction
    edits: Edits
    error_text: str


class ErrorProblemNode(TypedDict):
    index: int
    node_type: Literal["error_problem"]
    status: NodeStatus
    error: CompileError
    error_text: str
    suspected_instruction: Instruction | None
    suspected_edits: Edits | None


NodeData = SolutionNode | ProblemNode | ErrorSolutionNode | ErrorProblemNode


class InitialChange(BaseModel):
    error: str
    file_path: str
    error_position: tuple[int, int, int, int]

    @field_validator("file_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class Commit(BaseModel):
    branch_name: str
    git_path: str
    repo_url: str
    reset_branch: str | None = None

    @field_validator("git_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class RestrictionOptions(BaseModel):
    restrict_change_to_single_file: str | None = None
    restrict_to_project: str | None = None
    project_blacklist: list[str] | None = None


class CreateGraphInput(BaseModel):
    iteration_name: str
    project_name: str
    goal: str
    solution_path: str
    restriction_options: RestrictionOptions = Field(
        default=RestrictionOptions(
            project_blacklist=None,
            restrict_change_to_single_file=None,
            restrict_to_project=None,
        )
    )
    initial_change: InitialChange
    is_local: bool

    @field_validator("solution_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class CommitGraphInput(BaseModel):
    iteration_name: str
    project_name: str
    base_path: str
    commit: Commit
    is_local: bool

    @field_validator("base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class OptimizeGraphInput(BaseModel):
    iteration_name: str
    project_name: str
    base_path: str
    is_local: bool

    @field_validator("base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class ResumeInitialNode(BaseModel):
    index: int
    status: NodeStatus
    error: CompileError
    new_instruction: Instruction | None = Field(default=None)
    new_edits: Edits | None = Field(default=None)


class ResumeGraphInput(BaseModel):
    iteration_name: str
    project_name: str
    goal: str
    solution_path: str
    base_path: str
    commit: Commit
    restriction_options: RestrictionOptions = Field(
        default=RestrictionOptions(
            project_blacklist=None,
            restrict_change_to_single_file=None,
            restrict_to_project=None,
        )
    )
    resume_initial_node: ResumeInitialNode
    is_local: bool

    @field_validator("solution_path", "base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


SupportedLanguages = Literal["python", "c_sharp", "xml"]

DependencyGraphNodeType = Literal["Import", "Class", "Method", "Field"]
