import os
import pickle
import re

import networkx as nx


def extract_number_from_string(s: str) -> int:
    match = re.search(r"\d+", s)
    if match:
        return int(match.group(0))
    return -1


def process_pickle_files(directory: str, is_local: bool) -> list[nx.DiGraph]:
    files = []

    if is_local:
        for file in os.listdir(directory):
            if file.endswith(".pkl") or file.endswith(".pickle"):
                file_path = os.path.join(directory, file)
                files.append(file_path)
    else:
        from config.storage import bucket

        blobs = bucket.list_blobs(prefix=directory)
        for blob in blobs:
            if blob.name.endswith(".pkl") or blob.name.endswith(".pickle"):
                files.append(blob.name)

    graph_dict = {}

    for file_path in files:
        file_number = extract_number_from_string(file_path.split("/")[-1])
        if is_local:
            with open(file_path, "rb") as pickle_file:
                data = pickle.load(pickle_file)
                graph_dict[file_number] = data
        else:
            blob = bucket.blob(file_path)
            with blob.open("rb") as pickle_file:
                data = pickle.load(pickle_file)
                graph_dict[file_number] = data

    sorted_graphs = [graph_dict[num] for num in sorted(graph_dict)]

    return sorted_graphs
