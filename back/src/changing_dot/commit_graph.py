from typing import TYPE_CHECKING, Any, cast

from changing_dot_visualize.observer import Observer
from git import Repo

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.commit.commit_edits import commit_edits
from changing_dot.commit.conflict_handler import (
    IConflictHandler,
    create_openai_conflict_handler,
)
from changing_dot.custom_types import Commit, SolutionNode
from changing_dot.modifyle.modifyle import IModifyle, IntegralModifyle
from changing_dot.utils.process_pickle_files import process_pickle_files

if TYPE_CHECKING:
    from changing_dot.custom_types import (
        BlockEdit,
    )


def commit_graph(
    G: ChangingGraph,
    file_modifier: IModifyle,
    observer: Observer,
    conflict_handler: IConflictHandler,
    commit: Commit,
) -> None:
    ### Commit logic
    repo = Repo(commit.git_path)

    base_branch_name = commit.branch_name
    leaves = G.get_leaves()

    observer.log("Starting to commit")

    list_of_solution_nodes: list[SolutionNode] = []

    while len(leaves) > 0:
        leaf = leaves.pop()

        node = G.get_node(leaf)

        if node.node_type == "solution":
            node = cast(SolutionNode, node)
            if node.status != "handled":
                observer.log(
                    f"Removing node {node.index} because of status {node.status}"
                )
                G.remove_node(leaf)
                continue

            observer.log(f"adding solution {leaf} to commits to apply")

            list_of_solution_nodes.append(node)

        observer.log(f"Removed from graph node {leaf}")
        G.remove_node(leaf)
        leaves = G.get_leaves()

    # If this assertion is false then it means that
    # there is part of the graph that we can't commit
    assert G.get_number_of_nodes() == 0

    edits_list: list[list[BlockEdit]] = [node.edits for node in list_of_solution_nodes]

    observer.log("Got list of all edits, committing the changes one by one")

    commit_edits(
        repo, edits_list, base_branch_name, file_modifier, conflict_handler, observer
    )

    observer.save_graph_state()


def run_commit_graph(
    iteration_name: str,
    commit: Commit,
    output_path: str,
) -> None:
    graphs = process_pickle_files(f"{output_path}/{iteration_name}/")

    file_modifier: IModifyle = IntegralModifyle()

    G = ChangingGraph(graphs[-1])

    observer = Observer(
        G,
        iteration_name,
        output_folder=output_path,
        step=len(graphs),
    )

    conflict_handler = create_openai_conflict_handler()

    commit_graph(G, file_modifier, observer, conflict_handler, commit)


def run_commit_graph_from_config(config: dict[str, Any]) -> None:
    run_commit_graph(
        config["iteration_name"],
        config["commit"],
        config["output_path"],
    )
