from typing import Literal, TypedDict

import visdcc
import vizro.models as vm
from dash import html


class DccNode(TypedDict):
    id: int
    label: str
    shape: Literal["dot"] | Literal["square"]
    size: int
    color: str


# Alternative instanciation because from is a reserved keyword
DccEdge = TypedDict(
    "DccEdge",
    {"id": str, "from": int, "to": int, "width": int},
)


class VisDcc(vm.VizroBaseModel):
    type: Literal["visdcc"] = "visdcc"
    nodes: list[DccNode]
    edges: list[DccEdge]

    def build(self) -> html.Div:
        return html.Div(
            [
                visdcc.Network(
                    id="net",
                    data={
                        "nodes": self.nodes,
                        "edges": self.edges,
                    },
                    style={"width": "100%", "height": "100%"},
                    options={
                        "layout": {
                            "hierarchical": {"enabled": False, "sortMethod": "directed"}
                        },
                        "edges": {
                            "arrows": "to",
                            "color": {
                                "color": "grey",
                            },
                        },
                    },
                ),
            ],
            style={"width": "100%", "height": "100%"},
        )
