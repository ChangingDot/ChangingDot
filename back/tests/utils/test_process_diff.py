import pytest
from changing_dot.utils.process_diff import ProcessedDiff, process_diff


@pytest.fixture()
def simple_block_text() -> str:
    return """static string SimpleMethod()
    {
        return "Hello, World!";
    }"""


@pytest.fixture()
def block_text() -> str:
    return """static string SimpleMethod()
    {
        var x = 5;
        // This is a comment
        Console.WriteLine("Hello");

        if (x < 4)
        {
            Console.WriteLine("small");
        }
        else
        {
            Console.WriteLine("big");
        }

        return "Hello, World!";
    }"""


def test_processing_empty_diff_returns_empty_list(simple_block_text: str) -> None:
    diff = ""
    assert process_diff(diff, simple_block_text) == []


def test_processing_no_diff_returns_empty_list(simple_block_text: str) -> None:
    diff = """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
```

random blabla
    """
    assert process_diff(diff, simple_block_text) == []


def test_processing_simple_diff_returns_the_processed_diff(
    simple_block_text: str,
) -> None:
    diff = """
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
    assert process_diff(diff, simple_block_text) == [
        ProcessedDiff(
            before="""        return "Hello, World!";""",
            after="""        return "Welcome, World!";""",
        )
    ]


def test_processing_multiline_diff_returns_the_processed_diff(
    simple_block_text: str,
) -> None:
    diff = """
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
    assert process_diff(diff, simple_block_text) == [
        ProcessedDiff(
            before="""    static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
            after="""    static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
        )
    ]


def test_processing_multiline_diff_returns_the_processed_diff_plus_first(
    simple_block_text: str,
) -> None:
    diff = """
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
    assert process_diff(diff, simple_block_text) == [
        ProcessedDiff(
            before="""    static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
            after="""    static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
        )
    ]


def test_processing_multiple_diffs_in_single_block(block_text: str) -> None:
    diff = """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
-        var x = 5;
+        var x = 10;
something
-        Console.WriteLine("Hello");
+        Console.WriteLine("World");
random blabla
"""

    assert process_diff(diff, block_text) == [
        ProcessedDiff(
            before="        var x = 5;",
            after="        var x = 10;",
        ),
        ProcessedDiff(
            before='        Console.WriteLine("Hello");',
            after='        Console.WriteLine("World");',
        ),
    ]


def test_processing_multiple_diffs_in_single_block_no_divider(block_text: str) -> None:
    diff = """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
-        var x = 5;
+        var x = 10;
-        Console.WriteLine("Hello");
+        Console.WriteLine("World");
random blabla
"""

    assert process_diff(diff, block_text) == [
        ProcessedDiff(
            before="        var x = 5;",
            after="        var x = 10;",
        ),
        ProcessedDiff(
            before='        Console.WriteLine("Hello");',
            after='        Console.WriteLine("World");',
        ),
    ]


def test_processing_diff_with_remove_lines_only(block_text: str) -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
    var x = 5;
    // This is a comment
-    Console.WriteLine("Hello");

    if (x < 4)
    {
        Console.WriteLine("small");
    }
    else
    {
        Console.WriteLine("big");
    }
    random blabla
    """
    assert process_diff(diff, block_text) == [
        ProcessedDiff(
            before='    Console.WriteLine("Hello");',
            after="",
        )
    ]


def test_processing_diff_when_operators_are_not_first_char(
    simple_block_text: str,
) -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
        -return "Hello, World!";
        +return "Welcome, World!";
    random blabla
    """
    assert process_diff(diff, simple_block_text) == [
        ProcessedDiff(
            before='        return "Hello, World!";',
            after='        return "Welcome, World!";',
        )
    ]


def test_processing_diff_with_line_jumps(block_text: str) -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
        var x = 5;
        // This is a comment
-        Console.WriteLine("Hello");
-
+        Console.WriteLine("Welcome");
+
+
        if (x < 4)
    random blabla
    """
    assert process_diff(diff, block_text) == [
        ProcessedDiff(
            before='        Console.WriteLine("Hello");\n',
            after='        Console.WriteLine("Welcome");\n\n',
        )
    ]


def test_processing_diff_with_added_lines_only(simple_block_text: str) -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
static string SimpleMethod()
    {
+        // New comment
        return "Hello, World!";
    }
    random blabla
    """
    assert process_diff(diff, simple_block_text) == [
        ProcessedDiff(
            before="",
            after="        // New comment",
        )
    ]
