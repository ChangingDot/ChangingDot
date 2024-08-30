import pickle
from typing import Literal

import networkx as nx
import vizro.models as vm
from dash import dcc, html

from changing_dot_visualize.format_text import get_text_from_graph


class NodePresentation(vm.VizroBaseModel):
    type: Literal["nodepres"] = "nodepres"

    iteration_name: str
    project_name: str
    step_index: int
    base_path: str

    def build(self) -> html.Div:
        G = self.load_graph()
        text = get_text_from_graph(G, 0)
        return html.Div(
            [
                dcc.Markdown(
                    "### Node Info",
                    className="card_text",
                    dangerously_allow_html=False,
                    id=f"node_title_{self.step_index}",
                ),
                html.Div(
                    [text],
                    id=f"node_presentation_text_{self.step_index}",
                ),
            ]
        )

    def load_graph(self) -> nx.Graph:
        file_path = f"{self.base_path}/{self.iteration_name}/{self.step_index}_{self.project_name}.pickle"
        with open(file_path, "rb") as handle:
            G: nx.Graph = pickle.load(handle)
            return G
