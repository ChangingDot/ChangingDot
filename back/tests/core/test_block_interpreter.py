from typing import TYPE_CHECKING

from changing_dot.custom_types import BlockEdit, EmptyEdit
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_instruction_interpreter import (
    BlockInstructionInterpreter,
)
from langchain_community.chat_models.fake import FakeListChatModel

if TYPE_CHECKING:
    from changing_dot.custom_types import Instruction


def make_instruction_interpreter(
    expected_llm_output: str,
) -> BlockInstructionInterpreter:
    return BlockInstructionInterpreter(
        FakeListChatModel(responses=[expected_llm_output])
    )


def test_empty_instruction() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: Instruction = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "No changes",
    }

    interpreter = make_instruction_interpreter(
        """
    No changes needed
    """
    )

    expected_edit: BlockEdit = EmptyEdit(
        block_id=1,
        file_path="./tests/core/fixtures/block_interpreter/subject.cs",
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)


def test_basic_change() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: Instruction = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "Change Hello, World! to Welcome, World!",
    }

    interpreter = make_instruction_interpreter(
        """
Here is the new block
```csharp
    static string SimpleMethod()
    {
        return "Welcome, World!";
    }
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


def test_that_generated_code_matches_code_indentation() -> None:
    DG = DependencyGraph(["./tests/core/fixtures/block_interpreter/subject.cs"])
    instruction: Instruction = {
        "file_path": "./tests/core/fixtures/block_interpreter/subject.cs",
        "block_id": 1,
        "solution": "Change Hello, World! to Welcome, World!",
    }

    interpreter = make_instruction_interpreter(
        """
Here is the new block
```csharp
static string SimpleMethod()
{
    return "Welcome, World!";
}
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


def test_that_generated_code_matches_code_indentation_python() -> None:
    DG = DependencyGraph(["./tests/core/python_fixtures/subject.py"])
    instruction: Instruction = {
        "file_path": "./tests/core/python_fixtures/subject.py",
        "block_id": 2,
        "solution": "Change result to 'The value of attribute is: {self.attribute}'",
    }

    interpreter = make_instruction_interpreter(
        """
Here is the new block
```csharp
def method(self) -> str:
    return f"New string: {self.attribute}"
```

random blabla
    """
    )

    expected_edit: BlockEdit = BlockEdit(
        file_path="./tests/core/python_fixtures/subject.py",
        block_id=2,
        before='''def method(self) -> str:
        return f"The value of attribute is: {self.attribute}"''',
        after='''def method(self) -> str:
        return f"New string: {self.attribute}"''',
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)


def test_handles_empty_lines() -> None:
    DG = DependencyGraph(["./tests/core/python_fixtures/subject.py"])
    instruction: Instruction = {
        "file_path": "./tests/core/python_fixtures/subject.py",
        "block_id": 2,
        "solution": "Change result to 'The value of attribute is: {self.attribute}' and add an empty line",
    }

    interpreter = make_instruction_interpreter(
        """
Here is the new block
```csharp
def method(self) -> str:

    return f"New string: {self.attribute}"
```

random blabla
    """
    )

    expected_edit: BlockEdit = BlockEdit(
        file_path="./tests/core/python_fixtures/subject.py",
        block_id=2,
        before='''def method(self) -> str:
        return f"The value of attribute is: {self.attribute}"''',
        after='''def method(self) -> str:

        return f"New string: {self.attribute}"''',
    )

    assert expected_edit == interpreter.get_edit_from_instruction(instruction, DG)
