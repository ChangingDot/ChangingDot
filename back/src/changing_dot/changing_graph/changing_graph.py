from collections import Counter

import networkx as nx
from changing_dot.custom_types import (
    ErrorProblemNode,
    ErrorSolutionNode,
    NodeData,
    NodeStatus,
    ProblemNode,
    SolutionNode,
    edit_to_diff,
)


class ChangingGraph:
    next_index: int
    G: nx.DiGraph

    def __init__(self, G: nx.DiGraph | None = None) -> None:
        if G is None:
            G = nx.DiGraph()
            next_index = 0
        else:
            next_index = max(nx.get_node_attributes(G, "index").values()) + 1
        self.G = G
        self.next_index = next_index

    def add_solution_node(self, node_data: SolutionNode) -> int:
        index = self.next_index
        self.G.add_node(
            index,
            index=index,
            node_type=node_data["node_type"],
            status=node_data["status"],
            instruction=node_data["instruction"],
            edits=node_data["edits"],
        )
        self.next_index += 1
        return index

    def add_problem_node(self, node_data: ProblemNode) -> int:
        index = self.next_index
        self.G.add_node(
            index,
            index=index,
            node_type=node_data["node_type"],
            status=node_data["status"],
            error=node_data["error"],
        )
        self.next_index += 1
        return index

    def update_solution_node(self, node_data: SolutionNode) -> None:
        self.G.nodes[node_data["index"]].update(node_data)

    def update_problem_node(self, node_data: ProblemNode) -> None:
        self.G.nodes[node_data["index"]].update(node_data)

    def add_edge(self, source_index: int, target_index: int) -> None:
        self.G.add_edge(source_index, target_index)

    def remove_edge(self, source_index: int, target_index: int) -> None:
        self.G.remove_edge(source_index, target_index)

    def get_node(self, index: int) -> NodeData:
        node = self.G.nodes()[index]
        if node["node_type"] == "solution":
            return {
                "index": node["index"],
                "node_type": node["node_type"],
                "status": node["status"],
                "instruction": node["instruction"],
                "edits": node["edits"],
            }
        else:
            return {
                "index": node["index"],
                "node_type": node["node_type"],
                "status": node["status"],
                "error": node["error"],
            }

    def mark_node_as(self, node_index: int, status: NodeStatus) -> None:
        self.G.nodes()[node_index]["status"] = status

    def get_number_of_nodes(self) -> int:
        n: int = nx.number_of_nodes(self.G)
        return n

    def count_node_types(self) -> dict[str, int]:
        node_type_dict: dict[int, str] = nx.get_node_attributes(self.G, "node_type")
        return dict(Counter(node_type_dict.values()))

    def get_number_of_layers(self, source: int) -> int:
        path_lengths = nx.single_source_shortest_path_length(self.G, source)
        distances: list[int] = list(path_lengths.values())
        return max(distances)

    def get_nodes_at_distance(self, source_index: int, d: int) -> list[int]:
        path_lengths = nx.single_source_shortest_path_length(self.G, source_index)
        return [node for node, length in path_lengths.items() if length == d]

    def get_parent_nodes(self, node_index: int) -> list[int]:
        return list(self.G.predecessors(node_index))

    def get_shortest_distance(self, source: int, target: int) -> int:
        d: int = nx.shortest_path_length(self.G, source=source, target=target)
        return d

    def get_children(self, node_index: int) -> list[int]:
        return list(self.G.successors(node_index))

    def get_all_pending_nodes(self) -> list[int]:
        return [
            node["index"]
            for index, node in self.G.nodes(data=True)
            if node["status"] == "pending"
            and (node["node_type"] == "problem" or node["node_type"] == "solution")
        ]

    def get_all_pending_problem_nodes(self) -> list[ProblemNode]:
        return [
            node
            for index, node in self.G.nodes(data=True)
            if node["node_type"] == "problem" and node["status"] == "pending"
        ]

    def get_leaves(self) -> list[int]:
        return [node for node in self.G.nodes() if self.G.out_degree(node) == 0]

    def get_failed_solution_to_problem(self, node_index: int) -> list[SolutionNode]:
        problem_node = self.get_node(node_index)
        assert problem_node["node_type"] == "problem"
        failed_successors: list[SolutionNode] = [
            self.get_node(node_index)  # type: ignore
            for node_index in self.G.successors(node_index)
            if self.G.nodes[node_index]["status"] == "failed"
            and self.G.nodes[node_index]["node_type"] == "solution"
        ]
        return failed_successors

    def get_cycles(self) -> list[set[int]]:
        strongly_connected_components = list(nx.strongly_connected_components(self.G))
        cycles = [scc for scc in strongly_connected_components if len(scc) != 1]
        return cycles

    def in_edges(self, node_index: int) -> list[tuple[int, int]]:
        return self.G.in_edges(node_index)  # type: ignore

    def out_edges(self, node_index: int) -> list[tuple[int, int]]:
        return self.G.out_edges(node_index)  # type: ignore

    def remove_node(self, node_index: int) -> None:
        self.G.remove_node(node_index)

    def remove_redundant_edges(self) -> None:
        G_reduced = nx.transitive_reduction(self.G)
        # update attributes that were not copied
        for node in G_reduced:
            G_reduced.nodes[node].update(self.G.nodes[node])
        self.G = G_reduced

    def find_same_solution(
        self,
        instruction_path_to_match: str,
        line_number_to_match: int,
        diff_to_match: str,
    ) -> list[int]:
        matching_nodes = []
        for node, attrs in self.G.nodes(data=True):
            if attrs.get("node_type") != "solution":
                continue

            if attrs.get("status") == "failed":
                continue

            if attrs.get("instruction").get("file_path") != instruction_path_to_match:
                continue

            node_line_number = attrs.get("instruction").get("line_number")
            if node_line_number != line_number_to_match:
                continue

            if edit_to_diff(attrs.get("edits")[0]) != diff_to_match:
                continue

            matching_nodes.append(node)

        return matching_nodes

    def find_same_problem(
        self,
        error_path_to_match: str,
        line_number_to_match: int,
        error_text_to_match: str,
    ) -> list[int]:
        matching_nodes = []
        for node, attrs in self.G.nodes(data=True):
            if attrs.get("node_type") != "problem":
                continue

            if attrs.get("error").get("file_path") != error_path_to_match:
                continue

            node_line_number = attrs.get("error").get("pos")[0]
            if node_line_number != line_number_to_match:
                continue

            if attrs.get("error").get("text") != error_text_to_match:
                continue

            matching_nodes.append(node)

        return matching_nodes

    def error_on_problem_node(
        self,
        error_node: ErrorProblemNode,
    ) -> None:
        node = self.get_node(error_node["index"])
        assert node["node_type"] == "problem"
        self.G.nodes[error_node["index"]].update(error_node)

    def error_on_solution_node(
        self,
        error_node: ErrorSolutionNode,
    ) -> None:
        node = self.get_node(error_node["index"])
        assert node["node_type"] == "solution"
        self.G.nodes[error_node["index"]].update(error_node)
