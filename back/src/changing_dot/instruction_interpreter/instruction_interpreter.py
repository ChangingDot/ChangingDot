from changing_dot.custom_types import BlockEdit, Instruction
from changing_dot.dependency_graph.dependency_graph import DependencyGraph


class IBlockInstructionInterpreter:
    def get_edit_from_instruction(
        self, instruction: Instruction, DG: DependencyGraph
    ) -> BlockEdit:
        raise NotImplementedError()
