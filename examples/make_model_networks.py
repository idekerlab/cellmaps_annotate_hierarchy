from cellmaps_annotate_hierarchy.cx2_network import CX2Network, query_ndex_network
import os
ndexuser = os.getenv("NDEX_USER")
ndexpassword = os.getenv("NDEX_PASSWORD")

original_model_uuid ="df5b9a8b-45d0-11ed-b7d0-0ac135e8bacf"
interactome_uuid = "b463f0cf-5478-11ec-b3be-0ac135e8bacf"

# Download the model from NDEx
model = CX2Network.download_from_ndex(original_model_uuid, ndexuser, ndexpassword)

# for a test set of systems, query the interactome to make the system networks on NDEx
system_names = []

for system_name in system_names:
    system = model.get_node_by_name(system_name)
    genes = model.get_node_attribute(system["id"], "CD_MemberList")
    system_uuid = query_ndex_network(interactome_uuid,
                                     ndexuser,
                                     ndexpassword,
                                     genes,
                                     direct_only=True,
                                     save=True)




