from changing_dot.custom_types import BlockEdit, Instruction
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)


class HardCodedInstructionInterpreter(IBlockInstructionInterpreter):
    hardcoded_edit: BlockEdit

    def __init__(self, edit: BlockEdit):
        self.hardcoded_edit = edit

    def get_edit_from_instruction(
        self, instruction: Instruction, DG: DependencyGraph
    ) -> BlockEdit:
        return self.hardcoded_edit
