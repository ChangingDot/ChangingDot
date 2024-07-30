import uuid

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.checks.merge_cycles import merge_cycles
from changing_dot.utils.process_pickle_files import process_pickle_files


def optimize_graph(G: ChangingGraph, observer: Observer) -> None:
    observer.log("Optimizing: merge cycles")

    merge_cycles(G, observer)

    observer.log("Optimizing: removing redundant edges")

    G.remove_redundant_edges()

    observer.save_graph_state()


def run_optimize_graph(
    iteration_name: str, project_name: str, base_path: str, is_local: bool
) -> None:
    job_id = str(uuid.uuid4())

    graphs = process_pickle_files(f"{base_path}/{iteration_name}/", is_local)

    G = ChangingGraph(graphs[-1])

    observer = Observer(
        G, iteration_name, project_name, job_id=job_id, step=len(graphs)
    )

    optimize_graph(G, observer)