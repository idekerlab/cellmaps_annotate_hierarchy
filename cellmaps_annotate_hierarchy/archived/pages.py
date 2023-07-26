import os
import json
from io import StringIO
import pandas as pd
from model_nodes_edges import get_genes
from bs4 import BeautifulSoup

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
    folder_path = os.path.join(root_path, model, version, system_name)
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

def write_system_page_txt(text, model, version, system_name, extension, root_path):
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

def write_response_page_html(response_path,response_text, system):
    with open(response_path + '.html', "w") as f:
        title, summary, ref = parse_gpt4_response(response_text)
        chatgpt_res = f"<h2>{system} GPT response</h2><h3>{title}</h3><h4>Summary</h4><div>{summary}</div><h4>Reference</h4><div>{ref}</div>"
        f.write(f"<!DOCTYPE html>\n<html>\n{chatgpt_res}\n</html>")

def read_system_page(model, version, system_name, extension, root_path):
    # Construct the folder path and file path based on the provided parameters
    folder_path = os.path.join(root_path, model, version, system_name)
    file_name = f"{system_name}_{extension}.html"
    file_path = os.path.join(folder_path, file_name)

    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist")
        return None

    # If the file exists, read and return its contents
    with open(file_path, "r") as f:
        html_content = f.read()

    return html_content

def read_system_page_txt(model, version, system_name, extension, root_path):
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

def parse_gpt4_response(response):
    """
    Parses the GPT-4 response to extract the title, summary and references.

    :param response: The GPT-4 response in HTML format.
    :return: A tuple containing the title, summary and references.
    """
    soup = BeautifulSoup(response, "html.parser")

    # Extract the title, summary, and references from the GPT-4 response
    title = soup.title.string if soup.title else ''
    summary = str(soup.summary) if soup.summary else ''
    summary = summary.replace('\n', '<br>') # Replace newlines with <br> tags
    references = str(soup.references) if soup.references else ''
    references = references.replace('\n', '<br>') # Replace newlines with <br> tags

    return title, summary, references

def create_music_2_system_analysis_page(system, gpt4_response, nodes_table, tsv_data = [], n_genes=2):
    # Parse GPT-4 response
    gpt4_title, gpt4_summary, gpt4_references = parse_gpt4_response(gpt4_response)

    # Read the TSV data into a DataFrame
    if tsv_data:
        tsv_file = StringIO(tsv_data)
        df = pd.read_csv(tsv_file, sep='\t')

        # Filter the DataFrame based on the n_genes criterion
        df = df[df['Number of Genes'] >= n_genes]
        
        gene_feature_table = dataframe_to_html_table(df)

    # Insert the GPT-4 response in the analysis section
    chatgpt_analysis = f"<h2>GPT 4 Analysis</h2><h3>{gpt4_title}</h3><h4>Summary</h4><div>{gpt4_summary}</div><h4>Reference</h4><div>{gpt4_references}</div>"
    # define style 
    style = """
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
        """
    # Create the HTML page with the system summary
    page_title = f"{system} Analysis"
    html_page = f"<!DOCTYPE html>\n<html>\n<head>\n<title>{page_title}</title>\n{style}\n</head>\n<body>\n<h1>{system} System Summary</h1>\n<h2>Proteins</h2>\n<p>{', '.join(get_genes(system, nodes_table))}</p>\n{chatgpt_analysis}\n<h2>Gene Feature Summary</h2>\n{gene_feature_table}\n</body>\n</html>"
    return html_page

