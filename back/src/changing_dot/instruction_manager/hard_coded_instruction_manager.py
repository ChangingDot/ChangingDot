from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import InstructionBlock
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    IInstructionManagerBlock,
)


class HardCodedInstructionManager(IInstructionManagerBlock):
    hardcoded_instruction: InstructionBlock

    def __init__(self, instruction: InstructionBlock):
        self.hardcoded_instruction = instruction

    def get_node_instruction(
        self, G: ChangingGraph, DG: DependencyGraph, node_index: int
    ) -> InstructionBlock:
        return self.hardcoded_instruction
