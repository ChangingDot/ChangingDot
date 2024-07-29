from changing_dot.custom_types import Edits, Instruction


class IInstructionInterpreter:
    def get_edits_from_instruction(self, instruction: Instruction) -> Edits:
        raise NotImplementedError()
