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
    base_path: str
    is_local: bool

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
        file_path = f"{self.base_path}/{self.iteration_name}/{self.step_index}_{self.project_name}.pickle"
        if self.is_local:
            with open(file_path, "rb") as handle:
                G: nx.Graph = pickle.load(handle)
                return G
        else:
            from config.storage import bucket

            blob = bucket.blob(file_path)
            with blob.open("rb") as handle:
                blob_G: nx.Graph = pickle.load(handle)
                return blob_G
