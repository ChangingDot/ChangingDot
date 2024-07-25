import json

import networkx as nx
from dash import dcc, html


def get_text_from_graph(G: nx.Graph, i: int) -> html:
    if G.number_of_nodes() == 0:
        return "No nodes"

    common = [
        html.P(
            f"{json.dumps(G.nodes[i], indent=4)}",
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
        html.P(f"Node Type : {G.nodes[i]['node_type']}"),
        html.P(f"Node Status : {G.nodes[i]['status']}"),
    ]

    if G.nodes[i]["node_type"] == "problem":
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Error"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in G.nodes[i]["error"].items()
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

    if G.nodes[i]["node_type"] == "solution":
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Instruction"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in G.nodes[i]["instruction"].items()
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
                            for edit in G.nodes[i]["edits"]
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

    if G.nodes[i]["node_type"] == "error_solution":
        return html.Div(
            [
                *common,
                html.Details(
                    [
                        html.Summary("Node Instruction"),
                        html.Div(
                            [
                                html.P(f" - {key} : {value}")
                                for key, value in G.nodes[i]["instruction"].items()
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
                            for edit in G.nodes[i]["edits"]
                        ],
                    ],
                    style={
                        "color": "var(--text-secondary)",
                        "font-size": "var(--text-size-02)",
                        "font-weight": "var(--text-weight-regular)",
                    },
                ),
                html.P(f"Error : {G.nodes[i]['error_text']}"),
            ],
            style={"position": "relative"},
        )

    if G.nodes[i]["node_type"] == "error_problem":
        suspected_edits = (
            G.nodes[i]["suspected_edits"]
            if G.nodes[i]["suspected_edits"] is not None
            else []
        )
        suspected_instruction = (
            G.nodes[i]["suspected_instruction"]
            if G.nodes[i]["suspected_instruction"] is not None
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
                                for key, value in G.nodes[i]["error"].items()
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
                html.P(f"Error : {G.nodes[i]['error_text']}"),
            ],
            style={"position": "relative"},
        )

    else:
        # shouldn't happen
        return []
