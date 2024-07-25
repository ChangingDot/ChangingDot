import os
import shutil
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from core.commit.commit_edits import commit_edits
from core.commit.conflict_handler import ConflictHandler
from core.modifyle.modifyle import IModifyle, Modifyle
from git import Repo
from langchain_community.chat_models.fake import FakeListChatModel
from loguru import logger
from utils.text_functions import write_text

if TYPE_CHECKING:
    from core.custom_types import Edits

repo_dir = os.path.abspath("./tests/core/fake_repo/")


@pytest.fixture()
def repo() -> Repo:
    repo = Repo.init(repo_dir, initial_branch="master")
    repo.index.add(f"{repo_dir}/alphabet.txt")
    repo.index.add(f"{repo_dir}/numbers.txt")
    repo.index.commit("initial_commit")
    return repo


@pytest.fixture()
def file_modifier() -> Modifyle:
    return Modifyle()


def make_conflict_handler(expected_llm_output: str) -> ConflictHandler:
    return ConflictHandler(
        FakeListChatModel(responses=[f"""```language\n{expected_llm_output}```"""])
    )


@pytest.fixture(autouse=True)
def _reset_repo() -> Generator[None, None, None]:
    yield
    git_dir = os.path.join(repo_dir, ".git")
    if os.path.isdir(git_dir):
        shutil.rmtree(git_dir)
    write_text(
        f"{repo_dir}/alphabet.txt", "\n".join(["a", "b", "c", "d", "e", "f"]) + "\n"
    )
    write_text(
        f"{repo_dir}/numbers.txt", "\n".join(["1", "2", "3", "4", "5", "6", "7"]) + "\n"
    )


def get_content(file_path: str) -> str:
    with open(f"{repo_dir}/{file_path}") as file:
        file_contents = file.read()
    return file_contents


# for debugging purposes
def git_log(repo: Repo) -> None:
    logger.info("=" * 50)
    logger.info(f"branches -> {repo.branches}")
    logger.info(f"active_branch -> {repo.active_branch.name}")
    logger.info("-" * 50)
    for branch in repo.branches:  # type: ignore
        logger.info(f"Branch name: {branch.name}")
        for commit in repo.iter_commits(branch):
            logger.info(f"* {commit.hexsha[:7]} {commit.summary}")  # type: ignore
        logger.info("-" * 50)


def test_empty_commit(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler("")

    edits_list: list[Edits] = []

    initial_commit = repo.head.commit

    assert repo.active_branch.name == "master"

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert repo.head.commit == initial_commit
    assert repo.active_branch.name == "new_branch"


def test_one_edit_commit(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler("")

    initial_commit = repo.head.commit

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ]
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    git_log(repo)

    assert (
        get_content("alphabet.txt") == "\n".join(["A", "b", "c", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt")
        == "\n".join(["1", "2", "3", "4", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message == "commit"

    repo.git.checkout("master")

    assert repo.head.commit == initial_commit


def test_2_replace_commits_in_different_files(
    repo: Repo, file_modifier: IModifyle
) -> None:
    conflict_handler = make_conflict_handler("")

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ],
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/numbers.txt",
                "line_number": 4,
                "before": "4",
                "after": "44",
            }
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert (
        get_content("alphabet.txt") == "\n".join(["A", "b", "c", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt")
        == "\n".join(["1", "2", "3", "44", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message == "commit"
    assert repo.head.commit.parents[0].message == "commit"


def test_2_replace_commits_in_same_file(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler("")

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ],
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 3,
                "before": "c",
                "after": "C",
            }
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert (
        get_content("alphabet.txt") == "\n".join(["A", "b", "C", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt")
        == "\n".join(["1", "2", "3", "4", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message == "commit"
    assert repo.head.commit.parents[0].message == "commit"


def test_handling_replace_conflicts(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler(
        "\n".join(["conflict resolution", "b", "c", "d", "e", "f"]) + "\n"
    )

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ],
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "1",
            }
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert (
        get_content("alphabet.txt")
        == "\n".join(["conflict resolution", "b", "c", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt")
        == "\n".join(["1", "2", "3", "4", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message.strip() == "commit"
    assert repo.head.commit.parents[0].message.strip() == "commit"
    assert [branch.name for branch in repo.branches] == ["master", "new_branch"]  # type: ignore


def test_handling_add_conflicts(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler(
        "\n".join(["1", "A", "a", "b", "c", "d", "e", "f"]) + "\n"
    )

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "add",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "line_to_add": "1",
            }
        ],
        [
            {
                "edit_type": "add",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "line_to_add": "A",
            }
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert (
        get_content("alphabet.txt")
        == "\n".join(["1", "A", "a", "b", "c", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt")
        == "\n".join(["1", "2", "3", "4", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message.strip() == "commit"
    assert repo.head.commit.parents[0].message.strip() == "commit"


def test_handling_empty_commits(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler("")

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ],
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert (
        get_content("alphabet.txt") == "\n".join(["A", "b", "c", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt")
        == "\n".join(["1", "2", "3", "4", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message.strip() == "commit"


def test_handle_a_lot(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = make_conflict_handler(
        "\n".join(["1", "A", "b", "c", "d", "e", "f"]) + "\n"
    )

    edits_list: list[Edits] = [
        [
            {
                "edit_type": "add",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "line_to_add": "1",
            },
            {
                "edit_type": "remove",
                "file_path": f"{repo_dir}/numbers.txt",
                "line_number": 3,
                "line_to_remove": "3",
            },
        ],
        [
            {
                "edit_type": "replace",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 1,
                "before": "a",
                "after": "A",
            }
        ],
        [
            {
                "edit_type": "add",
                "file_path": f"{repo_dir}/alphabet.txt",
                "line_number": 4,
                "line_to_add": "4",
            }
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert (
        get_content("alphabet.txt")
        == "\n".join(["1", "A", "b", "c", "4", "d", "e", "f"]) + "\n"
        # We might want the bellow, but we get the above
        # The merge logic is handling this: putting this here to document
        # == "\n".join(["1", "A", "b", "4", "c", "d", "e", "f"]) + "\n"
    )
    assert (
        get_content("numbers.txt") == "\n".join(["1", "2", "4", "5", "6", "7"]) + "\n"
    )

    assert repo.head.commit.message.strip() == "commit"
