import argparse
import os
from typing import Any

import networkx as nx
import vizro.models as vm
import yaml
from changing_dot.config.constants import CDOT_PATH
from changing_dot.utils.file_utils import get_latest_directory
from changing_dot.utils.process_pickle_files import process_pickle_files
from dash import Input, Output, callback, html
from vizro import Vizro

from changing_dot_visualize.format_text import get_text_from_graph
from changing_dot_visualize.graph_vis import VisDcc
from changing_dot_visualize.node_presentation import NodePresentation
from changing_dot_visualize.step_presentation import StepPresentation


def get_node_color(node: Any) -> str:
    modifier = (
        "dark"
        if node["status"] == "pending"
        else "light"
        if node["status"] == "failed"
        else ""
    )

    color = (
        "blue"
        if node["index"] == 0
        else "green"
        if node["node_type"] == "solution"
        else "red"
    )

    return f"{modifier}{color}"


vm.Page.add_type("components", VisDcc)
vm.Page.add_type("components", NodePresentation)
vm.Page.add_type("components", StepPresentation)


def createPage(
    G: nx.Graph,
    step_index: int,
    iteration_name: str,
    output_path: str,
) -> vm.Page:
    @callback(
        Output(f"node_presentation_text_{step_index}", "children"),
        [Input("net", "selection")],
    )  # type: ignore
    def update_output_div(x: dict[str, list[int]]) -> html:
        if x is None or x.get("nodes") is None or len(x["nodes"]) == 0:
            return ""
        node_index: int = x["nodes"][0]
        text = get_text_from_graph(G, node_index)
        return text

    return vm.Page(
        title=f"Step {step_index}",
        layout=vm.Layout(grid=[[0, 1], [0, 2]]),
        components=[
            VisDcc(
                id=f"scatter_chart_{step_index}",
                nodes=[
                    {
                        "id": node,
                        "label": f"{node}",
                        "shape": (
                            "square"
                            if G.nodes[node]["node_type"] == "error_solution"
                            or G.nodes[node]["node_type"] == "error_problem"
                            else "dot"
                        ),
                        "size": 7,
                        "color": (get_node_color(G.nodes[node])),
                    }
                    for node in G.nodes()
                    # if G.number_of_nodes() > 0
                ],
                edges=[
                    {
                        "id": f"{edge[0]}__{edge[1]}",
                        "from": edge[0],
                        "to": edge[1],
                        "width": 2,
                    }
                    for edge in G.edges()
                ],
            ),
            StepPresentation(
                id=f"{step_index}_step",
                iteration_name=iteration_name,
                output_path=output_path,
                step_index=step_index,
            ),
            NodePresentation(
                id=f"{step_index}_node",
                iteration_name=iteration_name,
                output_path=output_path,
                step_index=step_index,
            ),
        ],
        controls=[],
    )


def visualize_graph(config: dict[str, Any]) -> None:
    output_path = config.get("output_path") or os.path.join(CDOT_PATH, "outputs")
    path_to_run = config.get("iteration_name") or get_latest_directory(output_path)

    if path_to_run is None:
        raise ValueError(
            f"No iteration was found in this output directory {output_path}"
        )

    iteration_name = os.path.basename(path_to_run)

    graphs = process_pickle_files(f"{output_path}/{iteration_name}")

    pages = [
        createPage(G, i, iteration_name, output_path) for i, G in enumerate(graphs)
    ]

    dashboard = vm.Dashboard(
        id="dashboard",
        title=f"Run {iteration_name}",
        theme="vizro_dark",
        pages=pages,
    )

    vizro = Vizro().build(dashboard)

    vizro.run(debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run")

    parser.add_argument("config_file_path", type=str, help="Path to config file")

    args = parser.parse_args()

    with open(args.config_file_path) as file:
        config = yaml.safe_load(file)

    visualize_graph(config)
