import glob
import os


def get_file_extension(file_name: str) -> str:
    _, file_extension = os.path.splitext(file_name)
    return file_extension[1:]


def get_csharp_files(dir_to_explore: str) -> list[str]:
    if not os.path.exists(dir_to_explore):
        raise FileNotFoundError(f"The path {dir_to_explore} does not exist.")

    dir_to_explore = os.path.dirname(dir_to_explore)

    csharp_files = glob.glob(os.path.join(dir_to_explore, "**", "*.cs"), recursive=True)

    exclude_patterns = [
        os.path.sep + "obj" + os.path.sep,
        os.path.sep + "bin" + os.path.sep,
        ".g.cs",
        ".generated.cs",
        ".designer.cs",
    ]

    filtered_files = []
    for file in csharp_files:
        if not any(pattern in file for pattern in exclude_patterns):
            filtered_files.append(os.path.abspath(file))

    print("filtered files", filtered_files)
    return filtered_files
