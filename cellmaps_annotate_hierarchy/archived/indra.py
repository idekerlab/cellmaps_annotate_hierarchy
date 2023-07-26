import requests
import indra


def query_indra(agent_a, agent_b, limit=50):
    base_url = "https://db.indra.bio/statements/from_agents"
    params = {
        "subject": agent_a,
        "object": agent_b,
        "offset": 0,
        "limit": limit,
        "format": "json",
        "query" = f'HasAgent({agent_a}) & HasAgent({agent_b})'
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data["statements"])
        return data["statements"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []


def sort_response_by_relationship_type(statements):
    """
    Sort a list of INDRA statements based on the order of the relationship and the relationship types in
    the provided indra_relationships_ranked list.

    :param statements: A list of INDRA statements to be sorted.
    :return: A list of ranked INDRA statements.

    You can refer to the INDRA documentation for a more comprehensive
    and up-to-date list: https://indra.readthedocs.io/en/latest/statements.html

    """

    indra_relationships_ranked = [
        "Complex",
        "Binding",
        "Activation",
        "Inhibition",
        "IncreaseAmount",
        "DecreaseAmount",
        "Translocation",
        "Phosphorylation",
        "Dephosphorylation",
        "Ubiquitination",
        "Deubiquitination",
        "Acetylation",
        "Deacetylation",
        "Methylation",
        "Demethylation",
        "Glycosylation",
        "Deglycosylation",
        "Palmitoylation",
        "Depalmitoylation",
        "Myristoylation",
        "Demyristoylation",
        "Hydroxylation",
        "Dehydroxylation",
        "Sumoylation",
        "Desumoylation",
        "Autophosphorylation",
        "SelfModification",
        "ActiveForm",
    ]

    # Create bins for each relationship type
    bins = {relation: [] for relation in indra_relationships_ranked}

    # Add statements to the appropriate bin based on the relationship type
    for statement in statements:
        relation = statement["type"]
        if relation in bins:
            bins[relation].append(statement)

    # Sort each bin based on the confidence score
    for relation in bins:
        bins[relation].sort(key=lambda s: s["evidence"][0]["confidence"], reverse=True)

    # Create a list to store the ranked statements
    ranked_statements = []

    # Loop through the bins, picking the statement with the highest confidence score
    # and adding it to the ranked_statements list until there are no statements remaining
    while True:
        statements_added = 0
        for relation in indra_relationships_ranked:
            if bins[relation]:
                ranked_statements.append(bins[relation].pop(0))
                statements_added += 1
        if statements_added == 0:
            break

    return ranked_statements

import requests
import json

def summarize_top_statements(statements, top_n=10):
    # Concatenate the text of the top 10 statements
    texts = [statement['text'] for statement in statements[:top_n]]
    concatenated_texts = ' '.join(texts)

    # Prepare the GPT prompt
    prompt = f"As an assistant to a molecular biologist, perform critical analysis of the following protein interactions: {concatenated_texts}"

    # Query the ChatGPT API
    api_url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "prompt": prompt,
        "max_tokens": 150,
        "n": 1,
        "stop": None,
        "temperature": 0.7,
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()["choices"][0]["text"].strip()
        analysis_and_citations = {
            "analysis": result,
            "citations": [statement["evidence"][0]["source_api"] for statement in statements[:top_n]]
        }
        return analysis_and_citations
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

'''
# Example usage
if __name__ == "__main__":
    agent_a = "BRCA1"
    agent_b = "TP53"
    statements = query_indra(agent_a, agent_b)
    ranked_statements = sort_response_by_relationship_type(statements)
    analysis_and_citations = summarize_top_statements(ranked_statements)
    print(json.dumps(analysis_and_citations, indent=2))

# earlier code, temporarily preserved for reference
def get_indra_pairwise_interactions(proteins, limit=50):
    pairwise_interactions = {}
    for agent_a, agent_b in combinations(proteins, 2):
        print(f'Querying {agent_a} - {agent_b}')

        statements =
        statements_a_b = query_indra(agent_a, agent_b)
        print(f'Querying {agent_b} -> {agent_a}')
        statements_b_a = query_indra(agent_b, agent_a)
        ranked_statements = rank_statements(statements)[:limit]
        pairwise_interactions[(agent_a, agent_b)] = [s[1] for s in statements]

    return pairwise_interactions
'''
