import os
import json
import sys
from file_io import get_model_directory_path,write_system_json, get_root_path
from model_cx2 import get_system, get_genes

from hugo import get_hugo_data
from file_io import read_system_json, write_system_tsv
import pandas as pd
from io import StringIO
from uniprot import get_uniprot_data_for_system, summarize_uniprot_features, summarized_uniprot_features_to_tsv
from chatgpt_prompts import create_system_prompt_page
from pages import write_system_page, write_model_page, dataframe_to_html_table

## Define MuSIC2 specific prompt functions
def create_music_2_chatGPT_prompt(system, tsv_data, n_genes=2, gene_candidacy_text=''):
    """
    Create a ChatGPT prompt based on the given protein list and TSV data.

    :param protein_list: A list of protein names.
    :param tsv_data: A string containing TSV formatted uniprot summary data.
    :param n_genes: An integer representing the minimum number of genes for a feature to be included.
    :return: A string containing the ChatGPT prompt in HTML format.
    """
    # Read the TSV data into a DataFrame
    tsv_file = StringIO(tsv_data)
    df = pd.read_csv(tsv_file, sep='\t')
    
    protein_list = get_genes(system)

    # Generate the ChatGPT prompt in HTML format
    prompt_text = f"Your response should be formatted as HTML paragraphs"
    prompt_text += f"The following is a system of interacting proteins."
    prompt_text += f' Write a critical analysis of this system, describing your reasoning as you go.'
    prompt_text += f'\nWhat mechanisms and biological processes are performed by this system?'
    prompt_text += f'\nWhat cellular components and complexes are involved in this system?'
    prompt_text += f"\nDiscuss potential names for the system. Select the best name and place it in a paragraph at the beginning of your output?"
    prompt_text += f'\nProvide references for your reasoning'
    prompt_text += f'\nProteins: '
    prompt_text += ", ".join(protein_list) + ".\n\n"
    prompt_text += f"\nA critical goal of the analysis is to determine what, if any, relationship this system has to cancer, and specifically to pediatric cancer" #or osteosarcoma
    prompt_text += f'\n\nSystem features from a Uniprot analysis: \n'
    
    prompt_text = add_uniprot_feature_summary(prompt_text, df)

    prompt = f"<div class='code-section'><button class='copy-prompt-button' onclick='copyPrompt()'>Copy Prompt</button>"
    prompt += f"<pre><code id='prompt-code'>{prompt_text}</code></pre></div>"
    prompt += "<script>function copyPrompt() {var copyText = document.getElementById('prompt-code').innerText; navigator.clipboard.writeText(copyText);}</script>"
    return prompt

# add uniprot feature summary
def add_uniprot_feature_summary(prompt_text, feature_dataframe, n_genes=2):
    for index, row in feature_dataframe.iterrows():
        number_of_genes = 0
        if row['Number of Genes'] is not None:
            number_of_genes = int(row['Number of Genes'])
        if number_of_genes >= n_genes:
            prompt_text += f"{row['Feature']}: {row['Number of Genes']} proteins: {row['Genes']}\n"
    return prompt_text

            
def create_music_2_system_analysis_page(system_name, tsv_data, n_genes=2):
    # Read the TSV data into a DataFrame
    tsv_file = StringIO(tsv_data)
    df = pd.read_csv(tsv_file, sep='\t')

    # Filter the DataFrame based on the n_genes criterion
    df = df[df['Number of Genes'] >= n_genes]
    
    uniprot_table = dataframe_to_html_table(df)

    # Create the ChatGPT analysis section with a placeholder for the analysis text
    chatgpt_analysis = "<h2>ChatGPT 4 Analysis</h2>\n<p>Paste ChatGPT analysis here:</p>\n<!-- Analysis goes here -->"

    # Create the HTML page with the system summary
    page_title = f"{system_name} Analysis"
    html_page = f"<!DOCTYPE html>\n<html>\n<head>\n<title>{page_title}</title>\n</head>\n<body>\n<h1>{system_name} System Summary</h1>\n<h2>Proteins</h2>\n<p>{', '.join(get_genes(system))}</p>\n<h2>UniProt Data</h2>\n{uniprot_table}\n{chatgpt_analysis}\n</body>\n</html>"

    return html_page



if __name__ == "__main__":

    workdir = sys.argv[1]
    sig_sys_txt = sys.argv[2]

    os.environ["MODEL_ANNOTATION_ROOT"] = workdir


    ## load the model 
    model_name = "MuSIC2_Maps"
    version = "v1.1_April2023"
    model_cx2_filename = "MuSIC2_v1.1_April2023.cx2"
    print(get_model_directory_path(model_name, version))

    model_path = os.path.join(get_model_directory_path(model_name, version), model_cx2_filename)

    with open(model_path, encoding='utf-8') as f:
        data = f.read()
        model = json.loads(data)
    # print(model)


    # load the system list
    with open(sig_sys_txt, 'r') as f:
        systems = [x.strip() for x in f.readlines()]
    # get genes for each system
    for system_name in systems:
        # select systems
        system = get_system(model, system_name)
        # system
        write_system_json(system, model_name, version+f'/{system_name}', system_name, "data", get_root_path())
        genes = get_genes(system)
        # print(f'{system_name}: {genes}')
        # for gene in genes:
        #     print(gene)
        if len(genes)<50: # right now checking small systems
            # get hugo data
            hugo_data = get_hugo_data(system)

            write_system_json(hugo_data, model_name, version +f'/{system_name}', system_name, "hugo", get_root_path())

            hugo_data = read_system_json(model_name, version +f'/{system_name}', system_name, "hugo", get_root_path())
            # get uniprot data
            uniprot_data = get_uniprot_data_for_system(system, hugo_data=hugo_data)
            write_system_json(uniprot_data, model_name, version +f'/{system_name}', system_name, "uniprot", get_root_path())
                
            # get uniprot summary
            summarized_features = summarize_uniprot_features(uniprot_data)
            tsv_data = summarized_uniprot_features_to_tsv(summarized_features)
            write_system_tsv(tsv_data, model_name, version +f'/{system_name}', system_name, "uniprot_summary", get_root_path())


            # create prompt page
            prompt = create_music_2_chatGPT_prompt(system, tsv_data)
            prompt_page = create_system_prompt_page(system_name, prompt)
            write_system_page(prompt_page, model_name, version +f'/{system_name}', system_name, "chatgpt_prompt", get_root_path())
            analysis_page = create_music_2_system_analysis_page(system_name, tsv_data)
            write_system_page(analysis_page, model_name, version +f'/{system_name}', system_name, "analysis", get_root_path())
            # update the model page to include links to the new pages
            write_model_page(model_name, version, get_root_path())
