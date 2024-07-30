from tree_sitter import Node

from changing_dot.utils.text_functions import read_text


def get_node_text_from_file_path(node: Node, file_path: str) -> str:
    source = read_text(file_path)
    return source[node.start_byte : node.end_byte]
