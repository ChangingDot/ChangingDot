from changing_dot.dependency_graph.dependency_graph import DependencyGraph


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/fixtures/syntax_errors/" + file_path


def test_empty_list() -> None:
    graph = DependencyGraph([])
    assert not graph.has_syntax_errors()


def test_empty_file() -> None:
    graph = DependencyGraph([get_fixture_path("empty.cs")])
    assert not graph.has_syntax_errors()


def test_syntax_error() -> None:
    graph = DependencyGraph([get_fixture_path("has_syntax_error.cs")])
    assert graph.has_syntax_errors()


def test_syntax_error_python() -> None:
    graph = DependencyGraph([get_fixture_path("has_syntax_error.py")])
    assert graph.has_syntax_errors()


def test_syntax_error_csproj() -> None:
    graph = DependencyGraph([get_fixture_path("has_syntax_error.csproj")])
    assert graph.has_syntax_errors()


def test_multiple_syntax_error() -> None:
    graph = DependencyGraph(
        [
            get_fixture_path("has_syntax_error.cs"),
            get_fixture_path("has_syntax_error_also.cs"),
        ]
    )
    assert graph.has_syntax_errors()


def test_multiple_with_and_without_syntax_error() -> None:
    graph = DependencyGraph(
        [
            get_fixture_path("has_syntax_error.cs"),
            get_fixture_path("empty.cs"),
        ]
    )
    assert graph.has_syntax_errors()
