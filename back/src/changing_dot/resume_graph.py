import uuid
from typing import TYPE_CHECKING, Literal

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.commit.reset_repo import set_repo
from changing_dot.custom_types import Commit, RestrictionOptions, ResumeInitialNode
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.error_manager import (
    RoslynErrorManager,
)
from changing_dot.handle_node import resume_problem_node
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    create_interpreter,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    create_instruction_manager,
)
from changing_dot.modifyle.modifyle import IntegralModifyle
from changing_dot.utils.file_utils import get_csharp_files
from changing_dot.utils.process_pickle_files import process_pickle_files

if TYPE_CHECKING:
    from changing_dot.custom_types import ProblemNode
    from changing_dot.modifyle.modifyle import IModifyle


def run_resume_graph(
    iteration_name: str,
    project_name: str,
    solution_path: str,
    goal: str,
    base_path: str,
    commit: Commit,
    restriction_options: RestrictionOptions,
    resume_initial_node: ResumeInitialNode,
    llm_provider: Literal["OPENAI", "MISTRAL"],
    is_local: bool = True,
) -> None:
    set_repo(commit)

    job_id = str(uuid.uuid4())

    instruction_manager = create_instruction_manager(goal, llm_provider)

    graphs = process_pickle_files(f"{base_path}/{iteration_name}/", is_local)

    error_manager = RoslynErrorManager(solution_path, restriction_options)

    file_modifier: IModifyle = IntegralModifyle()

    G = ChangingGraph(graphs[-1])

    DG = DependencyGraph(get_csharp_files(solution_path))

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id=job_id,
        is_local=is_local,
        step=len(graphs),
    )

    interpreter = create_interpreter(observer, llm_provider)

    node: ProblemNode = {
        "index": resume_initial_node.index,
        "node_type": "problem",
        "status": "pending",
        "error": resume_initial_node.error,
    }

    resume_problem_node(
        G,
        DG,
        node["index"],
        node,
        resume_initial_node.new_instruction,
        resume_initial_node.new_edits,
        error_manager,
        instruction_manager,
        interpreter,
        file_modifier,
        observer,
        restriction_options,
    )
