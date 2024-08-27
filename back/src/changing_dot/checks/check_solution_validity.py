import os

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.error_manager import (
    IErrorManager,
)
from changing_dot.modifyle.modifyle import applied_edits_context
from changing_dot_visualize.observer import Observer


def simple_check_solution_validity_block(
    G: ChangingGraph,
    DG: DependencyGraph,
    problem_node_index: int,
    edits: list[BlockEdit],
    error_manager: IErrorManager,
    observer: Observer,
) -> bool:
    problem_node = G.get_node(problem_node_index)
    assert problem_node["node_type"] == "problem"
    with applied_edits_context(DG, edits):
        compile_errors = error_manager.get_compile_errors(observer)

    # Do not take project_name into account
    return {
        "file_path": os.path.abspath(problem_node["error"].file_path),
        "pos": problem_node["error"].pos,
        "text": problem_node["error"].text,
    } not in [
        {
            "file_path": os.path.abspath(error.file_path),
            "pos": error.pos,
            "text": error.text,
        }
        for error in compile_errors
    ]
