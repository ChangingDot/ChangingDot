import os
import platform
import subprocess
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from time import sleep

import click
import requests
from changing_dot.config.constants import CDOT_PATH

FEEDBACK_SERVER_VERSION = "v0.0.1-alpha"


def get_platform_slug() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "win-x64"
    elif system == "linux":
        return "linux-x64"
    elif system == "darwin":  # macOS
        if "arm" in machine:
            return "osx-arm64"
        else:
            return "osx-x64"
    else:
        raise ValueError(f"Unsupported system: {system}")


def get_feedback_server_download_url() -> str:
    api_url = f"https://api.github.com/repos/ChangingDot/ChangingDot/releases/tags/{FEEDBACK_SERVER_VERSION}"
    response = requests.get(api_url)
    response.raise_for_status()

    release_data = response.json()

    for asset in release_data["assets"]:
        if asset["name"] == f"dotnet-{get_platform_slug()}.zip":
            url: str = asset["url"]
            return url

    raise ValueError("Binary not found")


def download_binary(url: str, save_path: str) -> None:
    headers = {
        "Accept": "application/octet-stream",
    }
    response = requests.get(
        url,
        headers=headers,
        stream=True,
    )
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    downloaded_size = 0

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                downloaded_size += len(chunk)
                click.echo(
                    f"Downloaded {downloaded_size} of {total_size} bytes", nl=False
                )
                click.echo("\r", nl=False)


def extract_zip(zip_path: str, extract_to: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def setup_binary_if_not_found() -> str:
    binary_dir = os.path.join(CDOT_PATH, "bin")

    os.makedirs(binary_dir, exist_ok=True)

    specific_os_folder_name = get_platform_slug()

    if os.path.exists(f"{binary_dir}/{specific_os_folder_name}/"):
        return f"{binary_dir}/{specific_os_folder_name}/DotnetAnalyzer"

    click.echo("Feedback server binary not present -> Downloading binary...")

    binary_url = get_feedback_server_download_url()

    zip_path = os.path.join(binary_dir, "tmp.zip")

    download_binary(binary_url, zip_path)
    # binary at  ~/.cdot/bin/platform-slug/

    # Extract the zip
    click.echo("Extracting binary...")
    extract_zip(zip_path, binary_dir)
    os.remove(zip_path)

    executable = f"{binary_dir}/{specific_os_folder_name}/DotnetAnalyzer"
    os.chmod(executable, 0o755)
    click.echo(f"Binary download at {binary_dir}/{specific_os_folder_name}")
    return executable


@contextmanager
def feedback_server() -> Iterator[None]:
    process = None
    try:
        executable_path = setup_binary_if_not_found()
        executable_dir = os.path.dirname(executable_path)
        process = subprocess.Popen([executable_path], cwd=executable_dir)
        sleep(2)
        yield
    finally:
        if process is not None:
            try:
                process.terminate()
                process.wait(
                    timeout=5
                )  # Wait up to 5 seconds for the process to terminate
            except subprocess.TimeoutExpired:
                click.echo("Process did not terminate in time, forcing...")
                process.kill()  # Force kill if it doesn't terminate
                process.wait()
