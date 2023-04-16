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
        response = requests.get(f'https://rest.genenames.org/fetch/symbol/{gene}',
                                headers=headers)
        data = json.loads(response.content)["response"]["docs"][0]
        # print(data)
        hugo_data[gene] = data
    return hugo_data
