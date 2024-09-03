from changing_dot.dependency_graph.dependency_graph import DependencyGraph


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/python/fixtures/" + file_path


def test_syntax_error_python() -> None:
    graph = DependencyGraph([get_fixture_path("has_syntax_error.py")])
    assert graph.has_syntax_errors()
