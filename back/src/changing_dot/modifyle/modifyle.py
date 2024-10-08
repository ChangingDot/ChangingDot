from collections.abc import Iterator
from contextlib import contextmanager

from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.utils.text_functions import read_text, write_text


class IModifyle:
    def revert_changes(self, DG: DependencyGraph) -> None:
        pass

    def apply_change(self, DG: DependencyGraph, edits: list[BlockEdit]) -> None:
        pass


class FakeModifyle(IModifyle):
    def revert_changes(self, DG: DependencyGraph) -> None:
        pass

    def apply_change(self, DG: DependencyGraph, edits: list[BlockEdit]) -> None:
        pass


class ManualModifyle(IModifyle):
    def revert_changes(self, DG: DependencyGraph) -> None:
        input("Revert")

    def apply_change(self, DG: DependencyGraph, edits: list[BlockEdit]) -> None:
        for edit in edits:
            input(f"Replace {edit.before} by {edit.after} in {edit.file_path}")


def apply_edits(DG: DependencyGraph, edits: list[BlockEdit]) -> None:
    for edit in edits:
        file_content = read_text(edit.file_path)

        file_lines = file_content.splitlines()

        after_lines = edit.after.splitlines()

        node = DG.get_node(edit.block_id)

        start_index = node.start_point[0]
        end_index = node.end_point[0] + 1

        # add back indentation to first line
        after_lines[0] = " " * node.start_point[1] + after_lines[0]

        changed_file = "\n".join(
            file_lines[:start_index] + after_lines + file_lines[end_index:]
        )

        write_text(edit.file_path, changed_file)

        DG.update_graph_from_edits([edit])


# Use when you need to stack multiple changes and then revert
class IntegralModifyle(IModifyle):
    def __init__(self) -> None:
        self.original_files_content: dict[str, str] = {}

    def apply_change(self, DG: DependencyGraph, edits: list[BlockEdit]) -> None:
        if len(edits) == 0:
            return

        DG.save_state()

        for edit in edits:
            if self.original_files_content.get(edit.file_path) is None:
                self.original_files_content[edit.file_path] = read_text(edit.file_path)

        apply_edits(DG, edits)

    def revert_changes(self, DG: DependencyGraph) -> None:
        for file_path in self.original_files_content:
            write_text(file_path, self.original_files_content[file_path])
        self.original_files_content = {}


# Use for 1 time changes that you need to revert just after
@contextmanager
def applied_edits_context(
    DG: DependencyGraph, edits: list[BlockEdit]
) -> Iterator[None]:
    original_files_content: dict[str, str] = {}
    for edit in edits:
        if original_files_content.get(edit.file_path) is None:
            original_files_content[edit.file_path] = read_text(edit.file_path)

    DG.save_state()

    try:
        apply_edits(DG, edits)
        yield
    finally:
        for file_path in original_files_content:
            write_text(file_path, original_files_content[file_path])
        DG.revert()
