import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def create_temporary_venv(python_interpreter_path: str) -> Iterator[str]:
    tmpdir = "./temporary_env"
    venv_path = os.path.join(tmpdir, "venv")

    subprocess.run(
        [python_interpreter_path, "-m", "venv", venv_path],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
    )

    print(f"Virtual environment created at {venv_path}")

    yield venv_path

    shutil.rmtree(tmpdir)
