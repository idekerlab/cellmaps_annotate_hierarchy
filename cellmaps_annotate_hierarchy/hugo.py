from file_io import read_system_json, get_root_path
from model_cx2 import get_genes
import requests
import json


def get_hugo_data(system):
    gene_names = get_genes(system)
    hugo_data = {}

    for gene in gene_names:
        print(f'getting Hugo data for {gene}')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}
        
        ## Old hugo names may not be found in the current Hugo database, added this following loop to search aliases and previous symbols --Clara
         # First, try searching with the current symbol
        response = requests.get(f'https://rest.genenames.org/fetch/symbol/{gene}', headers=headers)
        if response.status_code == 200 and response.json()['response']['numFound'] > 0:
            data = json.loads(response.content)["response"]["docs"][0]
            # print(data)
            hugo_data[gene] = data
            continue
            
        # If not found, try searching with alias symbols
        response = requests.get(f'https://rest.genenames.org/fetch/alias_symbol/{gene}', headers=headers)
        if response.status_code == 200 and response.json()['response']['numFound'] > 0:
            data = json.loads(response.content)["response"]["docs"][0]
            # print(data)
            hugo_data[gene] = data
            continue
        
        # If still not found, try searching with previous symbols
        response = requests.get(f'https://rest.genenames.org/fetch/prev_symbol/{gene}', headers=headers)
        if response.status_code == 200 and response.json()['response']['numFound'] > 0:
            data = json.loads(response.content)["response"]["docs"][0]
            # print(data)
            hugo_data[gene] = data
            continue
        
        print(f"Could not find information for {gene}.")

    return hugo_data
