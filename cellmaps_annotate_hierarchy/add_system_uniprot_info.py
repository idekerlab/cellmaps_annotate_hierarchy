import ndex2 as nc
from cellmaps_annotate_hierarchy.uniprot_2 import get_uniprot_data_for_system, summarize_uniprot_features

ndexuser = "examplemodel"
ndexpassword = "modelx"
SERVER = 'http://ndexbio.org'

model_uuid = "49f8211a-ec45-11ed-b4a3-005056ae23aa"
hierarchical_model = nc.create_nice_cx_from_server(SERVER, uuid=model_uuid, username=ndexuser, password=ndexpassword)


def process_system(model, system):
    system_name = system["n"]
    print(system_name)
    # get the system network
    system_uuid = model.get_node_attribute_value(system, "system_uuid")
    system_nice_cx = nc.create_nice_cx_from_server(SERVER, uuid=system_uuid, username=ndexuser, password=ndexpassword)
    # get its genes
    genes = model.get_node_attribute_value(system, "CD_MemberList").split(" ")
    print(genes)
    # get the uniprot data
    gene_data = get_uniprot_data_for_system(genes)
    print("got gene data")
    # add the data
    add_gene_data_to_system(system_nice_cx, gene_data)
    print("gene data added to system")
    add_summary_to_system(system, gene_data)
    # update the network on NDEx
    system_nice_cx.update_to(system_uuid, server=SERVER, username=ndexuser, password=ndexpassword)


def add_gene_data_to_system(system, gene_data):
    for symbol, data in gene_data.items():
        # find the node
        node = system.get_node_by_name(symbol)
        for att, value in data.items():
            system.set_node_attribute(node, att, value)


def add_summary_to_system_network(system_network, gene_data):
    summarized_features = summarize_uniprot_features(gene_data)
    text_summary = ""
    for feature in summarized_features:
        text_summary += f"{feature}\n"
    system_network.set_network_attribute("feature_summary", )



# for system_id, system in model.get_nodes():
#    process_system(system)

process_system(hierarchical_model, hierarchical_model.get_node_by_name("C2377"))
# res = model.upload_to('www.ndexbio.org', ndexuser, ndexpassword)
