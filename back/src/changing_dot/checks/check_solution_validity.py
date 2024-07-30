from typing import TYPE_CHECKING

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import CompileError, Edits, SolutionNode
from changing_dot.error_manager.error_manager import (
    IErrorManager,
)
from changing_dot.modifyle.modifyle import IModifyle, applied_edits_context
from changing_dot_visualize.observer import Observer

if TYPE_CHECKING:
    from changing_dot.custom_types import ProblemNode


def get_consecutive_errors(
    error: CompileError, compile_errors: list[CompileError]
) -> list[CompileError]:
    i = 1
    consecutive_errors = [error]
    found_next_error = True
    while found_next_error:
        next_error = error.copy()
        next_error["pos"] = (
            next_error["pos"][0] + i,
            next_error["pos"][1],
            next_error["pos"][2] + i,
            next_error["pos"][3],
        )

        if next_error in compile_errors:
            consecutive_errors.append(next_error)
            i += 1
        else:
            found_next_error = False

    return consecutive_errors


def is_error_removed(
    compile_error: CompileError,
    compile_errors: list[CompileError],
    G: ChangingGraph,
    solution_that_caused_error: SolutionNode,
) -> bool:
    is_error_removed = compile_error not in compile_errors

    if not is_error_removed:
        # check for a special edge case where
        # we can have the same error on consecutive lines
        # and the edit is remove line
        # then the errors slide up 1 and are never fixed
        # ex : import a from B; import b from B; import c from B;
        # On all lines error is B does not exist
        # To fix line 1 we do remove line 1
        # But we get the same error on line 1 after that
        # With error on line 3 being removed
        children_node_indexes = G.get_children(solution_that_caused_error["index"])

        children_nodes: list[ProblemNode] = [
            G.get_node(i)  # type: ignore
            for i in children_node_indexes
            if G.get_node(i)["node_type"] == "problem"
        ]

        all_solution_errors = [node["error"] for node in children_nodes]

        previous_consecutive_errors = get_consecutive_errors(
            compile_error, all_solution_errors
        )
        now_consecutive_errors = get_consecutive_errors(compile_error, compile_errors)

        # was on error removed ?
        return len(previous_consecutive_errors) == len(now_consecutive_errors) + 1

    return is_error_removed


def check_solution_validity(
    G: ChangingGraph,
    solution_node: SolutionNode,
    problem_node_index: int,
    file_modifier: IModifyle,
    error_manager: IErrorManager,
    observer: Observer,
) -> bool:
    problem_node = G.get_node(problem_node_index)
    assert problem_node["node_type"] == "problem"

    solution_that_caused_error_list = G.get_parent_nodes(problem_node_index)

    if len(solution_that_caused_error_list) == 0:
        # TODO maybe still need to do a check
        assert problem_node_index == 0
        return True

    result = True
    for solution_that_caused_error_index in solution_that_caused_error_list:
        # if result is false, then no need to continue
        if result:
            solution_that_caused_error = G.get_node(solution_that_caused_error_index)

            assert solution_that_caused_error["node_type"] == "solution"

            all_edits = [*solution_that_caused_error["edits"], *solution_node["edits"]]

            file_modifier.apply_change(all_edits)

            compile_errors = error_manager.get_compile_errors(
                [edit["file_path"] for edit in all_edits], observer
            )

            file_modifier.revert_change(all_edits)

            result = result and is_error_removed(
                problem_node["error"], compile_errors, G, solution_that_caused_error
            )

    return result


def simple_check_solution_validity(
    G: ChangingGraph,
    problem_node_index: int,
    edits: Edits,
    error_manager: IErrorManager,
    observer: Observer,
) -> bool:
    problem_node = G.get_node(problem_node_index)
    assert problem_node["node_type"] == "problem"
    # TODO [] does not make it work with omnisharp errormanager
    with applied_edits_context(edits):
        compile_errors = error_manager.get_compile_errors([], observer)

    return problem_node["error"] not in compile_errors