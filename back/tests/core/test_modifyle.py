from collections.abc import Generator

import pytest
from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.modifyle.modifyle import (
    IModifyle,
    IntegralModifyle,
    applied_edits_context,
)
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
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonIgnore]\n        public int ChangedSize { get; set; }",
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
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }",
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
            before="using Newtonsoft.Json;",
            after="// New line yo !\nusing Newtonsoft.Json;",
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
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        public int Size { get; set; }",
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
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        public int Size { get; set; }",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_remove.cs")

    modifyle.revert_changes(DG)

    assert get_subject() == get_fixture("base.cs")


def test_DG_is_updated_on_each_code_change(modifyle: IModifyle, base: str) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        public int Size { get; set; }",
        )
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_remove.cs")
    assert DG.get_node(7).text == "public int Size { get; set; }"

    modifyle.revert_changes(DG)

    assert get_subject() == get_fixture("base.cs")

    # Do not change DG on a revert changes
    assert DG.get_node(7).text == "public int Size { get; set; }"


def test_remove_line(
    modifyle: IModifyle,
    base: str,
) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=4,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }",
            after="        public string? DistinctId { get; set; }",
        ),
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("remove_line.cs")

    modifyle.revert_changes(DG)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_changes_same_file(
    modifyle: IModifyle,
    base: str,
) -> None:
    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=1,
            before="using Newtonsoft.Json;",
            after="// New line yo !\nusing Newtonsoft.Json;",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=4,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }",
            after="        public string? DistinctId { get; set; }",
        ),
    ]
    DG = DependencyGraph([edit.file_path for edit in edits])

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("multiple_changes.cs")

    modifyle.revert_changes(DG)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_applies_same_file(
    modifyle: IModifyle,
    base: str,
) -> None:
    DG = DependencyGraph(["./tests/core/fixtures/subject.cs"])

    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }",
        ),
    ]

    edits_2 = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=1,
            before="using Newtonsoft.Json;",
            after="// New line yo !\nusing Newtonsoft.Json;",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=4,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }",
            after="        public string? DistinctId { get; set; }",
        ),
    ]

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("duplicate_change.cs")

    modifyle.apply_change(DG, edits_2)

    assert get_subject() == get_fixture("multiple_changes.cs")

    modifyle.revert_changes(DG)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_changes_multiple_files(
    modifyle: IModifyle,
    base: str,
) -> None:
    DG = DependencyGraph(
        ["./tests/core/fixtures/subject2.cs", "./tests/core/fixtures/subject.cs"]
    )

    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=16,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=10,
            before="using Newtonsoft.Json;",
            after="// New line yo !\nusing Newtonsoft.Json;",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=13,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }",
            after="        public string? DistinctId { get; set; }",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonIgnore]\n        public int ChangedSize { get; set; }",
        ),
    ]

    modifyle.apply_change(DG, edits)

    assert get_subject() == get_fixture("basic_change.cs")
    assert get_fixture("subject2.cs") == get_fixture("multiple_changes.cs")

    modifyle.revert_changes(DG)

    assert get_subject() == get_fixture("base.cs")
    assert get_fixture("subject2.cs") == get_fixture("base.cs")


def test_applied_edits_context(
    modifyle: IModifyle,
    base: str,
) -> None:
    DG = DependencyGraph(
        ["./tests/core/fixtures/subject2.cs", "./tests/core/fixtures/subject.cs"]
    )

    edits: list[BlockEdit] = [
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=16,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonDataIgnore]\n        public int Size { get; set; }",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=10,
            before="using Newtonsoft.Json;",
            after="// New line yo !\nusing Newtonsoft.Json;",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject2.cs",
            block_id=13,
            before="        [JsonIgnore]\n        public string? DistinctId { get; set; }",
            after="        public string? DistinctId { get; set; }",
        ),
        BlockEdit(
            file_path="./tests/core/fixtures/subject.cs",
            block_id=7,
            before="        [JsonIgnore]\n        public int Size { get; set; }",
            after="        [JsonIgnore]\n        public int ChangedSize { get; set; }",
        ),
    ]

    with applied_edits_context(DG, edits):
        assert get_subject() == get_fixture("basic_change.cs")
        assert get_fixture("subject2.cs") == get_fixture("multiple_changes.cs")
        assert (
            DG.get_node(7).text
            == "[JsonIgnore]\n        public int ChangedSize { get; set; }"
        )

    assert get_subject() == get_fixture("base.cs")
    assert get_fixture("subject2.cs") == get_fixture("base.cs")
    assert DG.get_node(7).text == "[JsonIgnore]\n        public int Size { get; set; }"
