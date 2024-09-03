from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
)
from changing_dot.dependency_graph.types import (
    DependencyGraphNode,
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
            text="""public class Person
{
    public string Name { get; }
    public Person(string name)
    {
        Name = name;
    }
}""",
        )
    ]
    assert (graph.get_node_by_type("Field")) == [
        DependencyGraphNode(
            node_type="Field",
            start_point=(2, 4),
            end_point=(2, 31),
            file_path=get_fixture_path("simple_property.cs"),
            text="""public string Name { get; }""",
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(3, 4),
            end_point=(6, 5),
            file_path=get_fixture_path("simple_property.cs"),
            text="""public Person(string name)
    {
        Name = name;
    }""",
        ),
    ]
    assert DependencyGraphNode(
        node_type="Import",
        start_point=(10, 0),
        end_point=(10, 25),
        file_path=get_fixture_path("imports.cs"),
        text="using PostHog.Exceptions;",
    ) in graph.get_node_by_type("Import")
