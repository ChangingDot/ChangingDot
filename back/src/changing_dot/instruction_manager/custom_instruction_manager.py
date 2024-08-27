import json
from typing import Literal

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import Instruction
from changing_dot.instruction_manager.instruction_manager import IInstructionManager
from loguru import logger


class CustomInstructionManager(IInstructionManager):
    fake_memory: dict[
        str,
        tuple[Literal["replace"] | Literal["add"] | Literal["remove"], str]
        | tuple[Literal["replace"] | Literal["add"] | Literal["remove"], str, int],
    ]

    def __init__(self, memory_path: str, memory_key: str):
        self.fake_memory = get_fake_memory(memory_path, memory_key)

    def get_node_instruction(self, G: ChangingGraph, node_index: int) -> Instruction:
        node = G.get_node(node_index)

        assert node["node_type"] == "problem"

        # hack to get solution from error rather than node index
        node_error = "".join(node["error"].text.replace("'", "").split(" "))
        error_index = f"{node_error}_{node['error'].file_path}_{node['error'].pos[0]}"
        if self.fake_memory.get(error_index) is not None:
            value = self.fake_memory.get(error_index)
        else:
            value = self.fake_memory.get(f"{node['index']}")

        if value is None:
            logger.info("Here is the problem :")
            logger.info(node)
            solution = input("What is the solution ?")
            edit_type = input("What is the edit type ? (replace, add, remove)")
            line_number = int(input("Line number ?"))
            logger.info(f'"{error_index}" : ["{edit_type}","{solution}"]')
        else:
            edit_type = value[0]
            solution = value[1]
            line_number = value[2] if len(value) == 3 else None  # type: ignore

        if edit_type == "replace":
            return {
                "edit_type": edit_type,  # type: ignore
                "programming_language": "c#",
                "file_path": node["error"].file_path,
                "line_number": (line_number if line_number else node["error"].pos[0]),
                "error": node["error"].text,
                "solution": solution,
            }

        if edit_type == "add":
            return {
                "edit_type": edit_type,  # type: ignore
                "programming_language": "c#",
                "file_path": node["error"].file_path,
                "line_number": line_number if line_number else 1,
                "error": node["error"].text,
                "solution": solution,
            }

        return {
            "edit_type": edit_type,  # type: ignore
            "programming_language": "c#",
            "file_path": node["error"].file_path,
            "line_number": line_number if line_number else node["error"].pos[0],
            "error": node["error"].text,
            "solution": solution,
        }


def get_fake_memory(
    path: str, key: str
) -> dict[
    str,
    tuple[Literal["replace"] | Literal["add"] | Literal["remove"], str]
    | tuple[Literal["replace"] | Literal["add"] | Literal["remove"], str, int],
]:
    with open(path) as file:
        result = json.load(file)
        return result[key]  # type: ignore
