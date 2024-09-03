from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
)


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/fixtures/" + file_path


def test_empty_list() -> None:
    graph = DependencyGraph([])
    assert graph.get_number_of_nodes() == 0
    assert graph.get_parent_child_relationships() == []


def test_unrecognized_extension() -> None:
    graph = DependencyGraph([get_fixture_path("unrecognized_extension.eiei")])
    assert graph.get_number_of_nodes() == 0
    assert graph.get_parent_child_relationships() == []
