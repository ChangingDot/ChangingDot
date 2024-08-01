from collections.abc import Generator

import pytest
from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    DependencyGraphNode,
    DependencyGraphNodeWithIndex,
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
    graph.update_graph_from_edits([])
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("subject_1.cs"),
            text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        )
    ]


def test_no_updates() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])
    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=1,
                file_path=get_fixture_path("subject_1.cs"),
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
            )
        ]
    )
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("subject_1.cs"),
            text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        )
    ]


def test_update_with_no_graph_impact() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_1.cs"))

    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=1,
                file_path=get_fixture_path("subject_1.cs"),
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
            )
        ]
    )

    assert graph.get_number_of_nodes() == 2
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("subject_1.cs"),
            text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }
}""",
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
        )
    ]


def test_update_with_no_graph_impact_keeps_same_indexes() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_1.cs"))

    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=1,
                file_path=get_fixture_path("subject_1.cs"),
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
            )
        ]
    )
    assert graph.get_number_of_nodes() == 2
    assert graph.get_nodes_with_index() == [
        DependencyGraphNodeWithIndex(
            index=0,
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("subject_1.cs"),
            text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }
}""",
        ),
        DependencyGraphNodeWithIndex(
            index=1,
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
        ),
    ]


def test_update_that_adds_a_node() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_2.cs"))

    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=0,
                file_path=get_fixture_path("subject_1.cs"),
                before="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
                after="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
    static string AnotherMethod()
    {
        return "Another Hello, World!";
    }
}""",
            )
        ]
    )

    assert graph.get_number_of_nodes() == 3
    for method_dependency in [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(10, 1),
            file_path=get_fixture_path("subject_1.cs"),
            text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
    static string AnotherMethod()
    {
        return "Another Hello, World!";
    }
}""",
        ),
        DependencyGraphNode(
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        ),
        DependencyGraphNode(
            node_type="Method",
            start_point=(6, 4),
            end_point=(9, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string AnotherMethod()
    {
        return "Another Hello, World!";
    }""",
        ),
    ]:
        assert method_dependency in graph.get_nodes()


def test_handle_multiple_files() -> None:
    graph = DependencyGraph(
        [get_fixture_path("subject_1.cs"), get_fixture_path("subject_2.cs")]
    )

    assert graph.get_number_of_nodes() == 4

    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=1,
                file_path=get_fixture_path("subject_1.cs"),
                before="""static string SimpleMethod()
        {
            return "Hello, World!";
        }""",
                after="""static string SimpleMethod()
        {
            return "Hello, World!";
        }""",
            )
        ]
    )

    assert graph.get_number_of_nodes() == 4
