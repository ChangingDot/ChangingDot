import glob
import os


def get_file_extension(file_name: str) -> str:
    _, file_extension = os.path.splitext(file_name)
    return file_extension[1:]


def get_python_files(dir_to_explore: str) -> list[str]:
    if not os.path.exists(dir_to_explore):
        raise FileNotFoundError(f"The path {dir_to_explore} does not exist.")

    if os.path.isfile(dir_to_explore):
        dir_to_explore = os.path.dirname(dir_to_explore)

    python_files = glob.glob(os.path.join(dir_to_explore, "**", "*.py"), recursive=True)
    pip_req_files = glob.glob(
        os.path.join(dir_to_explore, "**", "requirements.txt"), recursive=True
    )

    exclude_patterns = [
        os.path.sep + "__pycache__" + os.path.sep,
        ".pyc",
        ".pyo",
        ".pyd",
    ]

    filtered_files = []
    for file in python_files + pip_req_files:
        if not any(pattern in file for pattern in exclude_patterns):
            filtered_files.append(os.path.abspath(file))

    return filtered_files


def get_csharp_files(dir_to_explore: str) -> list[str]:
    if not os.path.exists(dir_to_explore):
        raise FileNotFoundError(f"The path {dir_to_explore} does not exist.")

    if os.path.isfile(dir_to_explore) and dir_to_explore.lower().endswith(".sln"):
        dir_to_explore = os.path.dirname(dir_to_explore)

    csharp_files = glob.glob(os.path.join(dir_to_explore, "**", "*.cs"), recursive=True)
    cs_proj_files = glob.glob(
        os.path.join(dir_to_explore, "**", "*.csproj"), recursive=True
    )

    exclude_patterns = [
        os.path.sep + "obj" + os.path.sep,
        os.path.sep + "bin" + os.path.sep,
        ".g.cs",
        ".generated.cs",
        ".designer.cs",
    ]

    filtered_files = []
    for file in csharp_files + cs_proj_files:
        if not any(pattern in file for pattern in exclude_patterns):
            filtered_files.append(os.path.abspath(file))

    return filtered_files


def get_latest_directory(directory_path: str) -> str | None:
    files = [
        os.path.join(directory_path, f)
        for f in os.listdir(directory_path)
        if os.path.isdir(os.path.join(directory_path, f))
    ]

    if len(files) == 0:
        return None

    latest_file = max(files, key=os.path.getctime)

    return latest_file
