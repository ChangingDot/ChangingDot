from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    create_dependency_graph_from_folder,
)
from changing_dot.dependency_graph.types import (
    DependencyGraphNode,
    DependencyGraphNodeWithIndex,
)


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/c_sharp/fixtures/" + file_path


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
        text="""public class EmptyClass
{
}""",
    )
    assert graph.get_parent_child_relationships() == []


def test_empty_class_multiple_times_same_file_path() -> None:
    graph = DependencyGraph(
        [
            get_fixture_path("empty_class.cs"),
            get_fixture_path("empty_class.cs"),
            get_fixture_path("empty_class.cs"),
        ]
    )
    assert graph.get_number_of_nodes() == 1
    assert graph.get_node(0) == DependencyGraphNode(
        node_type="Class",
        start_point=(0, 0),
        end_point=(2, 1),
        file_path=get_fixture_path("empty_class.cs"),
        text="""public class EmptyClass
{
}""",
    )
    assert graph.get_parent_child_relationships() == []


def test_multiple_files() -> None:
    graph = DependencyGraph(
        [
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


def test_simple_method() -> None:
    graph = DependencyGraph([get_fixture_path("simple_method.cs")])
    assert graph.get_number_of_nodes() == 2
    assert graph.get_node_by_type("Class") == [
        DependencyGraphNode(
            node_type="Class",
            start_point=(0, 0),
            end_point=(6, 1),
            file_path=get_fixture_path("simple_method.cs"),
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
            file_path=get_fixture_path("simple_method.cs"),
            text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
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
            text="""public class SimpleField
{
    public int Field;
}""",
        )
    ]
    assert (graph.get_node_by_type("Field")) == [
        DependencyGraphNode(
            node_type="Field",
            start_point=(2, 4),
            end_point=(2, 21),
            file_path=get_fixture_path("simple_field.cs"),
            text="""public int Field;""",
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
            text="""public class Person
{
    public string Name;
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
            end_point=(2, 23),
            file_path=get_fixture_path("simple_constructor.cs"),
            text="""public string Name;""",
        ),
    ]
    assert (graph.get_node_by_type("Method")) == [
        DependencyGraphNode(
            node_type="Method",
            start_point=(3, 4),
            end_point=(6, 5),
            file_path=get_fixture_path("simple_constructor.cs"),
            text="""public Person(string name)
    {
        Name = name;
    }""",
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


def test_imports() -> None:
    graph = DependencyGraph([get_fixture_path("imports.cs")])
    assert len(graph.get_node_by_type("Import")) == 12
    assert DependencyGraphNode(
        node_type="Import",
        start_point=(10, 0),
        end_point=(10, 25),
        file_path=get_fixture_path("imports.cs"),
        text="using PostHog.Exceptions;",
    ) in graph.get_node_by_type("Import")


def test_comments_are_added_to_block() -> None:
    graph = DependencyGraph([get_fixture_path("comments.cs")])
    assert DependencyGraphNode(
        node_type="Import",
        start_point=(0, 0),
        end_point=(1, 33),
        file_path=get_fixture_path("comments.cs"),
        text="// comment added to import\nusing System.Collections.Generic;",
    ) in graph.get_node_by_type("Import")
    assert DependencyGraphNode(
        node_type="Method",
        start_point=(5, 4),
        end_point=(9, 5),
        file_path=get_fixture_path("comments.cs"),
        text="""// Comment added to method
static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
    ) in graph.get_node_by_type("Method")
    assert DependencyGraphNode(
        node_type="Class",
        start_point=(2, 0),
        end_point=(10, 1),
        file_path=get_fixture_path("comments.cs"),
        text="""// comment added to class
class SimpleClass
{
    // Comment added to method
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
    ) in graph.get_node_by_type("Class")


def test_class_parent_of_method() -> None:
    graph = DependencyGraph([get_fixture_path("simple_method.cs")])
    assert graph.get_parent_child_relationships() == [
        (
            DependencyGraphNode(
                node_type="Class",
                start_point=(0, 0),
                end_point=(6, 1),
                file_path=get_fixture_path("simple_method.cs"),
                text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
            ),
            DependencyGraphNode(
                node_type="Method",
                start_point=(2, 4),
                end_point=(5, 5),
                file_path=get_fixture_path("simple_method.cs"),
                text="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
            ),
        )
    ]


def test_xml_csproj_files() -> None:
    graph = DependencyGraph(
        [get_fixture_path("random.xml"), get_fixture_path("random.csproj")]
    )
    # for now each element is a method
    assert graph.get_number_of_nodes() == 38 + 7
    assert len(graph.get_parent_child_relationships()) == 37 + 6


def test_csproj_files() -> None:
    graph = DependencyGraph([get_fixture_path("small.csproj")])
    # for now each element is a method
    assert graph.get_number_of_nodes() == 3
    assert graph.get_nodes_with_index() == [
        DependencyGraphNodeWithIndex(
            index=0,
            node_type="Method",
            file_path=get_fixture_path("small.csproj"),
            start_point=(0, 0),
            end_point=(11, 10),
            text='<Project Sdk="Microsoft.NET.Sdk">\n\n  <PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>\n\n  <ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>\n\n</Project>',
        ),
        DependencyGraphNodeWithIndex(
            index=1,
            node_type="Method",
            file_path=get_fixture_path("small.csproj"),
            start_point=(2, 2),
            end_point=(5, 18),
            text="<PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>",
        ),
        DependencyGraphNodeWithIndex(
            index=2,
            node_type="Method",
            file_path=get_fixture_path("small.csproj"),
            start_point=(7, 2),
            end_point=(9, 14),
            text='<ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>',
        ),
    ]
    assert len(graph.get_parent_child_relationships()) == 2

    for relationship in [
        (
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(0, 0),
                end_point=(11, 10),
                text='<Project Sdk="Microsoft.NET.Sdk">\n\n  <PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>\n\n  <ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>\n\n</Project>',
            ),
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(2, 2),
                end_point=(5, 18),
                text="<PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>",
            ),
        ),
        (
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(0, 0),
                end_point=(11, 10),
                text='<Project Sdk="Microsoft.NET.Sdk">\n\n  <PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>\n\n  <ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>\n\n</Project>',
            ),
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(7, 2),
                end_point=(9, 14),
                text='<ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>',
            ),
        ),
    ]:
        assert relationship in graph.get_parent_child_relationships()


def test_relations_in_multiple_files() -> None:
    graph = DependencyGraph(
        [
            get_fixture_path("simple_method.cs"),
            get_fixture_path("simple_constructor.cs"),
        ]
    )

    assert len(graph.get_parent_child_relationships()) == 3

    for relation in [
        (
            DependencyGraphNode(
                node_type="Class",
                start_point=(0, 0),
                end_point=(6, 1),
                file_path=get_fixture_path("simple_method.cs"),
                text="""class SimpleClass
{
    static string SimpleMethod()
    {
        return "Hello, World!";
    }
}""",
            ),
            DependencyGraphNode(
                node_type="Method",
                start_point=(2, 4),
                end_point=(5, 5),
                file_path=get_fixture_path("simple_method.cs"),
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
                end_point=(7, 1),
                file_path=get_fixture_path("simple_constructor.cs"),
                text="""public class Person
{
    public string Name;
    public Person(string name)
    {
        Name = name;
    }
}""",
            ),
            DependencyGraphNode(
                node_type="Method",
                start_point=(3, 4),
                end_point=(6, 5),
                file_path=get_fixture_path("simple_constructor.cs"),
                text="""public Person(string name)
    {
        Name = name;
    }""",
            ),
        ),
        (
            DependencyGraphNode(
                node_type="Class",
                start_point=(0, 0),
                end_point=(7, 1),
                file_path=get_fixture_path("simple_constructor.cs"),
                text="""public class Person
{
    public string Name;
    public Person(string name)
    {
        Name = name;
    }
}""",
            ),
            DependencyGraphNode(
                node_type="Field",
                start_point=(2, 4),
                end_point=(2, 23),
                file_path=get_fixture_path("simple_constructor.cs"),
                text="""public string Name;""",
            ),
        ),
    ]:
        assert relation in graph.get_parent_child_relationships()


def test_we_can_give_c_sharp_and_folder_path() -> None:
    graph = create_dependency_graph_from_folder(get_fixture_path("folder"), "c_sharp")
    assert graph.get_number_of_nodes() == 2
