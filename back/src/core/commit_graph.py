import uuid
from typing import TYPE_CHECKING, Any

from git import Repo
from rq import get_current_job
from utils.process_pickle_files import process_pickle_files
from visualize.observer import Observer

from core.changing_graph.changing_graph import ChangingGraph
from core.commit.commit_edits import commit_edits
from core.commit.conflict_handler import (
    ConflictHandler,
    create_openai_conflict_handler,
)
from core.custom_types import Commit
from core.modifyle.modifyle import IModifyle, Modifyle

if TYPE_CHECKING:
    from core.custom_types import (
        Edits,
        SolutionNode,
    )


def commit_graph(
    G: ChangingGraph,
    file_modifier: IModifyle,
    observer: Observer,
    conflict_handler: ConflictHandler,
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

        if node["node_type"] == "solution":
            if node["status"] != "handled":
                observer.log(
                    f"Removing node {node['index']} because of status {node['status']}"
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

    edits_list: list[Edits] = [node["edits"] for node in list_of_solution_nodes]

    observer.log("Got list of all edits, committing the changes one by one")

    commit_edits(
        repo, edits_list, base_branch_name, file_modifier, conflict_handler, observer
    )

    observer.save_graph_state()


def run_commit_graph(
    iteration_name: str,
    project_name: str,
    commit: Commit,
    base_path: str,
    is_local: bool,
) -> None:
    job = get_current_job()
    job_id = str(uuid.uuid4())
    if job is not None:
        job_id = job.id

    graphs = process_pickle_files(f"{base_path}/{iteration_name}/", is_local)

    file_modifier: IModifyle = Modifyle()

    G = ChangingGraph(graphs[-1])

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id=job_id,
        step=len(graphs),
        is_local=is_local,
    )

    conflict_handler = create_openai_conflict_handler()

    commit_graph(G, file_modifier, observer, conflict_handler, commit)


def run_commit_graph_from_config(config: dict[str, Any], is_local: bool) -> None:
    run_commit_graph(
        config["iteration_name"],
        config["project_name"],
        config["commit"],
        config["base_path"],
        is_local,
    )
