import os
import pickle
from typing import Any

from core.changing_graph.changing_graph import ChangingGraph
from dash import html
from loguru import logger


def ensure_directory_exists(file_path: str) -> None:
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


class Observer:
    G: ChangingGraph
    iteration_name: str
    project_name: str
    is_local: bool

    step: int

    logs: list[html]

    def __init__(
        self,
        G: ChangingGraph,
        iteration_name: str,
        project_name: str,
        job_id: str,
        output_folder: str = "./outputs",
        is_local: bool = True,
        step: int | None = None,
    ):
        self.G = G
        self.iteration_name = iteration_name
        self.project_name = project_name
        self.is_local = is_local
        self.output_folder = output_folder if is_local else ""
        self.logs = []
        if step is None:
            step = 0
        self.step = step

        self.logger = logger.bind(request_id=job_id)

    def save_graph_state(self) -> None:
        if not self.is_local:
            raise NotImplementedError("Remote not yet implemented")

        # Create the path for the file in GCS
        path = f"{self.output_folder}/{self.iteration_name}/{self.step}_{self.project_name}.pickle"

        # Ensure directory exists (optional, for local operations, not required for GCS)
        if self.is_local:
            ensure_directory_exists(path)

        # Adding attribute to underlying nx graph
        self.G.G.graph["step_logs"] = self.logs

        # Serialize the graph object to a bytes object
        pickle_data = pickle.dumps(self.G.G, protocol=pickle.HIGHEST_PROTOCOL)

        if self.is_local:
            with open(path, "wb") as file:
                file.write(pickle_data)

        # Increment step and reset logs
        self.step += 1
        self.logs = []
        self.logger.info(
            f"Saved state to {'local' if self.is_local else 'GCS'} at {path}"
        )

    def log(self, log: str) -> None:
        self.logger.info(log)
        self.logs.append(html.P([log]))

    def log_dict(self, log: str, dic: Any) -> None:
        self.logger.info(log)
        self.logger.info(dic)
        self.logs.append(
            html.Div(
                [
                    html.Details(
                        [
                            html.Summary(log),
                            html.Div(
                                [
                                    html.P(f" - {key} : {value}")
                                    for key, value in dic.items()
                                ]
                            ),
                        ],
                        style={
                            "color": "var(--text-secondary)",
                            "font-size": "var(--text-size-02)",
                            "font-weight": "var(--text-weight-regular)",
                            "letter-spacing": "var(--letter-spacing-body-ui-02)",
                            "line-height": "var(--text-size-03)",
                        },
                    ),
                ],
            )
        )
