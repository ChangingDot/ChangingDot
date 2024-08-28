import traceback

from changing_dot_visualize.observer import Observer

from changing_dot.apply_graph_changes import apply_graph_changes
from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.checks.check_solution_syntax_correctness import (
    check_solution_syntax_correctness,
)
from changing_dot.checks.check_solution_validity import (
    simple_check_solution_validity_block,
)
from changing_dot.custom_types import (
    BlockEdit,
    ErrorProblemNode,
    Instruction,
    ProblemNode,
    RestrictionOptions,
    SolutionNode,
)
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.error_manager import (
    IErrorManager,
)
from changing_dot.instruction_interpreter.hard_coded_instruction_interpreter import (
    HardCodedInstructionInterpreter,
)
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    IInstructionManagerBlock,
)
from changing_dot.instruction_manager.hard_coded_instruction_manager import (
    HardCodedInstructionManager,
)
from changing_dot.modifyle.modifyle import IModifyle


def get_solution_node_from_problem(
    G: ChangingGraph,
    DG: DependencyGraph,
    node_index: int,
    instruction_manager: IInstructionManagerBlock,
    interpreter: IBlockInstructionInterpreter,
    observer: Observer,
) -> SolutionNode | ErrorProblemNode:
    # Initializing for exept block
    instruction = None
    edits = None

    node = G.get_problem_node(node_index)

    try:
        instruction = instruction_manager.get_node_instruction(G, DG, node_index)

        observer.log_dict("used instruction : ", instruction)

        edit = interpreter.get_edit_from_instruction(instruction, DG)

        observer.log_dict("got edit :", edit)

        return SolutionNode(
            index=-1,
            node_type="solution",
            status="pending",
            instruction=instruction,
            edits=[edit],
        )

    except Exception as e:
        observer.log(f"Encountered error {e}\n{traceback.format_exc()}")
        return ErrorProblemNode(
            index=node_index,
            node_type="error_problem",
            status=node.status,
            error=node.error,
            error_text=f"{e}",
            suspected_instruction=instruction,
            suspected_edits=edits,
        )


def handle_problem_node(
    G: ChangingGraph,
    DG: DependencyGraph,
    problem_node_index: int,
    instruction_manager: IInstructionManagerBlock,
    interpreter: IBlockInstructionInterpreter,
    file_modifier: IModifyle,
    error_manager: IErrorManager,
    observer: Observer,
) -> None:
    solution_node_or_error = get_solution_node_from_problem(
        G, DG, problem_node_index, instruction_manager, interpreter, observer
    )

    if solution_node_or_error.node_type == "error_problem":
        error = solution_node_or_error
        G.error_on_problem_node(error)
        return

    solution_node = solution_node_or_error

    is_solution_syntactically_correct = check_solution_syntax_correctness(
        DG, solution_node.edits, error_manager
    )

    observer.log(
        f"Is solution syntactically valid : {is_solution_syntactically_correct}"
    )

    does_solution_fix_problem = simple_check_solution_validity_block(
        G, DG, problem_node_index, solution_node.edits, error_manager, observer
    )

    observer.log(f"Does solution fix problem : {does_solution_fix_problem}")

    is_solution_valid = does_solution_fix_problem and is_solution_syntactically_correct

    observer.log(f"Is solution valid : {is_solution_valid}")

    while not is_solution_valid:
        solution_node.status = "failed"
        failed_node_index = G.add_solution_node(solution_node)
        G.add_edge(problem_node_index, failed_node_index)
        # try again
        observer.log(
            f"Added failed node {failed_node_index}, trying to handle {problem_node_index} again"
        )
        new_solution_node_or_error = get_solution_node_from_problem(
            G, DG, problem_node_index, instruction_manager, interpreter, observer
        )
        if new_solution_node_or_error.node_type == "error_problem":
            error = new_solution_node_or_error
            G.error_on_problem_node(error)
            return

        solution_node = new_solution_node_or_error

        is_solution_valid = simple_check_solution_validity_block(
            G,
            DG,
            problem_node_index,
            solution_node.edits,
            error_manager,
            observer,
        ) and check_solution_syntax_correctness(DG, solution_node.edits, error_manager)

    # Solution is now valid and can be added

    solution_node.status = "handled"
    file_modifier.apply_change(DG, solution_node.edits)

    new_solution_index = G.add_solution_node(solution_node)

    pending_problem_nodes = G.get_all_pending_problem_nodes()

    # connect all other problems that were solved
    current_compile_errors = error_manager.get_compile_errors(observer)

    existing_compile_errors = [node.error for node in pending_problem_nodes]

    for problem_node in pending_problem_nodes:
        if problem_node.error not in current_compile_errors:
            # problem was fixed by solution
            G.add_edge(problem_node.index, new_solution_index)
            G.mark_node_as(problem_node.index, "handled")
            observer.log(
                f"Solved problem {problem_node.index}, connecting it to {new_solution_index}"
            )

    for compile_error in current_compile_errors:
        if compile_error not in existing_compile_errors:
            # new problem
            new_problem_index = G.add_problem_node(
                ProblemNode(
                    index=-1,
                    node_type="problem",
                    status="pending",
                    error=compile_error,
                )
            )
            G.add_edge(new_solution_index, new_problem_index)
            observer.log(f"New problem -> Added new node {new_problem_index}")

    G.mark_node_as(problem_node_index, "handled")


def handle_node(
    G: ChangingGraph,
    DG: DependencyGraph,
    node_index: int,
    i: int,
    file_modifier: IModifyle,
    observer: Observer,
    error_manager: IErrorManager,
    interpreter: IBlockInstructionInterpreter,
    instruction_manager: IInstructionManagerBlock,
    restriction_options: RestrictionOptions,
) -> None:
    node = G.get_node(node_index)

    if node.node_type == "solution":
        assert True is False

    elif node.node_type == "problem":
        observer.log(f"Handling problem node {node_index}")
        handle_problem_node(
            G,
            DG,
            node_index,
            instruction_manager,
            interpreter,
            file_modifier,
            error_manager,
            observer,
        )

    observer.save_graph_state()


def resume_problem_node(
    G: ChangingGraph,
    DG: DependencyGraph,
    node_index: int,
    new_node: ProblemNode,
    new_instruction: Instruction | None,
    new_edits: list[BlockEdit] | None,
    error_manager: IErrorManager,
    instruction_manager: IInstructionManagerBlock,
    interpreter: IBlockInstructionInterpreter,
    file_modifier: IModifyle,
    observer: Observer,
    restriction_options: RestrictionOptions,
) -> None:
    assert (
        G.get_node(node_index).node_type == "error_problem"
        or G.get_node(node_index).node_type == "problem"
    )

    # Check we are in a correct state
    compile_errors = error_manager.get_compile_errors(observer)
    assert len(compile_errors) == 0

    G.update_problem_node(new_node)

    for child_index in G.get_children(new_node.index):
        G.remove_node(child_index)

    apply_graph_changes(G, DG, file_modifier, observer)

    observer.log_dict(
        f"Starting modification : Changing Node {node_index} to", new_node
    )

    if new_edits is not None and new_instruction is not None:
        observer.log_dict("We have new edits", new_edits)
        handle_problem_node(
            G,
            DG,
            node_index,
            HardCodedInstructionManager(new_instruction),
            # TODO we do not yet handle multiple edits
            HardCodedInstructionInterpreter(new_edits[0]),
            file_modifier,
            error_manager,
            observer,
        )
        observer.save_graph_state()

    if new_edits is None and new_instruction is not None:
        observer.log_dict("We have new instruction", new_instruction)
        handle_problem_node(
            G,
            DG,
            node_index,
            HardCodedInstructionManager(new_instruction),
            interpreter,
            file_modifier,
            error_manager,
            observer,
        )
        observer.save_graph_state()

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

    file_modifier.revert_changes(DG)

    observer.log("Finished modification")
