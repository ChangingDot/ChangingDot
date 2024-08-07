import uuid
from typing import TYPE_CHECKING

from changing_dot_visualize.observer import Observer

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import InitialChange, Initialization, RestrictionOptions
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.error_manager import (
    IErrorManager,
    RoslynErrorManager,
)
from changing_dot.handle_node import handle_node
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    create_openai_interpreter,
)
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    IInstructionManagerBlock,
    create_openai_instruction_manager,
)
from changing_dot.modifyle.modifyle_block import IModifyle, IntegralModifyle
from changing_dot.utils.file_utils import get_csharp_files

if TYPE_CHECKING:
    from changing_dot.custom_types import ErrorInitialization
    from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
        BlockInstructionManager,
    )


def run_create_graph(
    iteration_name: str,
    project_name: str,
    goal: str,
    solution_path: str,
    restriction_options: RestrictionOptions,
    initial_change: InitialChange,
    is_local: bool,
) -> None:
    job_id = str(uuid.uuid4())

    instruction_manager: BlockInstructionManager = create_openai_instruction_manager(
        goal
    )

    error_manager = RoslynErrorManager(solution_path, restriction_options)

    file_modifier: IModifyle = IntegralModifyle()

    G = ChangingGraph()

    DG = DependencyGraph(get_csharp_files(solution_path))

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id,
        is_local=is_local,
    )

    interpreter = create_openai_interpreter(observer)

    initialisation: ErrorInitialization = {
        "init_type": "error",
        "initial_error": initial_change.error,
        "initial_file_path": initial_change.file_path,
        "initial_error_position": initial_change.error_position,
    }

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


def create_graph(
    G: ChangingGraph,
    DG: DependencyGraph,
    initialization: Initialization,
    error_manager: IErrorManager,
    instruction_manager: IInstructionManagerBlock,
    interpreter: IBlockInstructionInterpreter,
    file_modifier: IModifyle,
    observer: Observer,
    restriction_options: RestrictionOptions,
) -> None:
    if initialization["init_type"] == "error":
        # Check we are in a correct state
        compile_errors = error_manager.get_compile_errors([], observer)
        assert len(compile_errors) == 0

        G.add_problem_node(
            {
                "index": -1,
                "node_type": "problem",
                "status": "pending",
                "error": {
                    "text": initialization["initial_error"],
                    "file_path": initialization["initial_file_path"],
                    "pos": initialization["initial_error_position"],
                    "project_name": "Initial project",
                },
            }
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
            G.get_shortest_distance(0, node_index),
            file_modifier,
            observer,
            error_manager,
            interpreter,
            instruction_manager,
            restriction_options,
        )

        pending_nodes = G.get_all_pending_nodes()

    file_modifier.revert_change(DG)

    observer.log("Finished")
