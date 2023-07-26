import pandas as pd

# function for summarizing gene location
def summarize_gene_location(gene_list, loc_df):
    '''
    gene_list: a list of gene names in the system of query
    loc_df: the dataframe of the location information from HPA
    return: a list of dictionaries, each dictionary is a summary of a location
    '''
    summarized_data = []

    # Iterate over each gene and its location(s)
    for _, row in loc_df.iterrows():
        if row['Gene name'] in gene_list:
            # there is uncertain in the reliability column, ignore it
            if row['Reliability'] != 'Uncertain':
                if pd.notnull(row['Main location']):
                    gene_name = row['Gene name']
                    locations = row['Main location'].split(';')
                    for location in locations:

                        existing_summary = next((item for item in summarized_data if location in item), None)
                        if existing_summary:
                # If this gene is not already associated with this location, add it
                            if gene_name not in existing_summary[location]["genes"]:
                                existing_summary[location]["number_of_genes"] += 1
                                existing_summary[location]["genes"].append(gene_name)
                        else:
                            # If the location does not exist in the summary yet, create a new summary for it
                            new_summary = {
                                location: {
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