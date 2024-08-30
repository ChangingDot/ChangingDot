import uuid

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import AnalyzerOptions
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    create_dependency_graph_from_folder,
)
from changing_dot.modifyle.modifyle import IModifyle, IntegralModifyle
from changing_dot.utils.process_pickle_files import process_pickle_files


def apply_graph_changes(
    G: ChangingGraph,
    DG: DependencyGraph,
    modifyle: IModifyle,
    observer: Observer | None,
) -> None:
    for node_index in G.get_all_handled_solution_nodes():
        node = G.get_solution_node(node_index)
        if observer:
            observer.log(f"applying edits {node.edits}")
        modifyle.apply_change(DG, node.edits)


def run_apply_graph_changes(
    iteration_name: str,
    project_name: str,
    base_path: str,
    analyzer_options: AnalyzerOptions,
) -> None:
    job_id = str(uuid.uuid4())
    graphs = process_pickle_files(f"{base_path}/{iteration_name}/")

    G = ChangingGraph(graphs[-1])

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id=job_id,
        output_folder=base_path,
        step=len(graphs),
    )

    file_modifier: IModifyle = IntegralModifyle()

    folder_to_analyse = (
        analyzer_options.folder_path
        if analyzer_options.language == "python"
        else analyzer_options.solution_path
    )

    DG = create_dependency_graph_from_folder(
        folder_to_analyse, analyzer_options.language
    )

    apply_graph_changes(G, DG, file_modifier, observer)
