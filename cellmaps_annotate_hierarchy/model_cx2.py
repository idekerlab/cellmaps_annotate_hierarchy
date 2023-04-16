

def get_aspect(cx2, name):
    """
    Find the first aspect in a list of aspect dictionaries that contains aspect name as a key

    :param dicts: A list of dictionaries.
    :param key_name: The key to search for.
    :return: The first dictionary that contains the key, or None if not found.
    """
    for aspect in cx2:
        if name in aspect:
            return aspect.get(name)
    return None


def get_cx2_nodes(cx2):
    nodes = get_aspect(cx2, "nodes")
    nodes = nodes
    if nodes is None:
        print("nodes is None")
        return None
    # print(nodes)
    return nodes


def get_node_by_name(cx2, node_name):
    nodes = get_cx2_nodes(cx2)
    for node in nodes:
        # print(node)
        values = node["v"]
        if node_name == values.get("name"):
            # print(f'{node_name} = {node}')
            return node
    return None


def get_node_value(node, attribute):
    values = node["v"]
    value = values.get(attribute)
    #print(f'{attribute} = {value}')
    return value


def get_system(model, system_name):
    # print(f"getting {system_name}")
    return get_node_by_name(model, system_name)


def get_genes(system):
    return get_node_value(system, "MemberList").split(" ")


