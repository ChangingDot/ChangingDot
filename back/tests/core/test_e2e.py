import os
import pickle
import shutil
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.create_graph import create_graph
from changing_dot.custom_types import (
    InitialChange,
    RestrictionOptions,
    ResumeInitialNode,
)
from changing_dot.error_manager.error_manager import (
    HardCodedErrorManager,
)
from changing_dot.handle_node import resume_problem_node
from changing_dot.instruction_interpreter.hard_coded_instruction_interpreter import (
    HardCodedInstructionInterpreter,
)
from changing_dot.instruction_manager.hard_coded_instruction_manager import (
    HardCodedInstructionManager,
)
from changing_dot.modifyle.modifyle import FakeModifyle
from changing_dot.optimize_graph import optimize_graph
from changing_dot_visualize.observer import Observer

if TYPE_CHECKING:
    from changing_dot.custom_types import ErrorInitialization


@pytest.fixture(autouse=True)
def _reset_repo() -> Generator[None, None, None]:
    yield
    if os.path.exists("./outputs/tmp") and os.path.isdir("./outputs/tmp"):
        shutil.rmtree("./outputs/tmp")


def test_e2e() -> None:
    job_id = "job_id"
    iteration_name = "tmp"
    project_name = "test"
    is_local = True
    initial_change = InitialChange(
        error="Change DistincId to NewVariableName",
        file_path="./tests/core/fixtures/base.cs",
        error_position=(11, 0, 11, 0),
    )
    restriction_options = RestrictionOptions(
        project_blacklist=None,
        restrict_change_to_single_file=None,
        restrict_to_project=None,
    )

    error_manager = HardCodedErrorManager(
        [
            [],  # fisrt assert to check if all is ok
            [
                {
                    "text": "DistincId does not exist",
                    "file_path": "./tests/core/fixtures/base.cs",
                    "project_name": "test",
                    "pos": (17, 0, 17, 0),
                }
            ],  # does solution fix error -> No
            [
                {
                    "text": "DistincId does not exist",
                    "file_path": "./tests/core/fixtures/base.cs",
                    "project_name": "test",
                    "pos": (17, 0, 17, 0),
                }
            ],  # create problem nodes
            [],  # does solution fix error -> Yes
        ]
    )

    instruction_manager = HardCodedInstructionManager(
        {
            "edit_type": "replace",
            "programming_language": "C#",
            "file_path": "./tests/core/fixtures/base.cs",
            "line_number": 17,
            "error": "DistincId does not exist",
            "solution": "Change DistincId to NewVariableName",
        }
    )

    interpreter = HardCodedInstructionInterpreter(
        [
            {
                "edit_type": "replace",
                "file_path": "./tests/core/fixtures/base.cs",
                "line_number": 17,
                "before": "        public string? DistinctId { get; set; }",
                "after": "        public string? NewVariableName { get; set; }",
            }
        ]
    )

    file_modifier = FakeModifyle()

    G = ChangingGraph()

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id,
        is_local=is_local,
    )

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

    ### assert

    expected_directory_path = "./outputs/tmp"

    files = [
        f
        for f in os.listdir(expected_directory_path)
        if os.path.isfile(os.path.join(expected_directory_path, f))
    ]

    assert len(files) == 2

    expected_file_path = "./outputs/tmp/1_test.pickle"

    with open(expected_file_path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
        data_graph = ChangingGraph(data)
        assert (
            data_graph.get_number_of_nodes() == 4
        )  # 1 initial -> 1 solution -> 1 problem -> 1 solution

    ### Optimize Graph

    optimize_graph(G, observer)

    ### assert

    expected_directory_path = "./outputs/tmp"

    files = [
        f
        for f in os.listdir(expected_directory_path)
        if os.path.isfile(os.path.join(expected_directory_path, f))
    ]

    assert len(files) == 3  # add a new optimize step

    expected_file_path = "./outputs/tmp/2_test.pickle"

    with open(expected_file_path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
        data_graph = ChangingGraph(data)
        assert (
            data_graph.get_number_of_nodes() == 4
        )  # Same as before since nothing is optimized

    # ### Resume graph

    resume_error_manager = HardCodedErrorManager(
        [
            [],  # fisrt assert to check if all is ok
            [],  # does new solution fix error -> Yes
        ]
    )

    resume_initial_node = ResumeInitialNode(
        index=2,
        status="handled",
        error={
            "text": "DistincId does not exist",
            "file_path": "./tests/core/fixtures/base.cs",
            "project_name": "test",
            "pos": (17, 0, 17, 0),
        },
    )

    resume_problem_node(
        G,
        resume_initial_node.index,
        {
            "index": resume_initial_node.index,
            "node_type": "problem",
            "status": "pending",
            "error": resume_initial_node.error,
        },
        resume_initial_node.new_instruction,
        resume_initial_node.new_edits,
        resume_error_manager,
        instruction_manager,
        interpreter,
        file_modifier,
        observer,
        restriction_options,
    )

    ## assert

    expected_directory_path = "./outputs/tmp"

    files = [
        f
        for f in os.listdir(expected_directory_path)
        if os.path.isfile(os.path.join(expected_directory_path, f))
    ]

    assert len(files) == 4  # add a new step

    expected_file_path = "./outputs/tmp/3_test.pickle"

    with open(expected_file_path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
        data_graph = ChangingGraph(data)
        assert data_graph.get_number_of_nodes() == 5  # Add a new solution
