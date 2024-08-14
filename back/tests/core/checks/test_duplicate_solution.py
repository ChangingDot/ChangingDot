from typing import TYPE_CHECKING

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.checks.check_if_duplicate_solution import (
    check_if_duplicate_solution_block,
)
from changing_dot.custom_types import BlockEdit, InstructionBlock

if TYPE_CHECKING:
    from changing_dot.custom_types import SolutionNode


def test_no_duplicates_find_no_duplicates() -> None:
    G = ChangingGraph()
    G.add_problem_node(
        {
            "index": 0,
            "node_type": "problem",
            "status": "pending",
            "error": {
                "text": "This is Hello World, it is not original",
                "file_path": "./tests/core/checks/fixtures/basic_file.cs",
                "pos": (5, 0, 5, 0),
                "project_name": "Initial project",
            },
        }
    )

    solution_node: SolutionNode = {
        "index": 1,
        "node_type": "solution",
        "status": "pending",
        "instruction": InstructionBlock(
            block_id=1,
            file_path="./tests/core/checks/fixtures/basic_file.cs",
            solution="Do this original change",
        ),
        "edits": [
            BlockEdit(
                block_id=1,
                file_path="./tests/core/checks/fixtures/basic_file.cs",
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
    }

    assert check_if_duplicate_solution_block(G, solution_node) is None


def test_duplicates_find_no_duplicates() -> None:
    G = ChangingGraph()
    G.add_problem_node(
        {
            "index": 0,
            "node_type": "problem",
            "status": "pending",
            "error": {
                "text": "This is Hello World, it is not original",
                "file_path": "./tests/core/checks/fixtures/basic_file.cs",
                "pos": (5, 0, 5, 0),
                "project_name": "Initial project",
            },
        }
    )

    existing_solution_node: SolutionNode = {
        "index": 1,
        "node_type": "solution",
        "status": "pending",
        "instruction": InstructionBlock(
            block_id=1,
            file_path="./tests/core/checks/fixtures/basic_file.cs",
            solution="Do this original change",
        ),
        "edits": [
            BlockEdit(
                block_id=1,
                file_path="./tests/core/checks/fixtures/basic_file.cs",
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
    }

    G.add_solution_node(existing_solution_node)

    new_solution_node: SolutionNode = {
        "index": 12,
        "node_type": "solution",
        "status": "pending",
        "instruction": InstructionBlock(
            block_id=1,
            file_path="./tests/core/checks/fixtures/basic_file.cs",
            solution="Do this original change",
        ),
        "edits": [
            BlockEdit(
                block_id=1,
                file_path="./tests/core/checks/fixtures/basic_file.cs",
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
    }

    assert (
        check_if_duplicate_solution_block(G, new_solution_node)
        == existing_solution_node
    )
