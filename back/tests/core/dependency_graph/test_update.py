from collections.abc import Generator

import pytest
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    DependencyGraphNode,
)
from changing_dot.utils.text_functions import write_text


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/fixtures/updates/" + file_path


def get_fixture(file_path: str) -> str:
    with open(get_fixture_path(file_path)) as file:
        file_contents = file.read()
    return file_contents


@pytest.fixture(autouse=True)
def base() -> Generator[None, None, str]:
    base = get_fixture("base.cs")
    yield
    write_text(get_fixture_path("subject_1.cs"), base)
    return base


def test_empty_updates() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])
    update_ranges = graph.update_graph_from_file_paths([])
    assert update_ranges == []


def test_no_updates() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])
    update_ranges = graph.update_graph_from_file_paths(
        [get_fixture_path("subject_1.cs")]
    )
    assert update_ranges == []


def test_update_with_no_graph_impact() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_1.cs"))

    update_ranges = graph.update_graph_from_file_paths(
        [get_fixture_path("subject_1.cs")]
    )

    assert len(update_ranges) == 1
    assert graph.get_number_of_nodes() == 2
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("subject_1.cs"),
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
        )
    ]


def test_update_that_adds_a_node() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_2.cs"))

    update_ranges = graph.update_graph_from_file_paths(
        [get_fixture_path("subject_1.cs")]
    )

    assert len(update_ranges) == 1
    assert graph.get_number_of_nodes() == 3
    for method_dependency in [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(10, 1),
            file_path=get_fixture_path("subject_1.cs"),
        ),
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
        ),
        DependencyGraphNode(
            node_type="Method",
            start_point=(6, 4),
            end_point=(9, 5),
            file_path=get_fixture_path("subject_1.cs"),
        ),
    ]:
        assert method_dependency in graph.get_nodes()
