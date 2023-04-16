import os
import json


def dataframe_to_html_table(df):
    table_html = "<table>\n"
    table_html += "<thead>\n<tr>\n"
    table_html += "".join([f"<th>{col}</th>" for col in df.columns])
    table_html += "</tr>\n</thead>\n<tbody>\n"
    for index, row in df.iterrows():
        table_html += "<tr>\n"
        table_html += "".join([f"<td>{val}</td>" for val in row.values])
        table_html += "</tr>\n"
    table_html += "</tbody>\n</table>"
    return table_html


def write_system_page(html_content, model, version, system_name, extension, root_path):
    # Create the folder for the system if it does not already exist
    folder_path = os.path.join(root_path, model, version)
    os.makedirs(folder_path, exist_ok=True)

    # Write the HTML content to a file
    file_name = f"{system_name}_{extension}.html"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as f:
        f.write(html_content)

    # Update the urls.json file
    urls_file_path = os.path.join(root_path, "urls.json")
    urls_data = []

    if os.path.isfile(urls_file_path) is True:
        with open(urls_file_path, "r") as f:
            urls_data = json.load(f)

    # Find the model and version in the urls data
    model_data = next((x for x in urls_data if x["name"] == model), None)
    if not model_data:
        model_data = {"name": model, "versions": []}
        urls_data.append(model_data)

    version_data = next((x for x in model_data["versions"] if x["name"] == version), None)
    if not version_data:
        version_data = {"name": version, "files": []}
        model_data["versions"].append(version_data)

    # Add the new system file to the version data
    file_url = f"{model}/{version}/{file_name}"
    version_data["files"].append({"name": system_name, "url": file_url})

    # Write the updated urls data to the file
    with open(urls_file_path, "w") as f:
        json.dump(urls_data, f, indent=4)


def write_model_page(model_name, version, root_path):
    """
    Write an index.html file to the same directory as the urls.json file.
    The index.html page should display links to the documents in a hierarchical format.
    It should also have a title "<model name> Annotation Analysis".

    :param model_name: The name of the model.
    :param version: The version of the model.
    :param root_path: The root path of the model.
    """
    # Create the HTML for the index page
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{model_name} Annotation Analysis</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                color: #333333;
                margin: 0;
                padding: 0;
            }}

            h1 {{
                font-size: 2em;
                margin: 0 0 0.5em;
            }}

            ul {{
                list-style-type: none;
                margin: 0;
                padding: 0;
            }}

            li {{
                font-size: 1.2em;
                margin: 0;
            }}

            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 2em;
                background-color: #ffffff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{model_name} Annotation Analysis</h1>
            <ul>
                {get_file_links(model_name, version, root_path)}
            </ul>
        </div>
    </body>
    </html>
    """

    # Write the HTML to the index file
    index_file_path = os.path.join(root_path, model_name, version, f"{model_name}_v_{version}.html")
    with open(index_file_path, "w") as index_file:
        index_file.write(html)


def get_file_links(model_name, version, root_path):
    """
    Get the HTML for the links to the files in the model directory.

    :param model_name: The name of the model.
    :param version: The version of the model.
    :param root_path: The root path of the model.
    :return: The HTML for the links to the files in the model directory.
    """
    file_links = ""
    model_path = os.path.join(root_path, model_name, version)

    # Get a sorted list of all the files in the model directory (excluding hidden files)
    file_list = sorted(
        f for f in os.listdir(model_path) if not f.startswith('.') and os.path.isfile(os.path.join(model_path, f)))

    # Group the files by directory
    files_by_dir = {}
    for file in file_list:
        file_path = os.path.join(model_path, file)
        dir_path = os.path.dirname(os.path.relpath(file_path, model_path))
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(file)

    # Generate the links for each directory and file
    for dir_path, files in files_by_dir.items():
        # Skip directories that don't have any visible files
        if not files:
            continue

        # Add a heading for the current directory
        file_links += f"<li><strong>{os.path.basename(dir_path)}</strong></li>"

        # Add links for all the files in the current directory
        for file in sorted(files):
            file_path = os.path.join(model_path, dir_path, file)
            file_url = os.path.relpath(file_path, model_path)
            file_links += f"<li><a href='{file_url}'>{file}</a></li>"

    return file_links
