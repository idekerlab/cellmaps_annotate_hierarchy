import requests


## function to get mygene info for root node and save to json file
def get_mygene_for_system(gene_names):

    url = "https://mygene.info/v3/query"

     # Batch query the mygene.info API using POST
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "q": ",".join(gene_names),
        "scopes": "symbol",
        "fields": "entrezgene, ensembl.gene, symbol, name, alias, summary, uniprot, pdb, pharmgkb, go, hgnc, clingen, pathway, interpro, generif",
        "species": "human"
    }
    data = "q=" + params["q"] + "&scopes=" + params["scopes"] + "&fields=" + params["fields"] + "&species=" + params["species"]

    response = requests.post(url, data=data, headers=headers)
    # print(response.text)  # Print the response
    results = response.json()
    return results


##VOID Function
def get_uniprot_id(gene_symbols):
    url = "https://mygene.info/v3/query"
    uniprot_ids = {}

    # Batch query the mygene.info API using POST
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "q": ",".join(gene_symbols),
        "scopes": "symbol",
        "fields": "uniprot, symbol",
        "species": "human"
    }
    data = "q=" + params["q"] + "&scopes=" + params["scopes"] + "&fields=" + params["fields"] + "&species=" + params["species"]

    response = requests.post(url, data=data, headers=headers)
    # print(response.text)  # Print the response
    results = response.json()
    for result in results:
        hugo_gene_symbol = result["symbol"]
        uniprot = result.get("uniprot", {})
        uniprot_id = uniprot.get("Swiss-Prot")
        if uniprot_id:
            uniprot_ids[hugo_gene_symbol] = uniprot_id

    return uniprot_ids