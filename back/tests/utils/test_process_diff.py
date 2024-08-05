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
