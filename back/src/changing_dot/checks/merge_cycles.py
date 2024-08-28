import functools
import operator

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import SolutionNode
from changing_dot_visualize.observer import Observer


def merge_solution_nodes(solution_nodes: list[SolutionNode]) -> SolutionNode:
    return SolutionNode(
        index=-1,
        node_type="solution",
        status="handled",
        instruction=solution_nodes[0].instruction,
        edits=functools.reduce(
            operator.iadd,
            (solution_node.edits for solution_node in solution_nodes),
            [],
        ),
    )


def merge_cycles(G: ChangingGraph, observer: Observer) -> None:
    cycles = G.get_cycles()

    observer.log(f"Found cycles {cycles}")

    for cycle in cycles:
        observer.log(f"Optimizing cycle {cycle}")

        cycle_solution_nodes: list[SolutionNode] = [
            G.get_node(index)  # type: ignore
            for index in cycle
            if G.get_node(index).node_type == "solution"
        ]

        merged_node_index = G.add_solution_node(
            merge_solution_nodes(cycle_solution_nodes)
        )

        observer.log(f"Create new node {merged_node_index}")
        # Redirect edges
        for node_index in cycle:
            for u, _v in list(G.in_edges(node_index)):
                if u not in cycle:
                    G.add_edge(u, merged_node_index)
                    observer.log(f"Add edge between {u}, {merged_node_index}")
            for _u, v in list(G.out_edges(node_index)):
                if v not in cycle:
                    G.add_edge(merged_node_index, v)
                    observer.log(f"Add edge between {merged_node_index}, {v}")

            G.remove_node(node_index)
            observer.log(f"Removing {node_index}")

        observer.save_graph_state()
