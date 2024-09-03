from changing_dot.dependency_graph.dependency_graph import DependencyGraph


def test_empty_list() -> None:
    graph = DependencyGraph([])
    assert not graph.has_syntax_errors()
