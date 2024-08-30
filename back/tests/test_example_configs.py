import json
import os

from changing_dot.custom_types import (
    ApplyGraphChangesInput,
    CreateGraphInput,
    ResumeGraphInput,
    ResumeInitialNode,
)
from changing_dot_cli.cli import get_config_dict


def test_example_configs() -> None:
    example_config_path = "../examples"
    for file_name in os.listdir(example_config_path):
        config_path = os.path.join(example_config_path, file_name)
        config_dict = get_config_dict(config_path)
        _create_graph_input = CreateGraphInput(**config_dict)
        _apply_graph_changes_input = ApplyGraphChangesInput(**config_dict)
        _resume_graph_input = ResumeGraphInput(
            **config_dict,
            resume_initial_node=ResumeInitialNode(
                **json.loads(
                    """{"index": 4,"node_type": "problem","status": "handled", "error": {"text": "text", "file_path": "./Level1/Item.cs","project_name": "Level1", "pos": [ 8,28,8,34]}}"""
                )
            ),
        )
