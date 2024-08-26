import os
import shutil
from collections.abc import Generator

import pytest
from changing_dot.commit.commit_edits import commit_edits
from changing_dot.commit.conflict_handler import (
    ConflictHandlerThatThrowsSinceConflictShoundntExist,
)
from changing_dot.custom_types import BlockEdit
from changing_dot.modifyle.modifyle import IModifyle, IntegralModifyle
from changing_dot.utils.text_functions import write_text
from git import Repo
from loguru import logger

repo_dir = os.path.abspath("./tests/core/fake_repo/")


@pytest.fixture()
def repo() -> Repo:
    repo = Repo.init(repo_dir, initial_branch="master")
    repo.index.add(f"{repo_dir}/file1.cs")
    repo.index.add(f"{repo_dir}/file2.cs")
    repo.index.commit("initial_commit")
    return repo


def get_fixture(file_path: str) -> str:
    with open("./tests/core/fixtures/commit/" + file_path) as file:
        file_contents = file.read()
    return file_contents


@pytest.fixture()
def file_modifier() -> IModifyle:
    return IntegralModifyle()


@pytest.fixture(autouse=True)
def _reset_repo() -> Generator[None, None, None]:
    yield
    git_dir = os.path.join(repo_dir, ".git")
    if os.path.isdir(git_dir):
        shutil.rmtree(git_dir)
    write_text(f"{repo_dir}/file1.cs", get_fixture("commit_base.cs"))
    write_text(f"{repo_dir}/file2.cs", get_fixture("commit_base_2.cs"))


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
    conflict_handler = ConflictHandlerThatThrowsSinceConflictShoundntExist()

    edits_list: list[list[BlockEdit]] = []

    initial_commit = repo.head.commit

    assert repo.active_branch.name == "master"

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert repo.head.commit == initial_commit
    assert repo.active_branch.name == "new_branch"


def test_one_edit_commit(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = ConflictHandlerThatThrowsSinceConflictShoundntExist()

    initial_commit = repo.head.commit

    edits_list: list[list[BlockEdit]] = [
        [
            BlockEdit(
                file_path=f"{repo_dir}/file1.cs",
                block_id=2,
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ]
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    git_log(repo)

    assert get_content("file1.cs") == get_fixture("commit_replace.cs")
    assert get_content("file2.cs") == get_fixture("commit_base_2.cs")

    assert repo.head.commit.message == "commit"

    repo.git.checkout("master")

    assert repo.head.commit == initial_commit


def test_2_replace_commits_in_different_files(
    repo: Repo, file_modifier: IModifyle
) -> None:
    conflict_handler = ConflictHandlerThatThrowsSinceConflictShoundntExist()

    edits_list: list[list[BlockEdit]] = [
        [
            BlockEdit(
                file_path=f"{repo_dir}/file1.cs",
                block_id=2,
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
        [
            BlockEdit(
                file_path=f"{repo_dir}/file2.cs",
                block_id=7,
                before="""[JsonIgnore]
        public int Size { get; set; }""",
                after="""[JsonIgnore]
        public int NewSize { get; set; }""",
            )
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert get_content("file1.cs") == get_fixture("commit_replace.cs")
    assert get_content("file2.cs") == get_fixture("commit_replace_2.cs")

    assert repo.head.commit.message == "commit"
    assert repo.head.commit.parents[0].message == "commit"


def test_2_replace_commits_in_same_file(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = ConflictHandlerThatThrowsSinceConflictShoundntExist()

    edits_list: list[list[BlockEdit]] = [
        [
            BlockEdit(
                file_path=f"{repo_dir}/file1.cs",
                block_id=2,
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
        [
            BlockEdit(
                file_path=f"{repo_dir}/file1.cs",
                block_id=0,
                before="using System;",
                after="using Revolution;",
            )
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert get_content("file1.cs") == get_fixture("commit_replace_twice.cs")
    assert get_content("file2.cs") == get_fixture("commit_base_2.cs")

    assert repo.head.commit.message == "commit"
    assert repo.head.commit.parents[0].message == "commit"


def test_handling_empty_commits(repo: Repo, file_modifier: IModifyle) -> None:
    conflict_handler = ConflictHandlerThatThrowsSinceConflictShoundntExist()

    edits_list: list[list[BlockEdit]] = [
        [
            BlockEdit(
                file_path=f"{repo_dir}/file1.cs",
                block_id=2,
                before="""static string SimpleMethod()
    {
        return "Hello, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
        [
            BlockEdit(
                file_path=f"{repo_dir}/file1.cs",
                block_id=2,
                before="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
                after="""static string SimpleMethod()
    {
        return "Welcome, World!";
    }""",
            )
        ],
    ]

    commit_edits(repo, edits_list, "new_branch", file_modifier, conflict_handler)

    assert get_content("file1.cs") == get_fixture("commit_replace.cs")
    assert get_content("file2.cs") == get_fixture("commit_base_2.cs")

    assert repo.head.commit.message.strip() == "commit"
