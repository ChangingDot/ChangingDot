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
    "Method": ["method_declaration", "constructor_declaration"],
    "Field": ["field_declaration", "property_declaration"],
    "Import": ["using_directive"],
}


class CSharpMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        return ast_node.type in c_sharp_node_type_to_terminal[node_type]


python_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": ["class_definition"],
    "Method": ["function_definition"],
    "Field": [],
    "Import": ["import_statement"],
}


class PythonMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        return ast_node.type in python_node_type_to_terminal[node_type]


xml_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": [],
    "Method": ["element"],
    "Field": [],
    "Import": [],
}


class XmlMatcher(ILanguageMatcher):
    def match_class(self, node_type: DependencyGraphNodeType, ast_node: Node) -> bool:
        return ast_node.type in xml_node_type_to_terminal[node_type]
