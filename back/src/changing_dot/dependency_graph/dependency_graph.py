import copy
from collections.abc import Generator
from typing import Any, Literal, TypedDict

import networkx as nx
from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.node_type_to_terminal import (
    NodeTypeToTerminal,
    get_node_type_to_terminal_from_file_path,
    parser_from_file_path,
)
from changing_dot.utils.tree_sitter_utils import get_node_text_from_file_path
from pydantic import BaseModel
from tree_sitter import Node, Tree


def iterate_nodes(
    node: Node, node_types: list[str] | None
) -> Generator[Node | Any, Any, None]:
    if node_types is None or node.type in node_types:
        yield node
    for child in node.children:
        yield from iterate_nodes(child, node_types)


def remove_comments(text: str) -> str:
    return "\n".join(
        line for line in text.split("\n") if not line.strip().startswith("//")
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


class MementoState(TypedDict):
    G: nx.DiGraph
    next_index: int
    trees: list[str]
    file_path_to_node_type_to_terminal: dict[str, NodeTypeToTerminal]


class Memento:
    def __init__(self, state: MementoState):
        self._state = state

    def get_state(self) -> MementoState:
        return self._state


class DependencyGraph:
    def __init__(self, file_paths: list[str]) -> None:
        self.G: nx.DiGraph = nx.DiGraph()
        self.next_index: int = 0
        self.trees: dict[str, Tree] = {}
        self.file_path_to_node_type_to_terminal: dict[str, NodeTypeToTerminal] = {
            path: get_node_type_to_terminal_from_file_path(path) for path in file_paths
        }
        self.create_graph_from_file_paths(sorted(set(file_paths)))
        self._saved_state: Memento

    def save_state(self) -> None:
        state: MementoState = {
            "G": copy.deepcopy(self.G),
            "next_index": self.next_index,
            "trees": list(self.trees.keys()),
            "file_path_to_node_type_to_terminal": copy.deepcopy(
                self.file_path_to_node_type_to_terminal
            ),
        }
        memento = Memento(state)
        self._saved_state = memento

    def revert(self) -> None:
        assert self._saved_state
        previous_state = self._saved_state.get_state()
        for path in previous_state["trees"]:
            parser = parser_from_file_path(path)
            if parser is None:
                continue
            with open(path) as file:
                code = file.read()
            tree = parser.parse(bytes(code, "utf8"))
            self.trees[path] = tree
        self.G = previous_state["G"]
        self.next_index = previous_state["next_index"]
        self.file_path_to_node_type_to_terminal = previous_state[
            "file_path_to_node_type_to_terminal"
        ]

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

    def update_graph_from_edits(self, edits: list[BlockEdit]) -> None:
        for edit in edits:
            with open(edit.file_path) as file:
                code_to_check: str = file.read()

            # Check that edit file_path and block ID are compatible
            node = self.get_node(edit.block_id)
            assert node.file_path == edit.file_path, "This block is not in this file"

            # Check that the files have actually been changed before updating graph
            assert edit.after.replace(" ", "").replace(
                "\n", ""
            ) in code_to_check.replace(" ", "").replace(
                "\n", ""
            ), "The files have not been modified"

        for edit in edits:
            parser = parser_from_file_path(edit.file_path)
            if parser is None:
                continue
            with open(edit.file_path) as file:
                code: str = file.read()
            new_tree = parser.parse(bytes(code, "utf8"))
            self.trees[edit.file_path] = new_tree

            # update the node
            ast_node = self.update_node_given_tree_and_text(
                new_tree, edit.block_id, edit.after
            )

            # update the parent nodes
            for parent_node_index in self.get_parent_nodes(edit.block_id):
                parent_node = self.get_node(parent_node_index)

                new_parent_text = parent_node.text.replace(edit.before, edit.after)

                self.update_node_given_tree_and_text(
                    new_tree,
                    parent_node_index,
                    new_parent_text,
                )
            # remove all the children nodes and replace them
            for child_node_index in self.get_children_nodes(edit.block_id):
                self.remove_node(child_node_index)
            for ast_child in ast_node.named_children:
                self.traverse_and_reduce(ast_child, edit.file_path, edit.block_id)

            # update all nodes that are below the node ( that may shift )
            for other_node in self.get_nodes_with_index():
                # compare to start_point because new end
                # point might be lower that old one
                if (
                    other_node.file_path == edit.file_path
                    and other_node.end_point[0] > ast_node.start_point[0]
                ):
                    self.update_node_given_tree_and_text(
                        new_tree,
                        other_node.index,
                        other_node.text,
                    )

    def create_graph_from_tree(self, tree: Tree, file_path: str) -> None:
        self.traverse_and_reduce(tree.root_node, file_path)

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

    def remove_node(self, node_index: int) -> None:
        self.G.remove_node(node_index)

    def update_node(self, index: int, node: DependencyGraphNode) -> None:
        self.G.nodes[index]["node_type"] = node.node_type
        self.G.nodes[index]["start_point"] = node.start_point
        self.G.nodes[index]["end_point"] = node.end_point
        self.G.nodes[index]["file_path"] = node.file_path
        self.G.nodes[index]["text"] = node.text

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

    def get_parent_nodes(self, index: int) -> list[int]:
        return list(nx.ancestors(self.G, index))

    def get_children_nodes(self, index: int) -> list[int]:
        return list(nx.descendants(self.G, index))

    def update_node_given_tree_and_text(
        self,
        new_tree: Tree,
        node_index: int,
        text: str,
    ) -> Node:
        node = self.get_node(node_index)

        matched_nodes = [
            ast_node
            for ast_node in iterate_nodes(
                new_tree.root_node,
                self.file_path_to_node_type_to_terminal[node.file_path][node.node_type],
            )
            if ast_node.text is not None
            and isinstance(ast_node.text, bytes)
            and ast_node.text.decode("utf-8").replace(" ", "").replace("\n", "")
            == remove_comments(text).replace(" ", "").replace("\n", "")
        ]

        assert len(matched_nodes) == 1

        updated_node = self.create_graph_node_from_ast_node(
            matched_nodes[0], node.file_path
        )

        assert updated_node is not None

        # update match nodes
        self.update_node(node_index, updated_node)

        return matched_nodes[0]

    def traverse_and_reduce(
        self, node: Node, file_path: str, parent_index: int | None = None
    ) -> None:
        node_index = None

        new_node = self.create_graph_node_from_ast_node(node, file_path)

        if new_node is not None:
            node_index = self.add_node(new_node)
            if parent_index is not None:
                self.add_edge(parent_index, node_index)

        for child in node.children:
            self.traverse_and_reduce(
                child, file_path, node_index if node_index is not None else parent_index
            )

    def create_graph_node_from_ast_node(
        self, node: Node, file_path: str
    ) -> DependencyGraphNode | None:
        comment_node = None

        if node.prev_sibling is not None and node.prev_sibling.type == "comment":
            comment_node = node.prev_sibling

        comment_text = (
            f"{comment_node.text.decode('utf-8')}\n"
            if comment_node is not None and isinstance(comment_node.text, bytes)
            else ""
        )

        start_point = (
            node.start_point if comment_node is None else comment_node.start_point
        )

        node_type: Literal["Import", "Class", "Method", "Field"] | None = None
        if node.type in self.file_path_to_node_type_to_terminal[file_path]["Class"]:
            node_type = "Class"
        elif node.type in self.file_path_to_node_type_to_terminal[file_path]["Method"]:
            node_type = "Method"
        elif node.type in self.file_path_to_node_type_to_terminal[file_path]["Field"]:
            node_type = "Field"
        elif node.type in self.file_path_to_node_type_to_terminal[file_path]["Import"]:
            node_type = "Import"

        if node_type is None:
            return None

        return DependencyGraphNode(
            node_type=node_type,
            start_point=start_point,
            end_point=node.end_point,
            file_path=file_path,
            text=f"{comment_text}{get_node_text_from_file_path(node, file_path)}",
        )
