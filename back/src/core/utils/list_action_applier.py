from typing import Literal, TypedDict

from core.utils.index_manager import IndexManager


class Action(TypedDict):
    action_type: Literal["remove"] | Literal["add"] | Literal["replace"]
    line_number: int
    after: str


def apply_actions_on_list(input_list: list[str], actions: list[Action]) -> list[str]:
    copied_list = input_list.copy()
    index_manager = IndexManager()
    for action in actions:
        line_index = action["line_number"] - 1
        updated_line_index = index_manager.get_updated_index(action["line_number"] - 1)
        if action["action_type"] == "replace":
            copied_list[updated_line_index] = action["after"]
        if action["action_type"] == "add":
            if line_index == len(copied_list):
                copied_list.append(action["after"])
            else:
                copied_list.insert(updated_line_index, action["after"])
            index_manager.add_from_index(line_index)
        if action["action_type"] == "remove":
            copied_list.pop(updated_line_index)
            index_manager.remove_from_index(line_index)
    return copied_list
