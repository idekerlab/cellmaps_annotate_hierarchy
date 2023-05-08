import pandas as pd
from io import StringIO

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

def create_chatGPT_prompt(protein_list, tsv_data, n_genes=2, gene_candidacy_text=''):
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
