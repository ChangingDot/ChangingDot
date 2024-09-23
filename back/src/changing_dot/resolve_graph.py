import os
import uuid
from typing import TYPE_CHECKING, Literal

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import (
    AnalyzerOptions,
    InitialResolveNode,
    RestrictionOptions,
)
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    create_dependency_graph_from_folder,
)
from changing_dot.error_manager.error_manager import IErrorManager
from changing_dot.error_manager.mypy_error_manager import MypyErrorManager
from changing_dot.error_manager.roslyn_error_manager import RoslynErrorManager
from changing_dot.handle_node import handle_node
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    create_instruction_interpreter,
)
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    IInstructionManagerBlock,
    create_instruction_manager,
)
from changing_dot.modifyle.modifyle import IModifyle, IntegralModifyle
from changing_dot.optimize_graph import optimize_graph

if TYPE_CHECKING:
    from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
        BlockInstructionManager,
    )


def run_resolve_graph(
    iteration_name: str,
    project_name: str,
    goal: str,
    output_path: str,
    restriction_options: RestrictionOptions,
    analyzer_options: AnalyzerOptions,
    llm_provider: Literal["OPENAI", "MISTRAL"],
) -> None:
    job_id = str(uuid.uuid4())

    instruction_manager: BlockInstructionManager = create_instruction_manager(
        goal, llm_provider
    )

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

    G = ChangingGraph()

    DG = create_dependency_graph_from_folder(
        folder_to_analyse, analyzer_options.language
    )

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id,
        output_path,
    )

    interpreter = create_instruction_interpreter(observer, llm_provider)

    resolve_graph(
        G,
        DG,
        error_manager,
        instruction_manager,
        interpreter,
        file_modifier,
        observer,
        restriction_options,
    )


def resolve_graph(
    G: ChangingGraph,
    DG: DependencyGraph,
    error_manager: IErrorManager,
    instruction_manager: IInstructionManagerBlock,
    interpreter: IBlockInstructionInterpreter,
    file_modifier: IModifyle,
    observer: Observer,
    restriction_options: RestrictionOptions,
) -> None:
    G.add_initial_resolve_node(
        InitialResolveNode(
            index=-1,
            node_type="initial_resolve",
            status="pending",
            repo_path=os.getcwd(),
        )
    )

    # while some nodes are pending
    pending_nodes = G.get_all_pending_nodes()
    observer.log(f"Continuing on all {len(pending_nodes)} next nodes")

    while len(pending_nodes) > 0:
        node_index = pending_nodes[0]

        handle_node(
            G,
            DG,
            node_index,
            file_modifier,
            observer,
            error_manager,
            interpreter,
            instruction_manager,
        )

        pending_nodes = G.get_all_pending_nodes()

    optimize_graph(G, observer)

    observer.log("Finished")
