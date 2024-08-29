import os
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


def validate_and_convert_path(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Path must be a string")
    if os.path.exists(value) or not os.path.isabs(value):
        return os.path.abspath(value)
    else:
        raise ValueError(f"Invalid path: {value}")


class Instruction(BaseModel):
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
        if v.startswith((" ", "\t", "\n", "\r")):
            raise ValueError("Field must not start with a whitespace")
        if v.endswith("\n"):
            raise ValueError("Field must not end with a newline character")
        return v


class EmptyEdit(BlockEdit):
    file_path: str
    block_id: int
    before: str = ""
    after: str = ""


class ErrorInitialization(BaseModel):
    init_type: Literal["error"]
    initial_error: str
    initial_file_path: str
    initial_error_position: tuple[int, int, int, int]


Initialization = ErrorInitialization


class CompileError(BaseModel):
    text: str
    file_path: str
    project_name: str
    pos: tuple[int, int, int, int]


NodeStatus = Literal["pending"] | Literal["handled"] | Literal["failed"]


class NodeData(BaseModel):
    index: int
    node_type: (
        Literal["solution"]
        | Literal["problem"]
        | Literal["error_problem"]
        | Literal["error_solution"]
    )
    status: NodeStatus


class SolutionNode(NodeData):
    node_type: Literal["solution"]
    instruction: Instruction
    edits: list[BlockEdit]


class ProblemNode(NodeData):
    node_type: Literal["problem"]
    error: CompileError


class ErrorSolutionNode(NodeData):
    node_type: Literal["error_solution"]
    instruction: Instruction
    edits: list[BlockEdit]
    error_text: str


class ErrorProblemNode(NodeData):
    node_type: Literal["error_problem"]
    error: CompileError
    error_text: str
    suspected_instruction: Instruction | None
    suspected_edits: list[BlockEdit] | None


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


class MypyAnalyzerOptions(BaseModel):
    name: Literal["mypy"] = "mypy"
    language: Literal["python"] = "python"
    folder_path: str
    python_interpreter_path: str
    requirements_path: str
    venv_path: str | None = None

    @field_validator("folder_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class RoslynAnalyzerOptions(BaseModel):
    name: Literal["roslyn"] = "roslyn"
    language: Literal["c_sharp"] = "c_sharp"
    solution_path: str

    @field_validator("solution_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


AnalyzerOptions = MypyAnalyzerOptions | RoslynAnalyzerOptions


class CreateGraphInput(BaseModel):
    iteration_name: str
    project_name: str
    goal: str
    restriction_options: RestrictionOptions = Field(
        default=RestrictionOptions(
            project_blacklist=None,
            restrict_change_to_single_file=None,
            restrict_to_project=None,
        )
    )
    initial_change: InitialChange
    analyzer_options: AnalyzerOptions
    is_local: bool
    llm_provider: Literal["OPENAI", "MISTRAL"]


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
    analyzer_options: AnalyzerOptions

    @field_validator("base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)


class ResumeInitialNode(BaseModel):
    index: int
    status: NodeStatus
    error: CompileError
    new_instruction: Instruction | None = Field(default=None)
    new_edits: list[BlockEdit] | None = Field(default=None)


class ResumeGraphInput(BaseModel):
    iteration_name: str
    project_name: str
    goal: str
    base_path: str
    commit: Commit
    initial_change: InitialChange
    restriction_options: RestrictionOptions = Field(
        default=RestrictionOptions(
            project_blacklist=None,
            restrict_change_to_single_file=None,
            restrict_to_project=None,
        )
    )
    resume_initial_node: ResumeInitialNode
    analyzer_options: AnalyzerOptions
    is_local: bool
    llm_provider: Literal["OPENAI", "MISTRAL"]

    @field_validator("base_path")
    def validate_path(cls, value: str) -> str:
        return validate_and_convert_path(value)
