from typing import TYPE_CHECKING

import pytest
from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    BlockInstructionInterpreter,
)
from langchain_community.chat_models.fake import FakeListChatModel

if TYPE_CHECKING:
    from changing_dot.custom_types import InstructionBlock


def make_instruction_interpreter(
    expected_llm_output: str,
) -> BlockInstructionInterpreter:
    return BlockInstructionInterpreter(
        FakeListChatModel(responses=[expected_llm_output])
    )


def test_empty_instruction() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: InstructionBlock = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "No changes",
    }

    interpreter = make_instruction_interpreter(
        """
    No changes needed
    """
    )

    expected_edit: BlockEdit = BlockEdit(
        block_id=1,
        file_path="./tests/core/fixtures/block_interpreter/subject.cs",
        before="",
        after="",
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)


def test_basic_change() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: InstructionBlock = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "Change Hello, World! to Welcome, World!",
    }

    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
-    static string SimpleMethod()
-    {
-        return "Hello, World!";
-    }
+    static string SimpleMethod()
+    {
+        return "Welcome, World!";
+    }
```

random blabla
    """
    )

    expected_edit: BlockEdit = BlockEdit(
        file_path="./tests/core/fixtures/block_interpreter/subject.cs",
        block_id=1,
        before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)


def test_basic_change_with_plus_before_minus() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: InstructionBlock = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "Change Hello, World! to Welcome, World!",
    }

    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
+    static string SimpleMethod()
+    {
+        return "Welcome, World!";
+    }
-    static string SimpleMethod()
-    {
-        return "Hello, World!";
-    }
```

random blabla
    """
    )

    expected_edit: BlockEdit = BlockEdit(
        file_path="./tests/core/fixtures/block_interpreter/subject.cs",
        block_id=1,
        before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)


def test_basic_change_but_LLM_returns_changes_not_full_block() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: InstructionBlock = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "Change Hello, World! to Welcome, World!",
    }

    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
-        return "Hello, World!";
+        return "Welcome, World!";
```

random blabla
    """
    )

    expected_edit: BlockEdit = BlockEdit(
        file_path="./tests/core/fixtures/block_interpreter/subject.cs",
        block_id=1,
        before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)


def test_that_no_context_add_fails() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: InstructionBlock = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "Change Hello, World! to Welcome, World!",
    }

    interpreter = make_instruction_interpreter(
        """
  There is no line number between @@
```diff
--- file.cs
+++ file.cs
@@ ... @@
+        add a new line
```

random blabla
    """
    )

    with pytest.raises(
        ValueError, match="Code was added, but we do not know where to put it"
    ):
        interpreter.get_edit_from_instruction(instruction, DG)
