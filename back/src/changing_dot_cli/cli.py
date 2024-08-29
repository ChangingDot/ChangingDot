import json
from typing import Any
from urllib.parse import urlparse

import click
import requests
import yaml
from changing_dot.apply_graph_changes import run_apply_graph_changes
from changing_dot.commit_graph import run_commit_graph_from_config
from changing_dot.create_graph import run_create_graph
from changing_dot.custom_types import (
    ApplyGraphChangesInput,
    CreateGraphInput,
    OptimizeGraphInput,
    ResumeGraphInput,
    ResumeInitialNode,
)
from changing_dot.optimize_graph import run_optimize_graph
from changing_dot.resume_graph import run_resume_graph
from changing_dot_visualize.main import visualize_graph
from python_analyzer.temporary_venv_creator import create_temporary_venv

from changing_dot_cli.setup_feedback_server import feedback_server


def is_url(path: str) -> bool:
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_config_dict(path: str) -> Any:
    if is_url(path):
        response = requests.get(path)
        if response.status_code == 200:
            config_content = response.text
            return yaml.safe_load(config_content)
        else:
            raise click.ClickException(
                f"Failed to fetch the config file from URL. Status code: {response.status_code}"
            )
    else:
        try:
            with open(path) as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise click.ClickException(
                f"Failed to read the config file from local path. Error: {e}"
            ) from e


@click.group()
def cdot() -> None:
    pass


@cdot.command()
@click.option(
    "--config",
    "-c",
    prompt="Path to yaml config file",
    help="Path to yaml config file.",
)
@click.option("--local/--remote", default=True)
@click.option("--dev", is_flag=True, default=False)
def create(config: str, local: bool, dev: bool) -> None:
    config_dict = get_config_dict(config)
    create_graph_input = CreateGraphInput(**config_dict, is_local=local)

    if create_graph_input.analyzer_options.language == "python":
        with create_temporary_venv(
            create_graph_input.analyzer_options.python_interpreter_path
        ) as venv_path:
            create_graph_input.analyzer_options.venv_path = venv_path
            run_create_graph(
                create_graph_input.iteration_name,
                create_graph_input.project_name,
                create_graph_input.goal,
                create_graph_input.restriction_options,
                create_graph_input.initial_change,
                create_graph_input.analyzer_options,
                create_graph_input.is_local,
                create_graph_input.llm_provider,
            )
            return

    if dev:
        run_create_graph(
            create_graph_input.iteration_name,
            create_graph_input.project_name,
            create_graph_input.goal,
            create_graph_input.restriction_options,
            create_graph_input.initial_change,
            create_graph_input.analyzer_options,
            create_graph_input.is_local,
            create_graph_input.llm_provider,
        )
        return

    with feedback_server():
        run_create_graph(
            create_graph_input.iteration_name,
            create_graph_input.project_name,
            create_graph_input.goal,
            create_graph_input.restriction_options,
            create_graph_input.initial_change,
            create_graph_input.analyzer_options,
            create_graph_input.is_local,
            create_graph_input.llm_provider,
        )


@cdot.command()
@click.option(
    "--config",
    "-c",
    prompt="Path to yaml config file",
    help="Path to yaml config file.",
)
@click.option("--local/--remote", default=True)
def visualize(config: str, local: bool) -> None:
    config_dict = get_config_dict(config)
    visualize_graph(config_dict, local)


@cdot.command()
@click.option(
    "--config",
    "-c",
    prompt="Path to yaml config file",
    help="Path to yaml config file.",
)
@click.option("--local/--remote", default=True)
def optimize(config: str, local: bool) -> None:
    config_dict = get_config_dict(config)
    optimize_graph_input = OptimizeGraphInput(**config_dict, is_local=local)
    run_optimize_graph(
        optimize_graph_input.iteration_name,
        optimize_graph_input.project_name,
        optimize_graph_input.base_path,
        local,
    )


@cdot.command()
@click.option(
    "--config",
    "-c",
    prompt="Path to yaml config file",
    help="Path to yaml config file.",
)
@click.option("--local/--remote", default=True)
def apply_changes(config: str, local: bool) -> None:
    config_dict = get_config_dict(config)
    apply_graph_changes_input = ApplyGraphChangesInput(**config_dict, is_local=local)
    run_apply_graph_changes(
        apply_graph_changes_input.iteration_name,
        apply_graph_changes_input.project_name,
        apply_graph_changes_input.base_path,
        apply_graph_changes_input.analyzer_options,
        local,
    )


@cdot.command()
@click.option(
    "--config",
    "-c",
    prompt="Path to yaml config file",
    help="Path to yaml config file.",
)
@click.option("--local/--remote", default=True)
@click.option(
    "--resume-node",
    "-r",
    prompt="Paste node from where you want to resume",
    help="Node from where you want to resume",
)
@click.option("--dev", is_flag=True, default=False)
def resume(config: str, local: bool, resume_node: str, dev: bool) -> None:
    config_dict = get_config_dict(config)
    resume_initial_node = ResumeInitialNode(**json.loads(resume_node))
    resume_graph_input = ResumeGraphInput(
        **config_dict, is_local=local, resume_initial_node=resume_initial_node
    )

    if resume_graph_input.analyzer_options.language == "python":
        with create_temporary_venv(
            resume_graph_input.analyzer_options.python_interpreter_path
        ) as venv_path:
            resume_graph_input.analyzer_options.venv_path = venv_path
            run_resume_graph(
                resume_graph_input.iteration_name,
                resume_graph_input.project_name,
                resume_graph_input.goal,
                resume_graph_input.base_path,
                resume_graph_input.commit,
                resume_graph_input.restriction_options,
                resume_graph_input.resume_initial_node,
                resume_graph_input.analyzer_options,
                resume_graph_input.llm_provider,
                resume_graph_input.is_local,
            )
        return

    if dev:
        run_resume_graph(
            resume_graph_input.iteration_name,
            resume_graph_input.project_name,
            resume_graph_input.goal,
            resume_graph_input.base_path,
            resume_graph_input.commit,
            resume_graph_input.restriction_options,
            resume_graph_input.resume_initial_node,
            resume_graph_input.analyzer_options,
            resume_graph_input.llm_provider,
            resume_graph_input.is_local,
        )
        return

    with feedback_server():
        run_resume_graph(
            resume_graph_input.iteration_name,
            resume_graph_input.project_name,
            resume_graph_input.goal,
            resume_graph_input.base_path,
            resume_graph_input.commit,
            resume_graph_input.restriction_options,
            resume_graph_input.resume_initial_node,
            resume_graph_input.analyzer_options,
            resume_graph_input.llm_provider,
            resume_graph_input.is_local,
        )


@cdot.command()
@click.option(
    "--config",
    "-c",
    prompt="Path to yaml config file",
    help="Path to yaml config file.",
)
@click.option("--local/--remote", default=True)
def commit(config: str, local: bool) -> None:
    config_dict = get_config_dict(config)
    run_commit_graph_from_config(config_dict, local)


if __name__ == "__main__":
    cdot()
