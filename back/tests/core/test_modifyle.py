from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from core.modifyle.modifyle import IModifyle, Modifyle
from utils.text_functions import write_text

if TYPE_CHECKING:
    from core.custom_types import Edits


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
    return Modifyle()


def test_no_change(modifyle: IModifyle, base: str) -> None:
    edits: Edits = []

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("base.cs")


def test_basic_change(modifyle: IModifyle, base: str) -> None:
    edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 26,
            "before": "        public int Size { get; set; }\n",
            "after": "        public int ChangedSize { get; set; }\n",
        }
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("basic_change.cs")


def test_basic_change_no_line_skip(modifyle: IModifyle, base: str) -> None:
    edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 26,
            "before": "        public int Size { get; set; }",
            "after": "        public int ChangedSize { get; set; }",
        }
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("basic_change.cs")


def test_duplicate_change(modifyle: IModifyle, base: str) -> None:
    edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 25,
            "before": "        [JsonIgnore]\n",
            "after": "        [JsonDataIgnore]\n",
        }
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("duplicate_change.cs")


def test_basic_add(modifyle: IModifyle, base: str) -> None:
    edits: Edits = [
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 2,
            "line_to_add": "// New line yo !\n",
        }
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("basic_add.cs")


def test_basic_remove(modifyle: IModifyle, base: str) -> None:
    edits: Edits = [
        {
            "edit_type": "remove",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 25,
            "line_to_remove": "        [JsonIgnore]\n",
        }
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("basic_remove.cs")


def test_revert(modifyle: IModifyle, base: str) -> None:
    edits: Edits = [
        {
            "edit_type": "remove",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 25,
            "line_to_remove": "        [JsonIgnore]\n",
        }
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("basic_remove.cs")

    modifyle.revert_change(edits)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_changes_same_file(
    modifyle: IModifyle,
    base: str,
) -> None:
    expected_result = get_fixture("multiple_changes.cs")

    edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 25,
            "before": "        [JsonIgnore]\n",
            "after": "        [JsonDataIgnore]\n",
        },
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 2,
            "line_to_add": "// New line yo !\n",
        },
        {
            "edit_type": "remove",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 16,
            "line_to_remove": "        [JsonIgnore]\n",
        },
    ]

    modifyle.apply_change(edits)

    assert get_subject() == expected_result

    modifyle.revert_change(edits)

    assert get_subject() == get_fixture("base.cs")


def test_multiple_changes_multiple_files(
    modifyle: IModifyle,
    base: str,
) -> None:
    edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 26,
            "before": "        public int Size { get; set; }\n",
            "after": "        public int ChangedSize { get; set; }\n",
        },
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject2.cs",
            "line_number": 2,
            "line_to_add": "// New line yo !\n",
        },
    ]

    modifyle.apply_change(edits)

    assert get_subject() == get_fixture("basic_change.cs")
    assert get_fixture("subject2.cs") == get_fixture("basic_add.cs")

    modifyle.revert_change(edits)

    assert get_subject() == get_fixture("base.cs")
    assert get_fixture("subject2.cs") == get_fixture("base.cs")
