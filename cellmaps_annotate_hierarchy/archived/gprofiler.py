import requests
import json


def query_gprofiler(gene_names):
    url = "https://biit.cs.ut.ee/gprofiler/api/gost/profile"
    headers = {"Content-Type": "application/json"}
    payload = {
        "organism": "hsapiens",
        "query": gene_names,
        "sources": ["GO:BP", "KEGG", "REAC", "WP", "MIRNA", "HPA", "CORUM"],
        "user_threshold": 0.1,
        "all_results": False,
        "ordered": False,
        "no_iea": False,
        "combined": True,
        "measure_underrepresentation": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    json_response = response.json()

    filtered_results = []
    for item in json_response['result']:
        filtered_item = {
            "name": item["name"],
            "description": item["description"],
            "source": item["source"],
            "p_value": item["p_values"]
        }
        filtered_results.append(filtered_item)

    return filtered_results


def gprofiler_results_to_text(gprofiler_results):
    result_names = [result['name'] for result in gprofiler_results]
    return '\n'.join(result_names)
