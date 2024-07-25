import uuid
from typing import TYPE_CHECKING

from visualize.observer import Observer

from core.changing_graph.changing_graph import ChangingGraph
from core.custom_types import InitialChange, Initialization, RestrictionOptions
from core.error_manager.error_manager import (
    IErrorManager,
    RoslynErrorManager,
)
from core.handle_node import handle_node
from core.instruction_interpreter.basic_instruction_interpreter import (
    create_openai_interpreter,
)
from core.instruction_interpreter.instruction_interpreter import (
    IInstructionInterpreter,
)
from core.instruction_manager.basic_instruction_manager.basic_instruction_manager import (
    create_mistral_instruction_manager,
)
from core.instruction_manager.instruction_manager import IInstructionManager
from core.modifyle.modifyle import IModifyle, IntegralModifyle

if TYPE_CHECKING:
    from core.custom_types import ErrorInitialization


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

    instruction_manager = create_mistral_instruction_manager(goal)

    error_manager = RoslynErrorManager(solution_path, restriction_options)

    file_modifier: IModifyle = IntegralModifyle()

    G = ChangingGraph()

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id,
        is_local=is_local,
    )

    interpreter: IInstructionInterpreter = create_openai_interpreter(observer)

    initialisation: ErrorInitialization = {
        "init_type": "error",
        "initial_error": initial_change.error,
        "initial_file_path": initial_change.file_path,
        "initial_error_position": initial_change.error_position,
    }

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


def create_graph(
    G: ChangingGraph,
    initialization: Initialization,
    error_manager: IErrorManager,
    instruction_manager: IInstructionManager,
    interpreter: IInstructionInterpreter,
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

    file_modifier.revert_change([])

    observer.log("Finished")
