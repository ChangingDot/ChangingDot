import uuid
from typing import TYPE_CHECKING

from analytics.wandb_analytics import WandbAnalytics
from core.changing_graph.changing_graph import ChangingGraph
from core.commit.conflict_handler import (
    create_openai_conflict_handler,
)
from core.commit.reset_repo import reset_repo, set_repo
from core.commit_graph import commit_graph
from core.create_graph import create_graph
from core.custom_types import (
    Commit,
    ErrorInitialization,
    InitialChange,
    RestrictionOptions,
)
from core.error_manager.error_manager import (
    RoslynErrorManager,
)
from core.instruction_interpreter.basic_instruction_interpreter import (
    create_openai_interpreter,
)
from core.instruction_interpreter.instruction_interpreter import (
    IInstructionInterpreter,
)
from core.instruction_manager.basic_instruction_manager.basic_instruction_manager import (
    create_mistral_instruction_manager,
)
from core.modifyle.modifyle import IModifyle, IntegralModifyle
from core.optimize_graph import optimize_graph
from loguru import logger
from visualize.observer import Observer

if TYPE_CHECKING:
    from core.custom_types import ErrorInitialization
    from core.instruction_interpreter.instruction_interpreter import (
        IInstructionInterpreter,
    )
    from core.modifyle.modifyle import IModifyle


def benchmark_job(
    iteration_name: str,
    project_name: str,
    solution_path: str,
    goal: str,
    initial_change: InitialChange,
    commit: Commit,
    restriction_options: RestrictionOptions | None = None,
) -> None:
    analytics = WandbAnalytics()

    number_of_runs = 3

    restriction_options = (
        restriction_options
        if restriction_options is not None
        else RestrictionOptions(
            restrict_change_to_single_file=None,
            restrict_to_project=None,
            project_blacklist=None,
        )
    )

    instruction_manager = create_mistral_instruction_manager(goal)

    error_manager = RoslynErrorManager(solution_path, restriction_options)

    for i in range(number_of_runs):
        file_modifier: IModifyle = IntegralModifyle()

        G = ChangingGraph()

        benchmark_item = f"{project_name}_{i}"

        logger.info(f"Handling {benchmark_item}")

        with analytics.benchmark_item(benchmark_item) as current_benchmark_result:
            job_id = str(uuid.uuid4())

            observer = Observer(G, analytics.run.name, benchmark_item, job_id)

            interpreter: IInstructionInterpreter = create_openai_interpreter(observer)

            initialisation: ErrorInitialization = {
                "init_type": "error",
                "initial_error": initial_change.error,
                "initial_file_path": initial_change.file_path,
                "initial_error_position": initial_change.error_position,
            }

            try:
                set_repo(commit)

                with analytics.changing_graph(G):
                    logger.info(f"Running for {benchmark_item}")

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
                    logger.info(f"Running optimize for {benchmark_item}")

                    optimize_graph(G, observer)

                if not current_benchmark_result["step_optimize"]:
                    continue

                with analytics.commit_graph(error_manager, observer):
                    logger.info(f"Running commit graph for {benchmark_item}")

                    conflict_handler = create_openai_conflict_handler()

                    try:
                        commit_graph(
                            G,
                            file_modifier,
                            observer,
                            conflict_handler,
                            commit,
                        )
                    except Exception as e:
                        logger.error(e)

            except Exception as e:
                logger.error(e)

        reset_repo(commit)
