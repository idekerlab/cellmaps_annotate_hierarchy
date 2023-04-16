import os
import json


def get_root_path():
    home_dir = os.path.expanduser("~")
    # Get the root path from the environment variable
    root_path = os.path.join(home_dir, os.getenv("MODEL_ANNOTATION_ROOT"))
    # Check if the environment variable is set and the path exists
    if not root_path or not os.path.isdir(root_path):
        raise ValueError("MODEL_ANNOTATION_ROOT environment variable is not set or does not exist")

    return root_path


def get_model_directory_path(model_name, version):
    return os.path.join(get_root_path(), model_name, version)


def read_system_json(model, version, system_name, extension, root_path):
    # Check if the file exists
    file_path = os.path.join(root_path, model, version, f"{system_name}_{extension}.json")
    if not os.path.isfile(file_path):
        return None

    # Read the JSON data from the file
    with open(file_path, "r") as f:
        json_data = json.load(f)

    return json_data


def write_system_json(json_data, model, version, system_name, extension, root_path):
    # Create the folder for the system if it does not already exist
    folder_path = os.path.join(root_path, model, version)
    os.makedirs(folder_path, exist_ok=True)

    # Write the JSON data to a file
    file_path = os.path.join(folder_path, f"{system_name}_{extension}.json")
    with open(file_path, "w") as f:
        json.dump(json_data, f, indent=4)


def write_system_tsv(tsv_data, model, version, system_name, extension, root_path):
    # Create the folder for the system if it does not already exist
    folder_path = os.path.join(root_path, model, version)
    os.makedirs(folder_path, exist_ok=True)

    # Write the TSV data to a file
    file_path = os.path.join(folder_path, f"{system_name}_{extension}.tsv")
    with open(file_path, "w") as f:
        f.write(tsv_data)
