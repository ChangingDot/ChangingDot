import uuid
from typing import TYPE_CHECKING, Literal

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.commit.reset_repo import set_repo
from changing_dot.custom_types import (
    AnalyzerOptions,
    Commit,
    ProblemNode,
    RestrictionOptions,
    ResumeInitialNode,
)
from changing_dot.dependency_graph.dependency_graph import (
    create_dependency_graph_from_folder,
)
from changing_dot.error_manager.mypy_error_manager import MypyErrorManager
from changing_dot.error_manager.roslyn_error_manager import (
    RoslynErrorManager,
)
from changing_dot.handle_node import resume_problem_node
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    create_instruction_interpreter,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    create_instruction_manager,
)
from changing_dot.modifyle.modifyle import IntegralModifyle
from changing_dot.optimize_graph import optimize_graph
from changing_dot.utils.process_pickle_files import process_pickle_files

if TYPE_CHECKING:
    from changing_dot.error_manager.error_manager import IErrorManager
    from changing_dot.modifyle.modifyle import IModifyle


def run_resume_graph(
    iteration_name: str,
    project_name: str,
    goal: str,
    output_path: str,
    commit: Commit,
    restriction_options: RestrictionOptions,
    resume_initial_node: ResumeInitialNode,
    analyzer_options: AnalyzerOptions,
    llm_provider: Literal["OPENAI", "MISTRAL"],
) -> None:
    set_repo(commit)

    job_id = str(uuid.uuid4())

    instruction_manager = create_instruction_manager(goal, llm_provider)

    graphs = process_pickle_files(f"{output_path}/{iteration_name}/")

    error_manager: IErrorManager
    folder_to_analyse: str
    if analyzer_options.name == "mypy":
        error_manager = MypyErrorManager(
            analyzer_options.folder_path,
            analyzer_options.requirements_path,
            restriction_options,
        )
        folder_to_analyse = analyzer_options.folder_path
    if analyzer_options.name == "roslyn":
        error_manager = RoslynErrorManager(
            analyzer_options.solution_path, restriction_options
        )
        folder_to_analyse = analyzer_options.solution_path

    file_modifier: IModifyle = IntegralModifyle()

    G = ChangingGraph(graphs[-1])

    DG = create_dependency_graph_from_folder(
        folder_to_analyse, analyzer_options.language
    )

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id=job_id,
        output_folder=output_path,
        step=len(graphs),
    )

    interpreter = create_instruction_interpreter(observer, llm_provider)

    node = ProblemNode(
        index=resume_initial_node.index,
        node_type="problem",
        status="pending",
        error=resume_initial_node.error,
    )

    resume_problem_node(
        G,
        DG,
        node.index,
        node,
        resume_initial_node.new_instruction,
        resume_initial_node.new_edits,
        error_manager,
        instruction_manager,
        interpreter,
        file_modifier,
        observer,
    )

    optimize_graph(G, observer)

    observer.log("Finished")
