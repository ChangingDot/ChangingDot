import uuid

from utils.process_pickle_files import process_pickle_files
from visualize.observer import Observer

from core.changing_graph.changing_graph import ChangingGraph
from core.checks.merge_cycles import merge_cycles


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
