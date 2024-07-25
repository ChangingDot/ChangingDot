from typing import TYPE_CHECKING

from core.instruction_interpreter.basic_instruction_interpreter import (
    BasicInstructionInterpreter,
)
from core.instruction_interpreter.instruction_interpreter import (
    IInstructionInterpreter,
)
from langchain_community.chat_models.fake import FakeListChatModel

if TYPE_CHECKING:
    from core.custom_types import Edits, Instruction


def make_instruction_interpreter(expected_llm_output: str) -> IInstructionInterpreter:
    return BasicInstructionInterpreter(
        FakeListChatModel(responses=[expected_llm_output])
    )


def test_empty_instruction() -> None:
    instruction: Instruction = {
        "edit_type": "replace",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 5,
        "error": "random_error",
        "solution": "random_solution",
    }

    interpreter = make_instruction_interpreter(
        """
    random blabla
    """
    )

    expected_edits: Edits = []

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_basic_instruction() -> None:
    instruction: Instruction = {
        "edit_type": "replace",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 5,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
-  Console.WriteLie("Hi");
+  Console.WriteLine("Hi");
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 5,
            "before": """  Console.WriteLie("Hi");\n""",
            "after": """  Console.WriteLine("Hi");\n""",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_basic_add() -> None:
    instruction: Instruction = {
        "edit_type": "add",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 0,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
+  Console.WriteLine("Line to add");
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 0,
            "line_to_add": """  Console.WriteLine("Line to add");\n""",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_add_failed_diff_1() -> None:
    instruction: Instruction = {
        "edit_type": "add",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 0,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- AsyncIntervalFlushHandler.cs
+++ AsyncIntervalFlushHandler.cs
@@ ... @@
+using System.Text.Json;
 }
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 0,
            "line_to_add": "using System.Text.Json;\n",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_add_failed_diff_2() -> None:
    instruction: Instruction = {
        "edit_type": "add",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 0,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- AsyncIntervalFlushHandler.cs
+++ AsyncIntervalFlushHandler.cs
@@ ... @@
 }
+using System.Text.Json;
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 0,
            "line_to_add": "using System.Text.Json;\n",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_add_failed_diff_3() -> None:
    instruction: Instruction = {
        "edit_type": "add",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 0,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- AsyncIntervalFlushHandler.cs
+++ AsyncIntervalFlushHandler.cs
@@ ... @@
 }
-using System;
+using System;
+using System.Text.Json;
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 0,
            "line_to_add": "using System.Text.Json;\n",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


# We anticipate that most of the relevant changes would be the lasts one
# because the first are most of the time imports
def test_add_failed_diff_when_multiple_then_take_last() -> None:
    instruction: Instruction = {
        "edit_type": "replace",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 5,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- BaseAction.cs
+++ BaseAction.cs
@@ ... @@
-using Newtonsoft.Json;
+using System.Text.Json.Serialization;
@@ ... @@
-   [JsonProperty(PropertyName = "distinct_id")]
+   [JsonPropertyName(name: "distinct_id")]
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "replace",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 5,
            "before": """   [JsonProperty(PropertyName = "distinct_id")]\n""",
            "after": """   [JsonPropertyName(name: "distinct_id")]\n""",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_basic_remove() -> None:
    instruction: Instruction = {
        "edit_type": "remove",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 3,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
-  Console.WriteLine("Line to remove");
```

random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "remove",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 3,
            "line_to_remove": """  Console.WriteLine("Line to remove");\n""",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_change_when_no_after_then_become_remove() -> None:
    instruction: Instruction = {
        "edit_type": "replace",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 5,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- BaseAction.cs
+++ BaseAction.cs
@@ ... @@
-   [JsonProperty(PropertyName = "distinct_id")]
```
random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "remove",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 5,
            "line_to_remove": """   [JsonProperty(PropertyName = "distinct_id")]\n""",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)


def test_change_when_no_before_then_become_add() -> None:
    instruction: Instruction = {
        "edit_type": "replace",
        "programming_language": "C#",
        "file_path": "./tests/core/fixtures/subject.cs",
        "line_number": 5,
        "error": "random_error",
        "solution": "random_solution",
    }
    interpreter = make_instruction_interpreter(
        """
    random blabla
```diff
--- BaseAction.cs
+++ BaseAction.cs
@@ ... @@
+   [JsonPropertyName(name: "distinct_id")]
```
random blabla
    """
    )

    expected_edits: Edits = [
        {
            "edit_type": "add",
            "file_path": "./tests/core/fixtures/subject.cs",
            "line_number": 5,
            "line_to_add": """   [JsonPropertyName(name: "distinct_id")]\n""",
        },
    ]

    assert expected_edits == interpreter.get_edits_from_instruction(instruction)
