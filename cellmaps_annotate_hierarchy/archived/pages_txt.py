import os
import json

def write_system_page(text, model, version, system_name, extension, root_path):
    """
    Write the prompt/analysis to a .txt file in the specified directory.

    :param text: The text to be written to the file.
    :param model: The name of the model.
    :param version: The version of the model.
    :param system_name: The name of the system.
    :param extension: The extension for the file (should be 'txt' for plain text files).
    :param root_path: The root directory where the file should be written.
    """
    # Create the folder for the system if it does not already exist
    folder_path = os.path.join(root_path, model, version, system_name)
    os.makedirs(folder_path, exist_ok=True)

    # Write the prompt text to a file
    file_name = f"{system_name}_{extension}.txt"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as f:
        f.write(text)

    
def read_system_page(model, version, system_name, extension, root_path):
    """
    Read the contents of a .txt file in the specified directory.

    :param model: The name of the model.
    :param version: The version of the model.
    :param system_name: The name of the system.
    :param extension: The extension for the file (should be 'txt' for plain text files).
    :param root_path: The root directory where the file should be read from.
    :return: The contents of the file as a string.
    """
    # Construct the path to the file
    folder_path = os.path.join(root_path, model, version, system_name)
    file_name = f"{system_name}_{extension}.txt"
    file_path = os.path.join(folder_path, file_name)

    # Read and return the contents of the file
    with open(file_path, "r") as f:
        return f.read()
