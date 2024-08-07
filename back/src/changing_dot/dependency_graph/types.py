from typing import Literal

from pydantic import BaseModel
from typing_extensions import TypedDict

SupportedLanguages = Literal["python", "c_sharp", "xml", "csproj"]


class NodeTypeToTerminal(TypedDict):
    Import: list[str]
    Class: list[str]
    Method: list[str]
    Field: list[str]


DependencyGraphNodeType = Literal["Import", "Class", "Method", "Field"]


class DependencyGraphNode(BaseModel):
    node_type: DependencyGraphNodeType
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    file_path: str
    text: str


class DependencyGraphNodeWithIndex(DependencyGraphNode):
    index: int
