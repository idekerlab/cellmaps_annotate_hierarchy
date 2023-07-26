import ndex2 as nc
from cellmaps_annotate_hierarchy.uniprot_2 import get_uniprot_data_for_system, summarize_uniprot_features

ndexuser = "examplemodel"
ndexpassword = "modelx"
SERVER = 'http://ndexbio.org'

model_uuid = "61a58f6e-ed06-11ed-b4a3-005056ae23aa"
hierarchical_model = nc.create_nice_cx_from_server(SERVER, uuid=model_uuid, username=ndexuser, password=ndexpassword)


def process_system(model, system):
    system_name = system["n"]
    print(system_name)
    # get the system network
    system_uuid = model.get_node_attribute_value(system, "system_uuid")
    system_network = nc.create_nice_cx_from_server(SERVER, uuid=system_uuid, username=ndexuser, password=ndexpassword)
    # get its genes
    genes = model.get_node_attribute_value(system, "CD_MemberList").split(" ")
    print(genes)
    # get the uniprot data
    gene_data = get_uniprot_data_for_system(genes)
    print("got gene data")
    # add the data
    add_gene_data_to_system_network(system_network, gene_data)
    print("gene data added to system")
    add_summary_to_system_network(system_network, gene_data)
    # update the system network on NDEx
    system_network_cx = system_network.to_cx()
    system_network.update_to(system_uuid, server=SERVER, username=ndexuser, password=ndexpassword)


def add_gene_data_to_system_network(system_network, gene_data):
    for symbol, data in gene_data.items():
        # find the node
        node = system_network.get_node_by_name(symbol)
        for att, value in data.items():
            system_network.set_node_attribute(node, f'#{att}', f'<i>{value}</i>', type="string")


def transform_feature_summary_to_html_list(data):
    html_list = "<ul>"
    for item in data:
        for key, value in item.items():
            # html_list += f"{key}: \t{value['number_of_genes']}\t"
            html_list += f"<li><b>{key}</b>: \t"
            genes_list = ' '.join(value['genes'])
            html_list += genes_list + "</li>"
    html_list += "</ul>"
    return html_list


def add_summary_to_system_network(system_network, gene_data):
    summarized_features = summarize_uniprot_features(gene_data)
    text_summary = transform_feature_summary_to_html_list(summarized_features)
    system_network.set_network_attribute("feature_summary", text_summary, type="string")
    system_network.set_network_attribute("description", "TBD", type="string")


for system_id, system in hierarchical_model.get_nodes():
    process_system(hierarchical_model, system)

#process_system(hierarchical_model, hierarchical_model.get_node_by_name("C2410"))
# res = model.upload_to('www.ndexbio.org', ndexuser, ndexpassword)
