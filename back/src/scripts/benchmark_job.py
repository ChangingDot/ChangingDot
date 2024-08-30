import uuid
from typing import TYPE_CHECKING, Literal

from analytics.wandb_analytics import WandbAnalytics
from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.commit.conflict_handler import (
    create_openai_conflict_handler,
)
from changing_dot.commit.reset_repo import reset_repo, set_repo
from changing_dot.commit_graph import commit_graph
from changing_dot.create_graph import create_graph
from changing_dot.custom_types import (
    Commit,
    ErrorInitialization,
    InitialChange,
    RestrictionOptions,
)
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.roslyn_error_manager import RoslynErrorManager
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    create_instruction_interpreter,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    create_instruction_manager,
)
from changing_dot.modifyle.modifyle import IModifyle, IntegralModifyle
from changing_dot.optimize_graph import optimize_graph
from changing_dot.utils.file_utils import get_csharp_files
from changing_dot_visualize.observer import Observer
from loguru import logger

if TYPE_CHECKING:
    from changing_dot.instruction_interpreter.instruction_interpreter import (
        IBlockInstructionInterpreter,
    )
    from changing_dot.modifyle.modifyle import IModifyle


def benchmark_job(
    iteration_name: str,
    project_name: str,
    solution_path: str,
    goal: str,
    initial_change: InitialChange,
    commit: Commit,
    llm_provider: Literal["OPENAI", "MISTRAL"],
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

    instruction_manager = create_instruction_manager(goal, llm_provider)

    error_manager = RoslynErrorManager(solution_path, restriction_options)

    for i in range(number_of_runs):
        file_modifier: IModifyle = IntegralModifyle()

        G = ChangingGraph()

        DG = DependencyGraph(get_csharp_files(solution_path))

        benchmark_item = f"{project_name}_{i}"

        logger.info(f"Handling {benchmark_item}")

        with analytics.benchmark_item(benchmark_item) as current_benchmark_result:
            job_id = str(uuid.uuid4())

            observer = Observer(
                G, analytics.run.name, benchmark_item, "./outputs", job_id
            )

            interpreter: IBlockInstructionInterpreter = create_instruction_interpreter(
                observer, llm_provider
            )

            initialisation = ErrorInitialization(
                init_type="error",
                initial_error=initial_change.error,
                initial_file_path=initial_change.file_path,
                initial_error_position=initial_change.error_position,
            )

            try:
                set_repo(commit)

                with analytics.changing_graph(G):
                    logger.info(f"Running for {benchmark_item}")

                    create_graph(
                        G,
                        DG,
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
