import ndex2 as nc
from chatgpt_query import chatgpt_query_to_text

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
    prompt = make_prompt(system_network)
    analysis = chatgpt_query_to_text(prompt)
    system_network.set_network_attribute("description", analysis.get("text"), type="string")
    system_network.set_network_attribute("@ChatGPT_name", analysis.get("name"), "TBD", type="string")
    # update the system network on NDEx
    system_network.update_to(system_uuid, server=SERVER, username=ndexuser, password=ndexpassword)


def make_prompt(system_network, genes):
    """
    Create a ChatGPT prompt based on the system network.
    :return: A string containing the ChatGPT prompt text
    """
    preamble = "You are assisting a molecular biologist in the analysis of a system of interacting proteins \n"
    general_analysis_instructions = "\nSave any summary analysis of the system to the last paragraph. \
                \nAvoid overly general statements of how the proteins are involved in various cellular processes\
                \nAvoid recapitulating the goals of the analysis.\
                \nYour response should be formatted as JSON with two attributes: name, text.\
                \nThe text attribute should be formatted as HTML"

    task_instructions = "\nWrite a critical analysis of this system, and place it in the text attribute of the returned JSON.\
    \nFor each important point, describe your reasoning and provide citations.\
    \nBe careful with the citations. Do not provide a citation unless you are sure it is genuine.\
    \nInclude the citations in the text in the (<first author> et.al., <journal> <year>) format.\
    \nPlace the full citations at the end.\
    \nWhat mechanisms and biological processes are performed by this system?\
    \nWhat cellular components and complexes are involved in this system?\n\
    \nDiscuss potential names for the system. The name should be very brief. Do not compose an acronym.\
    \nSelect the best name and place it in the name attribute of the JSON"

    # Generate the ChatGPT prompt in HTML format
    prompt_text = f"\n"
    prompt_text += preamble
    prompt_text += task_instructions
    prompt_text += general_analysis_instructions
    prompt_text += f'\nProteins: '
    prompt_text += ", ".join(genes) + ".\n\n"
    prompt_text += f'\n\nSystem features from a Uniprot analysis: \n'
    prompt_text += system_network.get_network_attribute("feature_summary")
    return prompt_text


# for system_id, system in model.get_nodes():
#    process_system(system)

process_system(hierarchical_model, hierarchical_model.get_node_by_name("C2410"))
