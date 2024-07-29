from changing_dot.custom_types import Commit
from git import Repo
from loguru import logger


def set_repo(commit: Commit) -> None:
    logger.info("Setting repo")

    try:
        logger.info("Trying to connect to repo")
        repo = Repo(commit.git_path)
    except Exception as e:
        logger.info(e)
        try:
            logger.info(
                f"Didn't find repo, cloning from {commit.repo_url} to {commit.git_path}"
            )
            repo = Repo.clone_from(commit.repo_url, commit.git_path)
        except Exception as e:
            logger.error(e)

    reset_branch = commit.reset_branch if commit.reset_branch is not None else "main"
    repo.git.checkout()
    logger.info(f"Checked out to {reset_branch}")


def reset_repo(commit: Commit) -> None:
    logger.info("Resetting repo")
    repo = Repo(commit.git_path)
    reset_branch = commit.reset_branch if commit.reset_branch is not None else "main"
    repo.git.stash("-u")
    try:
        repo.git.stash("drop")
    except Exception as e:
        logger.info(e)
    repo.git.checkout(reset_branch)
    logger.info(f"Checked out to {reset_branch}")
    try:
        logger.info(f"Deleting branch {commit.branch_name}")
        repo.git.branch("-D", commit.branch_name)
    except Exception as e:
        logger.warning(e)
    try:
        logger.info("Deleting branch temp")
        repo.git.branch("-D", "temp")
    except Exception as e:
        logger.warning(e)
