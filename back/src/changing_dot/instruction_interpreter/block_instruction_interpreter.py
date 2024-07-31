from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    InstructionBlock,
)
from changing_dot_visualize.observer import Observer
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel


class BlockEdit(BaseModel):
    file_path: str
    block_id: int
    before: str
    after: str


class BlockInstructionInterpreter:
    def __init__(self, model: BaseChatModel, observer: Observer | None = None):
        self.model = model
        self.observer = observer

    def get_edits_from_instruction(
        self, instruction: InstructionBlock, DG: DependencyGraph
    ) -> list[BlockEdit]:
        return []
