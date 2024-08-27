import uuid

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    create_dependency_graph_from_folder,
)
from changing_dot.modifyle.modifyle import IModifyle, IntegralModifyle
from changing_dot.utils.get_algorithm_language import get_language
from changing_dot.utils.process_pickle_files import process_pickle_files


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


def run_apply_graph_changes(
    iteration_name: str,
    project_name: str,
    solution_path: str,
    base_path: str,
    initial_change_file: str,
    is_local: bool,
) -> None:
    job_id = str(uuid.uuid4())
    graphs = process_pickle_files(f"{base_path}/{iteration_name}/", is_local)

    G = ChangingGraph(graphs[-1])

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id=job_id,
        step=len(graphs),
        is_local=is_local,
    )

    file_modifier: IModifyle = IntegralModifyle()

    language = get_language(initial_change_file)

    DG = create_dependency_graph_from_folder(solution_path, language)

    apply_graph_changes(G, DG, file_modifier, observer)
