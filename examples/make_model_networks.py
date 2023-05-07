from cellmaps_annotate_hierarchy.cx2_network import CX2Network, query_ndex_network
import os

ndexuser = os.getenv("WORKING_NDEX_USERNAME")
ndexpassword = os.getenv("WORKING_NDEX_PASSWORD")

ndexuser = "examplemodel"
ndexpassword = "modelx"

print(f'{ndexuser}, {ndexpassword}')

original_model_uuid = "aa97afe8-ead3-11ed-b4a3-005056ae23aa"
interactome_uuid = "b463f0cf-5478-11ec-b3be-0ac135e8bacf"
# sharing_group_uuid= "3217f0d2-eb64-11ed-b4a3-005056ae23aa"

# Download the model from NDEx
model = CX2Network.download_from_ndex(original_model_uuid, ndexuser, ndexpassword)
# interactome = CX2Network.download_from_ndex(interactome_uuid, ndexuser, ndexpassword)


# for a test set of systems, query the interactome to make the system networks on NDEx
system_names = ["C2419"]

print(model.get_network_attribute("description"))

for system_name in system_names:
    system = model.get_node_by_name(system_name)
    if system is not None:
        genes = model.get_node_attribute(system["id"], "CD_MemberList")
        print(genes)
        system_uuid = query_ndex_network(interactome_uuid,
                                         ndexuser,
                                         ndexpassword,
                                         genes,
                                         direct_only=True,
                                         save=True)
        system_id = system["id"]
        #model.set_node_attribute(system_id, "system_uuid", system_uuid)
        #system_link = f'<a href="https://www.ndexbio.org/viewer/networks/{system_uuid}" target="_blank">Open System</a>'
        #model.set_node_attribute(system_id, "system_link", system_link)
        #print(model.get_node_attribute(system_id, "system_link"))
    else:
        print(f"no system named {system_name}")

new_model_uuid = CX2Network.upload_to_ndex(model, ndexuser, ndexpassword)

print(f'new model uuid: {new_model_uuid}')




