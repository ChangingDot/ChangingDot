import argparse
from typing import Any

import networkx as nx
import vizro.models as vm
import yaml
from core.custom_types import NodeData
from core.utils.process_pickle_files import process_pickle_files
from dash import Input, Output, callback, html
from vizro import Vizro

from visualize.format_text import get_text_from_graph
from visualize.graph_vis import VisDcc
from visualize.node_presentation import NodePresentation
from visualize.step_presentation import StepPresentation


def get_node_color(node: NodeData) -> str:
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
    project_name: str,
    base_path: str,
    is_local: bool,
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
                project_name=project_name,
                iteration_name=iteration_name,
                base_path=base_path,
                step_index=step_index,
                is_local=is_local,
            ),
            NodePresentation(
                id=f"{step_index}_node",
                project_name=project_name,
                iteration_name=iteration_name,
                base_path=base_path,
                step_index=step_index,
                is_local=is_local,
            ),
        ],
        controls=[],
    )


def visualize_graph(config: dict[str, Any], is_local: bool) -> None:
    iteration_name = config["iteration_name"]
    project_name = config["project_name"]
    base_path = config["base_path"]

    graphs = process_pickle_files(f"{base_path}/{iteration_name}", is_local)

    pages = [
        createPage(G, i, iteration_name, project_name, base_path, is_local)
        for i, G in enumerate(graphs)
    ]

    dashboard = vm.Dashboard(
        id="dashboard",
        title=f"{project_name} - {iteration_name}",
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

    visualize_graph(config, True)
