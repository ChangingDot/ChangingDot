import pickle
from typing import Literal

import networkx as nx
import vizro.models as vm
from dash import dcc, html


class StepPresentation(vm.VizroBaseModel):
    type: Literal["steppres"] = "steppres"
    iteration_name: str
    project_name: str
    step_index: int
    output_path: str

    def build(self) -> html.Div:
        G = self.load_graph()

        return html.Div(
            [
                dcc.Markdown(
                    "### Step Info",
                    className="card_text",
                    dangerously_allow_html=False,
                    id=f"step_title_{self.step_index}",
                ),
                *G.graph["step_logs"],
            ],
            style={
                "overflow": "scroll",
                "width": "100%",
                "height": "100%",
            },
        )

    def load_graph(self) -> nx.Graph:
        file_path = f"{self.output_path}/{self.iteration_name}/{self.step_index}_{self.project_name}.pickle"
        with open(file_path, "rb") as handle:
            G: nx.Graph = pickle.load(handle)
            return G
