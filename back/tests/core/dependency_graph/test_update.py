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
    base2 = get_fixture("base_2.cs")
    base_full = get_fixture("base_full.cs")
    yield
    write_text(get_fixture_path("subject_1.cs"), base)
    write_text(get_fixture_path("subject_2.cs"), base)
    write_text(get_fixture_path("subject_3.cs"), base2)
    write_text(get_fixture_path("subject_full.cs"), base_full)
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


def test_insensitive_to_spacing_and_line_skips() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])
    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=1,
                file_path=get_fixture_path("subject_1.cs"),
                before=""" static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""   static string SimpleMethod()
        {
            return "Hello, World!";
        }
    """,
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


def test_update_graph_that_shifts_indexes_related_blocks() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("shift.cs"))

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
                after="""// this shifts everything
class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
            )
        ]
    )

    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(7, 1),
            file_path=get_fixture_path("subject_1.cs"),
            text="""// this shifts everything
class SimpleClass
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
            start_point=(3, 4),
            end_point=(6, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        )
    ]


def test_update_graph_that_shifts_indexes_unrelated_blocks() -> None:
    graph = DependencyGraph([get_fixture_path("subject_3.cs")])

    write_text(get_fixture_path("subject_3.cs"), get_fixture("shift_2.cs"))

    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=0,
                file_path=get_fixture_path("subject_3.cs"),
                before="using System;",
                after="// this shifts everything\nusing System;",
            )
        ]
    )

    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(3, 0),
            end_point=(9, 1),
            file_path=get_fixture_path("subject_3.cs"),
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
            start_point=(5, 4),
            end_point=(8, 5),
            file_path=get_fixture_path("subject_3.cs"),
            text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
        )
    ]
    assert (graph.get_node_by_type("Import")) == [
        DependencyGraphNode(
            node_type="Import",
            start_point=(0, 0),
            end_point=(1, 13),
            file_path=get_fixture_path("subject_3.cs"),
            text="// this shifts everything\nusing System;",
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
    for node in [
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
        assert node in graph.get_nodes()

    assert len(graph.get_parent_child_relationships()) == 2
    for relation in [
        (
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
        ),
        (
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
                start_point=(6, 4),
                end_point=(9, 5),
                file_path=get_fixture_path("subject_1.cs"),
                text="""static string AnotherMethod()
    {
        return "Another Hello, World!";
    }""",
            ),
        ),
    ]:
        assert relation in graph.get_parent_child_relationships()


def test_parent_that_updates_child_node() -> None:
    graph = DependencyGraph([get_fixture_path("subject_1.cs")])

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_1.cs"))

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
        return "Updated Hello, World!";
    }
}""",
            )
        ]
    )

    # What we want is for :
    # - the class node to be updated,
    # - the original method node to be removed
    # - a neww updated method node to be created

    assert graph.get_number_of_nodes() == 2
    for node in [
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
            index=2,
            node_type="Method",
            start_point=(2, 4),
            end_point=(5, 5),
            file_path=get_fixture_path("subject_1.cs"),
            text="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
        ),
    ]:
        assert node in graph.get_nodes_with_index()

    assert (
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
        )
        not in graph.get_nodes_with_index()
    )
    assert graph.get_parent_child_relationships() == [
        (
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
            DependencyGraphNode(
                node_type="Method",
                start_point=(2, 4),
                end_point=(5, 5),
                file_path=get_fixture_path("subject_1.cs"),
                text="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
            ),
        )
    ]


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


def test_handle_multiple_files_update_second() -> None:
    graph = DependencyGraph(
        [get_fixture_path("subject_1.cs"), get_fixture_path("subject_2.cs")]
    )

    assert graph.get_number_of_nodes() == 4

    graph.update_graph_from_edits(
        [
            BlockEdit(
                block_id=3,
                file_path=get_fixture_path("subject_2.cs"),
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


def test_handle_multiple_files_update_both() -> None:
    graph = DependencyGraph(
        [get_fixture_path("subject_1.cs"), get_fixture_path("subject_2.cs")]
    )
    write_text(get_fixture_path("subject_1.cs"), get_fixture("shift.cs"))
    write_text(get_fixture_path("subject_2.cs"), get_fixture("update_1.cs"))

    assert graph.get_number_of_nodes() == 4

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
                after="""// this shifts everything
class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
            ),
            BlockEdit(
                block_id=3,
                file_path=get_fixture_path("subject_2.cs"),
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Updated Hello, World!";
    }""",
            ),
        ]
    )

    assert graph.get_number_of_nodes() == 4


def test_no_class_duplication() -> None:
    graph = DependencyGraph([get_fixture_path("subject_full.cs")])

    write_text(get_fixture_path("subject_full.cs"), get_fixture("update_attribute.cs"))

    assert graph.get_number_of_nodes() == 4

    graph.update_graph_from_edits(
        [
            BlockEdit(
                file_path=get_fixture_path("subject_full.cs"),
                block_id=3,
                before="        [JsonIgnore]\n        public int Size { get; set; }\n",
                after="        [JsonDataIgnore]\n        public int Size { get; set; }\n",
            ),
        ]
    )
    assert graph.get_number_of_nodes() == 4


def test_that_if_edits_are_not_in_files_then_raise_assertion_error() -> None:
    graph = DependencyGraph([get_fixture_path("subject_full.cs")])

    # We do not change the file
    # write_text(get_fixture_path("subject_full.cs"),
    #  get_fixture("update_attribute.cs"))

    assert graph.get_number_of_nodes() == 4

    with pytest.raises(AssertionError, match="The files have not been modified"):
        graph.update_graph_from_edits(
            [
                BlockEdit(
                    file_path=get_fixture_path("subject_full.cs"),
                    block_id=3,
                    before="        [JsonIgnore]\n        public int Size { get; set; }\n",
                    after="        [JsonDataIgnore]\n        public int Size { get; set; }\n",
                ),
            ]
        )


def test_block_id_in_wrong_file_raises_error() -> None:
    graph = DependencyGraph(
        [get_fixture_path("subject_1.cs"), get_fixture_path("subject_2.cs")]
    )

    write_text(get_fixture_path("subject_1.cs"), get_fixture("update_1.cs"))

    node = graph.get_nodes_with_index()[0]

    with pytest.raises(AssertionError, match="This block is not in this file"):
        graph.update_graph_from_edits(
            [
                BlockEdit(
                    file_path=get_fixture_path("subject_2.cs"),
                    block_id=node.index,
                    before=node.text,
                    after=node.text,
                ),
            ]
        )
