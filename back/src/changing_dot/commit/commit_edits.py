import os

from changing_dot.commit.conflict_handler import ConflictHandler
from changing_dot.custom_types import Edits
from changing_dot.modifyle.modifyle import IModifyle
from changing_dot.utils.text_functions import read_text, write_text
from changing_dot_visualize.observer import Observer
from git import GitCommandError, Repo

CONFLICT_MARKER = "<<<<<<< HEAD"
EMPTY_COMMIT_CHERRYPICK_MARKER = "The previous cherry-pick is now empty"


def cherry_pick_continue(repo: Repo, observer: Observer | None) -> None:
    try:
        repo.git.cherry_pick("--continue")
    except GitCommandError as e:
        if EMPTY_COMMIT_CHERRYPICK_MARKER in f"{e}":
            if observer:
                observer.log("Skipping commit because it is empty")
            repo.git.cherry_pick("--skip")
        else:
            raise ValueError(str(e)) from e


def commit_edits(
    repo: Repo,
    edits_list: list[Edits],
    branch_name: str,
    file_modifier: IModifyle,
    conflict_handler: ConflictHandler,
    observer: Observer | None = None,
) -> None:
    # setup commit
    os.environ["GIT_AUTHOR_NAME"] = "ChangingDot"
    os.environ["GIT_AUTHOR_EMAIL"] = "bot@ChangingDot.com"
    os.environ["GIT_COMMITTER_NAME"] = "ChangingDot"
    os.environ["GIT_COMMITTER_EMAIL"] = "bot@ChangingDot.com"

    initial_head = repo.head.commit
    repo.git.checkout("-b", branch_name)
    for edits in edits_list:
        if observer:
            observer.log("handling edits")
        # add edits to new temp branch to trigger conflicts
        tmp_branch = "temp"
        repo.create_head(tmp_branch, initial_head)
        repo.git.checkout(tmp_branch)
        if observer:
            observer.log(f"applying edits on branch {tmp_branch}")
        file_modifier.apply_change(edits)
        changed_files = list({edit["file_path"] for edit in edits})
        repo.index.add(changed_files)
        commit = repo.index.commit("commit")
        ## doesn't work without, this clean the index (that should already be clean)
        repo.git.stash("--include-untracked")
        repo.git.checkout(branch_name)
        try:
            if observer:
                observer.log(
                    f"Adding commit {commit.hexsha[:7]} to branch {branch_name}"
                )
            repo.git.cherry_pick(commit)
        except GitCommandError as _e:
            if observer:
                observer.log("Merge conflict")
            for changed_file in changed_files:
                file_content = read_text(changed_file)
                if CONFLICT_MARKER in file_content:
                    fixed_file_content = conflict_handler.handle_conflict(file_content)
                    write_text(changed_file, fixed_file_content)
                    repo.git.add(changed_file)
            cherry_pick_continue(repo, observer)
        finally:
            repo.git.branch("-D", tmp_branch)

    del os.environ["GIT_AUTHOR_NAME"]
    del os.environ["GIT_AUTHOR_EMAIL"]
    del os.environ["GIT_COMMITTER_NAME"]
    del os.environ["GIT_COMMITTER_EMAIL"]

    return
