import requests
import json

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
    print(f'querying uniprot id {uniprot_id}')
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


def get_uniprot_data_for_system(gene_symbols):
    analysis_data = {}
    uniprot_ids = get_uniprot_ids(gene_symbols)
    for gene_symbol, uniprot_id in uniprot_ids.items():
        uniprot_data = query_uniprot_by_id(uniprot_id)
        if uniprot_data:
            filtered_data = filter_uniprot_response(uniprot_data)
            analysis_data[gene_symbol] = filtered_data
        else:
            print(f'no uniprot data found for {uniprot_id}')
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


def get_uniprot_ids(gene_symbols):
    base_url = "https://mygene.info/v3/query"

    params = {
        "q": "symbol:" + " OR symbol:".join(gene_symbols),
        "species": "human",
        "fields": "uniprot, symbol",
        "fetch_all": True
    }

    response = requests.get(base_url, params=params)

    uniprot_dict = {}
    if response.status_code == 200:
        results = response.json()
        for hit in results["hits"]:
            uniprot_id = hit["uniprot"]["Swiss-Prot"]
            symbol = hit["symbol"]
            uniprot_dict[symbol] = uniprot_id

    return uniprot_dict


'''
def get_uniprot_ids(gene_symbols):
    uniprot_dict = {}

    for symbol in gene_symbols:
        url = f"https://www.uniprot.org/uniprotkb/search?query=genename%3A{symbol}+AND+organism%3A%22Homo+sapiens+%28Human%29+%5B9606%5D%22&format=tab&columns=id"
        response = requests.get(url)

        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            if len(lines) > 1:
                uniprot_id = lines[1]
                uniprot_dict[symbol] = uniprot_id

    return uniprot_dict

def get_uniprot_ids(gene_symbols):
    base_url = "https://www.uniprot.org/uploadlists/"
    mapping_url = "https://www.uniprot.org/mapping/"

    # Step 1: Retrieve UniProt accessions for the provided gene symbols (human genes)
    params = {
        "from": "GENENAME",
        "to": "ACC",
        "format": "tab",
        "query": " ".join(gene_symbols),
        "organism": "human"
    }

    response = requests.get(base_url, params=params)
    lines = response.text.strip().split("\n")

    accessions_dict = {}
    for line in lines[1:]:
        symbol, accession = line.strip().split("\t")
        accessions_dict[symbol] = accession

    # Step 2: Retrieve UniProt IDs for the accessions (handles outdated symbols/aliases)
    uniprot_dict = {}
    for symbol, accession in accessions_dict.items():
        params = {
            "from": "ACC",
            "to": "ID",
            "format": "tab",
            "query": accession
        }

        response = requests.get(mapping_url, params=params)
        lines = response.text.strip().split("\n")

        if len(lines) > 1:
            uniprot_id = lines[1].strip().split("\t")[1]
            uniprot_dict[symbol] = uniprot_id

    return uniprot_dict
'''


def get_gene_data(gene_symbols):
    uniprot_ids = get_uniprot_ids(gene_symbols)

    gene_data = {}
    for symbol, uniprot_id in uniprot_ids.items():
        url = f"https://www.uniprot.org/uniprot/{uniprot_id}.json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            gene_data[symbol] = {}

            if "function" in data["entry"]:
                gene_data[symbol]["Function"] = data["entry"]["function"][0]["value"]

            if "cellular_component" in data["entry"]:
                gene_data[symbol]["Cellular Component"] = [cc["name"] for cc in data["entry"]["cellular_component"]]

            if "biological_process" in data["entry"]:
                gene_data[symbol]["Biological Process"] = [bp["name"] for bp in data["entry"]["biological_process"]]

            if "disease" in data["entry"]:
                gene_data[symbol]["Disease Associations"] = []
                for disease in data["entry"]["disease"]:
                    if "description" in disease:
                        citation = ""
                        if "reference" in disease:
                            citation = disease["reference"][0]["citation"]
                        gene_data[symbol]["Disease Associations"].append({
                            "name": disease["name"],
                            "description": disease["description"],
                            "citation": citation
                        })

            if "pathway" in data["entry"]:
                gene_data[symbol]["Reactome Pathways"] = [pw["name"] for pw in data["entry"]["pathway"]]

            if "subcellular_location" in data["entry"]:
                gene_data[symbol]["Subcellular Location"] = [sl["location"]["value"] for sl in data["entry"]["subcellular_location"]]

            gene_data[symbol]["GeneCards"] = f"https://www.genecards.org/cgi-bin/carddisp.pl?gene={symbol}"
            gene_data[symbol]["HGNC"] = f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:{symbol}"
            gene_data[symbol]["HPA"] = f"https://www.proteinatlas.org/search/{symbol}"
            gene_data[symbol]["CORUM"] = f"https://mips.helmholtz-muenchen.de/corum/#gene/{symbol}"
            gene_data[symbol]["STRING"] = f"https://string-db.org/network/{uniprot_id}"

    return gene_data


def get_gene_data_text(gene_symbols):
    uniprot_ids = get_uniprot_ids(gene_symbols)

    gene_data = {}
    for symbol, uniprot_id in uniprot_ids.items():
        gene_data[symbol] = {}

        # Retrieve gene data for each UniProt ID
        base_url = f"https://www.uniprot.org/uniprot/{uniprot_id}.txt"
        response = requests.get(base_url)
        data_lines = response.text.strip().split("\n")

        for line in data_lines:
            if line.startswith("DR   GeneCards"):
                gene_data[symbol]["GeneCards"] = line.split()[2]
            elif line.startswith("DR   HGNC"):
                gene_data[symbol]["HGNC"] = line.split()[2]
            elif line.startswith("DR   HPA"):
                gene_data[symbol]["HPA"] = line.split()[2]
            elif line.startswith("DR   CORUM"):
                gene_data[symbol]["CORUM"] = line.split()[2]
            elif line.startswith("DR   STRING"):
                gene_data[symbol]["STRING"] = line.split()[2]
            elif line.startswith("CC   -!- FUNCTION:"):
                gene_data[symbol]["Function"] = line.replace("CC   -!- FUNCTION: ", "")
            elif line.startswith("CC   -!- SUBCELLULAR LOCATION:"):
                gene_data[symbol]["Subcellular Location"] = line.replace("CC   -!- SUBCELLULAR LOCATION: ", "")
            elif line.startswith("DR   GO;"):
                go_data = line.split(";")
                go_id = go_data[1].strip()
                go_term = go_data[2].strip()
                go_aspect = go_data[3].strip()
                if go_aspect == "F":
                    gene_data[symbol].setdefault("GO Biological Process", []).append((go_id, go_term))
                elif go_aspect == "C":
                    gene_data[symbol].setdefault("GO Cellular Component", []).append((go_id, go_term))
            elif line.startswith("DR   Reactome;"):
                reactome_id = line.split()[1].strip(";")
                gene_data[symbol].setdefault("Reactome Pathways", []).append(reactome_id)
            elif line.startswith("DR   CTD"):
                disease_data = line.split()
                disease_id = disease_data[2].strip(";")
                disease_citation = " ".join(disease_data[3:])
                gene_data[symbol].setdefault("Disease Associations", []).append((disease_id, disease_citation))

    return gene_data
