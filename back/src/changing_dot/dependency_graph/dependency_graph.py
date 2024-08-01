from typing import TYPE_CHECKING, Literal

import networkx as nx
from changing_dot.dependency_graph.node_type_to_terminal import (
    get_node_type_to_terminal_from_file_path,
    parser_from_file_path,
)
from changing_dot.utils.tree_sitter_utils import get_node_text_from_file_path
from pydantic import BaseModel
from tree_sitter import Node, Range, Tree

if TYPE_CHECKING:
    from changing_dot.dependency_graph.node_type_to_terminal import (
        NodeTypeToTerminal,
    )

DependencyGraphNodeType = Literal["Import", "Class", "Method", "Field"]


class DependencyGraphNode(BaseModel):
    node_type: DependencyGraphNodeType
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    file_path: str
    text: str


class DependencyGraphNodeWithIndex(DependencyGraphNode):
    index: int


class DependencyGraph:
    def __init__(self, file_paths: list[str]) -> None:
        self.G: nx.DiGraph = nx.DiGraph()
        self.next_index: int = 0
        self.trees: dict[str, Tree] = {}
        self.file_path_to_node_type_to_terminal: dict[str, NodeTypeToTerminal] = {
            path: get_node_type_to_terminal_from_file_path(path) for path in file_paths
        }
        self.create_graph_from_file_paths(file_paths)

    def create_graph_from_file_paths(self, file_paths: list[str]) -> None:
        for path in file_paths:
            parser = parser_from_file_path(path)
            if parser is None:
                continue
            with open(path) as file:
                code = file.read()
            tree = parser.parse(bytes(code, "utf8"))
            self.create_graph_from_tree(tree, path)
            self.trees[path] = tree

    def update_graph_from_file_paths(self, file_paths: list[str]) -> list[Range]:
        self.next_index = 0
        all_change_ranges = []
        for path in file_paths:
            parser = parser_from_file_path(path)
            if parser is None:
                continue
            with open(path) as file:
                code: str = file.read()
            new_tree = parser.parse(bytes(code, "utf8"))
            if path in self.trees:
                old_tree = self.trees[path]
                changed_ranges = old_tree.changed_ranges(new_tree)
                all_change_ranges += changed_ranges
                nodes_to_remove = [
                    node
                    for node, data in self.G.nodes(data=True)
                    if data.get("file_path") == path
                ]
                self.G.remove_nodes_from(nodes_to_remove)
                self.create_graph_from_tree(new_tree, path)
            self.trees[path] = new_tree
        return all_change_ranges

    def create_graph_from_tree(self, tree: Tree, file_path: str) -> None:
        def traverse_and_reduce(node: Node, parent_index: int | None = None) -> None:
            node_index = None

            if node.type in self.file_path_to_node_type_to_terminal[file_path]["Class"]:
                node_index = self.add_node(
                    DependencyGraphNode(
                        node_type="Class",
                        start_point=node.start_point,
                        end_point=node.end_point,
                        file_path=file_path,
                        text=get_node_text_from_file_path(node, file_path),
                    )
                )
                if parent_index is not None:
                    self.add_edge(parent_index, node_index)

            elif (
                node.type
                in self.file_path_to_node_type_to_terminal[file_path]["Method"]
            ):
                node_index = self.add_node(
                    DependencyGraphNode(
                        node_type="Method",
                        start_point=node.start_point,
                        end_point=node.end_point,
                        file_path=file_path,
                        text=get_node_text_from_file_path(node, file_path),
                    )
                )
                if parent_index is not None:
                    self.add_edge(parent_index, node_index)

            elif (
                node.type in self.file_path_to_node_type_to_terminal[file_path]["Field"]
            ):
                node_index = self.add_node(
                    DependencyGraphNode(
                        node_type="Field",
                        start_point=node.start_point,
                        end_point=node.end_point,
                        file_path=file_path,
                        text=get_node_text_from_file_path(node, file_path),
                    )
                )
                if parent_index is not None:
                    self.add_edge(parent_index, node_index)

            elif (
                node.type
                in self.file_path_to_node_type_to_terminal[file_path]["Import"]
            ):
                node_index = self.add_node(
                    DependencyGraphNode(
                        node_type="Import",
                        start_point=node.start_point,
                        end_point=node.end_point,
                        file_path=file_path,
                        text=get_node_text_from_file_path(node, file_path),
                    )
                )
                if parent_index is not None:
                    self.add_edge(parent_index, node_index)

            for child in node.children:
                traverse_and_reduce(
                    child, node_index if node_index is not None else parent_index
                )

        traverse_and_reduce(tree.root_node)

    def add_edge(self, source: int, target: int) -> None:
        self.G.add_edge(source, target)

    def add_node(self, node: DependencyGraphNode) -> int:
        index = self.next_index
        self.G.add_node(
            index,
            node_type=node.node_type,
            start_point=node.start_point,
            end_point=node.end_point,
            file_path=node.file_path,
            text=node.text,
        )
        self.next_index += 1
        return index

    def get_number_of_nodes(self) -> int:
        n: int = nx.number_of_nodes(self.G)
        return n

    def get_node(self, index: int) -> DependencyGraphNode:
        node = self.G.nodes()[index]
        return DependencyGraphNode(**node)

    def get_node_by_type(
        self, node_type: DependencyGraphNodeType
    ) -> list[DependencyGraphNode]:
        return [
            DependencyGraphNode(**self.G.nodes()[index])
            for index in self.G.nodes()
            if self.G.nodes()[index]["node_type"] == node_type
        ]

    def get_nodes(self) -> list[DependencyGraphNode]:
        return [
            DependencyGraphNode(**self.G.nodes()[index]) for index in self.G.nodes()
        ]

    def get_nodes_with_index(self) -> list[DependencyGraphNodeWithIndex]:
        return [
            DependencyGraphNodeWithIndex(**self.G.nodes()[index], index=index)
            for index in self.G.nodes()
        ]

    def get_parent_child_relationships(
        self,
    ) -> list[tuple[DependencyGraphNode, DependencyGraphNode]]:
        parent_child_relationships: list[
            tuple[DependencyGraphNode, DependencyGraphNode]
        ] = []

        for i, j in self.G.edges():
            parent_child_relationships.append((self.get_node(i), self.get_node(j)))

        return parent_child_relationships

    def has_syntax_errors(self) -> bool:
        return any(tree.root_node.has_error for tree in self.trees.values())
