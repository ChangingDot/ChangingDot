from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.error_manager import (
    IErrorManager,
)
from changing_dot.modifyle.modifyle_block import applied_edits_context


def check_solution_syntax_correctness(
    DG: DependencyGraph,
    edits: list[BlockEdit],
    error_manager: IErrorManager,
) -> bool:
    with applied_edits_context(DG, edits):
        has_syntax_errors = error_manager.has_syntax_errors()
    return not has_syntax_errors
