from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.checks.merge_cycles import merge_cycles


def optimize_graph(G: ChangingGraph, observer: Observer) -> None:
    observer.log("Optimizing: merge cycles")

    merge_cycles(G, observer)

    observer.log("Optimizing: removing redundant edges")

    G.remove_redundant_edges()

    observer.save_graph_state()
