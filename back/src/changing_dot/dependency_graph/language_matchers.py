from changing_dot.dependency_graph.types import (
    DependencyGraphNodeType,
)
from tree_sitter import Node

TerminalToNodeType = dict[str, DependencyGraphNodeType]


class ILanguageMatcher:
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        raise NotImplementedError()


class EmptyMatcher(ILanguageMatcher):
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        return None


c_sharp_terminal_to_node_type: TerminalToNodeType = {
    "class_declaration": "Class",
    "method_declaration": "Method",
    "constructor_declaration": "Constructor",
    "field_declaration": "Field",
    "property_declaration": "Field",
    "using_directive": "Import",
}


class CSharpMatcher(ILanguageMatcher):
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        return c_sharp_terminal_to_node_type.get(ast_node.type)


python_terminal_to_node_type: TerminalToNodeType = {
    "class_definition": "Class",
    "function_definition": "Method",
    "import_statement": "Import",
}


class PythonMatcher(ILanguageMatcher):
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        node_type = python_terminal_to_node_type.get(ast_node.type)

        if (
            node_type == "Method"
            and ast_node.text is not None
            and "def __init__(" in ast_node.text.decode("utf-8")
        ):
            node_type = "Constructor"

        return node_type


pip_req_terminal_to_node_type: TerminalToNodeType = {
    "requirement": "Method",
}


class PipReqMatcher(ILanguageMatcher):
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        return pip_req_terminal_to_node_type.get(ast_node.type)


class XmlMatcher(ILanguageMatcher):
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        if ast_node.type == "element":
            return "Method"
        return None


class CsProjMatcher(ILanguageMatcher):
    def match_class(self, ast_node: Node) -> DependencyGraphNodeType | None:
        if ast_node.type == "element" and self.has_element_descendant(ast_node):
            return "Method"
        return None

    def has_element_descendant(self, node: Node) -> bool:
        for child in node.children:
            if child.type == "element":
                return True
            if self.has_element_descendant(child):
                return True
        return False
