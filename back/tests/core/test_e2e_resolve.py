import os
import pickle
import shutil
from collections.abc import Generator

import pytest
from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import (
    BlockEdit,
    CompileError,
    Instruction,
    RestrictionOptions,
)
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.error_manager.error_manager import (
    HardCodedErrorManager,
)
from changing_dot.instruction_interpreter.hard_coded_instruction_interpreter import (
    HardCodedInstructionInterpreter,
)
from changing_dot.instruction_manager.hard_coded_instruction_manager import (
    HardCodedInstructionManager,
)
from changing_dot.modifyle.modifyle import IntegralModifyle
from changing_dot.resolve_graph import resolve_graph
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


def test_e2e_resolve() -> None:
    changed_file_content = read_text("./tests/core/fixtures/e2e_results/base.cs")

    job_id = "job_id"
    iteration_name = "tmp"
    project_name = "test"
    output_path = "./outputs"

    restriction_options = RestrictionOptions(
        project_blacklist=None,
        restrict_change_to_single_file=None,
        restrict_to_project=None,
    )

    error_manager = HardCodedErrorManager(
        [
            [
                CompileError(
                    text="DistincId does not exist",
                    file_path="./tests/core/fixtures/e2e/base.cs",
                    project_name="test",
                    pos=(17, 0, 17, 0),
                )
            ],  # first errors
            [],  # does solution fix error -> Yes
            [],  # connect to solved errors
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

    ### assert

    expected_directory_path = "./outputs/tmp"

    files = [
        f
        for f in os.listdir(expected_directory_path)
        if os.path.isfile(os.path.join(expected_directory_path, f))
    ]

    assert len(files) == 3
    # init step -> solve step -> opti step

    expected_file_path = "./outputs/tmp/1_test.pickle"

    with open(expected_file_path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
        data_graph = ChangingGraph(data)
        assert (
            data_graph.get_number_of_nodes() == 3
        )  # 1 initial -> 1 problem -> 1 solution
        assert (
            data_graph.get_number_of_edges() == 2
        )  # 1 initial -> 1 problem -> 1 solution

    assert read_text("./tests/core/fixtures/e2e/base.cs") == changed_file_content
