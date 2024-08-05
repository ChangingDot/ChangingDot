from changing_dot.utils.process_diff import ProcessedDiff, process_diff


def test_processing_empty_diff_returns_empty_list() -> None:
    diff = ""
    assert process_diff(diff) == []


def test_processing_no_diff_returns_empty_list() -> None:
    diff = """
    random blabla
```diff
--- file.cs
+++ file.cs
@@ ... @@
```

random blabla
    """
    assert process_diff(diff) == []


def test_processing_simple_diff_returns_the_processed_diff() -> None:
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
    assert process_diff(diff) == [
        ProcessedDiff(
            before="""        return "Hello, World!";""",
            after="""        return "Welcome, World!";""",
        )
    ]


def test_processing_multiline_diff_returns_the_processed_diff() -> None:
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
    assert process_diff(diff) == [
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


def test_processing_multiple_diffs_in_single_block() -> None:
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

    assert process_diff(diff) == [
        ProcessedDiff(
            before="        var x = 5;",
            after="        var x = 10;",
        ),
        ProcessedDiff(
            before='        Console.WriteLine("Hello");',
            after='        Console.WriteLine("World");',
        ),
    ]


def test_processing_multiple_diffs_in_single_block_no_divider() -> None:
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

    assert process_diff(diff) == [
        ProcessedDiff(
            before="        var x = 5;",
            after="        var x = 10;",
        ),
        ProcessedDiff(
            before='        Console.WriteLine("Hello");',
            after='        Console.WriteLine("World");',
        ),
    ]


def test_processing_diff_with_added_lines_only() -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
public class Example
{
+    private string _name;
    public void Method()
    {
        // Some comment
    }
}
    random blabla
    """
    assert process_diff(diff) == [
        ProcessedDiff(
            before="",
            after="    private string _name;",
        )
    ]


def test_processing_diff_with_remove_lines_only() -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
public class Example
{
-    private string _name;
    public void Method()
    {
        // Some comment
    }
}
    random blabla
    """
    assert process_diff(diff) == [
        ProcessedDiff(
            before="    private string _name;",
            after="",
        )
    ]


def test_processing_diff_with_line_jumps() -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
public class Example
{
+    private string _name;
+
+
    public void Method()
    {
        // Some comment
    }
}
    random blabla
    """
    assert process_diff(diff) == [
        ProcessedDiff(
            before="",
            after="""    private string _name;

""",
        )
    ]


def test_processing_diff_when_operators_are_not_first_char() -> None:
    diff = """
    random blabla
    diffCopy--- file.cs
    +++ file.cs
    @@ ... @@
public class Example
{
    public void Method()
    {
    -var a = "a";
    +var b = "b";
    }
}
    random blabla
    """
    assert process_diff(diff) == [
        ProcessedDiff(before='    var a = "a";', after='    var b = "b";')
    ]
