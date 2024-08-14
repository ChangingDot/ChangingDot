from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.modifyle.modifyle_block import IModifyle


def apply_graph_changes(
    G: ChangingGraph,
    DG: DependencyGraph,
    modifyle: IModifyle,
    observer: Observer | None,
) -> None:
    for node_index in G.get_all_handled_solution_nodes():
        node = G.get_node(node_index)
        assert node["node_type"] == "solution"
        if observer:
            observer.log(f"applying edits {node['edits']}")
        modifyle.apply_change(DG, node["edits"])
