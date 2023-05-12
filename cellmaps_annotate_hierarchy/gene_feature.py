### functions to gather gene features from the root node mygene database
def get_go_terms(gene_info, go_type):
    '''
    :param gene_info: gene info from mygene database
    :param go_type: GO term type (CC, MF, BP)
    :return: go terms
    '''
    terms = []
    if 'go' in gene_info and go_type in gene_info['go']:
        data = gene_info['go'][go_type]
        # print(data)
        # If  not a list, make it a one-item list
        if not isinstance(data, list):
            data = [data]
        for desc in data:
            if 'term' in desc:
                terms.append(desc['term'])
    return terms

def summarize_gene_feature(root_node_info, gene_names):
    '''
    root_node_info: the json file of the root node
    gene_names: a list of gene names in the system of query
    return: a list of dictionaries, each dictionary is a summary of a gene
    '''
    summarized_data = []
    target_sections = ["MF", "BP", "CC"] # may need to change in the future 
    
    for result in root_node_info:
        gene_name = result["query"]
        if gene_name in gene_names: # The current gene name
            for section in target_sections:
                go_terms = get_go_terms(result, section)
                # pathway = result.get("pathway", {})
                # reactome =[name['name'] for name in pathway.get('reactome', [])]
                for term in go_terms:
                        # Check if this term is already in the summarized data
                        existing_summary = next((item for item in summarized_data if term in item), None)
                        if existing_summary:
                             # If this gene is not already associated with this term, add it
                            if gene_name not in existing_summary[term]["genes"]:
                                existing_summary[term]["number_of_genes"] += 1
                                existing_summary[term]["genes"].append(gene_name)
                        else:
                            new_summary = {
                                term: {
                                    "number_of_genes": 1,
                                    "genes": [gene_name]
                                }
                            }
                            summarized_data.append(new_summary)
    return summarized_data

def summarized_gene_feature_to_tsv(summarized_data):
    """
    Flatten the summarized data and sort it by the number of genes.

    :param summarized_data: The summarized data.
    :return: The flattened and sorted data in tsv format.
    """
    # Flatten the summarized data
    flattened_data = []
    for feature_dict in summarized_data:
        for feature, feature_data in feature_dict.items():
            flattened_data.append({
                "feature": feature,
                "number_of_genes": feature_data["number_of_genes"],
                "genes": ", ".join(feature_data["genes"])
            })

    # Sort the flattened data by the number of genes
    sorted_data = sorted(flattened_data, key=lambda x: x["number_of_genes"], reverse=True)

    # Convert the sorted data to tab-delimited text
    tsv_data = "Feature\tNumber of Genes\tGenes\n"
    for item in sorted_data:
        tsv_data += f"{item['feature']}\t{item['number_of_genes']}\t{item['genes']}\n"

    return tsv_data