from changing_dot.dependency_graph.dependency_graph import (
    DependencyGraph,
    create_dependency_graph_from_folder,
)
from changing_dot.dependency_graph.types import (
    DependencyGraphNodeWithIndex,
    DependencyGraphRelation,
)


def get_fixture_path(file_path: str) -> str:
    return "./tests/core/dependency_graph/python/fixtures/" + file_path


def test_full_python() -> None:
    graph_py = DependencyGraph([get_fixture_path("full.py")])
    assert len(graph_py.get_node_by_type("Import")) == 2
    assert len(graph_py.get_node_by_type("Class")) == 1
    assert len(graph_py.get_node_by_type("Method")) == 4
    assert len(graph_py.get_node_by_type("Constructor")) == 1
    assert len(graph_py.get_node_by_type("Field")) == 0


def test_we_can_give_python_and_folder_path() -> None:
    graph = create_dependency_graph_from_folder(
        get_fixture_path("python_folder"), "python"
    )
    assert graph.get_number_of_nodes() == 2


def test_full_python_relations() -> None:
    graph_py = DependencyGraph([get_fixture_path("full.py")])
    parent_child_relations = graph_py.get_parent_child_relations()
    assert (
        DependencyGraphRelation(
            origin=DependencyGraphNodeWithIndex(
                index=3,
                node_type="Constructor",
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
            target=DependencyGraphNodeWithIndex(
                index=2,
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
            return None""",
            ),
            relation_type="Constructs/ConstructedBy",
        )
        in parent_child_relations
    )
    assert len(parent_child_relations) == 5


def test_pip_requirements_files() -> None:
    graph = DependencyGraph([get_fixture_path("requirements.txt")])
    # for now each element is a method
    assert graph.get_nodes_with_index() == [
        DependencyGraphNodeWithIndex(
            index=0,
            node_type="Method",
            file_path=get_fixture_path("requirements.txt"),
            start_point=(0, 0),
            end_point=(0, 17),
            text="pydantic==1.10.18",
        )
    ]
    assert len(graph.get_parent_child_relations()) == 0
