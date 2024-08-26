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


class InstructionBlock(TypedDict):
    block_id: int
    file_path: str
    solution: str


class BlockEdit(BaseModel):
    file_path: str
    block_id: int
    before: str
    after: str

    @field_validator("before", "after")
    def check_no_trailing_newline(cls, v: str) -> str:
        if v.endswith("\n"):
            raise ValueError("Field must not end with a newline character")
        return v


class EmptyEdit(BlockEdit):
    file_path: str
    block_id: int
    before: str = ""
    after: str = ""


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


Edit = ReplaceEdit | AddEdit | RemoveEdit

Edits = list[Edit]


NodeStatus = Literal["pending"] | Literal["handled"] | Literal["failed"]


class SolutionNode(TypedDict):
    index: int
    node_type: Literal["solution"]
    status: NodeStatus
    instruction: InstructionBlock
    edits: list[BlockEdit]


class ProblemNode(TypedDict):
    index: int
    node_type: Literal["problem"]
    status: NodeStatus
    error: CompileError


class ErrorSolutionNode(TypedDict):
    index: int
    node_type: Literal["error_solution"]
    status: NodeStatus
    instruction: InstructionBlock
    edits: list[BlockEdit]
    error_text: str


class ErrorProblemNode(TypedDict):
    index: int
    node_type: Literal["error_problem"]
    status: NodeStatus
    error: CompileError
    error_text: str
    suspected_instruction: InstructionBlock | None
    suspected_edits: list[BlockEdit] | None


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
    llm_provider: Literal["OPENAI", "MISTRAL"]

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


class ApplyGraphChangesInput(BaseModel):
    iteration_name: str
    project_name: str
    solution_path: str
    base_path: str
    is_local: bool

    @field_validator("base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class ResumeInitialNode(BaseModel):
    index: int
    status: NodeStatus
    error: CompileError
    new_instruction: InstructionBlock | None = Field(default=None)
    new_edits: list[BlockEdit] | None = Field(default=None)


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
    llm_provider: Literal["OPENAI", "MISTRAL"]

    @field_validator("solution_path", "base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)
