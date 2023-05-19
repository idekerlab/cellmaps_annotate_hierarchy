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

def dataframe_to_markdown_table(df):
    table_md = "| " + " | ".join(df.columns) + " |\n"
    table_md += "| " + " | ".join("---" for _ in df.columns) + " |\n"
    for index, row in df.iterrows():
        table_md += "| " + " | ".join(str(val) for val in row.values) + " |\n"
    return table_md
    


def write_system_page(text, file_type, model, version, system_name, extension, root_path):
    """
    Write the prompt/analysis to a .txt file in the specified directory.

    :param text: The text to be written to the file.
    :param file_type: The type of file to be written (e.g. 'txt' or 'html' or 'md')
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
    file_name = f"{system_name}_{extension}.{file_type}"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as f:
        f.write(text)

def read_system_page(file_type, model, version, system_name, extension, root_path):
    """
    Read the contents of a .txt file in the specified directory.
    :param file_type: The type of file to be read (e.g. 'txt' or 'html' or 'md')
    :param model: The name of the model.
    :param version: The version of the model.
    :param system_name: The name of the system.
    :param extension: The extension for the file (should be 'txt' for plain text files).
    :param root_path: The root directory where the file should be read from.
    :return: The contents of the file as a string.
    """
    # Construct the path to the file
    folder_path = os.path.join(root_path, model, version, system_name)
    file_name = f"{system_name}_{extension}.{file_type}"
    file_path = os.path.join(folder_path, file_name)

    # Read and return the contents of the file
    with open(file_path, "r") as f:
        return f.read()

def parse_gpt4_response(response):
    """
    Parses the GPT-4 html formated response to extract the title, summary and references.

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
    # Read the TSV data into a DataFrame
    if tsv_data:
        tsv_file = StringIO(tsv_data)
        df = pd.read_csv(tsv_file, sep='\t')

        # Filter the DataFrame based on the n_genes criterion
        df = df[df['Number of Genes'] >= n_genes]
        
        gene_feature_table = dataframe_to_markdown_table(df)
    protein_list = get_genes(system, nodes_table)
    # Create the markdown page with the system summary
    page_title = f"# {system} Analysis"
    markdown_page = f"{page_title}\n\n## Proteins: \n\n{', '.join(sorted(protein_list))}\n\n{gpt4_response}\n\n## Gene Feature Summary: \n\n{gene_feature_table}\n"
    return markdown_page


