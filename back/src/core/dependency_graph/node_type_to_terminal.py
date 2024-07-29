import tree_sitter_c_sharp as tscsharp
from core.custom_types import SupportedLanguages
from core.utils.file_utils import get_file_extension
from tree_sitter import Language, Parser
from tree_sitter_xml import language_xml
from typing_extensions import TypedDict


class NodeTypeToTerminal(TypedDict):
    Import: list[str]
    Class: list[str]
    Method: list[str]
    Field: list[str]


c_sharp_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": ["class_declaration"],
    "Method": ["method_declaration", "constructor_declaration"],
    "Field": ["field_declaration", "property_declaration"],
    "Import": ["using_directive"],
}


python_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": ["class_definition"],
    "Method": ["function_definition"],
    "Field": [],
    "Import": ["import_statement"],
}

empty_node_type_to_terminal: NodeTypeToTerminal = {
    "Class": [],
    "Method": [],
    "Field": [],
    "Import": [],
}


extension_to_language: dict["str", SupportedLanguages] = {
    "py": "python",
    "cs": "c_sharp",
    "csproj": "xml",
    "xml": "xml",
}

CS_LANGUAGE = Language(tscsharp.language())
XML_LANGUAGE = Language(language_xml())


def parser_from_file_path(file_path: str) -> Parser | None:
    file_extension = get_file_extension(file_path)
    language = extension_to_language.get(file_extension)
    if language is None:
        return None
    if language == "python":
        raise NotImplementedError("Python not implemented yet")
    if language == "c_sharp":
        return Parser(CS_LANGUAGE)
    if language == "xml":
        return Parser(XML_LANGUAGE)


def get_node_type_to_terminal_from_file_path(
    file_path: str,
) -> NodeTypeToTerminal:
    language_or_none = extension_to_language.get(get_file_extension(file_path))
    if language_or_none is None:
        return empty_node_type_to_terminal
    return get_node_type_to_terminal_from_language(language_or_none)


def get_node_type_to_terminal_from_language(
    language: SupportedLanguages,
) -> NodeTypeToTerminal:
    if language == "c_sharp":
        return c_sharp_node_type_to_terminal
    if language == "python":
        return python_node_type_to_terminal
    if language == "xml":
        return empty_node_type_to_terminal
