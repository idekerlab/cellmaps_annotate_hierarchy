import pandas as pd
from io import StringIO
from model_nodes_edges import get_genes
import re
import os
import textwrap
from file_io import get_model_directory_path
from ontology_modify import find_children, parent_unique_genes

#CH: new gene feature summary from mygene GO terms
def add_gene_feature_summary(prompt_text, feature_dataframe, n_genes=2):
    for index, row in feature_dataframe.iterrows():
        number_of_genes = 0
        if row['Number of Genes'] is not None:
            number_of_genes = int(row['Number of Genes'])
        if number_of_genes >= n_genes:
            prompt_text += f"{row['Feature']}: {row['Number of Genes']} proteins: {row['Genes']}\n"
    return prompt_text

#####VOID uniprot feature summary####
def add_uniprot_feature_summary(prompt_text, feature_dataframe, n_genes=2):
    for index, row in feature_dataframe.iterrows():
        number_of_genes = 0
        if row['Number of Genes'] is not None:
            number_of_genes = int(row['Number of Genes'])
        if number_of_genes >= n_genes:
            prompt_text += f"{row['Feature']}: {row['Number of Genes']} proteins: {row['Genes']}\n"
    return prompt_text

def create_nesa_chatGPT_prompt(protein_list, tsv_data, n_genes=2, gene_candidacy_text=''):
    """
    Create a ChatGPT prompt based on the given protein list and TSV data.

    :param protein_list: A list of protein names.
    :param tsv_data: A string containing TSV formatted summary data.
    :param n_genes: An integer representing the minimum number of genes for a feature to be included.
    :return: A string containing the ChatGPT prompt in HTML format.
    """
    # Read the TSV data into a DataFrame
    tsv_file = StringIO(tsv_data)
    df = pd.read_csv(tsv_file, sep='\t')

    preamble = "You are assisting a molecular biologist in the analysis of a system of interacting proteins \n"
    
   # autism_instructions = "\nA critical goal of the analysis is to determine what, if any, relationship this system has to ASD (Autism Spectrum Disorder)" # SA: removed
    autism_instructions = "\n"
    
    general_analysis_instructions = "\nSave any summary analysis of the system to the last paragraph. \
                \nAvoid overly general statements of how the proteins are involved in various cellular processes\n\
                \nAvoid recapitulating the goals of the analysis. \n\
                \nsummarize your analysis in a jason data structure with the analysis text plus the references in a dictionary, indexed such that the references in the text are the keys to the dictionary."
    
    # \nYour response should be formatted as HTML paragraphs"
    
    task_instructions = "\nFirst, write a critical analysis of this system, describing your reasoning as you go and providing references to scientific papers.\
    \nWhat mechanisms and biological processes are performed by this system?\
    \nWhat cellular components and complexes are involved in this system?\
    \nSecond, analyze the proteins to discuss which of them might be the product of novel ASD-risk genes\
    \nThird, discuss potential names for the system. Names should reflect functional themes  and should be specific not general. The name should not be ASD-specific. Select the best name and place it in a paragraph \
    at the beginning of your output\
    \nFourth, provide complete paper references with pubmed link."
                

    # Generate the ChatGPT prompt in HTML format
    prompt_text = f"\n"
    prompt_text += preamble
    prompt_text += autism_instructions
    prompt_text += task_instructions
    prompt_text += general_analysis_instructions


    prompt_text += f'\nProteins: '
    prompt_text += ", ".join(protein_list) + ".\n\n"

    prompt_text += f"\nHere are some ASD-related facts about these proteins"
    prompt_text += f"\n{gene_candidacy_text}"
    
    prompt_text += f'\n\nSystem features from a Uniprot analysis: \n'
    prompt_text = add_uniprot_feature_summary(prompt_text, df)

    prompt = f"<div class='code-section'><button class='copy-prompt-button' onclick='copyPrompt()'>Copy Prompt</button>"
    prompt += f"<pre><code id='prompt-code'>{prompt_text}</code></pre></div>"
    prompt += "<script>function copyPrompt() {var copyText = document.getElementById('prompt-code').innerText; navigator.clipboard.writeText(copyText);}</script>"
    return prompt



# chatgpt prompt for music2
def create_music_2_chatGPT_prompt_html(system, nodes, tsv_data, n_genes=2, gene_candidacy_text=''):
    """
    Create a ChatGPT prompt based on the given protein list and TSV data.

    :param systems: name of the system 
    :param nodes: the nodes table from hidef
    :param tsv_data: A string containing TSV formatted uniprot summary data.
    :param n_genes: An integer representing the minimum number of genes for a feature to be included.
    :return: A string containing the ChatGPT prompt in HTML format.
    """
    # Read the TSV data into a DataFrame
    tsv_file = StringIO(tsv_data)
    df = pd.read_csv(tsv_file, sep='\t')
    
    protein_list = get_genes(system, nodes)

    # Generate the ChatGPT prompt in HTML format
    prompt_text = f"Your response should be formatted as HTML paragraphs"
    prompt_text += 'Write a critical and concise analysis of this system, describing your reasoning as you go and providing references to scientific papers. \
        \nFormat with Title, Summary, and References sections.\
        \nAvoid overly general statements of how the proteins are involved in various cellular processes\n\
        \nAvoid recapitulating the goals of the analysis. '
    prompt_text += '\nWhat cellular components and complexes are involved in this system?'
    prompt_text += '\nWhat mechanisms and biological processes are performed by this system?'
    prompt_text += "\nPropose a name for the system to reflect the function and location, and should be specific but brief. Do not compose an acronym. Place it as the title of your report"
    prompt_text += '\nProvide complete paper references with pubmed link'

    
    prompt_text += '\nProteins: '
    prompt_text += ", ".join(protein_list) + ".\n"

    prompt_text += "\nA critical goal of the analysis is to determine if this is a novel complex or if any proteins are novel members of a known complex"
    prompt_text += '\nSystem features from GO terms: \n'
    prompt_text = add_gene_feature_summary(prompt_text, df)

    prompt = f"<div class='code-section'><button class='copy-prompt-button' onclick='copyPrompt()'>Copy Prompt</button>"
    prompt += f"<pre><code id='prompt-code'>{prompt_text}</code></pre></div>"
    prompt += "<script>function copyPrompt() {var copyText = document.getElementById('prompt-code').innerText; navigator.clipboard.writeText(copyText);}</script>"
    return prompt

## CH: modify the function to generate text not html 
def create_music_2_chatGPT_prompt_text(system, nodes, tsv_data = [], n_genes=2, gene_candidacy_text=''):
    """
    Create a ChatGPT prompt based on the given protein list and TSV data.

    :param system: name of the system 
    :param nodes: the nodes table from hidef
    :param tsv_data: A string containing TSV formatted uniprot summary data.
    :param n_genes: An integer representing the minimum number of genes for a feature to be included.
    :return: A string containing the ChatGPT prompt in plain text format.
    """
    if tsv_data:   
        # Read the TSV data into a DataFrame
        tsv_file = StringIO(tsv_data)
        df = pd.read_csv(tsv_file, sep='\t')
    
    protein_list = get_genes(system, nodes)

    # Generate the ChatGPT prompt in plain text format
    # prompt_text = "You are assisting a molecular biologist in the analysis of a system of proteins that are physically close to each other and/or interact with each other."
    prompt_text = "Your response should be formatted as Markdown paragraphs\n"
    prompt_text += 'Write a critical and concise analysis of this human protein system, describing your reasoning as you go and providing references to scientific papers.\n'
    prompt_text += "\nA critical goal of the analysis is to determine if this is a novel complex or if any proteins are novel members of a known complex\n"
    prompt_text += '\nFormat with Title, Summary, and References sections.\
        \nAvoid overly general statements of how the proteins are involved in various cellular processes\
        \nAvoid repeating the goals of the analysis.\n'
    prompt_text += '\nWhat cellular components and complexes are involved in this system?'
    prompt_text += '\nWhat mechanisms and biological processes are performed by this system?'
    prompt_text += "\nPropose a name for the system to reflect the cellular location and function, and should be specific but brief. Do not compose an acronym. Place it as the title of your report"
    # prompt_text += '\nProvide paper references with pubmed link\n'
    

    prompt_text += '\nHuman Proteins: '
    prompt_text += ", ".join(protein_list) + ".\n"
    
    if tsv_data: 
        prompt_text += '\nSystem features from GO terms: \n'
        
        prompt_text = add_gene_feature_summary(prompt_text, df, n_genes=n_genes)
    
    return prompt_text


def create_music_2_chatGPT_prompt_parent(system, nodes, edges):

    children = find_children(system, edges)
    unique_genes = parent_unique_genes(system, children, nodes)
    # Generate the ChatGPT prompt in plain text format
    # prompt_text = "You are assisting a molecular biologist in the analysis of a system of proteins that are physically close to each other and/or interact with each other."
    prompt_text = "Your response should be formatted as Markdown paragraphs\n"
    prompt_text += 'This is a human protein system high in a cell hierarchy and has child systems connect to it as well as residual proteins only belong to this system. From the protein list and the knowledge of how these proteins cluster, write a critical and concise analysis of this human protein system. Describe your reasoning as you go and providing references to scientific papers.\n'
    prompt_text += "\nA critical goal of the analysis is to determine if this is a novel complex or if any proteins are novel members of a known complex\n"
    prompt_text += '\nFormat with Title, Summary, and References sections.\
        \nAvoid overly general statements of how the proteins are involved in various cellular processes\
        \nAvoid recapitulating the goals of the analysis.\n'
    prompt_text += '\nWhat cellular components and complexes are involved in this system?'
    prompt_text += '\nWhat mechanisms and biological processes are performed by this system?'
    prompt_text += "\nPropose a name for the system to reflect the function and location, and should be specific but brief. Do not compose an acronym. Place it as the title of your report"
    # prompt_text += '\nProvide paper references, if any\n'

    prompt_text += '\nHuman Protein List: \n'
    prompt_text +=f"proteins only in this high level system: " + ", ".join(unique_genes) + ".\n"
    for child in children:
        child_protein_list = get_genes(child, nodes)
        prompt_text += f"proteins in child system {child}: " + ", ".join(child_protein_list) + ".\n"
    
    return prompt_text

def create_chatGPT_prompt_parent():
    # Generate the ChatGPT prompt
    prompt_text = 'Write a critical and concise analysis of this system from integrating the child systems summary, describing your reasoning as you go.\
        \nFormat with Title, Summary, and References sections.\
        \nAvoid overly general statements of how the proteins are involved in various cellular processes\n\
        \nAvoid recapitulating the goals of the analysis. '
    prompt_text += '\nWhat cellular components and complexes are involved in this system?'
    prompt_text += '\nWhat mechanisms and biological processes are performed by this system?'
    prompt_text += "\nDiscuss potential names for the system. Names should reflect the function and location, and should be specific not general. Select the best name and place it as the title of your report"
    prompt_text += '\nProvide complete paper references with pubmed link, if any'
    prompt_text += "\nA critical goal of the analysis is to determine if this is a novel complex or if any proteins are novel members of a known complex"

    return prompt_text


def create_chatGPT_prompt(protein_list, tsv_data, n_genes=2, gene_candidacy_text=''):
    """
    Create a ChatGPT prompt based on the given protein list and TSV data.

    :param gene_candidacy_text:
    :param protein_list: A list of protein names.
    :param tsv_data: A string containing TSV formatted summary data.
    :param n_genes: An integer representing the minimum number of genes for a feature to be included.
    :return: A string containing the ChatGPT prompt in HTML format.
    """
    # Read the TSV data into a DataFrame
    tsv_file = StringIO(tsv_data)
    df = pd.read_csv(tsv_file, sep='\t')

    # Filter the DataFrame based on the n_genes criterion
    # df['Number of Genes'] = pd.to_numeric(df['Number of Genes'], errors='coerce')
    # print(df[df['Number of Genes']])

    # df = df[df['Number of Genes'] >= n_genes]

    # Generate the ChatGPT prompt in HTML format
    prompt_text = f"Your response should be formatted as HTML paragraphs"
    prompt_text += f"The following is a system of interacting proteins."
    prompt_text += f' Write a critical analysis of this system, describing your reasoning as you go.'
    prompt_text += f'\nWhat mechanisms and biological processes are performed by this system?'
    prompt_text += f'\nWhat cellular components and complexes are involved in this system?'
    prompt_text += f'\nProteins: '
    prompt_text += ", ".join(protein_list) + ".\n\n"
    prompt_text += f"\nA critical goal of the analysis is to determine what, if any, relationship this system has to ASD (Autism Spectrum Disorder)"
    prompt_text += f"\nHere are some ASD-related facts about these proteins"
    prompt_text += f"\n{gene_candidacy_text}"
    prompt_text += f'\n\nSystem features from a Uniprot analysis: \n'

    for index, row in df.iterrows():
        number_of_genes = 0
        if row['Number of Genes'] is not None:
            number_of_genes = int(row['Number of Genes'])
        if number_of_genes >= n_genes:
            prompt_text += f"{row['Feature']}: {row['Number of Genes']} proteins: {row['Genes']}\n"

    prompt = f"<div class='code-section'><button class='copy-prompt-button' onclick='copyPrompt()'>Copy Prompt</button>"
    prompt += f"<pre><code id='prompt-code'>{prompt_text}</code></pre></div>"
    prompt += "<script>function copyPrompt() {var copyText = document.getElementById('prompt-code').innerText; navigator.clipboard.writeText(copyText);}</script>"
    return prompt


def estimate_tokens(text):
    """
    Estimate the number of tokens in a text string based on the approximation that 1 token is around 4 characters in English.

    Args:
        text (str): The text string to be estimated.

    Returns:
        int: The estimated number of tokens.
    """

     # Count the number of characters
    char_count = len(text)

    # Count the number of words and punctuation
    word_punctuation_count = len(re.findall(r'\b\w+\b|[^\w\s]', text))
    # print(f"word_punctuation_count: {word_punctuation_count}")

    # Estimate tokens based on characters and words
    token_estimate_chars = char_count / 4
    token_estimate_words = word_punctuation_count * 1.5
    
    # print(f"token_estimate_chars: {token_estimate_chars}")
    # print(f"token_estimate_words: {token_estimate_words}")
 
    # Take the average of both estimations
    tokens = max(token_estimate_chars, token_estimate_words)


    return int(tokens)

def get_summary(file_name):
    with open(file_name, "r") as file:
        content = file.read()
        
    # Regular expression pattern for matching the Summary section
    pattern = re.compile(r'Summary:\s*(.*?)References:', re.DOTALL)
    match = re.search(pattern, content)
    
    if match:
        # The 1st group is the Summary content
        summary = match.group(1).strip()
        return summary
    else:
        print("No Summary found.")
        return None

def concat_children_summary(model_name, version, children, nodes_table):

    summary_string = "\n\nHere are the summaries of the child nodes directly branched from this parent system: \n"

    for child in children:
        genes = get_genes(child, nodes_table)
        # print(genes)

        summary = get_summary(os.path.join(get_model_directory_path(model_name, version), child, f'{child}_chatgpt_response.txt'))
        # Indent the summary
        indented_summary = textwrap.indent(summary, "    ")
        # Add to the overall summary
        summary_string += "\nChild cluster with Genes: " + ', '.join(genes) + "\n" + indented_summary + "\n"

    return summary_string


def create_system_prompt_page(system_name, prompt):
    """
    Create an HTML page with a ChatGPT prompt for the specified system.

    :param system_name: The name of the system.
    :param prompt: The ChatGPT prompt for the system.
    :return: A string containing the HTML page.
    """

    # Create the HTML page with the specified title and prompt content
    html = f"<!DOCTYPE html>\n<html>\n<head>\n<title>{system_name} Summary ChatGPT Prompt</title>\n</head>\n<body>\n{prompt}\n</body>\n</html>"
    return html


