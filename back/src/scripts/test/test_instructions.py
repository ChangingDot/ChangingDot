import json

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    create_instruction_manager,
)
from loguru import logger

G = ChangingGraph()

initial_problem_json = """{
    "index": 0,
    "node_type": "problem",
    "status": "handled",
    "error": {
        "text": "Remove Newtonsoft dependency to then change it to with System.Text.Json",
        "file_path": "/Users/matthieu/Documents/projects/codebase_to_gold/sample-codebases/update-dep/CustomChanges1/NewtonSoftMigration/NewtonSoftMigration.csproj",
        "pos": [
            11,
            0,
            11,
            0
        ]
    }
}"""

failed_solution_json = """{
    "index": 1,
    "node_type": "solution",
    "status": "failed",
    "instruction": {
        "edit_type": "remove",
        "programming_language": "c#",
        "file_path": "/Users/matthieu/Documents/projects/codebase_to_gold/sample-codebases/update-dep/CustomChanges1/NewtonSoftMigration/NewtonSoftMigration.csproj",
        "line_number": 11,
        "error": "Remove Newtonsoft dependency to then change it to with System.Text.Json",
        "solution": "To resolve the error and remove the Newtonsoft.Json dependency, you should remove the line that includes the Newtonsoft.Json package reference."
    },
    "edits": [
        {
            "edit_type": "remove",
            "file_path": "/Users/matthieu/Documents/projects/codebase_to_gold/sample-codebases/update-dep/CustomChanges1/NewtonSoftMigration/NewtonSoftMigration.csproj",
            "line_number": 11,
            "line_to_remove": "    <PackageReference Include='Newtonsoft.Json' Version='13.0.3' />"
        }
    ]
}"""

initial_problem = json.loads(initial_problem_json)
failed_solution = json.loads(failed_solution_json)

G.add_problem_node(initial_problem)
G.add_solution_node(failed_solution)
G.add_edge(0, 1)

instruction_manager = create_instruction_manager(
    "Remove Newtonsoft dependency to then change it to with System.Text.Json", "MISTRAL"
)

DG = DependencyGraph(["file"])

instruction = instruction_manager.get_node_instruction(G, DG, 0)

logger.info(instruction)
