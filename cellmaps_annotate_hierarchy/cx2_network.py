import json
import requests


class CX2Network:
    def __init__(self, cx2_data=None):
        if cx2_data is None:
            self.cx2_data = [
                {
                    "CXVersion": "2.0",
                    "hasFragments": False
                },
                {
                    "metaData": [
                        {"name": "attributeDeclarations", "elementCount": 1},
                        {"name": "networkAttributes", "elementCount": 0},
                        {"name": "edges", "elementCount": 0},
                        {"name": "nodes", "elementCount": 0}
                    ]
                },
                {
                    "attributeDeclarations": [{
                        "nodes": {},
                        "networkAttributes": {},
                        "edges": {}
                    }]
                },
                {"networkAttributes": []},
                {"nodes": []},
                {"edges": []}
            ]
        else:
            self.cx2_data = cx2_data

        self.metaData = self.cx2_data[1]["metaData"]
        self.attribute_declarations = self.cx2_data[2]["attributeDeclarations"][0]
        self.network_attributes = self.cx2_data[3]["networkAttributes"][0]
        self.nodes = self.cx2_data[4]["nodes"]
        self.edges = self.cx2_data[5]["edges"]

    # Other methods

    def _get_aspect(self, aspect_name):
        for aspect in self.cx2_data:
            if aspect_name in aspect:
                return aspect[aspect_name]
        return None

    def _get_data_type(self, aspect, attribute_name):
        declarations = self.attribute_declarations.get(aspect)
        if declarations is None:
            return None
        declaration = declarations.get(attribute_name)
        if declaration is None:
            return None
        return declaration["d"]

    #        if aspect in self.attribute_declarations[0]:
    #            if attribute_name in self.attribute_declarations[0][aspect]:
    #                return self.attribute_declarations[0][aspect][attribute_name]['d']
    #        return None

    @staticmethod
    def _check_data_type(value, data_type):
        if data_type == 'string':
            return isinstance(value, str)
        elif data_type == 'integer':
            return isinstance(value, int)
        elif data_type == 'double':
            return isinstance(value, float)
        elif data_type == 'boolean':
            return isinstance(value, bool)
        elif data_type == 'list_of_string':
            return isinstance(value, list) and all(isinstance(v, str) for v in value)
        else:
            return False

    def _update_attribute_declaration(self, aspect, attribute_name, data_type):
        if aspect not in self.attribute_declarations:
            self.attribute_declarations[aspect] = {}
        self.attribute_declarations[aspect][attribute_name] = {'d': data_type}

    def get_network_attribute(self, attribute_name):
        return self.network_attributes.get(attribute_name)

    def set_network_attribute(self, attribute_name, value):
        self.network_attributes[attribute_name] = value

    def get_node_attribute(self, node_id, attribute_name):
        for node in self.nodes:
            if node['id'] == node_id:
                return node['v'].get(attribute_name)
        return None

    def set_node_attribute(self, node_id, attribute_name, value):
        data_type = self._get_data_type('nodes', attribute_name)
        if data_type is None or self._check_data_type(value, data_type):
            if data_type is None:
                data_type = type(value).__name__
                if data_type == "str":
                    data_type = "string"
                # self._update_attribute_declaration('nodes', attribute_name, data_type)
            for node in self.nodes:
                if node['id'] == node_id:
                    node['v'][attribute_name] = value
                    return

    def get_edge_attribute(self, edge_id, attribute_name):
        for edge in self.edges:
            if edge['id'] == edge_id:
                return edge['v'].get(attribute_name)
        return None

    def set_edge_attribute(self, edge_id, attribute_name, value):
        data_type = self._get_data_type('edges', attribute_name)
        if data_type is None or self._check_data_type(value, data_type):
            if data_type is None:
                data_type = type(value).__name__
                self._update_attribute_declaration('edges', attribute_name, data_type)
            for edge in self.edges:
                if edge['id'] == edge_id:
                    edge['v'][attribute_name] = value
                    return

    def add_node(self, x, y, attributes=None):
        if attributes is None:
            attributes = {}
        node_id = max([node['id'] for node in self.nodes], default=0) + 1
        new_node = {'id': node_id, 'x': x, 'y': y, 'v': attributes}
        self.nodes.append(new_node)
        return node_id

    def delete_node(self, node_id):
        self.nodes = [node for node in self.nodes if node['id'] != node_id]
        self.edges = [edge for edge in self.edges if edge['s'] != node_id and edge['t'] != node_id]

    def add_edge(self, source_node_id, target_node_id, attributes=None):
        if attributes is None:
            attributes = {}
        source_node = None
        target_node = None
        for node in self.nodes:
            if node['id'] == source_node_id:
                source_node = node
            if node['id'] == target_node_id:
                target_node = node
            if source_node is not None and target_node is not None:
                break

        if source_node is None or target_node is None:
            raise ValueError("Source or target node ID not found in the network.")

        edge_id = max([edge['id'] for edge in self.edges], default=0) + 1
        new_edge = {'id': edge_id, 's': source_node_id, 't': target_node_id, 'v': attributes}
        self.edges.append(new_edge)
        return edge_id

    def delete_edge(self, edge_id):
        self.edges = [edge for edge in self.edges if edge['id'] != edge_id]

    def get_node_by_name(self, node_name):
        for node in self.nodes:
            if node['v'].get('n') == node_name:
                return node
        return None

    def remove_network_attribute(self, attribute_name):
        self.network_attributes = [attr for attr in self.network_attributes if attr['name'] != attribute_name]

    def remove_node_attribute(self, node_id, attribute_name):
        for node in self.nodes:
            if node['id'] == node_id and attribute_name in node['v']:
                del node['v'][attribute_name]

    def remove_edge_attribute(self, edge_id, attribute_name):
        for edge in self.edges:
            if edge['id'] == edge_id and attribute_name in edge['v']:
                del edge['v'][attribute_name]

    def remove_attribute_from_all_nodes(self, attribute_name):
        for node in self.nodes:
            if attribute_name in node['v']:
                del node['v'][attribute_name]
        if 'nodes' in self.attribute_declarations[0] and attribute_name in self.attribute_declarations[0]['nodes']:
            del self.attribute_declarations[0]['nodes'][attribute_name]

    def remove_attribute_from_all_edges(self, attribute_name):
        for edge in self.edges:
            if attribute_name in edge['v']:
                del edge['v'][attribute_name]
        if 'edges' in self.attribute_declarations[0] and attribute_name in self.attribute_declarations[0]['edges']:
            del self.attribute_declarations[0]['edges'][attribute_name]

    @staticmethod
    def update_on_ndex(cx2_network, uuid, username, password):
        """
        Updates a CX2Network on NDEx using the given UUID.

        Args:
            cx2_network (CX2Network): The CX2Network instance to be updated.
            uuid (str): The UUID of the network to be updated.
            username (str): The NDEx username.
            password (str): The NDEx password.
        """
        url = f"https://www.ndexbio.org/v3/networks/{uuid}"
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, auth=(username, password), headers=headers,
                                data=json.dumps(cx2_network.cx2_data))

        if response.status_code == 204:
            return response.json()["uuid"]
        else:
            response.raise_for_status()

    @staticmethod
    def upload_to_ndex(cx2_network, username, password):
        """
        Uploads a CX2Network to NDEx and returns its UUID.

        Args:
            cx2_network (CX2Network): The CX2Network instance to be uploaded.
            username (str): The NDEx username.
            password (str): The NDEx password.

        Returns:
            str: The UUID of the uploaded network.
        """
        url = "https://www.ndexbio.org/v3/networks"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(cx2_network.cx2_data)
        response = requests.post(url, auth=(username, password), headers=headers,
                                 data=data)

        if response.status_code == 201:
            return response.json()["uuid"]
        else:
            response.raise_for_status()

    @staticmethod
    def download_from_ndex(uuid, username, password):
        """
        Downloads a CX2 network from NDEx, creates a CX2Network object, and returns it.

        Args:
            uuid (str): The UUID of the network to be downloaded.
            username (str): The NDEx username.
            password (str): The NDEx password.

        Returns:
            CX2Network: The downloaded CX2Network instance.
        """
        url = f"https://www.ndexbio.org/v3/networks/{uuid}"
        response = requests.get(url, auth=(username, password))

        if response.status_code == 200:
            cx2_data = response.json()
            return CX2Network(cx2_data)
        else:
            response.raise_for_status()


def query_ndex_network(network_id, username, password, search_string, search_depth=1, edge_limit=None,
                       error_when_limit_is_over=False, direct_only=False, save=False):
    """
    Queries an NDEx network and returns a neighborhood subnetwork of the network specified by network_id.

    Args:
        network_id (str): The ID of the network to be queried.
        username (str): The NDEx username.
        password (str): The NDEx password.
        search_string (str): The search string to be used as the starting point for the traversal.
        search_depth (int, optional): The search depth for the traversal. Default is 1.
        edge_limit (int, optional): The maximum number of edges allowed in the subnetwork. Default is None.
        error_when_limit_is_over (bool, optional): If True, an error will be raised if the edge limit is exceeded.
                                                   Default is False.
        direct_only (bool, optional): If True, only direct connections between nodes are considered. Default is False.
        save (bool, optional): If True, saves the resulting network to NDEx and returns the UUID.
                               If False, returns the CX2Network object. Default is False.

    Returns:
        CX2Network or str: The resulting CX2Network instance or UUID if save is True.
    """
    save_string = str(save).lower()
    url = f"https://www.ndexbio.org/v2/search/network/{network_id}/query?save={save_string}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    data = {
        "searchString": search_string,
        "searchDepth": search_depth,
        "errorWhenLimitIsOver": error_when_limit_is_over,
        "directOnly": direct_only
    }
    if edge_limit is not None:
        data["edgeLimit"] = edge_limit

    response = requests.post(url, json=data, headers=headers, auth=(username, password))

    if response.status_code == 200:
        cx_data = response.json()
        #cx2_network = CX2Network(cx2_data)
        return cx_data
    if response.status_code == 201:
        return response.json().split('/')[-1]
    else:
        response.raise_for_status()
