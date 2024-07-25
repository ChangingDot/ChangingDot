import os
import re
from typing import TYPE_CHECKING, Literal, TypedDict

from core.custom_types import CompileError, Edit, Edits
from utils.list_action_applier import apply_actions_on_list
from utils.text_functions import read_text

if TYPE_CHECKING:
    from utils.list_action_applier import Action


class ErrorIndex(TypedDict):
    edit_type: Literal["error"]
    line_number: int
    text: str


ActionIndex = Edit | ErrorIndex


class PromptDiffIndex(TypedDict):
    file_path: str
    actions: list[ActionIndex]


def get_leading_spaces(s: str) -> str:
    match = re.match(r"\s*", s)
    if match:
        return match.group()
    return ""


def find_index_by_file_path(file_path: str, file_indexes: list[PromptDiffIndex]) -> int:
    for i, item in enumerate(file_indexes):
        if item["file_path"] == file_path:
            return i
    return -1


def create_prompt_diff_block(
    error: CompileError, edits_that_caused_problem: Edits
) -> str:
    ERROR_MARKER = "// ERROR"

    file_to_action: dict[str, list[Action]] = {}

    for edit in edits_that_caused_problem:
        actions: list[Action] = []

        if edit["edit_type"] == "replace":
            actions.append(
                {
                    "action_type": "replace",
                    "line_number": edit["line_number"],
                    "after": f"-{edit['before']}\n",
                }
            )
            actions.append(
                {
                    "action_type": "add",
                    "line_number": edit["line_number"] + 1,
                    "after": f"+{edit['after']}\n",
                }
            )

        elif edit["edit_type"] == "add":
            actions.append(
                {
                    "action_type": "add",
                    "line_number": edit["line_number"],
                    "after": f"+{edit['line_to_add']}\n",
                }
            )

        elif edit["edit_type"] == "remove":
            actions.append(
                {
                    "action_type": "replace",
                    "line_number": edit["line_number"],
                    "after": f"-{edit['line_to_remove']}\n",
                }
            )

        if edit["file_path"] in file_to_action:
            file_to_action[edit["file_path"]] += actions
        else:
            file_to_action[edit["file_path"]] = actions

    # add error
    file_text = read_text(error["file_path"])
    lines = file_text.splitlines(keepends=True)
    prefix_spaces = get_leading_spaces(lines[error["pos"][0]])
    error_text = f"{prefix_spaces}{ERROR_MARKER} {error['text']}\n"

    if error["file_path"] in file_to_action:
        file_to_action[error["file_path"]] += [
            {
                "action_type": "add",
                "line_number": error["pos"][0],
                "after": error_text,
            }
        ]
    else:
        file_to_action[error["file_path"]] = [
            {
                "action_type": "add",
                "line_number": error["pos"][0],
                "after": error_text,
            }
        ]

    total_lines: list[str] = []
    for file_path, actions in file_to_action.items():
        file_content = read_text(file_path)
        file_lines = file_content.splitlines(keepends=True)
        changed_lines = apply_actions_on_list(file_lines, actions)

        new_lines = (
            []
            if (len(file_to_action.keys()) == 1 or len(file_to_action.keys()) == 0)
            else [f"@@{os.path.basename(file_path)}@@\n"]
        )
        i = 1
        for line in changed_lines:
            if ERROR_MARKER in line or line[0] == "+":
                new_lines.append(line)
            else:
                new_lines.append(f"{i}{line}")
                i += 1

        if len(total_lines) > 0 and total_lines[-1][-1] != "\n":
            total_lines[-1] += "\n"
        total_lines += new_lines

    return "".join(total_lines)
