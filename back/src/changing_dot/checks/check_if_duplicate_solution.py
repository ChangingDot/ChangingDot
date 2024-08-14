from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import (
    BlockEdit,
    InstructionBlock,
    SolutionNode,
)
from changing_dot_visualize.observer import Observer


def find_same_solution_block(
    G: ChangingGraph,
    instruction_to_match: InstructionBlock,
    edits_to_match: list[BlockEdit],
) -> list[int]:
    matching_nodes = []
    for node, attrs in G.G.nodes(data=True):
        if attrs.get("node_type") != "solution":
            continue

        if attrs.get("status") == "failed":
            continue

        if (
            attrs.get("instruction").get("file_path")
            != instruction_to_match["file_path"]
        ):
            continue

        node_block_id = attrs.get("instruction")["block_id"]
        if node_block_id != instruction_to_match["block_id"]:
            continue

        node_edit_afters = [edit.after for edit in attrs.get("edits")]

        for edit in edits_to_match:
            if edit.after not in node_edit_afters:
                continue

        matching_nodes.append(node)

    return matching_nodes


def check_if_duplicate_solution_block(
    G: ChangingGraph,
    solution_node: SolutionNode,
    observer: Observer | None = None,
) -> SolutionNode | None:
    if observer:
        observer.log("Checking if solution already exists")

    matched_nodes = find_same_solution_block(
        G, solution_node["instruction"], solution_node["edits"]
    )

    assert len(matched_nodes) == 0 or len(matched_nodes) == 1
    if len(matched_nodes) == 1:
        existing_solution = G.get_node(matched_nodes[0])
        assert existing_solution["node_type"] == "solution"
        return existing_solution
    return None
