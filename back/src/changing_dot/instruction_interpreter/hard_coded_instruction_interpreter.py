from changing_dot.custom_types import Edits, Instruction
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IInstructionInterpreter,
)


class HardCodedInstructionInterpreter(IInstructionInterpreter):
    hardcoded_edits: Edits

    def __init__(self, edits: Edits):
        self.hardcoded_edits = edits

    def get_edits_from_instruction(self, instruction: Instruction) -> Edits:
        return self.hardcoded_edits
