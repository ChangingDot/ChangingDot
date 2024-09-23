import os
import pickle
import shutil
from collections.abc import Generator

import pytest
from changing_dot.apply_graph_changes import apply_graph_changes
from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.create_graph import create_graph
from changing_dot.custom_types import (
    BlockEdit,
    CompileError,
    ErrorInitialization,
    InitialChange,
    Instruction,
    ProblemNode,
    RestrictionOptions,
    ResumeInitialNode,
)
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
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
from changing_dot.modifyle.modifyle import IntegralModifyle
from changing_dot.utils.text_functions import read_text, write_text
from changing_dot_visualize.observer import Observer


@pytest.fixture(autouse=True)
def _reset_repo() -> Generator[None, None, None]:
    yield
    write_text(
        "./tests/core/fixtures/e2e/base.cs",
        read_text(
            "./tests/core/fixtures/base.cs",
        ),
    )
    if os.path.exists("./outputs/tmp") and os.path.isdir("./outputs/tmp"):
        shutil.rmtree("./outputs/tmp")


def test_e2e() -> None:
    ### setup
    initial_file_content = read_text("./tests/core/fixtures/e2e/base.cs")
    changed_file_content = read_text("./tests/core/fixtures/e2e_results/base.cs")

    job_id = "job_id"
    iteration_name = "tmp"
    project_name = "test"
    output_path = "./outputs"
    initial_change = InitialChange(
        error="DistincId does not exist",
        file_path="./tests/core/fixtures/e2e/base.cs",
        error_position=(17, 0, 17, 0),
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
                CompileError(
                    text="DistincId does not exist",
                    file_path="./tests/core/fixtures/e2e/base.cs",
                    project_name="test",
                    pos=(17, 0, 17, 0),
                )
            ],  # does solution fix error -> No
            [],  # does solution fix error -> Yes
        ]
    )

    instruction_manager = HardCodedInstructionManager(
        Instruction(
            block_id=4,
            file_path="./tests/core/fixtures/e2e/base.cs",
            solution="Change DistincId to NewVariableName",
        )
    )

    interpreter = HardCodedInstructionInterpreter(
        BlockEdit(
            block_id=4,
            file_path="./tests/core/fixtures/e2e/base.cs",
            before="[JsonIgnore]\n        public string? DistinctId { get; set; }",
            after="[JsonIgnore]\n        public string? NewVariableName { get; set; }",
        )
    )

    file_modifier = IntegralModifyle()

    G = ChangingGraph()

    DG = DependencyGraph(["./tests/core/fixtures/e2e/base.cs"])

    observer = Observer(
        G,
        iteration_name,
        project_name,
        job_id,
        output_path,
    )

    initialisation = ErrorInitialization(
        init_type="error",
        initial_error=initial_change.error,
        initial_file_path=initial_change.file_path,
        initial_error_position=initial_change.error_position,
    )

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
            data_graph.get_number_of_nodes() == 3
        )  # 1 initial -> 1 solution failed -> 1 solution ok

    assert read_text("./tests/core/fixtures/e2e/base.cs") == initial_file_content

    ### Apply changes

    new_DG = DependencyGraph(["./tests/core/fixtures/e2e/base.cs"])

    new_file_modifier = IntegralModifyle()

    apply_graph_changes(G, new_DG, new_file_modifier, observer)

    ### assert

    assert read_text("./tests/core/fixtures/e2e/base.cs") == changed_file_content

    # remove applied changes
    write_text(
        "./tests/core/fixtures/e2e/base.cs",
        read_text(
            "./tests/core/fixtures/base.cs",
        ),
    )

    # ### Resume graph

    resume_error_manager = HardCodedErrorManager(
        [
            [],  # fisrt assert to check if all is ok
            [],  # does new solution fix error -> Yes
        ]
    )

    resume_initial_node = ResumeInitialNode(
        index=0,
        status="handled",
        error=CompileError(
            text="DistincId does not exist",
            file_path="./tests/core/fixtures/e2e/base.cs",
            project_name="test",
            pos=(17, 0, 17, 0),
        ),
    )

    resume_DG = DependencyGraph(["./tests/core/fixtures/e2e/base.cs"])

    resume_file_modifier = IntegralModifyle()

    resume_problem_node(
        G,
        resume_DG,
        resume_initial_node.index,
        ProblemNode(
            index=resume_initial_node.index,
            node_type="problem",
            status="pending",
            error=resume_initial_node.error,
        ),
        resume_initial_node.new_instruction,
        resume_initial_node.new_edits,
        resume_error_manager,
        instruction_manager,
        interpreter,
        resume_file_modifier,
        observer,
    )

    ## assert

    expected_directory_path = "./outputs/tmp"

    files = [
        f
        for f in os.listdir(expected_directory_path)
        if os.path.isfile(os.path.join(expected_directory_path, f))
    ]

    assert len(files) == 3  # add a new step

    expected_file_path = "./outputs/tmp/2_test.pickle"

    with open(expected_file_path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
        data_graph = ChangingGraph(data)
        assert (
            data_graph.get_number_of_nodes() == 2
        )  # Removes failed and correct solution then adds a new solution
