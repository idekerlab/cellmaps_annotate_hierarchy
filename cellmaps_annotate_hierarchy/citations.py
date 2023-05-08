import requests
from xml.etree import ElementTree
'''
write a function to check the references in PubMed. Consider that you might have gotten
the reference slightly wrong but nevertheless retrieved a clearly correct match.
Return a datastructure with the verified matches in one section.
The verified matches should include the pubmed id, PMCID, PubMedCentral URL, abstract, and DOI of the article.
The other section should list the references that failed to verify.

This was intended to work with a datastructure like this:
summarize your analysis in a jason data structure with the analysis text in 100 tokens
plus the references in a dictionary, indexed such that the references in the text
are the keys to the dictionary.
But it will need modification for that. Or a wrapper.
'''

def search_pubmed(query):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmode=json"
    search_response = requests.get(search_url)
    search_data = search_response.json()
    # Check if there are any search results
    if int(search_data["esearchresult"]["count"]) > 0:
        return search_data["esearchresult"]["idlist"][0]
    else:
        return None


def fetch_pubmed_details(pubmed_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={pubmed_id}&retmode=xml"
    fetch_response = requests.get(fetch_url)
    root = ElementTree.fromstring(fetch_response.content)
    # Extract the required details
    pmcid = root.find(".//PMCID").text if root.find(".//PMCID") is not None else None
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else None
    abstract = root.find(".//AbstractText").text if root.find(".//AbstractText") is not None else None
    doi = root.find(".//ArticleId[@IdType='doi']").text if root.find(
        ".//ArticleId[@IdType='doi']") is not None else None
    return {"pubmed_id": pubmed_id, "PMCID": pmcid, "URL": url, "abstract": abstract, "DOI": doi}


# takes a list of reference strings
def verify_references(references):
    verified_matches = []
    failed_to_verify = []

    for ref in references:
        pubmed_id = search_pubmed(ref)
        if pubmed_id:
            details = fetch_pubmed_details(pubmed_id)
            verified_matches.append(details)
        else:
            failed_to_verify.append(ref)

    return {"verified_matches": verified_matches, "failed_to_verify": failed_to_verify}
