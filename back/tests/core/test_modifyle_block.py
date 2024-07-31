from collections.abc import Generator

import pytest
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_instruction_interpreter import BlockEdit
from changing_dot.modifyle.modifyle_block import IModifyle, IntegralModifyle
from changing_dot.utils.text_functions import write_text


def get_fixture(file_path: str) -> str:
    with open("./tests/core/fixtures/" + file_path) as file:
        file_contents = file.read()
    return file_contents


def get_subject() -> str:
    return get_fixture("subject.cs")


@pytest.fixture(autouse=True)
def base() -> Generator[None, None, str]:
    base = get_fixture("base.cs")
    yield
    write_text("./tests/core/fixtures/subject.cs", base)
    write_text("./tests/core/fixtures/subject2.cs", base)
    return base


@pytest.fixture()
def modifyle() -> IModifyle:
    return IntegralModifyle()


def test_no_change(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = []
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("base.cs")


def test_basic_change(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        [JsonIgnore]\n        public int ChangedSize { get; set; }\n",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_change.cs")


def test_duplicate_change(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }\n",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("duplicate_change.cs")


def test_basic_add(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=1,
            before="using Newtonsoft.Json;\n",
            after="// New line yo !\nusing Newtonsoft.Json;\n",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_add.cs")


def test_basic_remove(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        public int Size { get; set; }\n",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_remove.cs")


def test_revert(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        public int Size { get; set; }\n",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_remove.cs")

    modifyle.revert_change(edits)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_changes_same_file(
    modifyle: IModifyle,
    base: str,
) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }\n",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=1,
            before="using Newtonsoft.Json;\n",
            after="// New line yo !\nusing Newtonsoft.Json;\n",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=4,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }\n",
            after="        public string? DistinctId { get; set; }\n",
        ),
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("multiple_changes.cs")

    modifyle.revert_change(edits)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_changes_multiple_files(
    modifyle: IModifyle,
    base: str,
) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }\n",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=1,
            before="using Newtonsoft.Json;\n",
            after="// New line yo !\nusing Newtonsoft.Json;\n",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=4,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }\n",
            after="        public string? DistinctId { get; set; }\n",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }\n",
            after="        [JsonIgnore]\n        public int ChangedSize { get; set; }\n",
        ),
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_change.cs")
    assert get_fixture("subject2.cs") == get_fixture("multiple_changes.cs")

    modifyle.revert_change(edits)

    assert get_subject() == get_fixture("base.cs")
    assert get_fixture("subject2.cs") == get_fixture("base.cs")