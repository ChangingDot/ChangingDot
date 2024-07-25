from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from core.custom_types import Edits
from utils.list_action_applier import apply_actions_on_list
from utils.text_functions import read_text, write_text

if TYPE_CHECKING:
    from utils.list_action_applier import Action


class IModifyle:
    def revert_change(self, edits: Edits) -> None:
        pass

    def apply_change(self, edits: Edits) -> None:
        pass

    def can_revert(self) -> bool:
        pass
        return True


class FakeModifyle(IModifyle):
    def revert_change(self, edits: Edits) -> None:
        pass

    def apply_change(self, edits: Edits) -> None:
        pass

    def can_revert(self) -> bool:
        return True


class ManualModifyle(IModifyle):
    def revert_change(self, edits: Edits) -> None:
        input("Revert")

    def apply_change(self, edits: Edits) -> None:
        for edit in edits:
            if edit["edit_type"] == "replace":
                input(
                    f"Replace {edit['before']} by {edit['after']} in {edit['file_path']} : {edit['line_number']}"
                )
            elif edit["edit_type"] == "add":
                input(
                    f"Add {edit['line_to_add']} in {edit['file_path']} : {edit['line_number']}"
                )
            elif edit["edit_type"] == "remove":
                input(
                    f"Remove {edit['line_to_remove']} in {edit['file_path']} : {edit['line_number']}"
                )

    def can_revert(self) -> bool:
        return True


class Modifyle(IModifyle):
    def __init__(self) -> None:
        self.original_files_content: dict[str, str] = {}

    def apply_change(self, edits: Edits) -> None:
        if len(edits) == 0:
            return

        for edit in edits:
            self.original_files_content[edit["file_path"]] = read_text(
                edit["file_path"]
            )

        apply_edits(edits)

    def revert_change(self, edits: Edits) -> None:
        assert len(self.original_files_content.keys()) != 0

        if len(edits) == 0:
            return

        for edit in edits:
            write_text(
                edit["file_path"], self.original_files_content[edit["file_path"]]
            )
        self.original_files_content = {}

    def can_revert(self) -> bool:
        return len(self.original_files_content.keys()) != 0


def apply_edits(edits: Edits) -> None:
    file_to_action: dict[str, list[Action]] = {}

    for edit in edits:
        action: Action | None = None

        if edit["edit_type"] == "replace":
            action = {
                "action_type": "replace",
                "line_number": edit["line_number"],
                "after": (
                    edit["after"]
                    if edit["after"].endswith("\n")
                    else edit["after"] + "\n"
                ),
            }

        elif edit["edit_type"] == "add":
            action = {
                "action_type": "add",
                "line_number": edit["line_number"],
                "after": (
                    edit["line_to_add"]
                    if edit["line_to_add"].endswith("\n")
                    else edit["line_to_add"] + "\n"
                ),
            }

        elif edit["edit_type"] == "remove":
            action = {
                "action_type": "remove",
                "line_number": edit["line_number"],
                "after": "",
            }

        assert action is not None

        if edit["file_path"] in file_to_action:
            file_to_action[edit["file_path"]].append(action)
        else:
            file_to_action[edit["file_path"]] = [action]

    for file_path, actions in file_to_action.items():
        file_content = read_text(file_path)

        if not file_content.endswith("\n"):
            file_content = file_content + "\n"

        file_lines = file_content.splitlines(keepends=True)

        changed_lines = apply_actions_on_list(file_lines, actions)

        changed_file = "".join(changed_lines)

        write_text(file_path, changed_file)


class IntegralModifyle(IModifyle):
    def __init__(self) -> None:
        self.original_files_content: dict[str, str] = {}

    def apply_change(self, edits: Edits) -> None:
        if len(edits) == 0:
            return

        for edit in edits:
            if self.original_files_content.get(edit["file_path"]) is None:
                self.original_files_content[edit["file_path"]] = read_text(
                    edit["file_path"]
                )

        apply_edits(edits)

    def revert_change(self, edits: Edits) -> None:
        for file_path in self.original_files_content:
            write_text(file_path, self.original_files_content[file_path])
        self.original_files_content = {}

    def can_revert(self) -> bool:
        return len(self.original_files_content.keys()) != 0


@contextmanager
def applied_edits_context(edits: Edits) -> Iterator[None]:
    original_files_content: dict[str, str] = {}
    for edit in edits:
        if original_files_content.get(edit["file_path"]) is None:
            original_files_content[edit["file_path"]] = read_text(edit["file_path"])
    try:
        apply_edits(edits)
        yield
    finally:
        for file_path in original_files_content:
            write_text(file_path, original_files_content[file_path])
