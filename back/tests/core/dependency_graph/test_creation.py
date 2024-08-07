import pytest
from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
)
from changing_dot.dependency_graph.types import (
    DependencyGraphNode,
    DependencyGraphNodeWithIndex,
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
            text="""class GenericClass:
    def __init__(
        self, name: str, value: int, created_at: datetime.datetime | None = None
    ):
        self.name = name
        self.value = value
        self.created_at = created_at if created_at else datetime.datetime.now()
        logging.info(f"GenericClass created: {self}")

    def __repr__(self) -> str:
        return f"GenericClass(name={self.name}, value={self.value}, created_at={self.created_at})"

    def update_value(self, new_value: int) -> None:
        logging.info(f"Updating value from {self.value} to {new_value}")
        self.value = new_value

    def save_to_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w") as file:
                file.write(str(self))
            logging.info(f"Object saved to file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save object to file: {e}")

    def load_from_file(cls, file_path: str) -> None:
        try:
            with open(file_path) as file:
                data = file.read()
            name, value, created_at = data.strip().split(", ")
            name = name.split("=")[1]
            return None
        except Exception as e:
            logging.error(f"Failed to load object from file: {e}")
            return None
""",
        ),
        DependencyGraphNode(
            node_type="Method",
            start_point=(7, 4),
            end_point=(13, 53),
            file_path=get_fixture_path("full.py"),
            text="""def __init__(
        self, name: str, value: int, created_at: datetime.datetime | None = None
    ):
        self.name = name
        self.value = value
        self.created_at = created_at if created_at else datetime.datetime.now()
        logging.info(f"GenericClass created: {self}")""",
        ),
    ) in parent_child_relationships
    assert len(parent_child_relationships) == 5


def test_xml_csproj_files() -> None:
    graph = DependencyGraph(
        [get_fixture_path("random.xml"), get_fixture_path("random.csproj")]
    )
    # for now each element is a method
    assert graph.get_number_of_nodes() == 38 + 16
    assert len(graph.get_parent_child_relationships()) == 37 + 15


def test_csproj_files() -> None:
    graph = DependencyGraph([get_fixture_path("small.csproj")])
    # for now each element is a method
    assert graph.get_number_of_nodes() == 6
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
            start_point=(3, 4),
            end_point=(3, 32),
            text="<OutputType>Exe</OutputType>",
        ),
        DependencyGraphNodeWithIndex(
            index=3,
            node_type="Method",
            file_path=get_fixture_path("small.csproj"),
            start_point=(4, 4),
            end_point=(4, 45),
            text="<TargetFramework>net6.0</TargetFramework>",
        ),
        DependencyGraphNodeWithIndex(
            index=4,
            node_type="Method",
            file_path=get_fixture_path("small.csproj"),
            start_point=(7, 2),
            end_point=(9, 14),
            text='<ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>',
        ),
        DependencyGraphNodeWithIndex(
            index=5,
            node_type="Method",
            file_path=get_fixture_path("small.csproj"),
            start_point=(8, 4),
            end_point=(8, 67),
            text='<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />',
        ),
    ]
    assert len(graph.get_parent_child_relationships()) == 5

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
        (
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(2, 2),
                end_point=(5, 18),
                text="<PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>",
            ),
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(3, 4),
                end_point=(3, 32),
                text="<OutputType>Exe</OutputType>",
            ),
        ),
        (
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(2, 2),
                end_point=(5, 18),
                text="<PropertyGroup>\n    <OutputType>Exe</OutputType>\n    <TargetFramework>net6.0</TargetFramework>\n  </PropertyGroup>",
            ),
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(4, 4),
                end_point=(4, 45),
                text="<TargetFramework>net6.0</TargetFramework>",
            ),
        ),
        (
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(7, 2),
                end_point=(9, 14),
                text='<ItemGroup>\n    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />\n  </ItemGroup>',
            ),
            DependencyGraphNode(
                node_type="Method",
                file_path=get_fixture_path("small.csproj"),
                start_point=(8, 4),
                end_point=(8, 67),
                text='<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />',
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
