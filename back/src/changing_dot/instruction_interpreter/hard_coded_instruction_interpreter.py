from changing_dot.custom_types import BlockEdit, InstructionBlock
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)


class HardCodedInstructionInterpreter(IBlockInstructionInterpreter):
    hardcoded_edits: list[BlockEdit]

    def __init__(self, edits: list[BlockEdit]):
        self.hardcoded_edits = edits

    def get_edits_from_instruction(
        self, instruction: InstructionBlock, DG: DependencyGraph
    ) -> list[BlockEdit]:
        return self.hardcoded_edits
