from core.changing_graph.changing_graph import ChangingGraph
from core.custom_types import Instruction


class IInstructionManager:
    def get_node_instruction(self, G: ChangingGraph, node_index: int) -> Instruction:
        raise NotImplementedError()
