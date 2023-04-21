import requests


def query_stringdb(gene_names):
    string_api_url = "https://string-db.org/api/json/network"
    string_params = {
        "identifiers": "%0d".join(gene_names),
        "species": 9606,
        "caller_identity": "myapp"
    }
    response = requests.get(string_api_url, params=string_params)
    json_response = response.json()

    nodes = set()
    edges = []
    for interaction in json_response:
        nodes.add(interaction["preferredName_A"])
        nodes.add(interaction["preferredName_B"])
        edges.append({
            "source": interaction["preferredName_A"],
            "target": interaction["preferredName_B"]
        })

    return {"nodes": list(nodes), "edges": edges}
