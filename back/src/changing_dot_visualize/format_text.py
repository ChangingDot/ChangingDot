import difflib
import json

import networkx as nx
from dash import dcc, html

from changing_dot_visualize.utils import convert_to_dict


def get_diff_from_before_after(before: str, after: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            lineterm="",
            fromfile="before",
            tofile="after",
        )
    )


def get_text_from_graph(G: nx.Graph, i: int) -> html:
    if G.number_of_nodes() == 0:
        return "No nodes"

    node = convert_to_dict(G.nodes[i])

    common = [
        html.P(
            f"{json.dumps(convert_to_dict(node), indent=4)}",
            id=f"node_{i}",
            style={
                "display": "none",
            },
        ),
        dcc.Clipboard(
            target_id=f"node_{i}",
            style={
                "position": "absolute",
                "top": 0,
                "right": 20,
                "fontSize": 20,
            },
        ),
        html.P(f"Node index : {i}"),
        html.P(f"Node Type : {node['node_type']}"),
        html.P(f"Node Status : {node['status']}"),
    ]

    if node["node_type"] == "problem":
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Error"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in node["error"].items()
                            ]
                        ),
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
            ],
            style={"position": "relative"},
        )

    if node["node_type"] == "solution":
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Instruction"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in node["instruction"].items()
                            ]
                        ),
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.Details(
                    [
                        html.Summary("Node Edits"),
                        *[
                            html.Div(
                                [
                                    html.P(f" - {key} : {value}")
                                    for key, value in edit.items()
                                    if key != "before" and key != "after"
                                ]
                            )
                            for edit in node["edits"]
                        ],
                        *[
                            html.Div(
                                get_diff_from_before_after(
                                    edit["before"], edit["after"]
                                ),
                                style={"whiteSpace": "pre-line"},
                            )
                            for edit in node["edits"]
                        ],
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
            ],
            style={"position": "relative"},
        )

    if node["node_type"] == "error_solution":
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Instruction"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in node["instruction"].items()
                            ]
                        ),
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.Details(
                    [
                        html.Summary("Node Edits"),
                        *[
                            html.Div(
                                [
                                    html.P(f" - {key} : {value}")
                                    for key, value in edit.items()
                                ]
                            )
                            for edit in node["edits"]
                        ],
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.P(f"Error : {node['error_text']}"),
            ],
            style={"position": "relative"},
        )

    if node["node_type"] == "error_problem":
        suspected_edits = (
            node["suspected_edits"] if node["suspected_edits"] is not None else []
        )
        suspected_instruction = (
            node["suspected_instruction"]
            if node["suspected_instruction"] is not None
            else {}
        )
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Error"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in node["error"].items()
                            ]
                        ),
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.Details(
                    [
                        html.Summary("Suspected Instruction"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in suspected_instruction.items()
                            ]
                        ),
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.Details(
                    [
                        html.Summary("Suspected Edits"),
                        *[
                            html.Div(
                                [
                                    html.P(f" - {key} : {value}")
                                    for key, value in edit.items()
                                ]
                            )
                            for edit in suspected_edits
                        ],
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.P(f"Error : {node['error_text']}"),
            ],
            style={"position": "relative"},
        )

    else:
        # shouldn't happen
        return []
