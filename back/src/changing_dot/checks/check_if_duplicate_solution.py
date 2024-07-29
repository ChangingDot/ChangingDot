from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import (
    SolutionNode,
    edit_to_diff,
)
from changing_dot_visualize.observer import Observer


def check_if_duplicate_solution(
    G: ChangingGraph,
    solution_node: SolutionNode,
    observer: Observer,
) -> SolutionNode | None:
    observer.log("Checking if solution already exists")
    # TODO check if that is what we want for equality
    matched_nodes = G.find_same_solution(
        solution_node["instruction"]["file_path"],
        solution_node["instruction"]["line_number"],
        edit_to_diff(solution_node["edits"][0]),
    )

    assert len(matched_nodes) == 0 or len(matched_nodes) == 1
    if len(matched_nodes) == 1:
        existing_solution = G.get_node(matched_nodes[0])
        assert existing_solution["node_type"] == "solution"
        return existing_solution
    return None
