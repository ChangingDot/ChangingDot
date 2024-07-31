from typing import TYPE_CHECKING

from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    BlockInstructionInterpreter,
)
from langchain_community.chat_models.fake import FakeListChatModel

if TYPE_CHECKING:
    from changing_dot.instruction_interpreter.block_instruction_interpreter import (
        BlockEdit,
    )
    from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
        InstructionBlock,
    )


def make_instruction_interpreter(
    expected_llm_output: str,
) -> BlockInstructionInterpreter:
    return BlockInstructionInterpreter(
        FakeListChatModel(responses=[expected_llm_output])
    )


def test_empty_instruction() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/subject.cs"])
    instruction: InstructionBlock = {
        "file_path": "./tests/core/fixtures/subject.cs",
        "block_id": 5,
        "solution": "random_solution",
    }

    interpreter = make_instruction_interpreter(
        """
    random blabla
    """
    )

    expected_edits: list[BlockEdit] = []

    assert expected_edits == interpreter.get_edits_from_instruction(instruction, DG)
