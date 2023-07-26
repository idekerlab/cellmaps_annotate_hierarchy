import ndex2 as nc
from cellmaps_annotate_hierarchy.uniprot_2 import get_uniprot_data_for_system, summarize_uniprot_features

ndexuser = "examplemodel"
ndexpassword = "modelx"
SERVER = 'http://ndexbio.org'

model_uuid = "61a58f6e-ed06-11ed-b4a3-005056ae23aa"
hierarchical_model = nc.create_nice_cx_from_server(SERVER, uuid=model_uuid, username=ndexuser, password=ndexpassword)


def process_system(model, system_name):
    system = model.get_node_by_name(system_name)
    genes = model.get_node_attribute_value(system, "CD_MemberList").split(" ")
    get_uniprot_data_for_system(genes)


#process_system(hierarchical_model, "C2419")
process_system(hierarchical_model, "C2315")



#process_system(hierarchical_model, hierarchical_model.get_node_by_name("C2311"))
