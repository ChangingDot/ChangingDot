from changing_dot.dependency_graph.types import (
    DependencyGraphNodeType,
    NodeTypeToTerminal,
)
from tree_sitter import Node


class ILanguageMatcher:
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        raise NotImplementedError()


class EmptyMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        return False


c_sharp_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": ["class_declaration"],
    "Method": ["method_declaration"],
    "Constructor": ["constructor_declaration"],
    "Field": ["field_declaration", "property_declaration"],
    "Import": ["using_directive"],
}


class CSharpMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        return ast_node.type in c_sharp_node_type_to_terminal[node_type]


python_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": ["class_definition"],
    "Method": ["function_definition"],
    "Constructor": [],
    "Field": [],
    "Import": ["import_statement"],
}


class PythonMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        if node_type != "Constructor" and node_type != "Method":
            return ast_node.type in python_node_type_to_terminal[node_type]
        else:
            if node_type == "Constructor":
                return (
                    ast_node.type in python_node_type_to_terminal["Method"]
                    and ast_node.text is not None
                    and "def __init__(" in ast_node.text.decode("utf-8")
                )
            elif node_type == "Method":
                return ast_node.type in python_node_type_to_terminal["Method"] and not (
                    ast_node.text is not None
                    and "def __init__(" in ast_node.text.decode("utf-8")
                )


pip_req_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": [],
    "Method": ["requirement"],
    "Constructor": [],
    "Field": [],
    "Import": [],
}


class PipReqMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        return ast_node.type in pip_req_node_type_to_terminal[node_type]


class XmlMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        if node_type != "Method":
            return False
        return ast_node.type == "element"


class CsProjMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        if node_type != "Method":
            return False
        return ast_node.type == "element" and self.has_element_descendant(ast_node)

    def has_element_descendant(self, node: Node) -> bool:
        for child in node.children:
            if child.type == "element":
                return True
            if self.has_element_descendant(child):
                return True
        return False
