import ndex2 as nc
from cellmaps_annotate_hierarchy.cx2_network import query_ndex_network

ndexuser = "examplemodel"
ndexpassword = "modelx"
SERVER = 'http://ndexbio.org'

print(f'{ndexuser}, {ndexpassword}')

ndex_client = nc.Ndex2("http://public.ndexbio.org")

original_model_uuid = "aa97afe8-ead3-11ed-b4a3-005056ae23aa"
interactome_uuid = "b463f0cf-5478-11ec-b3be-0ac135e8bacf"
# sharing_group_uuid= "3217f0d2-eb64-11ed-b4a3-005056ae23aa"

model = nc.create_nice_cx_from_server(SERVER, uuid=original_model_uuid)
interactome = nc.create_nice_cx_from_server(SERVER, uuid=interactome_uuid)

print(model.get_network_attribute("description")["v"])

# for a test set of systems, query the interactome to make the system networks on NDEx "C2419"
system_names = ["C2419"]

for system_id, system in model.get_nodes():
    if system is not None:
        system_name = system["n"]
        print(system_name)
        genes = model.get_node_attribute_value(system, "CD_MemberList")
        print(genes)
        cx_data = query_ndex_network(interactome_uuid,
                                         ndexuser,
                                         ndexpassword,
                                         genes,
                                         direct_only=True,
                                         save=False)
        nice_cx = nc.create_nice_cx_from_raw_cx(cx_data)
        nice_cx.set_name(system_name)
        print(nice_cx)
        system_uuid = nice_cx.upload_to('www.ndexbio.org', ndexuser, ndexpassword).split('/')[-1]
        model.set_node_attribute(system, "system_uuid", system_uuid)
        system_link = f'<a href="https://www.ndexbio.org/viewer/networks/{system_uuid}" target="_blank">Open System</a>'
        model.set_node_attribute(system, "system_link", system_link)
        print(model.get_node_attribute_value(system, "system_link"))

res = model.upload_to('www.ndexbio.org', ndexuser, ndexpassword)

print('URL returned by upload_to call: ' + res)
new_network_uuid = res.split('/')[-1]

print('Network UUID: ' + new_network_uuid)
