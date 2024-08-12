from changing_dot.custom_types import BlockEdit, InstructionBlock
from changing_dot.dependency_graph.dependency_graph import DependencyGraph


class IBlockInstructionInterpreter:
    def get_edit_from_instruction(
        self, instruction: InstructionBlock, DG: DependencyGraph
    ) -> BlockEdit:
        raise NotImplementedError()
