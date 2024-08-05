import os
import uuid

import yaml
from analytics.wandb_analytics import WandbAnalytics
from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.commit.conflict_handler import (
    create_openai_conflict_handler,
)
from changing_dot.commit.reset_repo import reset_repo, set_repo
from changing_dot.commit_graph import commit_graph
from changing_dot.create_graph import create_graph
from changing_dot.custom_types import ErrorInitialization
from changing_dot.error_manager.error_manager import (
    RoslynErrorManager,
)
from changing_dot.instruction_interpreter.basic_instruction_interpreter import (
    create_openai_interpreter,
)
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IInstructionInterpreter,
)
from changing_dot.instruction_manager.basic_instruction_manager.basic_instruction_manager import (
    create_mistral_instruction_manager,
)
from changing_dot.modifyle.modifyle_block import IModifyle, IntegralModifyle
from changing_dot.optimize_graph import optimize_graph
from changing_dot_visualize.observer import Observer

if __name__ == "__main__":
    analytics = WandbAnalytics()

    folder_path = "src/scripts/benchmark_configs"

    for benchmark_config_file in os.listdir(folder_path):
        benchmark_item, _extension = os.path.splitext(benchmark_config_file)

        print(f"Handling {benchmark_item}")

        benchmark_config_file_path = os.path.join(folder_path, benchmark_config_file)

        with open(benchmark_config_file_path) as file:
            config = yaml.safe_load(file)

        with analytics.benchmark_item(benchmark_item) as current_benchmark_result:
            job_id = str(uuid.uuid4())

            instruction_manager = create_mistral_instruction_manager(config["goal"])

            restriction_options = config.get(
                "restriction_options",
                {
                    "restrict_change_to_single_file": None,
                    "restrict_to_project": None,
                    "project_blacklist": None,
                },
            )

            error_manager = RoslynErrorManager(
                config["solution_path"], restriction_options
            )

            file_modifier: IModifyle = IntegralModifyle()

            G = ChangingGraph()

            observer = Observer(G, analytics.run.name, benchmark_item, job_id)

            interpreter: IInstructionInterpreter = create_openai_interpreter(observer)

            initialisation: ErrorInitialization = {
                "init_type": "error",
                "initial_error": config["initial_change"]["error"],
                "initial_file_path": config["initial_change"]["file_path"],
                "initial_error_position": config["initial_change"]["error_position"],
            }

            try:
                set_repo(config["commit"])

                with analytics.changing_graph(G):
                    print(f"Running for {benchmark_item}")

                    create_graph(
                        G,
                        initialisation,
                        error_manager,
                        instruction_manager,
                        interpreter,
                        file_modifier,
                        observer,
                        restriction_options,
                    )

                if not current_benchmark_result["step_graph"]:
                    continue

                with analytics.optimize_graph(G):
                    print(f"Running optimize graph for {benchmark_item}")

                    optimize_graph(G, observer)

                if not current_benchmark_result["step_optimize"]:
                    continue

                with analytics.commit_graph(error_manager, observer):
                    print(f"Running commit graph for {benchmark_item}")

                    conflict_handler = create_openai_conflict_handler()

                    try:
                        commit_graph(
                            G,
                            file_modifier,
                            observer,
                            conflict_handler,
                            config["commit"],
                        )
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)

        reset_repo(config["commit"])
