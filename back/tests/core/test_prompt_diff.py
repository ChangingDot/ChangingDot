from typing import TYPE_CHECKING

from changing_dot.instruction_manager.prompt_diff import create_prompt_diff_block

if TYPE_CHECKING:
    from changing_dot.custom_types import (
        AddEdit,
        CompileError,
        Edits,
        RemoveEdit,
        ReplaceEdit,
    )


def get_fixture(file_name: str) -> str:
    with open("./tests/core/fixtures/prompt_diff/" + file_name) as file:
        file_contents = file.read()
    return file_contents


def test_empty_edits() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }
    edits: Edits = []

    result = create_prompt_diff_block(error, edits)

    assert result == get_fixture("empty_edits.cs")


def test_simple_replace_edit_after() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: ReplaceEdit = {
        "edit_type": "replace",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 16,
        "before": "        [JsonIgnore]",
        "after": "        [DifferentJsonIgnore]",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("simple_change_edit_after.cs")


def test_simple_replace_edit_before() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: ReplaceEdit = {
        "edit_type": "replace",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 6,
        "before": "    public class BaseAction",
        "after": "    public class BaseActionNew",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("simple_change_edit_before.cs")


def test_replace_edit_same() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: ReplaceEdit = {
        "edit_type": "replace",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 10,
        "before": "            Event = @event;",
        "after": "            NewEvent = @event;",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("change_edit_same.cs")


def test_simple_add_edit_after() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: AddEdit = {
        "edit_type": "add",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 16,
        "line_to_add": "        [OtherAttribute]",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("simple_add_edit_after.cs")


def test_simple_add_edit_before() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: AddEdit = {
        "edit_type": "add",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 6,
        "line_to_add": "    [New]",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("simple_add_edit_before.cs")


def test_simple_remove_edit_after() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: RemoveEdit = {
        "edit_type": "remove",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 16,
        "line_to_remove": "        [JsonIgnore]",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("simple_remove_edit_after.cs")


def test_simple_remove_edit_before() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: RemoveEdit = {
        "edit_type": "remove",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "line_number": 2,
        "line_to_remove": "using Newtonsoft.Json;",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("simple_remove_edit_before.cs")


def test_edits_in_other_file_as_error() -> None:
    error: CompileError = {
        "text": "Error text",
        "file_path": "./tests/core/fixtures/prompt_diff/base.cs",
        "project_name": "project_name",
        "pos": (10, 2, 10, 8),
    }

    edit: RemoveEdit = {
        "edit_type": "remove",
        "file_path": "./tests/core/fixtures/prompt_diff/fake_proj.csproj",
        "line_number": 13,
        "line_to_remove": """    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />""",
    }

    result = create_prompt_diff_block(error, [edit])

    assert result == get_fixture("edits_in_other_file_as_error.txt")
