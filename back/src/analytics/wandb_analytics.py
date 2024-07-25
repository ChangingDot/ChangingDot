from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from typing import TypedDict

import pandas as pd
import wandb
from core.changing_graph.changing_graph import ChangingGraph
from core.error_manager.error_manager import IErrorManager
from dotenv import load_dotenv
from loguru import logger
from visualize.observer import Observer
from wandb.sdk.wandb_run import Run


class ItemResult(TypedDict, total=False):
    name: str
    path_to_graph: str
    # graph
    step_graph: bool
    step_graph_number_of_problem_nodes: int
    step_graph_number_of_errors: int
    step_graph_number_of_solution_nodes: int
    step_graph_duration: float
    # optimize
    step_optimize: bool
    step_optimize_number_of_problem_nodes: int
    step_optimize_number_of_errors: int
    step_optimize_number_of_solution_nodes: int
    step_optimize_duration: float
    # commit
    step_commit: bool
    step_commit_duration: float
    is_build_fixed: bool


class WandbAnalytics:
    item_results: list[ItemResult]
    run: Run
    current_item_result: ItemResult

    def __init__(self) -> None:
        load_dotenv()
        wandb.login()
        self.run = wandb.init(
            project="test",
            config={},
        )  # type: ignore
        self.item_results = []

    @contextmanager
    def benchmark_item(self, benchmark_item: str) -> Iterator[ItemResult]:
        self.current_item_result = {
            "name": benchmark_item,
            "step_graph": False,
            "step_optimize": False,
            "step_commit": False,
            "is_build_fixed": False,
        }
        yield self.current_item_result
        self.item_results.append(self.current_item_result)
        logger.info("Sending result to wandb")
        results = wandb.Table(dataframe=pd.DataFrame.from_records(self.item_results))
        wandb.log({"Results": results})

    @contextmanager
    def changing_graph(self, G: ChangingGraph) -> Iterator[None]:
        start_time = datetime.now()
        yield
        end_time = datetime.now()
        node_type_dict = G.count_node_types()
        self.current_item_result["step_graph_number_of_problem_nodes"] = (
            node_type_dict.get("problem", 0)
        )
        self.current_item_result["step_graph_number_of_solution_nodes"] = (
            node_type_dict.get("solution", 0)
        )
        self.current_item_result["step_graph_number_of_errors"] = node_type_dict.get(
            "error_solution", 0
        ) + node_type_dict.get("error_problem", 0)
        self.current_item_result["step_graph_duration"] = (
            end_time - start_time
        ).total_seconds() / 60
        self.current_item_result["step_graph"] = (
            self.current_item_result["step_graph_number_of_errors"] == 0
        )

    @contextmanager
    def optimize_graph(self, G: ChangingGraph) -> Iterator[None]:
        start_time = datetime.now()
        yield
        end_time = datetime.now()
        node_type_dict = G.count_node_types()
        self.current_item_result["step_optimize"] = True
        self.current_item_result["step_optimize_number_of_problem_nodes"] = (
            node_type_dict.get("problem", 0)
        )
        self.current_item_result["step_optimize_number_of_solution_nodes"] = (
            node_type_dict.get("solution", 0)
        )
        self.current_item_result["step_optimize_number_of_errors"] = node_type_dict.get(
            "error_solution", 0
        ) + node_type_dict.get("error_problem", 0)
        self.current_item_result["step_optimize_duration"] = (
            end_time - start_time
        ).total_seconds() / 60

    @contextmanager
    def commit_graph(
        self, error_manager: IErrorManager, observer: Observer
    ) -> Iterator[None]:
        start_time = datetime.now()
        yield
        end_time = datetime.now()
        errors = error_manager.get_compile_errors([], observer)
        self.current_item_result["is_build_fixed"] = len(errors) == 0
        self.current_item_result["step_commit"] = True
        self.current_item_result["step_commit_duration"] = (
            end_time - start_time
        ).total_seconds() / 60
