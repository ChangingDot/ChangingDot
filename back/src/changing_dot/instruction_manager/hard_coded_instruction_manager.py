from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import Instruction
from changing_dot.instruction_manager.instruction_manager import IInstructionManager


class HardCodedInstructionManager(IInstructionManager):
    hardcoded_instruction: Instruction

    def __init__(self, instruction: Instruction):
        self.hardcoded_instruction = instruction

    def get_node_instruction(self, G: ChangingGraph, node_index: int) -> Instruction:
        return self.hardcoded_instruction
