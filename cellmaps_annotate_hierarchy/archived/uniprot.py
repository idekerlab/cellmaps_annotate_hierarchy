import requests
import json
from model_cx2 import get_genes
from FixGeneSymbols import latestGeneSymbol_2_uniprotID


def query_uniprot_by_id(uniprot_id):
    """
    Query UniProt for data about a protein given its gene symbol.

    :param gene_symbol: The gene symbol to search for.
    :return: The response text from UniProt or None if not found.
    """
    url = f"https://www.uniprot.org/uniprot/{uniprot_id}.json"
    # url = "https://www.uniprot.org/uniprot/"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}
   # print(f'querying uniprot id {uniprot_id}')
    response = requests.get(url,
                            headers=headers)
    # print(response.text)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def filter_uniprot_response(uniprot_json):
    """
    Filter a UniProt JSON response to include specific fields.

    :param uniprot_json: A parsed JSON response from UniProt.
    :return: A dictionary containing the filtered data.
    """
    filtered_data = {
        "UniProtKB_ID": uniprot_json["uniProtkbId"],
        "Description": uniprot_json["proteinDescription"]["recommendedName"]["fullName"]["value"],
        "GO": [],
        "Location": [],
        "Disease": [],
        "Disease_description": [],
        "Complexes": []
    }

    for comment in uniprot_json.get("comments", []):

        comment_type = comment.get("commentType")
        # print(f'comment of type: {comment_type}')
        if comment_type is not None:
            if comment_type == "SUBCELLULAR LOCATION":
                for loc in comment.get("subcellularLocations"):
                    location = loc.get("location")
                    # print(location)
                    values = location.get("value").split(",")
                    for value in values:
                        cleaned_value = value.strip().lower()
                        # print(cleaned_value)
                        filtered_data["Location"].append(cleaned_value)
            if comment_type == "DISEASE":
                # print(comment)
                disease = comment.get("disease")
                # print(disease)
                if disease is not None:
                    disease_id = disease.get("diseaseId")
                    disease_name = disease_id.split(",")[0]
                    description = disease.get("description")
                    filtered_data["Disease"].append(disease_name)
                    filtered_data["Disease_description"].append(f'{disease_name}: {description}')

            if comment_type == "SUBUNIT":
                for text in comment.get("texts"):
                    filtered_data["Complexes"].append(text.get("value"))
    for keyword in uniprot_json.get("keywords"):
        if keyword.get("category") == "Cellular component":
            name = keyword.get("name")
            cleaned_value = name.strip().lower()
            # print(cleaned_value)
            filtered_data["Location"].append(cleaned_value)
        if keyword.get("category") == "Disease":
            filtered_data["Disease"].append(keyword.get("name"))

    for db_ref in uniprot_json.get("uniProtKBCrossReferences", []):
        if db_ref["database"] == "GO":
            for prop in db_ref["properties"]:
                if prop["key"] == "GoTerm":
                    if prop["value"].split("0")[0] != "M":
                        filtered_data["GO"].append(prop["value"].split(":")[1])

    filtered_data["Location"] = list(set(filtered_data["Location"]))

    return filtered_data


def get_uniprot_data_for_system(system, useHGNC_Uniprot, hugo_data=None): # uses useHGNC_Uniprot flag
    gene_names = get_genes(system)
    analysis_data = {}
    # gene_names = [gene_names[0], gene_names[1]]
  #  print(f'gene names: {gene_names}')

    for gene_name in gene_names:
      #  print(f'gene name = {gene_name}')
        hugo_gene = hugo_data[gene_name]
        if useHGNC_Uniprot: ## SA: added if statement here
            # print("using hgnc table to map to uniprot ID")
            uniprot_ids = latestGeneSymbol_2_uniprotID(gene_name) 
        else:
            uniprot_ids = hugo_gene.get("uniprot_ids") # ToDo: remove
      #  print(f'uniprot_ids = {uniprot_ids}')
        if uniprot_ids is not None:
            uniprot_id = uniprot_ids[0]
            uniprot_data = query_uniprot_by_id(uniprot_id)

            if uniprot_data:
                filtered_data = filter_uniprot_response(uniprot_data)
                analysis_data[gene_name] = filtered_data
        else:
            print(f'no uniprot id found for {gene_name}')
    return analysis_data

def summarize_uniprot_features(data):
    """
    Take a data structure and output a new list of dictionaries
    summarizing specific features.

    :param data: The input data structure.
    :return: A list of dictionaries summarizing the features.
    """
    summarized_data = []
    target_sections = ["GO", "Location", "Disease"]

    for gene, gene_data in data.items():
        for feature, values in gene_data.items():
            if feature in target_sections and isinstance(values, list):
                for value in values:
                    existing_summary = next((item for item in summarized_data if value in item), None)
                    if existing_summary:
                        if gene not in existing_summary[value]["genes"]:
                            existing_summary[value]["number_of_genes"] += 1
                            existing_summary[value]["genes"].append(gene)
                    else:
                        new_summary = {
                            value: {
                                "number_of_genes": 1,
                                "genes": [gene]
                            }
                        }
                        summarized_data.append(new_summary)

    return summarized_data


def summarized_uniprot_features_to_tsv(summarized_data):
    """
    Take the summarized data, sort it by the number of genes for each feature, and output it as tab-delimited text.

    :param summarized_data: A list of dictionaries containing summarized data.
    :return: A string containing the tab-delimited text.
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
