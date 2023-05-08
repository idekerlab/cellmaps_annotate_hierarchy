from file_io import read_system_json, get_root_path
from model_cx2 import get_genes
import requests
import json
import csv
from collections import defaultdict


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


###NEW CODE ADDED BY CLARA TO VALIDATE HUGO SYMBOLS
class GeneValidator:
    def __init__(self, file_path):
        self.gene_symbol_set = set()
        self.alias_map = defaultdict(str)

        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            next(reader)  # Skip header row
            for cells in reader:
                if cells[0]:
                    gene = cells[0].upper()
                    self.gene_symbol_set.add(gene)

                    if len(cells) > 1 and cells[1]:
                        previous_symbols = cells[1].split(", ")
                        for symbol in previous_symbols:
                            self.alias_map[symbol.upper()] = gene

                    if len(cells) > 2 and cells[2]:
                        alias_symbols = cells[2].split(", ")
                        for alias in alias_symbols:
                            self.alias_map[alias.upper()] = gene

    def validate_human_genes(self, genes):
        official_genes = set()
        invalid_genes = set()
        updated_genes = {}

        for raw_term in genes:
            # print(f'validate Hugo symbol for {raw_term}')
            term = raw_term.upper()
            if term in self.gene_symbol_set:
                official_genes.add(term)
            elif term in self.alias_map:
                official_gene = self.alias_map[term]
                official_genes.add(official_gene)
                updated_genes[term] = official_gene
                invalid_genes.add(term)
            else:
                invalid_genes.add(term)

        return {
            'official_genes': official_genes,
            'invalid': invalid_genes,
            'updated_genes': updated_genes
        }

def get_gene_symbols(system, hgnc_file_path = './hgnc_genes.tsv' ):
    genes = get_genes(system)
    validator = GeneValidator(hgnc_file_path)
    result = validator.validate_human_genes(genes)
    updated_gene_symbols = list(result['official_genes'])
    return updated_gene_symbols