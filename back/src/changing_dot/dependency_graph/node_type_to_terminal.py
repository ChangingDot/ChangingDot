import tree_sitter_c_sharp as tscsharp
from cdot_tree_sitter_python import language as language_py
from changing_dot.dependency_graph.language_matchers import (
    CSharpMatcher,
    CsProjMatcher,
    EmptyMatcher,
    ILanguageMatcher,
    PipReqMatcher,
    PythonMatcher,
    XmlMatcher,
)
from changing_dot.dependency_graph.types import SupportedLanguages
from changing_dot.utils.file_utils import get_file_extension
from tree_sitter import Language, Parser
from tree_sitter_requirements import language as language_pip_requirements
from tree_sitter_xml import language_xml

extension_to_language: dict["str", SupportedLanguages] = {
    "py": "python",
    "cs": "c_sharp",
    "csproj": "csproj",
    "xml": "xml",
}


def get_language_from_file_path(file_path: str) -> SupportedLanguages | None:
    if file_path.endswith("requirements.txt"):
        return "pip_requirements"

    file_extension = get_file_extension(file_path)

    language = extension_to_language.get(file_extension)

    return language


PY_LANGUAGE = Language(language_py())
PIP_REQ_LANGUAGE = Language(language_pip_requirements())
CS_LANGUAGE = Language(tscsharp.language())
XML_LANGUAGE = Language(language_xml())


def parser_from_file_path(file_path: str) -> Parser | None:
    language = get_language_from_file_path(file_path)

    if language is None:
        return None
    if language == "python":
        return Parser(PY_LANGUAGE)
    if language == "c_sharp":
        return Parser(CS_LANGUAGE)
    if language == "xml" or language == "csproj":
        return Parser(XML_LANGUAGE)
    if language == "pip_requirements":
        return Parser(PIP_REQ_LANGUAGE)


def get_matcher_from_file_path(
    file_path: str,
) -> ILanguageMatcher:
    language_or_none = get_language_from_file_path(file_path)
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
    if language == "csproj":
        return CsProjMatcher()
    if language == "pip_requirements":
        return PipReqMatcher()
