from Bio import Entrez
import requests
from file_io import get_model_directory_path,get_root_path
from pages_io import write_system_page
from model_nodes_edges import load_nodes_edges
import os
import json
import re

## Read an example response from the chatgpt_response (only the Summary)
with open('config.json') as config_file:
    data = json.load(config_file)

#`MODEL_ANNOTATION_ROOT` is the path to the root directory of the model annotation repository
os.environ['MODEL_ANNOTATION_ROOT'] = data["MODEL_ANNOTATION_ROOT"]

# load the API key
key = data["OPENAI_API_KEY"]
os.environ['MODEL_ANNOTATION_ROOT'] = 'Projects/cellmaps_annotate_hierarchy/cellmaps_annotate_hierarchy/'
model_name = data["MAP_NAME"]

version = data["MAP_V"]

file_name = data["MAP_FILE"]
api_key = data["OPENAI_API_KEY"]
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

max_tokens = data["MAX_TOKENS"] # Set your max tokens here
rate_per_token = data["RATE_PER_TOKEN"]# Set your rate per token here 
model = data["GPT_MODEL"]
DOLLAR_LIMIT = data["DOLLAR_LIMIT"]  # Set your dollar limit here
logfile_name = "valid_ref_" #data["LOG_NAME"] # Set your log file name here
LOG_FILE = os.path.join(get_model_directory_path(model_name, version), f"{logfile_name}log.json")

def load_log(LOG_FILE):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    else:
        return {"tokens_used": 0, "dollars_spent": 0.0, "time_taken_last_run": 0.0, "time_taken_total": 0.0}

def save_log(LOG_FILE,log_data):
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=4)

def estimate_cost(tokens, rate_per_token):
    return tokens * rate_per_token


def get_keyword_from_paragraph(paragraph, gpt_model='gpt-4', verbose=False):
    log_data = load_log(LOG_FILE)
    tokens_estimate = len(paragraph) + max_tokens
    query = """I have paragraph\nParagraph:\n%s\nI would like to search PubMed to validate this abstract. give me a list of 5 keywords. Keywords must include gene symbols and their related functions. please order keywords by their importance in paragraph, from high important to low important. Also genes should be located first. Just tell me keywords only with comma seperated without spacing"""%paragraph

    # print(query)

    keyword_extraction_data = {
    "model": gpt_model,
        "temperature": 0,
        "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
    ] + [{"role": "user", "content": query}]}
    
    if estimate_cost(log_data["tokens_used"] + tokens_estimate, rate_per_token) > DOLLAR_LIMIT:
        print("The API call is estimated to exceed the dollar limit. Aborting.")
        return

    try:

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=keyword_extraction_data)

        response_json = response.json()

        tokens_used = response_json["usage"]["total_tokens"]
        # Update and save the log
        log_data["tokens_used"] += tokens_used
        log_data["dollars_spent"] = estimate_cost(log_data["tokens_used"], rate_per_token)
        print(tokens_used)
        save_log(LOG_FILE,log_data)

        if 'choices' in response_json.keys():
            result = response_json["choices"][0]["message"]["content"]
            
        else:
            result = None
        if verbose: 
            print("Query:")
            print(query)
            print("Result:")
            print(result)
        if result is not None:
            print("Tokens used: %s"%tokens_used)
            return [keyword.strip() for keyword in result.split(",")]
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def get_mla_citation(doi):
    url = f'https://api.crossref.org/works/{doi}'
    headers = {'accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        #print(data)
        item = data['message']
        
        authors = item['author']
        formatted_authors = []
        for author in authors:
            formatted_authors.append(f"{author['family']}, {author.get('given', '')}")
        authors_str = ', '.join(formatted_authors)
        
        title = item['title'][0]
        container_title = item['container-title'][0]
        year = item['issued']['date-parts'][0][0]
        volume = item.get('volume', '')
        issue = item.get('issue', '')
        page = item.get('page', '')
        
        mla_citation = f"{authors_str}. \"{title}.\" {container_title}"
        if volume or issue:
            mla_citation += f", vol. {volume}" if volume else ''
            mla_citation += f", no. {issue}" if issue else ''
        mla_citation += f", {year}, pp. {page}."
        
        return mla_citation

def get_mla_citation_from_pubmed_id(paper_dict):
    article = paper_dict['MedlineCitation']['Article']
    #print(article.keys())
    authors = article['AuthorList']
    formatted_authors = []
    for author in authors:
        last_name = author['LastName'] if author['LastName'] is not None else ''
        first_name = author['ForeName'] if author['ForeName'] is not None else ''
        formatted_authors.append(f"{last_name}, {first_name}")
    authors_str = ', '.join(formatted_authors)

    title = article['ArticleTitle']
    journal = article['Journal']['Title']
    year = article['Journal']['JournalIssue']['PubDate']['Year']
    page = article['Pagination']['MedlinePgn']
    mla_citation = f"{authors_str}. \"{title}\" {journal}"
    if "Volume" in article['Journal']['JournalIssue']['PubDate']:
        volume = article['Journal']['JournalIssue']['PubDate']['Volume']
        mla_citation += f", vol. {volume}" if volume else ''
    elif "Issue" in article['Journal']['JournalIssue']['PubDate']:
        issue = article['Journal']['JournalIssue']['PubDate']['Issue']
        mla_citation += f", no. {issue}" if issue else ''
    mla_citation += f", {year}, pp. {page}."
    return mla_citation

def get_citation(paper):
    names = ",".join([author['name'] for author in paper['authors']])
    corrected_title = paper['title']
    journal = paper['journal']['name']
    pub_date = paper['publicationDate']
    if 'volume' in paper['journal'].keys(): 
        volume = paper['journal']['volume'].strip()
    else:
        volume = ''
    if 'pages' in paper['journal'].keys():
        pages = paper['journal']['pages'].strip()
    else:
        doi = paper['externalIds']['DOI']
        pages = doi.strip().split(".")[-1]
    citation = f"{names}. {corrected_title} {journal} {volume} ({pub_date[0:4]}):{pages}"
    return citation

def get_references(queried_papers, paragraph, gpt_model='gpt-4', n=10, verbose=False):
    citations = []
    for paper in queried_papers:
        abstract = paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        message = """I have pharagraph\n Pharagraph:\n%s\nand abstract.\n Abstract:\n%s\nDoes this abstract support this paragraph? Please tell me yes or no"""%(paragraph, abstract)
        
        reference_check_data = {
            "model": gpt_model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
            ] + [{"role": "user", "content": message }],
        }
        reference_check_data['messages'].append({"role":"user", "content":message})

        log_data = load_log(LOG_FILE)
        tokens_estimate = len(paragraph) + max_tokens

        if estimate_cost(log_data["tokens_used"] + tokens_estimate, rate_per_token) > DOLLAR_LIMIT:
            print("The API call is estimated to exceed the dollar limit. Aborting.")
            return

        else:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=reference_check_data)

            response_json = response.json()
            tokens_used = response_json["usage"]["total_tokens"]
            # Update and save the log
            log_data["tokens_used"] += tokens_used
            log_data["dollars_spent"] = estimate_cost(log_data["tokens_used"], rate_per_token)
            print(tokens_used)
            save_log(LOG_FILE,log_data)

            if 'choices' in response_json.keys():
                result = response_json['choices'][0]['message']['content']
                if result[:3].lower()=='yes':
                    try:
                        citation = get_mla_citation_from_pubmed_id(paper)
                        if citation not in citations:
                            citations.append(citation)
                    except Exception as e:
                        print("Cannot parse citation even though this paper support pargraph")
                        print("Error detail: ", e)
                        pass
                    if len(citations)>=n:
                        return citations
            else:
                result = "No"    
            if verbose:
                print("Title: ", paper['MedlineCitation']['Article']['ArticleTitle'])
                print("Query: ")
                print(message)
                print("Result:")
                print(result)
                print("="*200)

    return citations
        
def search_pubmed(keywords, email, sort_by='citation_count', retmax=10):
    Entrez.email = email

    search_query = f"{keywords} AND (hasabstract[text])"
    search_handle = Entrez.esearch(db='pubmed', term=search_query, sort=sort_by, retmax=retmax)
    search_results = Entrez.read(search_handle)
    search_handle.close()

    id_list = search_results['IdList']

    if not id_list:
        print("No results found.")
        return []

    fetch_handle = Entrez.efetch(db='pubmed', id=id_list, retmode='xml')
    articles = Entrez.read(fetch_handle)['PubmedArticle']
    fetch_handle.close()

    return articles

def get_papers(keywords, n, email):
    total_papers = []
    while True:
        keyword_joined = " AND ".join(["("+keyword+"[Title/Abstract])" for keyword in keywords])
        if len(keywords)==2:
                return total_papers
        try:
            semantic_scholar_queried_keywords= search_pubmed(keyword_joined, email=email, retmax=n)
            total_papers += list(semantic_scholar_queried_keywords[:n])
        except:
            pass
        keywords = keywords[:-1]
        print("Reducing keywords to %s"%",".join(keywords))
                
def get_references_for_paragraphs(paragraphs, email, n=5, gpt_model='gpt-4', verbose=False):
    references_paragraphs = []
    for i, paragraph in enumerate(paragraphs):
        if verbose:
            print("""Extracting keywords from paragraph\nParagraph:\n%s"""%paragraph)
            print("="*75)
        keywords = get_keyword_from_paragraph(paragraph, gpt_model=gpt_model, verbose=verbose)
        #keywords = list(sorted(keywords, key=len))
        keyword_joined = ",".join(keywords)
        print("Keywords: ", keyword_joined)
        print("Serching paper with keywords...")
        semantic_scholar_queried_keywords = get_papers(keywords, n, email)
        if len(semantic_scholar_queried_keywords)==0:
            print("No paper searched!!")
            references_paragraphs.append([])
        print("In paragraph %d, %d references are queried"%(i+1, len(semantic_scholar_queried_keywords)))
        references = get_references(semantic_scholar_queried_keywords, paragraph, gpt_model=gpt_model, n=n, verbose=verbose)
        references_paragraphs.append(references)
        print("In paragraph %d, %d references are matched"%(i+1, len(references)))
        print("")
        print("")
    n_refs = sum([len(refs) for refs in references_paragraphs])
    print("Total %d references are queried"%n_refs)
    print(references_paragraphs)
    # i = 1
    # referenced_paragraphs = ""
    # footer = "="*200+"\n"
    # for paragraph, references in zip(paragraphs, references_paragraphs):
    #     referenced_paragraphs += paragraph
    #     for reference in references:
    #         referenced_paragraphs += "[%d]"%i
    #         footer += "[%d] %s"%(i, reference) + '\n'
    #         i+=1
    #     referenced_paragraphs += "\n"
    # return referenced_paragraphs + footer
    i = 1
    footer = "### Validated References: \n"
    for references in references_paragraphs:
        for reference in references:
            if reference:
                footer += "[%d] %s"%(i, reference) + '\n'
                i+=1
    return footer

def get_summary(file_name):
        with open(file_name, "r") as file:
            content = file.read()
            
        # Regular expression pattern for matching the Summary section
        pattern = re.compile(r'(#+\s*)?(\*{1,2}|_{1,2})?Summary[:\s]*(.*?)(#+\s*)?References', re.DOTALL | re.IGNORECASE)
        match = pattern.search(content)

        if match:
            cleaned_text = re.sub(r'[\*#]', '', match.group(3))  # Remove remaining asterisks and hash symbols
            summary = cleaned_text.strip()  # Remove leading and trailing whitespace
            # print(summary)
            return summary
        else:
            print("No Summary found.")
            return None

if __name__ == "__main__":
        
    nodes, edges = load_nodes_edges(model_name, version, file_name)
    # sort nodes by size 
    nodes = nodes.sort_values(by=['size'], ascending=True)
    systems = nodes['term'].values.tolist()[:-3] #remove the root and 2 huge organelle nodes
    for system in systems[:6]:
        response_path = os.path.join(get_model_directory_path(model_name, version),
        system, f"{system}_chatgpt_response")

        paragraphs = get_summary(response_path+'.md')
        paragraphs = list(filter(lambda p: len(p.split()) > 5, paragraphs.split("\n")))
        # check if the valid reference is already generated
        if os.path.exists(os.path.join(get_model_directory_path(model_name, version),
        system, f"{system}_valid_references.md")):
            print("Valid reference already generated for %s"%system)
            continue
        else:
            print("Generating valid reference for %s"%system)
            reference = get_references_for_paragraphs(paragraphs, email = data['EMAIL'], n=3, gpt_model=model, verbose=False)
            write_system_page(reference,'md',model_name, version, system, "valid_references", get_root_path())
        