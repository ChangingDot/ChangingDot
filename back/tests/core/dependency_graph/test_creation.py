import pytest
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    DependencyGraphNode,
)


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/fixtures/" + file_path


def test_empty_list() -> None:
    graph = DependencyGraph([])
    assert graph.get_number_of_nodes() == 0
    assert graph.get_parent_child_relationships() == []


def test_empty_file() -> None:
    graph = DependencyGraph([get_fixture_path("empty.cs")])
    assert graph.get_number_of_nodes() == 0
    assert graph.get_parent_child_relationships() == []


def test_empty_class() -> None:
    graph = DependencyGraph([get_fixture_path("empty_class.cs")])
    assert graph.get_number_of_nodes() == 1
    assert graph.get_node(0) == DependencyGraphNode(
        node_type="Class",
        start_point=(0, 0),
        end_point=(2, 1),
        file_path=get_fixture_path("empty_class.cs"),
    )
    assert graph.get_parent_child_relationships() == []


def test_simple_method() -> None:
    graph = DependencyGraph([get_fixture_path("simple_method.cs")])
    assert graph.get_number_of_nodes() == 2
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("simple_method.cs"),
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("simple_method.cs"),
        )
    ]


def test_simple_field() -> None:
    graph = DependencyGraph([get_fixture_path("simple_field.cs")])
    assert graph.get_number_of_nodes() == 2
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(3, 1),
            file_path=get_fixture_path("simple_field.cs"),
        )
    ]
    assert (graph.get_node_by_type("Field")) == [
        DependencyGraphNode(
            node_type="Field",
            start_point=(2, 4),
            end_point=(2, 21),
            file_path=get_fixture_path("simple_field.cs"),
        )
    ]


def test_simple_constructor() -> None:
    graph = DependencyGraph([get_fixture_path("simple_constructor.cs")])
    assert graph.get_number_of_nodes() == 3
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(7, 1),
            file_path=get_fixture_path("simple_constructor.cs"),
        )
    ]
    assert (graph.get_node_by_type("Field")) == [
        DependencyGraphNode(
            node_type="Field",
            start_point=(2, 4),
            end_point=(2, 23),
            file_path=get_fixture_path("simple_constructor.cs"),
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(3, 4),
            end_point=(6, 5),
            file_path=get_fixture_path("simple_constructor.cs"),
        ),
    ]


def test_simple_property() -> None:
    graph = DependencyGraph([get_fixture_path("simple_property.cs")])
    assert graph.get_number_of_nodes() == 3
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(7, 1),
            file_path=get_fixture_path("simple_property.cs"),
        )
    ]
    assert (graph.get_node_by_type("Field")) == [
        DependencyGraphNode(
            node_type="Field",
            start_point=(2, 4),
            end_point=(2, 31),
            file_path=get_fixture_path("simple_property.cs"),
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(3, 4),
            end_point=(6, 5),
            file_path=get_fixture_path("simple_property.cs"),
        ),
    ]


def test_imports() -> None:
    graph = DependencyGraph([get_fixture_path("imports.cs")])
    assert len(graph.get_node_by_type("Import")) == 12
    assert DependencyGraphNode(
        node_type="Import",
        start_point=(10, 0),
        end_point=(10, 25),
        file_path=get_fixture_path("imports.cs"),
    ) in graph.get_node_by_type("Import")


@pytest.mark.skip(reason="Waiting for tree-sitter-python pip fix")
def test_full_python() -> None:
    graph_py = DependencyGraph([get_fixture_path("full.py")])
    assert len(graph_py.get_node_by_type("Import")) == 2
    assert len(graph_py.get_node_by_type("Class")) == 1
    assert len(graph_py.get_node_by_type("Method")) == 5
    assert len(graph_py.get_node_by_type("Field")) == 0


def test_unrecognized_extension() -> None:
    graph = DependencyGraph([get_fixture_path("unrecognized_extension.eiei")])
    assert graph.get_number_of_nodes() == 0
    assert graph.get_parent_child_relationships() == []


def test_multiple_files() -> None:
    graph = DependencyGraph(
        [
            get_fixture_path("unrecognized_extension.eiei"),
            get_fixture_path("simple_property.cs"),
            get_fixture_path("imports.cs"),
        ]
    )
    assert graph.get_number_of_nodes() == 15
    assert len(graph.get_node_by_type("Import")) == 12
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(7, 1),
            file_path=get_fixture_path("simple_property.cs"),
        )
    ]
    assert (graph.get_node_by_type("Field")) == [
        DependencyGraphNode(
            node_type="Field",
            start_point=(2, 4),
            end_point=(2, 31),
            file_path=get_fixture_path("simple_property.cs"),
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(3, 4),
            end_point=(6, 5),
            file_path=get_fixture_path("simple_property.cs"),
        ),
    ]
    assert DependencyGraphNode(
        node_type="Import",
        start_point=(10, 0),
        end_point=(10, 25),
        file_path=get_fixture_path("imports.cs"),
    ) in graph.get_node_by_type("Import")


def test_class_parent_of_method() -> None:
    graph = DependencyGraph([get_fixture_path("simple_method.cs")])
    assert graph.get_parent_child_relationships() == [
        (
            DependencyGraphNode(
                node_type="Class",
                start_point=(0, 0),
                end_point=(6, 1),
                file_path=get_fixture_path("simple_method.cs"),
            ),
            DependencyGraphNode(
                node_type="Method",
                start_point=(2, 4),
                end_point=(5, 5),
                file_path=get_fixture_path("simple_method.cs"),
            ),
        )
    ]


@pytest.mark.skip(reason="Waiting for tree-sitter-python pip fix")
def test_full_python_relationships() -> None:
    graph_py = DependencyGraph([get_fixture_path("full.py")])
    parent_child_relationships = graph_py.get_parent_child_relationships()
    assert (
        DependencyGraphNode(
            node_type="Class",
            start_point=(6, 0),
            end_point=(39, 23),
            file_path=get_fixture_path("full.py"),
        ),
        DependencyGraphNode(
            node_type="Method",
            start_point=(7, 4),
            end_point=(13, 53),
            file_path=get_fixture_path("full.py"),
        ),
    ) in parent_child_relationships
    assert len(parent_child_relationships) == 5


def test_xml_csproj_files() -> None:
    graph = DependencyGraph(
        [get_fixture_path("random.xml"), get_fixture_path("random.csproj")]
    )
    assert graph.get_number_of_nodes() == 0
    assert graph.get_parent_child_relationships() == []
