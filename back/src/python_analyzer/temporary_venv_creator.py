import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager

from changing_dot.config.constants import CDOT_PATH


@contextmanager
def create_temporary_venv(python_interpreter_path: str) -> Iterator[None]:
    tmpdir = os.path.join(CDOT_PATH, "temporary_env")
    venv_path = os.path.join(tmpdir, "venv")

    subprocess.run(
        [python_interpreter_path, "-m", "venv", venv_path],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
    )

    yield

    shutil.rmtree(tmpdir)
