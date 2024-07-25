from core.changing_graph.changing_graph import ChangingGraph
from core.custom_types import (
    ProblemNode,
)
from utils.index_manager import IndexManager
from visualize.observer import Observer


def split_new_and_duplicate_nodes(
    G: ChangingGraph,
    problems_to_split: list[ProblemNode],
    index_manager: IndexManager,
    observer: Observer,
) -> tuple[list[ProblemNode], list[tuple[int, ProblemNode]]]:
    observer.log("Checking if we can simplify duplicate problems")

    new_nodes: list[ProblemNode] = []
    duplicate_nodes: list[tuple[int, ProblemNode]] = []

    for problem in problems_to_split:
        assert problem["node_type"] == "problem"

        matched_nodes = G.find_same_problem(
            problem["error"]["file_path"],
            index_manager.get_updated_index(problem["error"]["pos"][0]),
            problem["error"]["text"],
        )

        assert len(matched_nodes) == 0 or len(matched_nodes) == 1

        if len(matched_nodes) == 1:
            matched_node = matched_nodes[0]
            duplicate_nodes.append((matched_node, problem))
        if len(matched_nodes) == 0:
            new_nodes.append(problem)

    return new_nodes, duplicate_nodes
