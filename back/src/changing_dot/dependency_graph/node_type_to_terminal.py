import tree_sitter_c_sharp as tscsharp
from changing_dot.dependency_graph.language_matchers import (
    CSharpMatcher,
    EmptyMatcher,
    ILanguageMatcher,
    PythonMatcher,
    XmlMatcher,
)
from changing_dot.dependency_graph.types import SupportedLanguages
from changing_dot.utils.file_utils import get_file_extension
from tree_sitter import Language, Parser
from tree_sitter_xml import language_xml

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


def get_matcher_from_file_path(
    file_path: str,
) -> ILanguageMatcher:
    language_or_none = extension_to_language.get(get_file_extension(file_path))
    if language_or_none is None:
        return EmptyMatcher()
    return get_matcher_from_language(language_or_none)


def get_matcher_from_language(
    language: SupportedLanguages,
) -> ILanguageMatcher:
    if language == "c_sharp":
        return CSharpMatcher()
    if language == "python":
        return PythonMatcher()
    if language == "xml":
        return XmlMatcher()
