from changing_dot.dependency_graph.dependency_graph import DependencyGraph


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/fixtures/syntax_errors/" + file_path


def test_empty_list() -> None:
    graph = DependencyGraph([])
    assert not graph.has_syntax_errors()
