import copy
from collections.abc import Generator
from typing import Any, TypedDict

import networkx as nx
from changing_dot.custom_types import BlockEdit
from changing_dot.dependency_graph.language_matchers import ILanguageMatcher
from changing_dot.dependency_graph.node_type_to_terminal import (
    get_matcher_from_file_path,
    parser_from_file_path,
)
from changing_dot.dependency_graph.types import (
    DependencyGraphNode,
    DependencyGraphNodeType,
    DependencyGraphNodeWithIndex,
    DependencyGraphRelation,
    RelationType,
    SupportedLanguages,
)
from changing_dot.utils.file_utils import get_csharp_files, get_python_files
from changing_dot.utils.text_functions import read_text
from changing_dot.utils.tree_sitter_utils import get_node_text_from_file_path
from tree_sitter import Node, Tree


def iterate_nodes(node: Node) -> Generator[Node | Any, Any, None]:
    yield node
    for child in node.children:
        yield from iterate_nodes(child)


def remove_comments(text: str) -> str:
    return "\n".join(
        line for line in text.split("\n") if not line.strip().startswith("//")
    )


class MementoState(TypedDict):
    G: nx.DiGraph
    next_index: int
    trees: list[str]
    file_path_to_language_matcher: dict[str, ILanguageMatcher]


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
        self.file_path_to_language_matcher: dict[str, ILanguageMatcher] = {
            path: get_matcher_from_file_path(path) for path in file_paths
        }
        self.create_graph_from_file_paths(sorted(set(file_paths)))
        self._saved_state: Memento

    def save_state(self) -> None:
        state: MementoState = {
            "G": copy.deepcopy(self.G),
            "next_index": self.next_index,
            "trees": list(self.trees.keys()),
            "file_path_to_language_matcher": copy.deepcopy(
                self.file_path_to_language_matcher
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
            code = read_text(path)
            tree = parser.parse(bytes(code, "utf8"))
            self.trees[path] = tree
        self.G = previous_state["G"]
        self.next_index = previous_state["next_index"]
        self.file_path_to_language_matcher = previous_state[
            "file_path_to_language_matcher"
        ]

    def create_graph_from_file_paths(self, file_paths: list[str]) -> None:
        for path in file_paths:
            parser = parser_from_file_path(path)
            if parser is None:
                continue
            code = read_text(path)
            tree = parser.parse(bytes(code, "utf8"))
            self.create_graph_from_tree(tree, path)
            self.trees[path] = tree

    def update_graph_from_edits(self, edits: list[BlockEdit]) -> None:
        for edit in edits:
            code_to_check = read_text(edit.file_path)

            # Check that edit file_path and block ID are compatible
            node = self.get_node(edit.block_id)
            assert node.file_path == edit.file_path, "This block is not in this file"

            assert edit.before.replace(" ", "").replace("\n", "") in node.text.replace(
                " ", ""
            ).replace("\n", ""), "The before does not match the text in block"

            # Check that the files have actually been changed before updating graph
            assert edit.after.replace(" ", "").replace(
                "\n", ""
            ) in code_to_check.replace(" ", "").replace(
                "\n", ""
            ), "The files have not been modified"

        for edit in edits:
            original_start_point = self.get_node(edit.block_id).start_point[0]
            parent_nodes = self.get_parent_nodes(edit.block_id)
            children_nodes = self.get_children_nodes(edit.block_id)

            parser = parser_from_file_path(edit.file_path)
            if parser is None:
                continue
            code = read_text(edit.file_path)
            new_tree = parser.parse(bytes(code, "utf8"))
            self.trees[edit.file_path] = new_tree

            # update the node
            ast_node = self.update_node_given_tree_and_text(
                new_tree, edit.block_id, edit.after
            )

            # update the parent nodes
            for parent_node_index in parent_nodes:
                parent_node = self.get_node(parent_node_index)

                new_parent_text = parent_node.text.replace(edit.before, edit.after)

                self.update_node_given_tree_and_text(
                    new_tree,
                    parent_node_index,
                    new_parent_text,
                )
            # remove all the children nodes and replace them
            for child_node_index in children_nodes:
                self.remove_node(child_node_index)

            # if ast node is none then there are no children
            if ast_node is not None:
                for ast_child in ast_node.named_children:
                    self.traverse_and_reduce(ast_child, edit.file_path, edit.block_id)

            # update all nodes that are below the node ( that may shift )
            for other_node in self.get_nodes_with_index():
                # compare to start_point because new end
                # point might be lower that old one
                if (
                    other_node.file_path == edit.file_path
                    and other_node.end_point[0] > original_start_point
                ):
                    self.update_node_given_tree_and_text(
                        new_tree,
                        other_node.index,
                        other_node.text,
                    )

    def create_graph_from_tree(self, tree: Tree, file_path: str) -> None:
        self.traverse_and_reduce(tree.root_node, file_path)

    def add_edge(self, source: int, target: int, relation_type: RelationType) -> None:
        self.G.add_edge(source, target, relation_type=relation_type)

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

    def get_node_with_index(self, index: int) -> DependencyGraphNodeWithIndex:
        node = self.G.nodes()[index]
        return DependencyGraphNodeWithIndex(**node, index=index)

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

    def get_parent_child_relations(
        self,
    ) -> list[DependencyGraphRelation]:
        parent_child_relations: list[DependencyGraphRelation] = []

        for i, j, metadata in self.G.edges(data=True):
            parent_child_relations.append(
                DependencyGraphRelation(
                    origin=self.get_node_with_index(i),
                    target=self.get_node_with_index(j),
                    relation_type=metadata["relation_type"],
                )
            )

        return parent_child_relations

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
    ) -> Node | None:
        text_to_match = remove_comments(text).replace(" ", "").replace("\n", "")

        # edge case where you remove a block
        # In that case you can't find a node in tree-sitter, because it doen not
        # exist anymore so we remove associated node
        if text_to_match == "":
            self.remove_node(node_index)
            return None

        node = self.get_node(node_index)

        language_matcher = self.file_path_to_language_matcher[node.file_path]

        matched_nodes = [
            ast_node
            for ast_node in iterate_nodes(new_tree.root_node)
            if language_matcher.match_class(ast_node) == node.node_type
            and ast_node.text is not None
            and isinstance(ast_node.text, bytes)
            and remove_comments(ast_node.text.decode("utf-8"))
            .replace(" ", "")
            .replace("\n", "")
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
            relation_type: RelationType = (
                "Constructs/ConstructedBy"
                if new_node.node_type == "Constructor"
                else "ParentOf/ChildOf"
            )

            if parent_index is not None:
                if relation_type == "Constructs/ConstructedBy":
                    self.add_edge(node_index, parent_index, relation_type)
                else:
                    self.add_edge(parent_index, node_index, relation_type)

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

        node_type: DependencyGraphNodeType | None = self.file_path_to_language_matcher[
            file_path
        ].match_class(node)

        if node_type is None:
            return None

        return DependencyGraphNode(
            node_type=node_type,
            start_point=start_point,
            end_point=node.end_point,
            file_path=file_path,
            text=f"{comment_text}{get_node_text_from_file_path(node, file_path)}",
        )


def create_dependency_graph_from_folder(
    folder_path: str, language: SupportedLanguages
) -> DependencyGraph:
    if language == "python":
        python_files = get_python_files(folder_path)
        return DependencyGraph(python_files)
    if language == "c_sharp":
        python_files = get_csharp_files(folder_path)
        return DependencyGraph(python_files)

    else:
        raise NotImplementedError("This language is not implemented yet")
